# coding=utf-8
from ._common import *

bp_alarmas = Blueprint('alarmas', __name__, url_prefix='/alarmas')

@bp_alarmas.route("/agregelimalarma", methods=['GET', 'POST'])
@login_required
def menu_agregelimalarma():
    if request.method == "GET":
        db = get_db()
        insus = db.query(Insumo).order_by(Insumo.nombre).all()
        alarmas = db.query(Alarma).all()
        alarmasinus = db.query(Insumo).join(Alarma).order_by(Insumo.nombre).all()

        r = make_response(render_template(
            'menu/alarmas/agregelimalarma.html',
            insus=insus,
            alarmas=alarmas,
            alarmasinus=alarmasinus
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('insumo', 'cantidadnueva'))
            except Exception as e:
                return str(e), 400
        elif request.form['operation'] == 'delete':
            try:
                checkparams(request.form, ('alarma_insumo',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400

        db = get_db()

        if request.form['operation'] == 'add':
            alarma_cant = int(request.form['cantidadnueva'])
            alarma_exists = db.query(Alarma).filter(Alarma.insumo_id==request.form['insumo']).first()
            if alarma_exists:
                alarma_exists.cantidad = alarma_cant
            else:
                db.add(Alarma(insumo=db.query(Insumo).get(request.form['insumo']), cantidad=alarma_cant))
            db.commit()
            #check_alarmas()
        elif request.form['operation'] == 'delete':
            db.query(Alarma).filter(Alarma.insumo_id==request.form['alarma_insumo']).delete()
            db.commit()

        return ''

@bp_alarmas.route("/listadoalarmas", methods=['GET'])
@login_required
def menu_listadoalarmas():
    if request.method == "GET":
        db = get_db()
        # alarmas = db.query(Alarma).join(Insumo).order_by(Insumo.nombre).all()
        alarmas_stocks = db.query(Alarma, StockInsumo).filter(StockInsumo.insumo_id == Alarma.insumo_id).all()

        r = make_response(render_template(
            'menu/alarmas/listadoalarmas.html',
            alarmas_stocks=alarmas_stocks
        ))
        return r