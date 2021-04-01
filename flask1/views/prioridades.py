# coding=utf-8
from ._common import *
import csv

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

        try: checkparams(request.form, ('pika_id',))
        except Exception as e: return str(e), 400

        db = get_db()

        pika = db.query(Pika).get(request.form['pika_id'])

        operation = request.form['operation']
        if operation == 'cambiar_prod':
            try: checkparams(request.form, ('factor_nuevo',))
            except Exception as e: return str(e), 400
            factor_cant = float(request.form['factor_nuevo'])
            dtnow = datetime.datetime.now()

            factorprod = db.query(FactorProductividad).get(pika.id)
            if not factorprod:
                factorprod = FactorProductividad(pika=pika, factor=factor_cant, fecha_actualizado=dtnow)
                db.add(factorprod)
            else:
                factorprod.factor = factor_cant
                factorprod.fecha_actualizado = dtnow
        elif operation == 'cambiar_vd':
            try: checkparams(request.form, ('vd_nueva',))
            except Exception as e: return str(e), 400
            vd_cant = request.form['vd_nueva']
            if vd_cant != '':
                try:
                    vd_cant = float(vd_cant)
                except ValueError:
                    return 'El valor debe ser un número. El separador decimal es "." (punto)', 400
            else:
                vd_cant = None
            pika.venta_diaria_manual = vd_cant
        else:
            return 'Operación inválida', 400

        db.commit()

        return ''



