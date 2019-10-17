# coding=utf-8
from ._common import *

bp_prioridades = Blueprint('prioridades', __name__, url_prefix='/prioridades')

dias_factor_venta = 60.0
        
@bp_prioridades.route("/factoresdeimpresion", methods = ['GET', 'POST'])
@login_required
def menu_factoresdeimpresion():
    if request.method == "GET":
        db = get_db()
        #pikas = db.query(Pika).order_by(Pika.nombre).all()
        #factores = db.query(FactorProductividad).all()
        pika_factores = db.query(Pika, FactorProductividad).outerjoin(FactorProductividad).all()

        dtnow = datetime.datetime.now()
        dtventas = dtnow - datetime.timedelta(days=dias_factor_venta)
        #print(dias_factor_venta, dtventas)
        
        #ventapikas = db.query(VentaPika).join(Venta).filter(Venta.fecha != None)
        ventapikas = db.query(
            VentaPika.pika_id,
            func.sum(VentaPika.cantidad/dias_factor_venta).label('total')
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
            dias_factor=dias_factor_venta,
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

@bp_prioridades.route("/prioridadimpresion", methods = ['GET', 'POST'])
@login_required
def menu_prioridadimpresion():
    if request.method == "GET":
        db = get_db()
        
        pikasdata_keys = {}
        pikasdata = db.query(Pika, PrestockPika, StockPika, FactorProductividad) \
            .join(PrestockPika) \
            .join(StockPika) \
            .join(FactorProductividad) \
            .order_by(Pika.nombre).all()
        #print(pikasdata)
        
        '''stocksreales = {}
        for pika, prestock, stock in pikasdata:
            prestck = prestock.cantidad
            stck = stock.cantidad
            pedidos = pikapedidos.get(pika.id, 0)
            stocksreales[pika.id] = prestck + stck - pedidos'''
        #print(stocksreales)
        
        pikas = {}
        
        class PikaData:
            id=0
            prestock=0
            stock=0
            pedidos=0
            stockreal=0.0
            factorventa=0.0
            factorprod=0.0
            
        for pika, prestock, stock, factor_prod in pikasdata:
            pikasdata_keys[pika.id] = pika
            
            p = PikaData()
            p.id = pika.id
            p.prestock = prestock.cantidad
            p.stock = stock.cantidad
            p.pedidos = 0
            p.stockreal = float(p.prestock + p.stock - p.pedidos)
            p.factorventa = 0.0
            p.factorprod = float(factor_prod.factor)
            pikas[pika.id] = p
        
        # Cargamos pedidos de ventas (afecto stock real)
        ventapedidos = db.query(
                VentaPika.pika_id,
                func.sum(VentaPika.cantidad).label('total')
            ).join(Venta
            ).filter(Venta.fecha_pedido != None
            ).filter(Venta.fecha == None
            ).group_by(VentaPika.pika_id
            ).all()
        #print(ventapedidos)
        pikapedidos = {}
        for pika_id, pedidos_totales in ventapedidos:
            p = pikas[pika_id]
            p.pedidos = pedidos_totales
            p.stockreal = float(p.prestock + p.stock - p.pedidos)
        #print(pikapedidos)

        # Cargamos factores de venta
        dtnow = datetime.datetime.now()
        dtventas = dtnow - datetime.timedelta(days=dias_factor_venta)
        ventasdiarias = db.query(
            VentaPika.pika_id,
            func.sum(VentaPika.cantidad/dias_factor_venta).label('total')
        ).join(Venta
        ).filter(Venta.fecha != None
        ).filter(Venta.fecha >= dtventas
        ).group_by(VentaPika.pika_id
        ).all()
        #print(ventasdiarias)
        pikaventasdiarias = {}
        for pika_id, ventas_diarias in ventasdiarias:
            p = pikas[pika_id]
            p.factorventa = float(ventas_diarias)
        #print(pikaventasdiarias)
        
        # imprime mal esto
        #print('pikas=', pikas)
        
        # stock real / factor de venta
        prioridades = []
        cant_prioris = 11
        while cant_prioris:
            print(f'------------Comienzo iteración (restan {cant_prioris})')
            
            stock_relativos = {}
            for pi in pikas.values():    
                stockreal = pi.stockreal
                facvent = pi.factorventa
                
                stckrelativo = stockreal/facvent
                stock_relativos[pi.id] = stckrelativo
                print(f"pika_id={pi.id:2}, stockreal={stockreal:5}, facvent={facvent:.4f}, stckrelativo={stckrelativo:5.1f}")
            #print(stock_relativos)
                
            pika_id_min = min(stock_relativos, key=stock_relativos.get)
            stockrel_min = stock_relativos[pika_id_min]
            print('min pika & stock rel=', pika_id_min, stockrel_min)
            
            prioridades.append((pika_id_min, stockrel_min))
            
            pikas[pika_id_min].stockreal += pikas[pika_id_min].factorprod * dias_factor_venta
            print('upd stockrel to', pikas[pika_id_min].stockreal)
            
            cant_prioris -= 1
            print('------------Fin iteración')
        print('prioridades=', prioridades)
                
        r = make_response(render_template(
            'menu/prioridades/prioridadimpresion.html',
            pikasdata_keys=pikasdata_keys,
            prioridades=prioridades
        ))
        return r
    else: #request.method == "POST":
        print('post form:',request.form)

        try: checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e: return str(e), 400

        db = get_db()
        
        pass
        
        db.commit()

        return ''

