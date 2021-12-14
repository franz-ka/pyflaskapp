# coding=utf-8
from ._common import *

bp_pikas = Blueprint('pikas', __name__, url_prefix='/pikas')


@bp_pikas.route("/ingresarprestock", methods=['GET', 'POST'])
@login_required
def menu_ingresarprestock():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).order_by(Pika.nombre).all()
        svg_icon = open(current_app._static_path + '/img/box.svg').read()

        r = make_response(render_template(
            'menu/pikas/ingresarprestock.html',
            svg_icon=svg_icon,
            pikas=pikas
        ))

        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try: checkparams(request.form, ('pika', 'cantidad'))
        except Exception as e: return str(e), 400

        db = get_db()

        pikas = request.form.getlist('pika')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        tipoinsu_prestock = db.query(InsumoTipo).filter(InsumoTipo.nombre == 'Prestock').one()
        for i, pikaid in enumerate(pikas):
            if i < len(cants) and cants[i] and pikaid:
                pika = db.query(Pika).get(pikaid)
                pikacant = int(cants[i])
                prestock = db.query(PrestockPika).get(pikaid)
                pikainsus = db.query(PikaInsumo).join(Insumo).filter(PikaInsumo.pika == pika, Insumo.insumotipo == tipoinsu_prestock)

                # restamos stock de insumos de prestock
                for pikainsu in pikainsus:
                    stockinsu = db.query(StockInsumo).get(pikainsu.insumo_id)
                    if stockinsu.cantidad < pikainsu.cantidad * pikacant:
                        return 'No hay suficiente stock de "{}" para el pika "{}" (hay {}, requiere {})'.format(pikainsu.insumo.nombre, pika.nombre, stockinsu.cantidad, pikainsu.cantidad * pikacant), 400

                    inc_stock_insumo(pikainsu.insumo, stockinsu, -pikainsu.cantidad * pikacant, dtnow, INSU_STOCK_CAUSA.PRESTOCK)

                inc_prestock_pika(pika, prestock, cants[i], dtnow, 'ingreso prestock')

        db.commit()

        if not current_app.config['DEBUG_FLASK']:
            check_alarmas(current_app)

        return ''


