# coding=utf-8
from ._common import *

bp_insumos = Blueprint('insumos', __name__, url_prefix='/insumos')

@bp_insumos.route("/ingresarinsumo", methods=['GET', 'POST'])
@login_required
def menu_ingresarinsumo():
    if request.method == "GET":
        db = get_db()
        insus = db.query(Insumo).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/insumos/ingresarinsumo.html',
            insus=insus
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try: checkparams(request.form, ('insumo', 'cantidad'))
        except Exception as e: return str(e), 400

        db = get_db()

        insus = request.form.getlist('insumo')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        for i, insuid in enumerate(insus):
            if i<len(cants) and cants[i] and insuid:
                insu = db.query(Insumo).get(insuid)
                insucant = int(cants[i])
                stockinsu = db.query(StockInsumo).get(insuid)

                #sumamos stock de insumo
                inc_stock_insumo(insu, stockinsu, insucant, dtnow, INSU_STOCK_CAUSA.INGRESO)

        db.commit()

        return ''

@bp_insumos.route("/stockinsumos", methods=['GET', 'POST'])
@login_required
def menu_stockinsumos():
    if request.method == "GET":
        db = get_db()
        DATA = db.query(StockInsumo).join(Insumo).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/insumos/stockinsumos.html',
            DATA=DATA
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        return redirect(url_for('main.menu_stockinsumos'))

@bp_insumos.route("/exportar/stockinsumos.csv", methods=['GET'])
@login_required
def exportar_stockinsumos():
    db = get_db()
    stoins = db.query(StockInsumo).join(Insumo).order_by(Insumo.nombre).all()

    ex = CsvExporter('stockinsumos.csv')
    ex.writeHeaders('Id,Nombre,Cantidad,Actualizado')
    for s in stoins:
        ex.writeVals([s.insumo_id, s.insumo.nombre, s.cantidad, s.fecha])
    return ex.send()

@bp_insumos.route("/asociarinsumospika", methods=['GET', 'POST'])
@login_required
def menu_asociarinsumospika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).order_by(Pika.nombre).all()
        insus = db.query(Insumo).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/insumos/asociarinsumospika.html',
            pikas=pikas,
            insus=insus
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('pika', 'insumo', 'cantidad'))
        except Exception as e:
            return str(e), 400

        db = get_db()
        insus = request.form.getlist('insumo')
        cants = request.form.getlist('cantidad')
        pika = db.query(Pika).get(int(request.form['pika']))
        pikainsus =  db.query(PikaInsumo).filter(PikaInsumo.pika==pika)
        for i, insuid in enumerate(insus):
            if i<len(cants) and cants[i] and insuid:
                insu = db.query(Insumo).get(insuid)
                insucant = int(cants[i])

                #update/add
                insuexist = pikainsus.filter(PikaInsumo.insumo == insu).one_or_none()
                if insuexist:
                    insuexist.cantidad = insucant
                else:
                    db.add(PikaInsumo(pika=pika, insumo=insu, cantidad=insucant))

        db.commit()

        return ''

@bp_insumos.route("/listadoinsumospikas", methods=['GET'])
@login_required
def menu_listadoinsumospikas():
    db = get_db()
    pikainsus = db.query(PikaInsumo).join(Pika).order_by(Pika.nombre).all()

    r = make_response(render_template(
        'menu/insumos/listadoinsumospikas.html',
        pikainsus=pikainsus
    ))

    return r

@bp_insumos.route("/rolloplaabierto", methods=['GET', 'POST'])
@login_required
def menu_rolloplaabierto():
    if request.method == "GET":
        db = get_db()
        plas = db.query(Insumo).join(StockInsumo).filter(Insumo.nombre.ilike("pla %") & StockInsumo.cantidad > 0).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/insumos/rolloplaabierto.html',
            plas=plas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('rollopla', 'cantidad'))
        except Exception as e:
            return str(e), 400

        db = get_db()

        rollos = request.form.getlist('rollopla')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        for i, rolloid in enumerate(rollos):
            if i<len(cants) and cants[i] and rolloid:
                rollo = db.query(Insumo).get(rolloid)
                rollocant = int(cants[i])
                stockrollo = db.query(StockInsumo).get(rolloid)

                if stockrollo.cantidad < rollocant:
                    return 'No hay suficiente stock del rollo "{}" (hay {}, requiere {})'.format(rollo.nombre, stockrollo.cantidad, rollocant), 400

                #restamos stock de rollo
                inc_stock_insumo(rollo, stockrollo, -rollocant, dtnow, INSU_STOCK_CAUSA.ABIERTO)

        db.commit()

        if not current_app.config['DEBUG_FLASK']:
            check_alarmas()

        return ''

