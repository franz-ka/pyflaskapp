# coding=utf-8
from flask import current_app, Blueprint, request, make_response, render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user
import datetime

from flask1.db import get_db
from flask1.login import User, loginUserPass, logoutUser
from .models import *
from .csvexport import CsvExporter
from .alarmas import check_alarma, check_alarmas

bp = Blueprint('main', __name__, url_prefix='')

def checkparams(form, musthave):
    if len(form) < len(musthave):
        raise Exception('Pocos parámetros enviados ({}<{})'.format(len(form), len(musthave)))
    for v in musthave:
        if v not in form:
            raise Exception('Falta el parámetro "{}"'.format(v))


########################### ERRORES/LOGIN/OUT/INDEX
@bp.app_errorhandler(500)
def server_error(e):
    #404-error-handling https://www.geeksforgeeks.org/python-404-error-handling-in-flask/
    print(e)
    return render_template("500.html",url=request.path)

@bp.app_errorhandler(404)
def not_found(e):
    return render_template("404.html",url=request.path)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        print('post form:', request.form)

        try: checkparams(request.form, ('user', 'password'))
        except Exception as e: return str(e), 400

        if loginUserPass(request.form['user'], request.form['password']):
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            return "Credenciales inválidas", 400

@bp.route("/logout")
@login_required
def logout():
    logoutUser()
    return redirect(url_for('main.login'))

@bp.route("/")
@login_required
def index():
    r = make_response(render_template(
        'index.html'
    ))
    return r


########################### PIKAS
@bp.route("/menu/armadopika", methods = ['GET', 'POST'])
@login_required
def menu_armadopika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/armadopika.html',
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
        for i, pikaid in enumerate(pikas):
            if i<len(cants) and cants[i] and pikaid:
                pika = db.query(Pika).get(pikaid)
                pikacant = int(cants[i])
                stockpika = db.query(StockPika).get(pikaid)
                pikainsus = db.query(PikaInsumo).filter(PikaInsumo.pika==pika)

                #restamos stock de insumos
                for pikainsu in pikainsus:
                    stockinsu = db.query(StockInsumo).get(pikainsu.insumo_id)
                    if stockinsu.cantidad < pikainsu.cantidad*pikacant:
                        return 'No hay suficiente stock de "{}" para el pika "{}" (hay {}, requiere {})'.format(pikainsu.insumo.nombre, pika.nombre, stockinsu.cantidad, pikainsu.cantidad*pikacant), 400

                    movinsu = MovStockInsumo(insumo=pikainsu.insumo, cantidad=pikainsu.cantidad, fecha=dtnow)
                    db.add(movinsu)
                    stockinsu.cantidad -= movinsu.cantidad*pikacant
                    stockinsu.fecha = movinsu.fecha

                #sumamos stock de pika
                mov = MovStockPika(pika=pika, cantidad=int(cants[i]), fecha=dtnow)
                db.add(mov)
                stockpika.cantidad += pikacant
                stockpika.fecha = mov.fecha

        db.commit()

        check_alarmas()

        return ''

