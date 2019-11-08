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
        
        pikas = {}
        
        class PikaData:
            id=0
            nombre=''
            prestock=0
            stock=0
            stockreal=0.0
            factorventa=0.0001
            factorprod=0.0
            css_class=''
            img=''
            __pedidos=0.0
                        
            #getter
            @property
            def pedidos(self):
                return self.__pedidos
                
            @pedidos.setter
            def pedidos(self, pedidos):
                self.__pedidos = float(pedidos)
                self.upd_stock()
            
            def upd_stock(self):
                self.stockreal = float(self.prestock + self.stock - self.pedidos)
            
            
            def __repr__(self):
                return f'(#{self.id}) {self.nombre}, prestk={self.prestock}, stk={self.stock}, ped={self.pedidos}, stkR={self.stockreal}, facVen={self.factorventa:.3}'
        
        pikasdata = db.query(Pika, PrestockPika, StockPika, FactorProductividad) \
            .join(PrestockPika) \
            .join(StockPika) \
            .join(FactorProductividad) \
            .order_by(Pika.nombre).all()
        #print(pikasdata)
        # cargamos pikas prestocks, stocks y factor prod
        for pika, prestock, stock, factor_prod in pikasdata:            
            p = PikaData()
            p.id = pika.id
            p.nombre = pika.nombre
            p.prestock = prestock.cantidad
            p.stock = stock.cantidad
            p.upd_stock()
            p.factorprod = float(factor_prod.factor)            
            # ícono y clase css
            p.css_class = pika.nombre.replace(' ', '')
            p.img = 'img/pikas-prioridades/' + pika.nombre.replace(' ', '') + '.png'
            pikas[pika.id] = p
        
        # Cargamos pedidos de ventas (afecto stock real)
        
        ventatipo_mayorista = db.query(VentaTipo).filter(VentaTipo.nombre=='Mayorista').one()
        ventatipo_tiendaonl = db.query(VentaTipo).filter(VentaTipo.nombre=='Tienda Online').one()
        
        # los 2 pedidos de tipo mayoristas más antiguos
        cant_mayoristas = 2
        ventapedidos_mayoristas_slice = db.query(
                Venta.id
            ).filter(Venta.fecha_pedido != None, Venta.fecha == None
            ).filter(Venta.ventatipo==ventatipo_mayorista
            ).order_by(Venta.fecha_pedido
            ).all()[ : cant_mayoristas ]
            
        # sus ids
        ventapedidos_mayoristas_ids = [v.id for v in ventapedidos_mayoristas_slice]
        
        # sus datos de pikas
        ventapedidos_mayorista = db.query(
                VentaPika.pika_id,
                func.sum(VentaPika.cantidad).label('total')
            ).join(Venta
            ).filter(Venta.id.in_(ventapedidos_mayoristas_ids)
            ).group_by(VentaPika.pika_id
            ).all()
        
        # cargamos
        for pika_id, pedidos_totales in ventapedidos_mayorista:
            pikas[pika_id].pedidos += pedidos_totales
            
        # todos los pedidos de tienda online, y datos de pikas
        ventapedidos_tiendaonl = db.query(
                VentaPika.pika_id,
                func.sum(VentaPika.cantidad).label('total')
            ).join(Venta
            ).filter(Venta.fecha_pedido != None, Venta.fecha == None
            ).filter(Venta.ventatipo==ventatipo_tiendaonl
            ).group_by(VentaPika.pika_id
            ).all()

        # cargamos
        for pika_id, pedidos_totales in ventapedidos_tiendaonl:
            pikas[pika_id].pedidos += pedidos_totales

        # Calculamos factores de venta
        
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
            if p.factorventa == 0:
                p.factorventa = 0.0001
        #print(pikaventasdiarias)
        
        # imprimimos data
        print('=== Pikas Data:')
        pprint(pikas)
        
        # stock real / factor de venta
        prioridades = []
        cant_prioris_tot = 12
        cant_prioris = cant_prioris_tot
        while cant_prioris:
            print(f'-------------Iteración #{cant_prioris_tot-cant_prioris+1}')
            
            stock_relativos = {}
            for pi in pikas.values():    
                stockreal = pi.stockreal
                facvent = pi.factorventa
                #print(f"pika_id={pi.id:2}, pika_nombre={pi.nombre}")

                stckrelativo = stockreal/facvent
                stock_relativos[pi.id] = stckrelativo
                #print(f"pika=({pi.id:2})'{pi.nombre}', stockreal={stockreal:5}, facvent={facvent:.4f}, stckrelativo={stckrelativo:5.1f}")
            #print(stock_relativos)
                
            pika_id_min = min(stock_relativos, key=stock_relativos.get)
            stockrel_min = stock_relativos[pika_id_min]
            print(f'min pika = {pikas[pika_id_min].nombre}, stkR={stockrel_min}')
            
            prioridades.append((pika_id_min, stockrel_min))
            
            pikas[pika_id_min].stockreal += pikas[pika_id_min].factorprod * 1.0
            print('nuevo stkR=', pikas[pika_id_min].stockreal)
            
            cant_prioris -= 1
            #print('------------Fin iteración')
        
        # imprimimos data
        #print('=== Prioridades Data:')
        #pprint(prioridades)
                
        r = make_response(render_template(
            'menu/prioridades/prioridadimpresion.html',
            pikas=pikas,
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

