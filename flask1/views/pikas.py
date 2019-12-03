# coding=utf-8
from ._common import *

bp_pikas = Blueprint('pikas', __name__, url_prefix='/pikas')

@bp_pikas.route("/ingresarprestock", methods = ['GET', 'POST'])
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
    else: #request.method == "POST":
        print('post form:',request.form)

        try: checkparams(request.form, ('pika', 'cantidad'))
        except Exception as e: return str(e), 400

        db = get_db()

        pikas = request.form.getlist('pika')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        tipoinsu_prestock = db.query(InsumoTipo).filter(InsumoTipo.nombre=='Prestock').one()
        for i, pikaid in enumerate(pikas):
            if i<len(cants) and cants[i] and pikaid:
                pika = db.query(Pika).get(pikaid)
                pikacant = int(cants[i])
                prestock = db.query(PrestockPika).get(pikaid)
                pikainsus = db.query(PikaInsumo).join(Insumo).filter(PikaInsumo.pika==pika, Insumo.insumotipo==tipoinsu_prestock)
                
                #restamos stock de insumos de prestock
                for pikainsu in pikainsus:
                    stockinsu = db.query(StockInsumo).get(pikainsu.insumo_id)
                    if stockinsu.cantidad < pikainsu.cantidad*pikacant:
                        return 'No hay suficiente stock de "{}" para el pika "{}" (hay {}, requiere {})'.format(pikainsu.insumo.nombre, pika.nombre, stockinsu.cantidad, pikainsu.cantidad*pikacant), 400

                    movinsu = MovStockInsumo(insumo=pikainsu.insumo, cantidad=pikainsu.cantidad, fecha=dtnow)
                    db.add(movinsu)
                    stockinsu.cantidad -= movinsu.cantidad*pikacant
                    stockinsu.fecha = movinsu.fecha

                inc_prestock_pika(pika, prestock, cants[i], dtnow, 'ingreso prestock')

        db.commit()

        check_alarmas()

        return ''

@bp_pikas.route("/armadopika", methods = ['GET', 'POST'])
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
    else: #request.method == "POST":
        print('post form:',request.form)

        try: checkparams(request.form, ('pika', 'cantidad'))
        except Exception as e: return str(e), 400

        db = get_db()

        pikas = request.form.getlist('pika')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        tipoinsu_armado = db.query(InsumoTipo).filter(InsumoTipo.nombre=='Armado').one()
        for i, pikaid in enumerate(pikas):
            if i<len(cants) and cants[i] and pikaid:
                pika = db.query(Pika).get(pikaid)
                pikacant = int(cants[i])
                prestockpika = db.query(PrestockPika).get(pikaid)
                stockpika = db.query(StockPika).get(pikaid)
                pikainsus = db.query(PikaInsumo).join(Insumo).filter(PikaInsumo.pika==pika, Insumo.insumotipo==tipoinsu_armado)

                if pikacant > prestockpika.cantidad:
                    return 'No hay suficiente prestock para el pika "{}" (hay {}, requiere {})'.format(
                        pika.nombre, prestockpika.cantidad, pikacant), 400

                #restamos prestock
                inc_prestock_pika(pika, prestockpika, -pikacant, dtnow, 'armado pika')
                
                #restamos stock de insumos de armado
                for pikainsu in pikainsus:
                    stockinsu = db.query(StockInsumo).get(pikainsu.insumo_id)
                    if stockinsu.cantidad < pikainsu.cantidad*pikacant:
                        return 'No hay suficiente stock de "{}" para el pika "{}" (hay {}, requiere {})'.format(pikainsu.insumo.nombre, pika.nombre, stockinsu.cantidad, pikainsu.cantidad*pikacant), 400

                    movinsu = MovStockInsumo(insumo=pikainsu.insumo, cantidad=pikainsu.cantidad, fecha=dtnow)
                    db.add(movinsu)
                    stockinsu.cantidad -= movinsu.cantidad*pikacant
                    stockinsu.fecha = movinsu.fecha

                #sumamos stock
                inc_stock_pika(pika, stockpika, pikacant, dtnow, 'armado pika')

        db.commit()

        check_alarmas()

        return ''

