from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, make_response
)
from flask_login import login_required, login_user, logout_user
from flask1.db import get_db
from flask1.loginuser import User
from .models import *
import datetime

bp = Blueprint('main', __name__, url_prefix='')

def checkparams(form, musthave):
    if len(form) < len(musthave):
        raise Exception('Pocos parámetros enviados ({}<{})'.format(len(form), len(musthave)))
    for v in musthave:
        if v not in form:
            raise Exception('Falta el parámetro "{}"'.format(v))

################################################
######################## ERRORES
################################################
@bp.errorhandler(404)
def not_found(e):
    #404-error-handling https://www.geeksforgeeks.org/python-404-error-handling-in-flask/
    return render_template("404.html",url=request.path)


################################################
######################## LOGIN/OUT
################################################
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        print('post form:', request.form)

        try: checkparams(request.form, ('user', 'password'))
        except Exception as e: return str(e), 400

        db = get_db()
        usu = db.query(Usuario).filter(Usuario.nombre==request.form['user']).first()
        print('uu', usu)
        import hashlib
        if usu and hashlib.sha256( request.form['password'].encode('utf-8') ).hexdigest() == usu.passhash:
            user = User(usu.id, usu.nombre, usu.esadmin)
            login_user(user)
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            return "Credenciales incorrectas", 400
    else:
        return render_template('login.html')

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


################################################
######################## Menu
################################################
@bp.route("/")
@login_required
def index():
    r = make_response(render_template(
        'index.html',
        mail = current_app.config["MAIL_FROM_EMAIL"]
    ))
    return r

################################################
######################## PIEZAS
################################################
@bp.route("/menu/piezas", methods = ['GET', 'POST'])
@login_required
def menu_piezas():
    if request.method == "GET":
        r = make_response(render_template(
            'menu/??piezas.html',
            piezs = get_db().query(Pieza).all()
        ))
        return r
    else: #request.method == "POST":
        print('post form:',request.form)

        musthave = ('nombre','cantidad')
        if len(request.form) < len(musthave):
            return 'err:too few params'
        for v in musthave:
            if v not in request.form:
                return 'err:'+v+' missing'

        db = get_db()
        db.add( Pieza(nombre=request.form['nombre'], cantidad=request.form['cantidad']) )
        db.commit()

        return redirect(url_for('main.menu_piezas'))


################################################
######################## IMPRESIONES
################################################
@bp.route("/menu/impresiones", methods = ['GET', 'POST'])
@login_required
def menu_impresiones():
    if request.method == "GET":
        db = get_db()
        imppiezs = db.query(ImpresionPieza).all()
        piezs = db.query(Pieza).all()
        d = datetime.datetime.now()
        nowfecha = d.strftime("%d/%m/%Y")
        nowtiempo = d.strftime("%X")

        r = make_response(render_template(
            'menu/??impresiones.html',
            imppiezs=imppiezs,
            piezs=piezs,
            nowfecha=nowfecha,
            nowtiempo=nowtiempo
        ))
        return r
    else: #request.method == "POST":
        print('post form:',request.form)

        musthave = ('fecha','hora','pieza','cantidad')
        if len(request.form) < len(musthave):
            return 'err:too few params'
        for v in musthave:
            if v not in request.form:
                return 'err:'+v+' missing'

        db = get_db()

        imp = Impresion(fecha=datetime.datetime.strptime(request.form['fecha'] + ' ' + request.form['hora'], '%d/%m/%Y %H:%M:%S'))
        db.add(imp)
        # este commit actualiza imp.id
        db.commit()

        piezs = request.form.getlist('pieza')
        cants = request.form.getlist('cantidad')
        ips=[]
        for i, piezid in enumerate(piezs):
            ips.append( ImpresionPieza(impresion_id=str(imp.id), pieza_id=str(piezid), cantidad=cants[i]) )
        print(ips)
        db.add_all(ips)
        db.commit()
        #except ValueError as e:
        #    return "err:bad type, " + str(e)

        return redirect(url_for('main.menu_impresiones'))