@bp_pikas.route("/armadopika", methods=['GET', 'POST'])
@login_required
def menu_armadopika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).order_by(Pika.nombre).all()
        svg_icon = open(current_app._static_path + '/img/arrow.svg').read()

        r = make_response(render_template(
            'menu/pikas/armadopika.html',
            svg_icon=svg_icon,
            pikas=pikas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try: checkparams(request.form, ('pika', 'cantidad'))
        except Exception as e: return str(e), 400

        db = get_db()

        pikas = request.form.getlist('pika')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        tipoinsu_armado = db.query(InsumoTipo).filter(InsumoTipo.nombre == 'Armado').one()
        for i, pikaid in enumerate(pikas):
            if i < len(cants) and cants[i] and pikaid:
                pika = db.query(Pika).get(pikaid)
                pikacant = int(cants[i])
                prestockpika = db.query(PrestockPika).get(pikaid)
                stockpika = db.query(StockPika).get(pikaid)
                pikainsus = db.query(PikaInsumo).join(Insumo).filter(PikaInsumo.pika == pika, Insumo.insumotipo == tipoinsu_armado)

                if pikacant > prestockpika.cantidad:
                    return 'No hay suficiente prestock para el pika "{}" (hay {}, requiere {})'.format(
                        pika.nombre, prestockpika.cantidad, pikacant), 400

                # restamos prestock
                inc_prestock_pika(pika, prestockpika, -pikacant, dtnow, 'armado pika')

                # restamos stock de insumos de armado
                for pikainsu in pikainsus:
                    stockinsu = db.query(StockInsumo).get(pikainsu.insumo_id)
                    if stockinsu.cantidad < pikainsu.cantidad * pikacant:
                        return 'No hay suficiente stock de "{}" para el pika "{}" (hay {}, requiere {})'.format(pikainsu.insumo.nombre, pika.nombre, stockinsu.cantidad, pikainsu.cantidad * pikacant), 400

                    inc_stock_insumo(pikainsu.insumo, stockinsu, -pikainsu.cantidad * pikacant, dtnow, INSU_STOCK_CAUSA.ARMADO)

                # sumamos stock
                inc_stock_pika(pika, stockpika, pikacant, dtnow, 'armado pika')

        db.commit()

        if not current_app.config['DEBUG_FLASK']:
            check_alarmas(current_app)

        return ''


@bp_pikas.route("/stockpikas", methods=['GET', 'POST'])
@login_required
def menu_stockpikas():
    if request.method == "GET":
        db = get_db()
        # esto devuelve un array de listas de 4 elementos [0]=Pika [1]=PrestockPika [2]=StockPika
        pedidos_query = db.query(VentaPika.pika_id, func.sum(VentaPika.cantidad).label('pedidos')) \
            .join(Venta) \
            .filter(Venta.fecha_pedido != None) \
            .filter(Venta.fecha == None) \
            .group_by(VentaPika.pika_id) \
            .subquery()

        DATA = db.query(Pika, PrestockPika, StockPika, pedidos_query.columns.pedidos) \
            .join(PrestockPika) \
            .join(StockPika) \
            .join(pedidos_query, Pika.id == pedidos_query.columns.pika_id, isouter=True) \
            .order_by(Pika.nombre) \
            .all()

        pikascolores = db.query(StockPikaColor).all()
        pikascolores_modif = {}
        for pc in pikascolores:
            pikascolores_modif[pc.pika_id] = [pc.cantidad_bajo, pc.cantidad_medio]
        print(pikascolores_modif)

        r = make_response(render_template(
            'menu/pikas/stockpikas.html',
            DATA=DATA,
            pikascolores=pikascolores_modif
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        return redirect(url_for('main.menu_stockpikas'))


@bp_pikas.route("/exportar/stockpikas.csv", methods=['GET'])
@login_required
def exportar_stockpikas():
    db = get_db()
    stopiks = db.query(Pika, PrestockPika, StockPika).filter(Pika.id == PrestockPika.pika_id).filter(Pika.id == StockPika.pika_id).order_by(Pika.nombre).all()

    ex = CsvExporter('stockpikas.csv')
    ex.writeHeaders('Id,Nombre,Prestock,Stock,Total,Actualizado')
    for pika_spika_pspika in stopiks:
        # print(pika_spika_pspika)
        fecha_mayor = pika_spika_pspika[1].fecha if pika_spika_pspika[1].fecha > pika_spika_pspika[2].fecha else pika_spika_pspika[2].fecha
        ex.writeVals([
            pika_spika_pspika[0].id,
            pika_spika_pspika[0].nombre,
            pika_spika_pspika[1].cantidad,
            pika_spika_pspika[2].cantidad,
            pika_spika_pspika[1].cantidad + pika_spika_pspika[2].cantidad,
            fecha_mayor])
    return ex.send()


@bp_pikas.route("/agregelimpika", methods=['GET', 'POST'])
@login_required
def menu_agregelimpika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).all()

        r = make_response(render_template(
            'menu/pikas/agregelimpika.html',
            pikas=pikas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombrepika',))
            except Exception as e:
                return str(e), 400
        elif request.form['operation'] == 'hide':
            try:
                checkparams(request.form, ('pika',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400

        db = get_db()

        if request.form['operation'] == 'add':
            dtnow = datetime.datetime.now()

            if db.query(Pika).filter(Pika.nombre == request.form['nombrepika']).first():
                return str('Ya existe un pika con ese nombre'), 400
            # siempre al agregar un pika se debe agregar su StockPika en 0 sino después hay errores
            pika = Pika(nombre=request.form['nombrepika'], oculto=False)
            db.add(pika)

            prestockpika = PrestockPika(pika=pika, cantidad=0, fecha=dtnow)
            stockpika = StockPika(pika=pika, cantidad=0, fecha=dtnow)
            db.add(prestockpika)
            db.add(stockpika)
            set_prestock_pika(pika, prestockpika, 0, dtnow, 'nuevo pika')
            set_stock_pika(pika, stockpika, 0, dtnow, 'nuevo pika')
        elif request.form['operation'] == 'hide':
            pika = db.query(Pika).get(request.form['pika'])
            pika.oculto = True
            db.commit()

        db.commit()

        return ''


@bp_pikas.route("/modificarstockpika", methods=['GET', 'POST'])
@login_required
def menu_modificarstockpika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).order_by(Pika.nombre).all()
        prestocks = db.query(PrestockPika).all()
        stocks = db.query(StockPika).all()

        r = make_response(render_template(
            'menu/pikas/modificarstockpika.html',
            pikas=pikas,
            prestocks=prestocks,
            stocks=stocks
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('pika',))
        except Exception as e:
            return str(e), 400

        if not (request.form['precantidadnueva'] or request.form['cantidadnueva']):
            return str('Debe proporcionar algún número de stock nuevo'), 400

        db = get_db()

        pika = db.query(Pika).get(request.form['pika'])
        dtnow = datetime.datetime.now()

        if request.form['precantidadnueva']:
            pikacant = int(request.form['precantidadnueva'])
            prestockpika = db.query(PrestockPika).get(request.form['pika'])

            set_prestock_pika(pika, prestockpika, pikacant, dtnow, 'modificación manual')

        if request.form['cantidadnueva']:
            pikacant = int(request.form['cantidadnueva'])
            stockpika = db.query(StockPika).get(request.form['pika'])

            set_stock_pika(pika, stockpika, pikacant, dtnow, 'modificación manual')

        db.commit()

        return ''


@bp_pikas.route("/modificarcolorpikas", methods=['GET', 'POST'])
@login_required
def menu_modificarcolorpikas():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).all()
        pikascolores = db.query(StockPikaColor).all()

        r = make_response(render_template(
            'menu/pikas/modificarcolorpikas.html',
            pikas=pikas,
            pikascolores=pikascolores
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('pika',))
        except Exception as e:
            return str(e), 400

        if not (request.form['cantidad_bajo_nueva'] or request.form['cantidad_medio_nueva']):
            return str('Debe proporcionar alguna cantidad nueva'), 400

        db = get_db()

        pika = db.query(Pika).get(request.form['pika'])
        stockpikacolor = db.query(StockPikaColor).get(request.form['pika'])
        if not stockpikacolor:
            stockpikacolor = StockPikaColor(pika=pika)
            db.add(stockpikacolor)

        if request.form['cantidad_bajo_nueva']:
            colorcant = int(request.form['cantidad_bajo_nueva'])
            stockpikacolor.cantidad_bajo = colorcant

        if request.form['cantidad_medio_nueva']:
            colorcant = int(request.form['cantidad_medio_nueva'])
            stockpikacolor.cantidad_medio = colorcant

        db.commit()

        return ''


@bp_pikas.route("/factoresdeimpresion", methods=['GET', 'POST'])
@login_required
def menu_factoresdeimpresion():
    if request.method == "GET":
        db = get_db()
        # pikas = db.query(Pika).order_by(Pika.nombre).all()
        # factores = db.query(FactorProductividad).all()
        pika_factores = db.query(Pika, FactorProductividad).outerjoin(FactorProductividad).all()

        from sqlalchemy import func
        dias_factor = 60.0
        dtnow = datetime.datetime.now()
        dtventas = dtnow - datetime.timedelta(days=dias_factor)
        # print(dias_factor, dtventas)

        # ventapikas = db.query(VentaPika).join(Venta).filter(Venta.fecha != None)
        ventapikas = db.query(
            VentaPika.pika_id,
            func.sum(VentaPika.cantidad / dias_factor).label('total')
        ).join(Venta
        ).filter(Venta.fecha != None
        ).filter(Venta.fecha >= dtventas
        ).group_by(VentaPika.pika_id
        ).all()
        # print(ventapikas)

        ventas_promedios = {}
        for pika_id, venta_promedio in ventapikas:
            ventas_promedios[pika_id] = "{0:.2f}".format(venta_promedio)
        # print(ventas_promedios)

        r = make_response(render_template(
            'menu/pikas/factoresdeimpresion.html',
            pika_factores=pika_factores,
            dias_factor=dias_factor,
            dtventas=dtventas,
            ventas_promedios=ventas_promedios
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try: checkparams(request.form, ('pika_id', 'factor_nuevo'))
        except Exception as e: return str(e), 400

        db = get_db()

        pika = db.query(Pika).get(request.form['pika_id'])
        factor_cant = float(request.form['factor_nuevo'])
        dtnow = datetime.datetime.now()

        factorprod = db.query(FactorProductividad).get(pika.id)
        if not factorprod:
            factorprod = FactorProductividad(pika=pika, factor=factor_cant, fecha_actualizado=dtnow)
            db.add(factorprod)
        else:
            factorprod.factor = factor_cant
            factorprod.fecha_actualizado = dtnow

        db.commit()

        return ''


@bp_pikas.route("/graficostock", methods=['GET', 'POST'])
@login_required
def menu_graficostock():
    if request.method == "GET":
        pikas_select = request.args.get('pikas_select', 'cogos')
        fecha_desde = request.args.get('fechadesde')
        fecha_hasta = request.args.get('fechahasta')

        '''
        El script general de gráficos tiene dos inputs:
        La cantidad de días desde hoy hacia el pasado a tomar = D
        Los ids de picas a mirar = Ps

        El gráfico tiene un punto por cada día desde D hasta hoy
        Cada punto muestra el prestock+stock-pedidos que había en ese momento
        Por ende, hay que traer estos 3 datos

        Prestock y stock provienen de sus respectivas tablas de movimiento
        Pedidos hay que deducirlo de la tabla de ventas
        Todo filtrado por los pikas ids que se seleccionaron

        Dado un punto X en el gráfico (fecha), se mira
        - el pre/stock con max(mov.fecha<=X)
        - la venta con fecha_pedido <= X y fecha_venta[= None or > X]
        '''

        class PikaData:

            def __init__(self, id, nombre):
                self.id = id
                self.nombre = nombre
                self.movs_prestock = None
                self.movs_stock = None
                self.pedidos = None
                self.points = []
                self.points_data = []

            def print(self):
                print(f'Pika id={self.id}, nombre={self.nombre}')
                print(f'- movs_prestock:')
                pprint(self.movs_prestock)
                print(f'- movs_stock:')
                pprint(self.movs_stock)
                print(f'- pedidos:')
                pprint(self.pedidos)

            def print_points(self):
                print(f'Pika id={self.id}, nombre={self.nombre}')
                print(f'- points:')
                pprint(self.points)
                print(f'- points_data:')
                pprint(self.points_data)

        pikas = {}

        def grouperPikaId(item):
            if (hasattr(item, 'VentaPika')):
                return item.VentaPika.pika_id
            else:
                return item.pika_id

        db = get_db()

        # Parámetros iniciales
        dtend_default = datetime.datetime.now() #+ datetime.timedelta(days=1) #datetime.datetime(day=25, month=11, year=2019)#
        dtend = datetime.datetime.strptime(fecha_hasta,'%d/%m/%Y') if fecha_hasta else dtend_default
        if fecha_desde:
            dtstart = datetime.datetime.strptime(fecha_desde,'%d/%m/%Y')
        else:
            dtstart = dtend - datetime.timedelta(days=60)
        days_totales = (dtend - dtstart).days
        print(f"Días totales={days_totales}, fecha comienzo={dtstart}, fecha fin={dtend}")

        # Traer ids y nombres de pikas
        pikas_sql = db.query(Pika)
        if pikas_select == 'todos':
            pass
        elif pikas_select == 'cogos':
            pikas_sql = pikas_sql.filter(Pika.nombre.ilike('cogo %'))
        elif pikas_select == 'minis':
            pikas_sql = pikas_sql.filter(Pika.nombre.ilike('mini %'))
        elif pikas_select == 'xls':
            pikas_sql = pikas_sql.filter(Pika.nombre.ilike('xl %'))
        pikas_sql = pikas_sql.all()

        # Cargar
        for pika in pikas_sql:
            pikas[pika.id] = PikaData(pika.id, pika.nombre)

        # Traer stocks de pikas
        first_prestock = db.query(MovPrestockPika).order_by(MovPrestockPika.fecha).limit(1).one()

        movprestock = db.query(MovPrestockPika) \
            .filter(MovPrestockPika.fecha >= dtstart, MovPrestockPika.pika_id.in_(pikas.keys())) \
            .order_by(MovPrestockPika.pika_id, MovPrestockPika.fecha) \
            .all()

        movstock = db.query(MovStockPika) \
            .filter(MovStockPika.fecha >= dtstart, MovStockPika.pika_id.in_(pikas.keys())) \
            .order_by(MovStockPika.pika_id, MovStockPika.fecha) \
            .all()

        pedidos = db.query(VentaPika, Venta) \
            .join(Venta) \
            .filter(
                Venta.fecha_pedido != None,
                Venta.fecha_pedido >= dtstart,  # no queremos pedidos históricos, solo los del plazo
                or_(Venta.fecha == None, Venta.fecha > dtstart),  # si se vendieron antes del comienzo del plazo no nos interesan (ya se contabilizan en los stocks)
                VentaPika.pika_id.in_(pikas.keys())
            ) \
            .order_by(VentaPika.pika_id, Venta.fecha_pedido) \
            .all()

        # Cargar stocks en objetos de pikas
        for pika_id, movs in itertools.groupby(movprestock, grouperPikaId):
            pikas[pika_id].movs_prestock = list(movs)

        for pika_id, movs in itertools.groupby(movstock, grouperPikaId):
            pikas[pika_id].movs_stock = list(movs)

        for pika_id, peds in itertools.groupby(pedidos, grouperPikaId):
            pikas[pika_id].pedidos = list(peds)

        # Reportar data de pikas cargada
        for p in pikas.values():
            print('=' * 50, 'Pikas data')
            p.print()

        # Calcular puntos de gráfico (+ 1 porque hay que contar el día de hoy)
        print('@' * 50, 'Days data')
        fechas = []
        for day in range(days_totales + 1):
            date = dtstart + datetime.timedelta(days=day)
            fechas.append(date.strftime("%d/%m/%Y"))
            print(f"Day {day}, dtstart={dtstart}, date={date}")

            for pika in pikas.values():
                # Calculamos la última actualización de prestock antes (o igual) que la fecha del punto
                if pika.movs_prestock:
                    for mov in pika.movs_prestock:
                        if mov.fecha > date:
                            break
                    prestock = mov.cantidad
                else:
                    prestock = 0

                # Idem prestock
                if pika.movs_stock:
                    for mov in pika.movs_stock:
                        if mov.fecha > date:
                            break
                    stock = mov.cantidad
                else:
                    stock = 0

                # Calculamos pedido al día del punto
                pedido = 0
                if pika.pedidos:
                    for venta_pika, venta in pika.pedidos:
                        if venta.fecha_pedido > date:
                            break
                        # Si no se vendió, todo ok, está como pedido pendiente
                        # Si se vendió, pero después de la fecha del punto, estuvo como pedido en ese momento
                        if not venta.fecha or venta.fecha > date:
                            pedido += venta_pika.cantidad

                stock_real = prestock + stock - pedido
                pika.points.append(stock_real)
                pika.points_data.append((prestock, stock, pedido))

        # Reportar points
        for p in pikas.values():
            print('#' * 50, 'Points data')
            p.print_points()

        r = make_response(render_template(
            'menu/pikas/graficostock.html',
            pikas_nombres = [p.nombre for p in pikas.values()],
            pikas_points = [p.points for p in pikas.values()],
            fechas = fechas,
            filter_params = {
                'pikas_select': pikas_select,
                'fechadesde': dtstart.strftime("%d/%m/%Y") if fecha_desde else '',
                'fechahasta': dtend.strftime("%d/%m/%Y")
            },
            first_prestock = first_prestock.fecha.strftime("%d/%m/%Y") if dtstart <= first_prestock.fecha else ''
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try: checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e: return str(e), 400

        db = get_db()

        pass

        db.commit()

        return ''