@bp_pikas.route("/stockpikas", methods=['GET', 'POST'])
@login_required
def menu_stockpikas():
    if request.method == "GET":
        db = get_db()
        # esto devuelve un array de listas de 4 elementos [0]=Pika [1]=PrestockPika [2]=StockPika
        DATA = db.query(Pika, PrestockPika, StockPika, func.sum(VentaPika.cantidad).label('pedidos')) \
            .join(PrestockPika) \
            .join(StockPika) \
            .join(VentaPika) \
            .join(Venta) \
            .filter(Venta.fecha_pedido != None) \
            .filter(Venta.fecha == None) \
            .group_by(VentaPika.pika_id) \
            .order_by(Pika.nombre)
            
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
    stopiks = db.query(Pika, PrestockPika, StockPika).filter(Pika.id==PrestockPika.pika_id).filter(Pika.id==StockPika.pika_id).order_by(Pika.nombre).all()

    ex = CsvExporter('stockpikas.csv')
    ex.writeHeaders('Id,Nombre,Prestock,Stock,Total,Actualizado')
    for pika_spika_pspika in stopiks:
        #print(pika_spika_pspika)
        fecha_mayor = pika_spika_pspika[1].fecha if pika_spika_pspika[1].fecha > pika_spika_pspika[2].fecha else pika_spika_pspika[2].fecha
        ex.writeVals([
            pika_spika_pspika[0].id,
            pika_spika_pspika[0].nombre,
            pika_spika_pspika[1].cantidad,
            pika_spika_pspika[2].cantidad,
            pika_spika_pspika[1].cantidad+pika_spika_pspika[2].cantidad,
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
        else:
            return str('Operación inválida'), 400
        '''elif request.form['operation'] == 'delete':
        try:
            checkparams(request.form, ('id'))
        except Exception as e:
            return str(e), 400'''

        db = get_db()

        if request.form['operation'] == 'add':
            dtnow = datetime.datetime.now()
            
            if db.query(Pika).filter(Pika.nombre==request.form['nombrepika']).first():
                return str('Ya existe un pika con ese nombre'), 400
            # siempre al agregar un pika se debe agregar su StockPika en 0 sino después hay errores
            pika = Pika(nombre=request.form['nombrepika'])
            db.add(pika)
            
            prestockpika = PrestockPika(pika=pika, cantidad=0, fecha=dtnow)
            stockpika = StockPika(pika=pika, cantidad=0, fecha=dtnow)
            db.add(prestockpika)
            db.add(stockpika)
            set_prestock_pika(pika, prestockpika, 0, dtnow, 'nuevo pika')
            set_stock_pika(pika, stockpika, 0, dtnow, 'nuevo pika')
            
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
            checkparams(request.form, ('pika', ))
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

@bp_pikas.route("/modificarcolorpikas", methods = ['GET', 'POST'])
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
    else: #request.method == "POST":
        print('post form:',request.form)

        try:
            checkparams(request.form, ('pika', ))
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

@bp_pikas.route("/factoresdeimpresion", methods = ['GET', 'POST'])
@login_required
def menu_factoresdeimpresion():
    if request.method == "GET":
        db = get_db()
        #pikas = db.query(Pika).order_by(Pika.nombre).all()
        #factores = db.query(FactorProductividad).all()
        pika_factores = db.query(Pika, FactorProductividad).outerjoin(FactorProductividad).all()

        from sqlalchemy import func
        dias_factor = 60.0
        dtnow = datetime.datetime.now()
        dtventas = dtnow - datetime.timedelta(days=dias_factor)
        #print(dias_factor, dtventas)
        
        #ventapikas = db.query(VentaPika).join(Venta).filter(Venta.fecha != None)
        ventapikas = db.query(
            VentaPika.pika_id,
            func.sum(VentaPika.cantidad/dias_factor).label('total')
        ).join(Venta
        ).filter(Venta.fecha != None
        ).filter(Venta.fecha >= dtventas
        ).group_by(VentaPika.pika_id
        ).all()
        #print(ventapikas)
        
        ventas_promedios = {}
        for pika_id, venta_promedio in ventapikas:
            ventas_promedios[pika_id] = "{0:.2f}".format(venta_promedio)
        #print(ventas_promedios)

        r = make_response(render_template(
            'menu/pikas/factoresdeimpresion.html',
            pika_factores=pika_factores,
            dias_factor=dias_factor,
            dtventas=dtventas,
            ventas_promedios=ventas_promedios
        ))
        return r
    else: #request.method == "POST":
        print('post form:',request.form)

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