################################################
######################## MODELOS
################################################
@bp.route("/menu/modelos", methods = ['GET', 'POST'])
@login_required
def menu_modelos():
    if request.method == "GET":
        db = get_db()

        mods = db.query(Modelo).all()

        modpiezs = {}
        _modpiezs = db.query(ModeloPieza).all()
        for mp in _modpiezs:
            if mp.modelo_id not in modpiezs:
                modpiezs[mp.modelo_id] = []
            modpiezs[mp.modelo_id].append(mp)

        modartis = {}
        _modartis = db.query(ModeloArticulo).all()
        for ma in _modartis:
            if ma.modelo_id not in modartis:
                modartis[ma.modelo_id] = []
            modartis[ma.modelo_id].append(ma)

        r = make_response(render_template(
            'menu/??modelos.html',
            mods = db.query(Modelo).all(),
            modpiezs = modpiezs,
            modartis = modartis,
            piezs = db.query(Pieza).all(),
            artis = db.query(Articulo).all()
        ))
        return r
    else: #request.method == "POST":
        print('post form:',request.form)

        if len(request.form) < 2:
            return 'err:too few params'
        if 'nombre' not in request.form:
            return 'err:nombre missing'
        if 'pieza' not in request.form and 'articulo' not in request.form:
            return 'err:pieza o articulo missing'

        db = get_db()

        mod = Modelo(nombre=request.form['nombre'])
        db.add(mod)
        # este commit actualiza mod.id
        db.commit()

        if 'pieza' in request.form:
            piezs = request.form.getlist('pieza')
            piecants = request.form.getlist('piezacantidad')
            ips=[]
            for i, piezid in enumerate(piezs):
                ips.append( ModeloPieza(modelo_id=str(mod.id), pieza_id=str(piezid), cantidad=piecants[i]) )
            print(ips)
            db.add_all(ips)
            db.commit()

        if 'articulo' in request.form:
            artis = request.form.getlist('articulo')
            artcants = request.form.getlist('articulocantidad')
            arts=[]
            for i, artid in enumerate(artis):
                arts.append( ModeloArticulo(modelo_id=str(mod.id), articulo_id=str(artid), cantidad=artcants[i]) )
            print(arts)
            db.add_all(arts)
            db.commit()

        return redirect(url_for('main.menu_modelos'))



'''
@bp.route("/menu/modelos")
@login_required
def menu_modelos():
    db = get_db()
    newmod = Modelo(nombre='baku')
    db.add(newmod)
    db.commit()

    newimp = Impresion(modelo=newmod)
    db.add(newimp)
    db.commit()

    imps = db.query(Impresion).all()
    #mods = db.query(Modelo).all()
    #modmats = db.query(ModeloMaterial).all()
    return render_template('menu/??modelos.html', mods=mods, modmats=modmats)

'''


@bp.route("/menu/armadopika", methods = ['GET', 'POST'])
@login_required
def menu_armadopika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).all()

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
                        return 'No hay suficiente stock de "{}" para el pika "{}" ({} < {})'.format(pikainsu.insumo.nombre, pika.nombre, stockinsu.cantidad, pikainsu.cantidad*pikacant), 400

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

        return ''

@bp.route("/menu/stockpikas", methods=['GET', 'POST'])
@login_required
def menu_stockpikas():
    if request.method == "GET":
        db = get_db()
        DATA = db.query(StockPika).all()

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


@bp.route("/menu/ingresarinsumo", methods=['GET', 'POST'])
@login_required
def menu_ingresarinsumo():
    if request.method == "GET":
        db = get_db()
        DATA = db.query(TABLE).all()

        r = make_response(render_template(
            'menu/ingresarinsumo.html',
            DATA=DATA
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        return redirect(url_for('main.menu_ingresarinsumo'))


@bp.route("/menu/stockinsumos", methods=['GET', 'POST'])
@login_required
def menu_stockinsumos():
    if request.method == "GET":
        db = get_db()
        DATA = db.query(StockInsumo).all()

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


@bp.route("/menu/listadoventas", methods=['GET', 'POST'])
@login_required
def menu_listadoventas():
    if request.method == "GET":
        db = get_db()
        ventas = db.query(Venta).all()

        r = make_response(render_template(
            'menu/listadoventas.html',
            ventas=ventas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        return redirect(url_for('main.menu_listadoventas'))

@bp.route("/menu/ingresarventa", methods=['GET', 'POST'])
@login_required
def menu_ingresarventa():
    if request.method == "GET":
        db = get_db()
        ventatipos = db.query(VentaTipo).all()
        pikas = db.query(Pika).all()

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
                    return 'No hay suficiente stock del pika "{}" ({} < {})'.format(pika.nombre, stockpika.cantidad, pikacant), 400

                #agregamos entrada de venta
                db.add(VentaPika(venta=vent, pika=pika, cantidad=pikacant))

                #restamos stock de pika
                mov = MovStockPika(pika=pika, cantidad=-int(cants[i]), fecha=dtnow)
                db.add(mov)
                stockpika.cantidad -= pikacant
                stockpika.fecha = mov.fecha

        db.commit()

        return ''

