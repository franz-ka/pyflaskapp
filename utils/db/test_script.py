from sqlalchemy import or_, func
from dbconfig import init_db_engine, get_db_session,\
    Insumo, InsumoTipo, VentaPika, Pika, PikaInsumo, \
    Venta, VentaTipo, PrestockPika, StockPika, Alarma, \
    StockInsumo
import sys, datetime

db = get_db_session()

days_totales = 60
dtnow = datetime.datetime.now()
dtstart = dtnow - datetime.timedelta(days=days_totales)
movstocks = db.query(MovStockPika) \
    .filter(MovStockPika.fecha >= dtstart) \
    .join(Pika) \
    .order_by(Pika.id, MovStockPika.fecha) \
    .all()
    
import itertools 


def grouperPika( item ): 
    return item.pika
def grouperMonthDay( item ): 
    return item.fecha.month, item.fecha.day

for (pika, grpPika) in itertools.groupby(movstocks, grouperPika):
    #pika_data = PikaData(pika.id, pika.nombre)
    #pikasdata.append(pika_data)
    sum_dates = {}
    for ((month, day), grpMonDay) in itertools.groupby(grpPika, grouperMonthDay):
        if month not in sum_dates:
            sum_dates[month] = {}
        if day not in sum_dates[month]:
            sum_dates[month][day] = 0
        for mvs in grpMonDay:
            sum_dates[month][day] += mvs.cantidad
    print(pika, sum_dates)
print(dtstart)
print(dtstart + datetime.timedelta(days=1))
print(dtstart + datetime.timedelta(days=2))
print(dtstart + datetime.timedelta(days=3))
print(dtstart + datetime.timedelta(days=4))
sys.exit()

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

