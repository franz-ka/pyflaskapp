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
        print('post form:',request.form[0])
        accvars = ('fecha','hora','pieza','cantidad')
        vars = {piezs:[],cants:[]}
        for keyval in request.form[0]:
            k = keyval[0]
            if k not in accvars:
                return "error:campo " + k + " no aceptado"
            v = keyval[1]
            if k=='pieza':
                piezs.append(v)
            elif k=='cantidad':
                cants.append(v)
            else:
                vars[k]=v
        print(vars)
        return "ok"
    else:
        db = get_db()
        imppiezs = db.query(ImpresionPieza).all()
        piezs = db.query(Pieza).all()
        d = datetime.datetime.now()
        nowfecha = d.strftime("%d/%m/%y")
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
