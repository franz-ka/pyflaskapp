from sqlalchemy import or_, func
from dbconfig import init_db_engine, get_db_session,\
    Insumo, InsumoTipo, VentaPika, Pika, PikaInsumo, \
    Venta, VentaTipo, PrestockPika, StockPika, Alarma, \
    StockInsumo

db = get_db_session()


q2 = db \
    .query(Insumo, func.sum(VentaPika.cantidad*PikaInsumo.cantidad).label('pedidos')) \
    .join(Venta) \
    .filter(Venta.fecha_pedido != None, Venta.fecha == None) \
    .join(PikaInsumo, VentaPika.pika_id == PikaInsumo.pika_id) \
    .group_by(PikaInsumo.insumo_id) \
    .join(Insumo) \
    .subquery()
print(q2)
print(dir(q2))
print(q2.name, 123, q2.alias, 234, q2.columns)

q = db \
    .query(Insumo, Alarma, StockInsumo, 'anon_1.pedidos', (StockInsumo.cantidad - q2.pedidos).label('stock_total')) \
    .join(Alarma) \
    .join(StockInsumo) \
    .join(q2, isouter=True)
print(q)
r = q.all()
print(r)
#print(len(r))

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

