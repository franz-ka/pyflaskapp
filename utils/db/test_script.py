from sqlalchemy import or_, func
from dbconfig import init_db_engine, get_db_session,\
    Insumo, InsumoTipo, VentaPika, Pika, PikaInsumo, \
    Venta, VentaTipo, PrestockPika, StockPika

db = get_db_session()

q = db.query(VentaPika, func.sum(VentaPika.cantidad)) \
    .join(Venta) \
    .filter(Venta.fecha_pedido != None) \
    .filter(Venta.fecha == None) \
    .group_by(VentaPika.pika_id) \
    .order_by(Venta.fecha_pedido.asc())

#r = q.all()
#print(r)
#print([(rr[0].pika_id, rr[1]) for rr in r])

q = db.query(Pika, PrestockPika, StockPika, func.sum(VentaPika.cantidad).label('pedidos')) \
    .join(PrestockPika) \
    .join(StockPika) \
    .join(VentaPika) \
    .join(Venta) \
    .filter(Venta.fecha_pedido != None) \
    .filter(Venta.fecha == None) \
    .group_by(VentaPika.pika_id) \
    .order_by(Pika.nombre)
r = q.all()
print(r)
print(dir(r[1]))
print(r[1].PrestockPika)
print(r[1]['PrestockPika'])

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

