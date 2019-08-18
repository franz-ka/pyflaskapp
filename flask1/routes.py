# coding=utf-8
from flask import current_app, Blueprint, request, make_response, render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user
import datetime

from flask1.db import get_db
from flask1.login import User, loginUserPass, logoutUser
from .models import *
from .csvexport import CsvExporter
from .alarmas import check_alarma, check_alarmas
from sqlalchemy import or_

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