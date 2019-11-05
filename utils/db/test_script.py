from sqlalchemy import or_, func
from dbconfig import init_db_engine, get_db_session,\
    Insumo, InsumoTipo, VentaPika, Pika, PikaInsumo, Venta, VentaTipo

db = get_db_session()


ventatipo_mayorista = db.query(VentaTipo).filter(VentaTipo.nombre=='Mayorista').one()
ventatipo_tiendaonl = db.query(VentaTipo).filter(VentaTipo.nombre=='Tienda Online').one()

# Cargamos pedidos de ventas (afecto stock real)

# los 2 pedidos mayoristas más antiguos
ventapedidos_2mayoristas = db.query(
        Venta.id
    ).filter(Venta.fecha_pedido != None, Venta.fecha == None
    ).filter(Venta.ventatipo==ventatipo_mayorista
    ).order_by(Venta.fecha_pedido
    ).all()[:2]
ventapedidos_2mayoristas = [v.id for v in ventapedidos_2mayoristas]

# y sus datos de pedidos por pikas
ventapedidos_mayorista = db.query(
        VentaPika.pika_id,
        func.sum(VentaPika.cantidad).label('total')
    ).join(Venta
    ).filter(Venta.id.in_(ventapedidos_2mayoristas)
    ).group_by(VentaPika.pika_id
    ).all()
    
# todos los pedidos de tienda online, y datos de pikas
ventapedidos_tiendaonl = db.query(
        VentaPika.pika_id,
        func.sum(VentaPika.cantidad).label('total')
    ).join(Venta
    ).filter(Venta.fecha_pedido != None, Venta.fecha == None
    ).filter(Venta.ventatipo==ventatipo_tiendaonl
    ).group_by(VentaPika.pika_id
    ).all()
    
# juntamos las listas
ventapedidos = []
_ventapedidos_added = {}
for pika_id, pedidos_totales in ventapedidos_mayorista + ventapedidos_tiendaonl:
    if pika_id not in _ventapedidos_added:
        _ventapedidos_added[pika_id] = len(ventapedidos)
        ventapedidos.append((pika_id, pedidos_totales))
    else:
        i = _ventapedidos_added[pika_id]
        tup = ventapedidos[i]
        ventapedidos[i] = (tup[0], tup[1] + pedidos_totales)
    
    
print(ventapedidos_2mayoristas)
print(ventapedidos_mayorista)
print(ventapedidos_tiendaonl)
print('PP', ventapedidos)
print('PP', _ventapedidos_added)

#q = db.query(VentaTipo).all()

#print([(v.id, v.nombre) for v in q])
#alarmas_stocks = db.query(Alarma, StockInsumo).filter(StockInsumo.insumo_id == Alarma.insumo_id).all()

'''q = db.query(func.sum(VentaPika.cantidad*PikaInsumo.cantidad).label('insumo_pedidos')) \
.join(Venta) \
.filter(Venta.fecha_pedido != None, Venta.fecha == None) \
.join(PikaInsumo, VentaPika.pika_id == PikaInsumo.pika_id) \
.filter(PikaInsumo.insumo_id==30) \
.group_by(PikaInsumo.insumo_id)
#print(q)

db.query(PikaInsumo).filter()
r = q.all()
print('RRRR', r)
print('RRRR', r[0], r[0].insumo_pedidos)'''
#print(dir(r[0]))

#for a in r:
#    print('+', a.VentaPika.venta.fecha_pedido, a.PikaInsumo.insumo_id, a.PikaInsumo.cantidad)