@bp_prioridades.route("/prioridadimpresion", methods = ['GET', 'POST'])
@login_required
def menu_prioridadimpresion():
    if request.method == "GET":
        exportar_csv = 'exportar_csv' in request.args and request.args['exportar_csv'] == 'si'
        modo_noche = 'modo_noche' in request.args and request.args['modo_noche'] == 'si'
        pantalla_completa = 'pantalla_completa' in request.args and request.args['pantalla_completa'] == 'si'

        if exportar_csv:
            dtnow = datetime.datetime.now()
            csv_file_prefix = 'Cogosys - Prioridades de impresión'
            # https://strftime.org/
            csv_file_name = csv_file_prefix + dtnow.strftime(' %Y-%m-%d.csv')
            print(f'Dump csv creado en {csv_file_name}')
            csv_exporter = CsvExporter(csv_file_name)
            csv_exporter.writeVals([
                '~ Valores usados por algoritmo de prioridades de impresión de pikas ~'
            ])
            csv_exporter.writeVals(['Fecha:', dtnow.strftime('%d/%m/%Y %H:%M:%S')])
            csv_exporter.writeVals(['Modo noche activo:', 'sí' if modo_noche else 'no'])
            csv_exporter.writeVals([])

        db = get_db()

        pikas = {}

        class PikaData:
            id=0
            nombre=''
            venta_diaria_manual=None
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

        # cargamos pikas prestocks, stocks y factor prod
        if exportar_csv:
            csv_exporter.writeVals(['Valores iniciales de pikas:'])
            csv_exporter.writeVals('Pika,Venta diaria manual,Prestock,Stock,Factor prod,Pedidos,Factor venta'.split(','))
        for pika, prestock, stock, factor_prod in pikasdata:
            if modo_noche and pika.nombre.lower().startswith('xl '):
                continue
            p = PikaData()
            p.id = pika.id
            p.nombre = pika.nombre
            p.venta_diaria_manual = pika.venta_diaria_manual
            p.prestock = prestock.cantidad
            p.stock = stock.cantidad
            p.upd_stock()
            p.factorprod = float(factor_prod.factor)
            # ícono y clase css
            p.css_class = pika.nombre.replace(' ', '')
            p.img = 'img/pikas-prioridades/' + pika.nombre.replace(' ', '') + '.png'
            pikas[pika.id] = p
            if exportar_csv:
                csv_exporter.writeVals([p.nombre,p.venta_diaria_manual,p.prestock,p.stock,p.factorprod,p.pedidos,p.factorventa])
        #pprint(pikas)
        if exportar_csv:
            csv_exporter.writeVals([])
            csv_exporter.writeVals(['Pikas totales:', len(pikas)])
            csv_exporter.writeVals([])

        urgentes = get_urgentes()

        if urgentes:
            urgentes_ids = [p.venta_id for p in urgentes]
            print('urgentes_ids', urgentes_ids)
            if exportar_csv:
                csv_exporter.writeVals(['Tomando pedidos urgentes, totales:', len(urgentes_ids)])

            # todos los pedidos urgentes, y datos de pikas
            ventapedidos_urgentes = db.query(
                    VentaPika.pika_id,
                    func.sum(VentaPika.cantidad).label('total')
                ).join(Venta
                ).filter(Venta.fecha_pedido != None, Venta.fecha == None
                ).filter(Venta.id.in_(urgentes_ids)
                ).group_by(VentaPika.pika_id
                ).all()
            print('ventapedidos_urgentes', ventapedidos_urgentes)

            # cargamos
            #if exportar_csv:
            #    csv_exporter.writeVals('Pika,Pedidos'.split(','))
            for pika_id, pedidos_totales in ventapedidos_urgentes:
                if pika_id in pikas:
                    pikas[pika_id].pedidos += pedidos_totales
                    #if exportar_csv:
                    #    csv_exporter.writeVals([pikas[pika_id].nombre, pedidos_totales])
            #if exportar_csv:
            #    csv_exporter.writeVals([])
        else:
            # si no hay urgentes, usar mayoristas y tienda online
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

            if exportar_csv:
                csv_exporter.writeVals(['Tomando pedidos mayoristas por antigüedad:', len(ventapedidos_mayoristas_slice)])

            # sus ids
            ventapedidos_mayoristas_ids = [v.id for v in ventapedidos_mayoristas_slice]
            print('ventapedidos_mayoristas_ids', ventapedidos_mayoristas_ids)

            # sus datos de pikas
            ventapedidos_mayorista = db.query(
                    VentaPika.pika_id,
                    func.sum(VentaPika.cantidad).label('total')
                ).join(Venta
                ).filter(Venta.id.in_(ventapedidos_mayoristas_ids)
                ).group_by(VentaPika.pika_id
                ).all()
            print('ventapedidos_mayorista', ventapedidos_mayorista)

            # cargamos
            if exportar_csv:
                csv_exporter.writeVals('Pika,Pedidos'.split(','))
            for pika_id, pedidos_totales in ventapedidos_mayorista:
                if pika_id in pikas:
                    pikas[pika_id].pedidos += pedidos_totales
                    if exportar_csv:
                        csv_exporter.writeVals([pikas[pika_id].nombre, pedidos_totales])
            if exportar_csv:
                csv_exporter.writeVals([])

            # todos los pedidos de tienda online, y datos de pikas
            ventapedidos_tiendaonl = db.query(
                    VentaPika.pika_id,
                    func.sum(VentaPika.cantidad).label('total')
                ).join(Venta
                ).filter(Venta.fecha_pedido != None, Venta.fecha == None
                ).filter(Venta.ventatipo==ventatipo_tiendaonl
                ).group_by(VentaPika.pika_id
                ).all()
            print('ventapedidos_tiendaonl', ventapedidos_tiendaonl)
            if exportar_csv:
                pedidos_tiendaonl = db.query(Venta
                    ).filter(Venta.fecha_pedido != None, Venta.fecha == None
                    ).filter(Venta.ventatipo==ventatipo_tiendaonl
                    ).all()
                csv_exporter.writeVals(['Tomando pedidos de tienda online, totales:', len(pedidos_tiendaonl)])

            # cargamos
            if exportar_csv:
                csv_exporter.writeVals('Pika,Pedidos'.split(','))
            for pika_id, pedidos_totales in ventapedidos_tiendaonl:
                if pika_id in pikas:
                    pikas[pika_id].pedidos += pedidos_totales
                    if exportar_csv:
                        csv_exporter.writeVals([pikas[pika_id].nombre, pedidos_totales])
            if exportar_csv:
                csv_exporter.writeVals([])

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
        print('ventasdiarias', ventasdiarias)
        if exportar_csv:
            csv_exporter.writeVals(['Días tomados para calcular factor de venta:', dias_factor_venta])
            csv_exporter.writeVals(['Factor de venta calculado desde fecha:', dtventas])

        cant_factor_manual = 0
        cant_factor_cero = 0
        for pika_id, ventas_diarias in ventasdiarias:
            if pika_id in pikas:
                p = pikas[pika_id]
                if p.venta_diaria_manual != None:
                    p.factorventa = p.venta_diaria_manual
                    cant_factor_manual+=1
                else:
                    p.factorventa = float(ventas_diarias)
                if p.factorventa == 0:
                    p.factorventa = 0.0001
                    cant_factor_cero+=1
        if exportar_csv:
            csv_exporter.writeVals(['Factores de venta en manual', cant_factor_manual])
            csv_exporter.writeVals(['Factores de venta en cero', cant_factor_cero])

        # imprimimos data
        print('=== Pikas Data:')
        pprint(pikas)

        if exportar_csv:
            csv_exporter.writeVals([])
            csv_exporter.writeVals(['Fórmula de stock real:', 'prestock + stock - pedidos'])
            csv_exporter.writeVals(['Nuevos valores calculados de pikas:'])
            #csv_exporter.writeVals('Pika,Venta diaria,Prestock,Stock,Factor prod,Pedidos,Factor venta'.split(','))
            csv_exporter.writeVals('Pika,Pedidos,Factor venta,Stock real'.split(','))
            for p in pikas.values():
                #csv_exporter.writeVals([p.nombre,p.venta_diaria_manual,p.prestock,p.stock,p.factorprod,p.pedidos,round(p.factorventa, 3)])
                csv_exporter.writeVals([p.nombre,p.pedidos,round(p.factorventa, 3), p.stockreal])

        # stock real / factor de venta
        prioridades = []
        cant_prioris_tot = 18 if pantalla_completa else 16
        cant_prioris = cant_prioris_tot
        if exportar_csv:
            csv_exporter.writeVals([])
            csv_exporter.writeVals(['Prioridades a calcular:', cant_prioris])
            csv_exporter.writeVals(['Fórmula de stock relativo:', 'stock real / factor de venta'])
            # cada key es un pika_id; cada value su historia de stock relativos
            history_stock_relativos = {p.id: [] for p in pikas.values()}
            history_pika_min = []
            history_stockreal_viejo = []
            history_stockreal_nuevo = []
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

            if exportar_csv:
                for p in pikas.values():
                    history_stock_relativos[p.id].append(round(stock_relativos[p.id], 2))
                history_pika_min.append(pikas[pika_id_min].nombre)
                history_stockreal_viejo.append(pikas[pika_id_min].stockreal - pikas[pika_id_min].factorprod * 1.0)
                history_stockreal_nuevo.append(pikas[pika_id_min].stockreal)

            cant_prioris -= 1
            #print('------------Fin iteración')
        #fin while

        if exportar_csv:
            cant_prioris_numarr = [f'#{i+1}' for i in range(cant_prioris_tot)]
            csv_exporter.writeVals(['Stocks relativos por iteración por pika:'])
            csv_exporter.writeVals(['Iteración:'] + cant_prioris_numarr)
            for p in pikas.values():
                csv_exporter.writeVals([p.nombre] + history_stock_relativos[p.id])
            csv_exporter.writeVals(['Pika con menor stock relativo:'] + history_pika_min)
            csv_exporter.writeVals(['Stock real anterior de pika:'] + history_stockreal_viejo)
            csv_exporter.writeVals(['Stock real nuevo de pika:'] + history_stockreal_nuevo)

        # imprimimos data
        #print('=== Prioridades Data:')
        #pprint(prioridades)

        if urgentes:
            urgentes_ventapikas = db.query(VentaPika
            ).join(Venta
            ).filter(Venta.fecha_pedido != None, Venta.fecha == None
            ).filter(Venta.id.in_(urgentes_ids)
            ).all()
        else:
            urgentes_ventapikas = None

        if exportar_csv:
            r = csv_exporter.send()
            print('Dump csv terminado')
        else:
            r = make_response(render_template(
                'menu/prioridades/prioridadimpresion.html',
                pikas=pikas,
                prioridades=prioridades,
                urgentes_ventapikas=urgentes_ventapikas,
                pantalla_completa=pantalla_completa
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
