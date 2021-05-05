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
            #check_alarmas(current_app)
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
        insus_pedidos = db \
            .query(Insumo, func.sum(VentaPika.cantidad*PikaInsumo.cantidad).label('pedidos')) \
            .join(Venta) \
            .filter(Venta.fecha_pedido != None, Venta.fecha == None) \
            .join(PikaInsumo, VentaPika.pika_id == PikaInsumo.pika_id) \
            .group_by(PikaInsumo.insumo_id) \
            .join(Insumo) \
            .subquery()

        alarmas_stocks = db \
            .query(Insumo, Alarma, StockInsumo, 'anon_1.pedidos') \
            .join(Alarma) \
            .join(StockInsumo) \
            .join(insus_pedidos, isouter=True) \
            .order_by(Insumo.nombre) \
            .all()

        alarmas_stocks_vencidas = list(filter(
            lambda e: e[2].cantidad-(e[3] or 0) <= e[1].cantidad,
            alarmas_stocks
        ))
        alarmas_stocks_novenc = list(filter(
            lambda e: e not in alarmas_stocks_vencidas,
            alarmas_stocks
        ))

        r = make_response(render_template(
            'menu/alarmas/listadoalarmas.html',
            alarmas_stocks=alarmas_stocks_vencidas + alarmas_stocks_novenc
        ))
        return r
