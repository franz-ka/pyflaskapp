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