@bp_insumos.route("/agregeliminsu", methods=['GET', 'POST'])
@login_required
def menu_agregeliminsu():
    if request.method == "GET":
        db = get_db()
        insus = db.query(Insumo).order_by(Insumo.nombre).all()
        tipoinsus = db.query(InsumoTipo).all()

        r = make_response(render_template(
            'menu/insumos/agregeliminsu.html',
            tipoinsus=tipoinsus,
            insus=insus
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombreinsu','tipoinsu'))
            except Exception as e:
                return str(e), 400
        elif request.form['operation'] == 'delete':
            try:
                checkparams(request.form, ('insumo',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400

        db = get_db()

        if request.form['operation'] == 'add':
            if db.query(Insumo).filter(Insumo.nombre==request.form['nombreinsu']).first():
                return 'Ya existe un insumo con ese nombre', 400
            tipoinsu = int(request.form['tipoinsu'])
            insu = Insumo(nombre=request.form['nombreinsu'], insumotipo_id=tipoinsu)
            db.add(insu)
            db.add(StockInsumo(insumo=insu, cantidad=0, fecha=datetime.datetime.now()))
            if request.form['alarmacantidad']:
                db.add(Alarma(insumo=insu, cantidad=int(request.form['alarmacantidad'])))
        elif request.form['operation'] == 'delete':
            insu = db.query(Insumo).get(int(request.form['insumo']))
            db.query(PikaInsumo).filter(PikaInsumo.insumo==insu).delete()
            db.query(MovStockInsumo).filter(MovStockInsumo.insumo==insu).delete()
            db.query(StockInsumo).filter(StockInsumo.insumo==insu).delete()
            db.query(Alarma).filter(Alarma.insumo==insu).delete()
            db.query(Insumo).filter(Insumo.id==insu.id).delete()

        db.commit()

        return ''

@bp_insumos.route("/modificarstockinsu", methods=['GET', 'POST'])
@login_required
def menu_modificarstockinsu():
    if request.method == "GET":
        db = get_db()
        insus = db.query(Insumo).order_by(Insumo.nombre).all()
        stocks = db.query(StockInsumo).all()

        r = make_response(render_template(
            'menu/insumos/modificarstockinsu.html',
            insus=insus,
            stocks=stocks
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('insumo', 'cantidadnueva'))
        except Exception as e:
            return str(e), 400

        db = get_db()

        insu = db.query(Insumo).get(request.form['insumo'])
        stockinsu = db.query(StockInsumo).get(request.form['insumo'])
        insucant = int(request.form['cantidadnueva'])
        dtnow = datetime.datetime.now()

        # modificamos stock de insumo
        set_stock_insumo(insu, stockinsu, insucant, dtnow, INSU_STOCK_CAUSA.MANUAL)

        db.commit()

        if not current_app.config['DEBUG_FLASK']:
            check_alarma(insu)

        return ''

@bp_insumos.route("/insumoabierto", methods=['GET', 'POST'])
@login_required
def menu_insumoabierto():
    if request.method == "GET":
        db = get_db()
        tipoinsu_consumible = db.query(InsumoTipo).filter(InsumoTipo.nombre=='Consumible').one()
        insuscons = db.query(Insumo).join(StockInsumo).filter(Insumo.insumotipo == tipoinsu_consumible, StockInsumo.cantidad > 0, ~Insumo.nombre.ilike("pla %")).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/insumos/insumoabierto.html',
            insuscons=insuscons
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('insumo_consumible', 'cantidad'))
        except Exception as e:
            return str(e), 400

        db = get_db()

        insuscons = request.form.getlist('insumo_consumible')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        for i, insuconsid in enumerate(insuscons):
            if i<len(cants) and cants[i] and insuconsid:
                insucons = db.query(Insumo).get(insuconsid)
                insuconscant = int(cants[i])
                stockinsucons = db.query(StockInsumo).get(insuconsid)

                if stockinsucons.cantidad < insuconscant:
                    return 'No hay suficiente stock del insumo consumible "{}" (hay {}, requiere {})'.format(insucons.nombre, stockinsucons.cantidad, insuconscant), 400

                #restamos stock de insumo consumible
                inc_stock_insumo(insucons, stockinsucons, -insuconscant, dtnow, INSU_STOCK_CAUSA.ABIERTO)

        db.commit()

        if not current_app.config['DEBUG_FLASK']:
            check_alarmas()

        return ''

@bp_insumos.route("/listadoeditable", methods = ['GET', 'POST'])
@login_required
def menu_listadoeditable():
    if request.method == "GET":
        db = get_db()
        insumos = db.query(Insumo).order_by(Insumo.nombre).all()
        tipoinsus = db.query(InsumoTipo).all()

        r = make_response(render_template(
            'menu/insumos/listadoeditable.html',
            insumos=insumos,
            tipoinsus=tipoinsus
        ))
        return r
    else: #request.method == "POST":
        print('post form:',request.form)

        try: checkparams(request.form, ('operation', 'insu_id'))
        except Exception as e: return str(e), 400

        db = get_db()

        insumo = db.query(Insumo).get(request.form['insu_id'])
        operation = request.form['operation']
        if operation == 'cambiar_tipo':
            tipo = int(request.form['tipoinsu'])
            insumo.insumotipo_id = tipo
        elif operation == 'cambiar_nombre':
            nombre = request.form['nombreinsu'].strip()
            insumo.nombre = nombre
        else:
            return 'Operación inválida', 400

        db.commit()

        return ''

@bp_insumos.route("/movimientosstock", methods=['GET', 'POST'])
@login_required
def menu_movimientosstock():
    if request.method == "GET":
        db = get_db()

        limit = 300
        insus = db.query(Insumo).order_by(Insumo.nombre).all()
        if len(request.args) and request.args['insumo']:
            insuid = int(request.args['insumo'])
            insu = db.query(Insumo).get(insuid)
            movstocks = db.query(MovStockInsumo) \
                .filter(MovStockInsumo.insumo_id==insuid) \
                .order_by(MovStockInsumo.fecha.asc()) \
                .limit(limit).all()
        else:
            insu = None
            movstocks = db.query(MovStockInsumo) \
                .order_by(MovStockInsumo.fecha.asc()) \
                .limit(limit).all()

        diferenciales = {}
        for mov in movstocks:
            if not mov.insumo_id in diferenciales:
                mov.diferencial = ''
            else:
                mov.diferencial = mov.cantidad - diferenciales[mov.insumo_id]
            diferenciales[mov.insumo_id] = mov.cantidad
        movstocks.reverse()

        r = make_response(render_template(
            'menu/insumos/movimientosstock.html',
            insus=insus,
            insu=insu,
            movstocks=movstocks,
            truncated=len(movstocks)==limit
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        return redirect(url_for('main.menu_stockinsumos'))

@bp_insumos.route("/exportar/movimientosstock.csv", methods=['GET'])
@login_required
def exportar_movimientosstock():
    db = get_db()

    if len(request.args) and request.args['insumo']:
        insuid = int(request.args['insumo'])
        movstocks = db.query(MovStockInsumo).join(Insumo).filter(MovStockInsumo.insumo_id==insuid).order_by(MovStockInsumo.fecha.asc()).all()
    else:
        movstocks = db.query(MovStockInsumo).join(Insumo).order_by(MovStockInsumo.fecha.asc()).all()

    diferenciales = {}
    for mov in movstocks:
        if not mov.insumo_id in diferenciales:
            mov.diferencial = ''
        else:
            mov.diferencial = mov.cantidad - diferenciales[mov.insumo_id]
        diferenciales[mov.insumo_id] = mov.cantidad
    movstocks.reverse()

    ex = CsvExporter('stockinsumos.csv')
    ex.writeHeaders('Id,Nombre,Diferencial,Stock,Causa,Fecha')
    for m in movstocks:
        ex.writeVals([m.insumo_id, m.insumo.nombre, m.diferencial, m.cantidad, m.causa, m.fecha])
    return ex.send()


@bp_insumos.route("/stockextendidoinsumos", methods=['GET', 'POST'])
@login_required
def menu_stockextendidoinsumos():
    if request.method == "GET":

        db = get_db()

        try:
            rango_tiempo_semanas = int(db.query(Valor).filter(Valor.nombre=='insumos_stock_extendido_semanas').one().valor)
        except:
            rango_tiempo_semanas = 10
        dtnow = datetime.datetime.now()
        dtcomienzo = dtnow - datetime.timedelta(days=rango_tiempo_semanas*7)
        print(f'El parámetro de rango de semanas es {rango_tiempo_semanas}. Tomando como fecha de inicio {dtcomienzo}')

        # Traemos movimientos históricos de stock de insumos
        movstocks = db.query(MovStockInsumo) \
            .filter(MovStockInsumo.fecha >= dtcomienzo) \
            .order_by(MovStockInsumo.insumo_id, MovStockInsumo.fecha.asc()) \
            .all()
        print(f'Encontrados {len(movstocks)} movimientos de stock')

        InsumoValores = collections.namedtuple('InsumoValores', 'consumo_total, stock_actual')
        insumos_valores = {}

        # Agrupamos movimientos por insumo
        # itertools.groupby() in Python - https://www.geeksforgeeks.org/itertools-groupby-in-python/
        key_func = lambda i: i.insumo_id
        for insumo_id, insumo_movstocks in itertools.groupby(movstocks, key_func):

            # Viene como enumerador así que lo convertimos a lista
            insumo_movstocks = list(insumo_movstocks)
            primer_stock = insumo_movstocks[0]
            print(f'Analizando {len(insumo_movstocks)} movimientos de stock de insumo {insumo_id}')

            # Traemos el movimiento justo anterior al primer movimiento de nuestra lista
            # (si existe)
            pre_primer_stock = db.query(MovStockInsumo) \
                .filter(MovStockInsumo.insumo_id == insumo_id, MovStockInsumo.fecha < primer_stock.fecha) \
                .order_by(MovStockInsumo.fecha.desc()) \
                .first()

            # Si existe usarlo para calcular el primer (posible) consumo. Si no existe
            # el primer bucle del for va a estar de más pero no genera problemas.
            if pre_primer_stock:
                stock_inicial = pre_primer_stock.cantidad
            else:
                stock_inicial = primer_stock.cantidad

            consumo_total = 0
            last_stock = stock_inicial
            for movstock in insumo_movstocks:
                # Si el stock actual es menor al stock anterior, hubo consumo
                if movstock.cantidad < last_stock:
                    consumo_total += last_stock - movstock.cantidad
                last_stock = movstock.cantidad

            # Guardamos valores
            insumos_valores[insumo_id] = InsumoValores(consumo_total=consumo_total, stock_actual=last_stock)

        print(f'Valores de insumos:')
        # Cargamos valores como campos "naturales" de insumos
        insumos = db.query(Insumo).filter(Insumo.id.in_(insumos_valores.keys())).all()
        for insumo in insumos:
            insumo_valores = insumos_valores[insumo.id]
            insumo.consumo_total = insumo_valores.consumo_total
            insumo.stock_actual = insumo_valores.stock_actual
            print(f'- {insumo.nombre}: consumo={insumo.consumo_total}, stock={insumo.stock_actual}')

        insumos_no_repuestos = [insumo for insumo in insumos if insumo.fecha_ultima_reposicion is None]
        insumos_repuestos = [insumo for insumo in insumos if insumo.fecha_ultima_reposicion is not None]

        r = make_response(render_template(
            'menu/insumos/stockextendidoinsumos.html',
            insumos=insumos_no_repuestos+insumos_repuestos,
            rango_tiempo_semanas=rango_tiempo_semanas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('rango_tiempo',))
        except Exception as e:
            return str(e), 400

        db = get_db()

        valor = db.query(Valor).filter(Valor.nombre=='insumos_stock_extendido_semanas').one()
        valor.valor = request.form['rango_tiempo']

        db.commit()

        return redirect(url_for('insumos.menu_stockextendidoinsumos'))

@bp_insumos.route("/stockextendidoinsumos-guardar", methods=['POST'])
@login_required
def stockextendidoinsumos_guardar():
    print('post form:',request.form)

    try: checkparams(request.form, ('insumo_id', 'delay', 'margen', 'ciclo'))
    except Exception as e: return str(e), 400

    db = get_db()

    insumo = db.query(Insumo).get(request.form['insumo_id'])
    try: delay = int(request.form['delay'] or 0)
    except ValueError as e: return 'Número de delay de reposición inválido', 400
    try: margen = int(request.form['margen'] or 0)
    except ValueError as e: return 'Número de margen de seguridad inválido', 400
    try: ciclo = int(request.form['ciclo'] or 0)
    except ValueError as e: return 'Número de ciclo de reposición inválido', 400
    insumo.delay_reposicion = delay
    insumo.margen_seguridad = margen
    insumo.ciclo_reposicion = ciclo

    db.commit()

    return f'{{"delay":"{delay}", "margen":"{margen}", "ciclo":"{ciclo}"}}'

@bp_insumos.route("/stockextendidoinsumos-reponer", methods=['POST'])
@login_required
def stockextendidoinsumos_reponer():
    print('post form:',request.form)

    try: checkparams(request.form, ('insumo_id','marcar'))
    except Exception as e: return str(e), 400

    db = get_db()

    marcar = int(request.form['marcar'])
    insumo = db.query(Insumo).get(request.form['insumo_id'])
    if marcar:
        dtnow = datetime.datetime.now()
        insumo.fecha_ultima_reposicion = dtnow
    else:
        insumo.fecha_ultima_reposicion = None


    db.commit()

    return f'{{"msg":"ok"}}'
