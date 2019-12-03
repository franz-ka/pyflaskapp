from flask import current_app, Blueprint, request, make_response, render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user

from sqlalchemy import or_, not_, and_, func
import datetime
from pprint import pprint
import itertools

from flask1.db import get_db
from flask1.login import User, loginUserPass, logoutUser
from flask1.models import *
from flask1.csvexport import CsvExporter
from flask1.alarmas import check_alarma, check_alarmas

from .pikas_logics import *
from .ventas_logics import *

def checkparams(form, musthave):
    if len(form) < len(musthave):
        raise Exception('Pocos parámetros enviados ({}<{})'.format(len(form), len(musthave)))
    for v in musthave:
        if v not in form:
            raise Exception('Falta el parámetro "{}"'.format(v))

def hasquery(args):
    for v in args.values():
        if v: return True
    return False