@bp.route("/menu/stockpikas", methods=['GET', 'POST'])
@login_required
def menu_stockpikas():
    if request.method == "GET":
        db = get_db()
        DATA = db.query(StockPika).join(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/stockpikas.html',
            DATA=DATA
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        return redirect(url_for('main.menu_stockpikas'))

@bp.route("/exportar/stockpikas.csv", methods=['GET'])
@login_required
def exportar_stockpikas():
    db = get_db()
    stopik = db.query(StockPika).join(Pika).order_by(Pika.nombre).all()

    ex = CsvExporter('stockpikas.csv')
    ex.writeHeaders('Id,Nombre,Cantidad,Actualizado')
    for s in stopik:
        print(s)
        ex.writeVals([s.pika_id, s.pika.nombre, s.cantidad, s.fecha])
    return ex.send()

@bp.route("/menu/agregelimpika", methods=['GET', 'POST'])
@login_required
def menu_agregelimpika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).all()

        r = make_response(render_template(
            'menu/agregelimpika.html',
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
            if db.query(Pika).filter(Pika.nombre==request.form['nombrepika']).first():
                return str('Ya existe un pika con ese nombre'), 400
            pika = Pika(nombre=request.form['nombrepika'])
            db.add(pika)
            db.add(StockPika(pika=pika, cantidad=0, fecha=datetime.datetime.now()))

        db.commit()

        return ''

@bp.route("/menu/modificarstockpika", methods=['GET', 'POST'])
@login_required
def menu_modificarstockpika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).order_by(Pika.nombre).all()
        stocks = db.query(StockPika).all()

        r = make_response(render_template(
            'menu/modificarstockpika.html',
            pikas=pikas,
            stocks=stocks
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('pika', 'cantidadnueva'))
        except Exception as e:
            return str(e), 400

        db = get_db()

        pika = db.query(Pika).get(request.form['pika'])
        pikacant = int(request.form['cantidadnueva'])
        dtnow = datetime.datetime.now()

        # modificamos stock de pika
        mov = MovStockPika(pika=pika, cantidad=pikacant, fecha=dtnow)
        db.add(mov)

        stockpika = db.query(StockPika).get(request.form['pika'])
        stockpika.cantidad = pikacant
        stockpika.fecha = mov.fecha

        db.commit()

        return ''


########################### INSUMOS
@bp.route("/menu/ingresarinsumo", methods=['GET', 'POST'])
@login_required
def menu_ingresarinsumo():
    if request.method == "GET":
        db = get_db()
        insus = db.query(Insumo).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/ingresarinsumo.html',
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
                mov = MovStockInsumo(insumo=insu, cantidad=insucant, fecha=dtnow)
                db.add(mov)
                stockinsu.cantidad += insucant
                stockinsu.fecha = dtnow

        db.commit()

        return ''

@bp.route("/menu/stockinsumos", methods=['GET', 'POST'])
@login_required
def menu_stockinsumos():
    if request.method == "GET":
        db = get_db()
        DATA = db.query(StockInsumo).join(Insumo).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/stockinsumos.html',
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

@bp.route("/exportar/stockinsumos.csv", methods=['GET'])
@login_required
def exportar_stockinsumos():
    db = get_db()
    stoins = db.query(StockInsumo).join(Insumo).order_by(Insumo.nombre).all()

    ex = CsvExporter('stockinsumos.csv')
    ex.writeHeaders('Id,Nombre,Cantidad,Actualizado')
    for s in stoins:
        ex.writeVals([s.insumo_id, s.insumo.nombre, s.cantidad, s.fecha])
    return ex.send()

@bp.route("/menu/asociarinsumospika", methods=['GET', 'POST'])
@login_required
def menu_asociarinsumospika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).order_by(Pika.nombre).all()
        insus = db.query(Insumo).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/asociarinsumospika.html',
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

@bp.route("/menu/listadoinsumospikas", methods=['GET'])
@login_required
def menu_listadoinsumospikas():
    db = get_db()
    pikainsus = db.query(PikaInsumo).join(Pika).order_by(Pika.nombre).all()

    r = make_response(render_template(
        'menu/listadoinsumospikas.html',
        pikainsus=pikainsus
    ))

    return r

@bp.route("/menu/rolloplaabierto", methods=['GET', 'POST'])
@login_required
def menu_rolloplaabierto():
    if request.method == "GET":
        db = get_db()
        plas = db.query(Insumo).join(StockInsumo).filter(Insumo.nombre.ilike("pla %") & StockInsumo.cantidad > 0).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/rolloplaabierto.html',
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
                mov = MovStockInsumo(insumo=rollo, cantidad=-rollocant, fecha=dtnow)
                db.add(mov)
                stockrollo.cantidad -= rollocant
                stockrollo.fecha = mov.fecha

        db.commit()

        check_alarmas()

        return ''

@bp.route("/menu/agregeliminsu", methods=['GET', 'POST'])
@login_required
def menu_agregeliminsu():
    if request.method == "GET":
        db = get_db()
        insus = db.query(Insumo).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/agregeliminsu.html',
            insus=insus
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombreinsu',))
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
            insu = Insumo(nombre=request.form['nombreinsu'])
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

@bp.route("/menu/modificarstockinsu", methods=['GET', 'POST'])
@login_required
def menu_modificarstockinsu():
    if request.method == "GET":
        db = get_db()
        insus = db.query(Insumo).order_by(Insumo.nombre).all()
        stocks = db.query(StockInsumo).all()

        r = make_response(render_template(
            'menu/modificarstockinsu.html',
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
        insucant = int(request.form['cantidadnueva'])
        dtnow = datetime.datetime.now()

        # modificamos stock de pika
        mov = MovStockInsumo(insumo=insu, cantidad=insucant, fecha=dtnow)
        db.add(mov)

        stockinsu = db.query(StockInsumo).get(request.form['insumo'])
        stockinsu.cantidad = insucant
        stockinsu.fecha = mov.fecha

        db.commit()

        check_alarma(insu)

        return ''


########################### VENTAS
@bp.route("/menu/listadoventas", methods=['GET', 'POST'])
@login_required
def menu_listadoventas():
    if request.method == "GET":
        db = get_db()

        ventapikas = db.query(VentaPika).join(Venta).order_by(Venta.fecha.desc(), Venta.id.desc())
        filtrado = False
        if len(request.args):
            query = []
            for arg in request.args:
                k, v = arg, request.args[arg]
                if v:
                    if k=='tipo': query.append(Venta.ventatipo_id == v)
                    elif k=='comentario': query.append(Venta.comentario.ilike("%{}%".format(v)))
                    elif k=='fechadesde': query.append(Venta.fecha >= datetime.datetime.strptime(v,'%d/%m/%Y'))
                    elif k=='fechahasta': query.append(Venta.fecha <= datetime.datetime.strptime(v,'%d/%m/%Y') + datetime.timedelta(days=1))
            if query:
                from functools import reduce
                ventapikas = ventapikas.filter(reduce(lambda x, y: x&y, query))
                filtrado = True

            if request.args['pika']:
                pikaid = int(request.args['pika'])
                #ventas = ventas.join(VentaPika).filter(VentaPika.pika_id == pikaid)
                ventapikas = ventapikas.filter(VentaPika.pika_id == pikaid)
                filtrado = True

        ventapikas = ventapikas.all()
        ventatipos = db.query(VentaTipo).order_by(VentaTipo.nombre).all()
        pikas = db.query(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/listadoventas.html',
            ventapikas=ventapikas,
            ventatipos=ventatipos,
            pikas=pikas,
            filtrado=filtrado
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        from flask import send_file
        return send_file('/home/franzisca/PycharmProjects/pyflaskapp/flask1/models.py', attachment_filename='db.py', as_attachment=True)

@bp.route("/exportar/ventas.csv", methods=['GET'])
@login_required
def exportar_ventas():
    db = get_db()

    if not len(request.args):
        ventas = db.query(Venta)
        filtrado = False
    else:
        query = []
        for arg in request.args:
            k, v = arg, request.args[arg]
            if v:
                if k=='tipo': query.append(Venta.ventatipo_id == v)
                elif k=='comentario': query.append(Venta.comentario.ilike("%{}%".format(v)))
                elif k=='fechadesde': query.append(Venta.fecha >= datetime.datetime.strptime(v,'%d/%m/%Y'))
                elif k=='fechahasta': query.append(Venta.fecha <= datetime.datetime.strptime(v,'%d/%m/%Y') + datetime.timedelta(days=1))
        if query:
            from functools import reduce
            ventas = db.query(Venta).filter(reduce(lambda x, y: x&y, query))
            filtrado = True
        else:
            ventas = db.query(Venta)
            filtrado = False
        if request.args['pika']:
            pikaid = int(request.args['pika'])
            ventas = ventas.join(VentaPika).filter(VentaPika.pika_id == pikaid)
            filtrado = True
    ventas = ventas.order_by(Venta.fecha.desc()).all()

    ex = CsvExporter('ventas.csv')
    ex.writeHeaders('Id,Fecha,Tipo,Comentario,Pika,Cantidad')
    for v in ventas:
        vals = [v.id, v.fecha, v.ventatipo.nombre, v.comentario, '', '']
        if len(v.ventapikas):
            for vpi in v.ventapikas:
                vals[4] = vpi.pika.nombre
                vals[5] = vpi.cantidad
                ex.writeVals(vals)
        else:
            ex.writeVals(vals)
    return ex.send()

@bp.route("/menu/ingresarventa", methods=['GET', 'POST'])
@login_required
def menu_ingresarventa():
    if request.method == "GET":
        db = get_db()
        ventatipos = db.query(VentaTipo).order_by(VentaTipo.nombre).all()
        pikas = db.query(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/ingresarventa.html',
            ventatipos=ventatipos,
            pikas=pikas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('tipo', 'pika', 'cantidad'))
        except Exception as e:
            return str(e), 400

        db = get_db()
        pikas = request.form.getlist('pika')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        vent = Venta(
            ventatipo=db.query(VentaTipo).filter(VentaTipo.id == request.form['tipo']).one(),
            fecha=dtnow,
            comentario=request.form['comentario'] if 'comentario' in request.form else None
        )
        db.add(vent)
        for i, pikaid in enumerate(pikas):
            if i<len(cants) and cants[i] and pikaid:
                pika = db.query(Pika).get(pikaid)
                pikacant = int(cants[i])
                stockpika = db.query(StockPika).get(pikaid)

                if stockpika.cantidad < pikacant:
                    return 'No hay suficiente stock del pika "{}" (hay {}, requiere {})'.format(pika.nombre, stockpika.cantidad, pikacant), 400

                #agregamos entrada de venta
                db.add(VentaPika(venta=vent, pika=pika, cantidad=pikacant))

                #restamos stock de pika
                mov = MovStockPika(pika=pika, cantidad=-int(cants[i]), fecha=dtnow)
                db.add(mov)
                stockpika.cantidad -= pikacant
                stockpika.fecha = mov.fecha

        db.commit()

        return ''

@bp.route("/menu/agregelimtipoventa", methods = ['GET', 'POST'])
@login_required
def menu_agregelimtipoventa():
    if request.method == "GET":
        db = get_db()
        ventatipos = db.query(VentaTipo).order_by(VentaTipo.nombre).all()

        r = make_response(render_template(
            'menu/agregelimtipoventa.html',
            ventatipos=ventatipos
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombretipoven',))
            except Exception as e:
                return str(e), 400
        elif request.form['operation'] == 'delete':
            try:
                checkparams(request.form, ('tipo',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400

        db = get_db()

        if request.form['operation'] == 'add':
            if db.query(VentaTipo).filter(VentaTipo.nombre==request.form['nombretipoven']).first():
                return 'Ya existe un tipo de venta con ese nombre', 400
            tipo = VentaTipo(nombre=request.form['nombretipoven'])
            db.add(tipo)
        elif request.form['operation'] == 'delete':
            tipo = db.query(VentaTipo).get(int(request.form['tipo']))
            ventas = db.query(Venta).filter(Venta.ventatipo==tipo)
            for v in ventas:
                db.query(VentaPika).filter(VentaPika.venta==v).delete()
            ventas.delete()
            db.query(VentaTipo).filter(VentaTipo.id==tipo.id).delete()

        db.commit()

        return ''

@bp.route("/menu/eliminarventa", methods=['GET', 'POST'])
@login_required
def menu_eliminarventa():
    if request.method == "GET":
        db = get_db()
        ventas = db.query(Venta).order_by(Venta.fecha.desc()).all()
        ventasmodif = []
        for v in ventas:
            ventasmodif.append({
                'id': v.id,
                'fecha': v.fecha.strftime("%d/%m/%Y %H:%M"),
                'comentario': v.comentario
            })

        r = make_response(render_template(
            'menu/eliminarventa.html',
            ventas=ventasmodif
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('venta',))
        except Exception as e:
            return str(e), 400

        db = get_db()

        venta = db.query(Venta).get(int(request.form['venta']))
        dtnow = datetime.datetime.now()
        ventapikas = db.query(VentaPika).filter(VentaPika.venta == venta)

        for vp in ventapikas.all():
            #sumamos stock de pika
            pikacant = int(vp.cantidad)
            mov = MovStockPika(pika=vp.pika, cantidad=pikacant, fecha=dtnow)
            db.add(mov)

            stockpika = db.query(StockPika).get(vp.pika_id)
            stockpika.cantidad += pikacant
            stockpika.fecha = mov.fecha

        ventapikas.delete()
        db.query(Venta).filter(Venta.id == venta.id).delete()

        db.commit()

        return ''


########################### FALLAS
@bp.route("/menu/listadofallas", methods=['GET', 'POST'])
@login_required
def menu_listadofallas():
    if request.method == "GET":
        db = get_db()
        if not len(request.args):
            fallas = db.query(Falla)
            filtrado = False
        else:
            query = []
            for arg in request.args:
                k, v = arg, request.args[arg]
                if v:
                    if k=='maquina': query.append(Falla.maquina_id == v)
                    elif k=='descripcion': query.append(Falla.descripcion.ilike("%{}%".format(v)))
                    elif k=='gcode': query.append(Falla.gcode_id == v)
                    elif k=='fechadesde': query.append(Falla.fecha >= datetime.datetime.strptime(v,'%d/%m/%Y'))
                    elif k=='fechahasta': query.append(Falla.fecha <= datetime.datetime.strptime(v,'%d/%m/%Y') + datetime.timedelta(days=1))
            if query:
                from functools import reduce
                fallas = db.query(Falla).filter(reduce(lambda x, y: x&y, query))
                filtrado = True
            else:
                fallas = db.query(Falla)
                filtrado = False
            if request.args['pika']:
                pikaid = int(request.args['pika'])
                fallas = fallas.join(Gcode).filter(Gcode.pika_id == pikaid)
                filtrado = True
        fallas = fallas.order_by(Falla.fecha.desc()).all()

        maqs = db.query(Maquina).order_by(Maquina.nombre).all()
        gcods = db.query(Gcode).order_by(Gcode.nombre).all()
        pikas=[]
        for g in gcods:
            if g.pika and g.pika not in pikas:
                pikas.append(g.pika)
        def pika_sort_key(ele):
            print(ele)
            return ele.nombre
        print(pikas)
        pikas.sort(key=pika_sort_key)
        print(pikas)

        r = make_response(render_template(
            'menu/listadofallas.html',
            fallas=fallas,
            maqs=maqs,
            pikas=pikas,
            gcods=gcods,
            filtrado=filtrado
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        return redirect(url_for('main.menu_listadofallas'))

@bp.route("/exportar/fallas.csv", methods=['GET'])
@login_required
def exportar_fallas():
    db = get_db()

    if not len(request.args):
        fallas = db.query(Falla)
        filtrado = False
    else:
        query = []
        for arg in request.args:
            k, v = arg, request.args[arg]
            if v:
                if k=='maquina': query.append(Falla.maquina_id == v)
                elif k=='descripcion': query.append(Falla.descripcion.ilike("%{}%".format(v)))
                elif k=='gcode': query.append(Falla.gcode_id == v)
                elif k=='fechadesde': query.append(Falla.fecha >= v)
                elif k=='fechahasta': query.append(Falla.fecha <= v)
        if query:
            from functools import reduce
            fallas = db.query(Falla).filter(reduce(lambda x, y: x&y, query))
            filtrado = True
        else:
            fallas = db.query(Falla)
            filtrado = False
        if request.args['pika']:
            pikaid = int(request.args['pika'])
            fallas = fallas.join(Gcode).filter(Gcode.pika_id == pikaid)
            filtrado = True
    fallas = fallas.order_by(Falla.fecha.desc()).all()

    ex = CsvExporter('fallas.csv')
    ex.writeHeaders('Id,Fecha,Máquina,Pika,G-code,Descripción')
    for f in fallas:
        vals = [f.id, f.fecha, f.maquina.nombre, '', '', f.descripcion]
        if f.gcode:
            vals[4] = f.gcode.nombre
            if f.gcode.pika:
                vals[3] = f.gcode.pika.nombre
        ex.writeVals(vals)
    return ex.send()

@bp.route("/menu/ingresarfalla", methods=['GET', 'POST'])
@login_required
def menu_ingresarfalla():
    if request.method == "GET":
        db = get_db()
        maqs = db.query(Maquina).order_by(Maquina.nombre).all()
        gcods = db.query(Gcode).order_by(Gcode.nombre).all()
        pikas=[]
        for g in gcods:
            if g.pika and g.pika not in pikas:
                pikas.append(g.pika)
        def pika_sort_key(ele):
            print(ele)
            return ele.nombre
        print(pikas)
        pikas.sort(key=pika_sort_key)
        print(pikas)

        r = make_response(render_template(
            'menu/ingresarfalla.html',
            maqs=maqs,
            pikas=pikas,
            gcods=gcods
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('maquina', 'descripcion'))
        except Exception as e:
            return str(e), 400

        db = get_db()
        dtnow = datetime.datetime.now()
        if request.form['gcode']:
            db.add(Falla(
                maquina=db.query(Maquina).filter(Maquina.id == request.form['maquina']).one(),
                gcode=db.query(Gcode).filter(Gcode.id == request.form['gcode']).one(),
                descripcion=request.form['descripcion'],
                fecha=dtnow
            ))
        else:
            db.add(Falla(
                maquina=db.query(Maquina).filter(Maquina.id == request.form['maquina']).one(),
                descripcion=request.form['descripcion'],
                fecha=dtnow
            ))

        db.commit()

        return ''

@bp.route("/menu/agregelimmaquina", methods = ['GET', 'POST'])
@login_required
def menu_agregelimmaquina():
    if request.method == "GET":
        db = get_db()
        maqs = db.query(Maquina).order_by(Maquina.nombre).all()

        r = make_response(render_template(
            'menu/agregelimmaquina.html',
            maqs=maqs
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombremaqui',))
            except Exception as e:
                return str(e), 400
        elif request.form['operation'] == 'delete':
            try:
                checkparams(request.form, ('maquina',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400

        db = get_db()

        if request.form['operation'] == 'add':
            if db.query(Insumo).filter(Maquina.nombre==request.form['nombremaqui']).first():
                return 'Ya existe una máquina con ese nombre', 400
            maq = Maquina(nombre=request.form['nombremaqui'])
            db.add(maq)
        elif request.form['operation'] == 'delete':
            maq = db.query(Maquina).get(int(request.form['maquina']))
            db.query(Falla).filter(Falla.maquina==maq).delete()
            db.query(Maquina).filter(Maquina.id==maq.id).delete()

        db.commit()

        return ''

@bp.route("/menu/agregelimgcode", methods = ['GET', 'POST'])
@login_required
def menu_agregelimgcode():
    if request.method == "GET":
        db = get_db()
        gcods = db.query(Gcode).order_by(Gcode.nombre).all()
        pikas = db.query(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/agregelimgcode.html',
            gcods=gcods,
            pikas=pikas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombregcode',))
            except Exception as e:
                return str(e), 400
        elif request.form['operation'] == 'delete':
            try:
                checkparams(request.form, ('gcode',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400

        db = get_db()

        if request.form['operation'] == 'add':
            if db.query(Gcode).filter(Gcode.nombre==request.form['nombregcode']).first():
                return 'Ya existe una g-code con ese nombre', 400
            if request.form['pika']:
                gcod = Gcode(nombre=request.form['nombregcode'],pika=db.query(Pika).get(int(request.form['pika'])))
            else:
                gcod = Gcode(nombre=request.form['nombre'])
            db.add(gcod)
        elif request.form['operation'] == 'delete':
            gcod = db.query(Gcode).get(int(request.form['gcode']))
            db.query(Falla).filter(Falla.gcode==gcod).delete()
            db.query(Gcode).filter(Gcode.id==gcod.id).delete()

        db.commit()

        return ''


########################### ALARMAS
@bp.route("/menu/agregelimalarma", methods=['GET', 'POST'])
@login_required
def menu_agregelimalarma():
    if request.method == "GET":
        db = get_db()
        DATA = db.query(TABLE).all()

        r = make_response(render_template(
            'menu/agregelimalarma.html',
            DATA=DATA
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        db = get_db()

        pass

        db.commit()

        return ''
