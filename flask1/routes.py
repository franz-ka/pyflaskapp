from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, make_response
)
from flask_login import login_required, login_user, logout_user
from flask1.db import get_db
from flask1.loginuser import User
from .models import *
import datetime

bp = Blueprint('main', __name__, url_prefix='')

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
        user = User(3)
        login_user(user)
        return redirect(request.args.get('next') or url_for('main.index'))
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

@bp.route("/menu/impresiones", methods = ['POST', 'GET'])
@login_required
def menu_impresiones():
    if request.method == "POST":
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
    else:
        db = get_db()
        imppiezs = db.query(ImpresionPieza).all()
        piezs = db.query(Pieza).all()
        d = datetime.datetime.now()
        nowfecha = d.strftime("%d/%m/%Y")
        nowtiempo = d.strftime("%X")

        r = make_response(render_template(
            'menu/impresiones.html',
            imppiezs=imppiezs,
            piezs=piezs,
            nowfecha=nowfecha,
            nowtiempo=nowtiempo
        ))
        return r





@bp.route("/menu/modelos")
@login_required
def menu_modelos():
    db = get_db()
    '''
    newmod = Modelo(nombre='baku')
    db.add(newmod)
    db.commit()

    newimp = Impresion(modelo=newmod)
    db.add(newimp)
    db.commit()

    imps = db.query(Impresion).all()
    '''
    #mods = db.query(Modelo).all()
    #modmats = db.query(ModeloMaterial).all()
    return render_template('menu/modelos.html', mods=mods, modmats=modmats)
