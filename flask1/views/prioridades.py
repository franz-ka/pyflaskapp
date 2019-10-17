# coding=utf-8
from ._common import *

bp_prioridades = Blueprint('prioridades', __name__, url_prefix='/prioridades')

@bp_prioridades.route("/factoresdeimpresion", methods = ['GET', 'POST'])
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
            'menu/prioridades/factoresdeimpresion.html',
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

