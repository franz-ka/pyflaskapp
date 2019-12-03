from sqlalchemy import or_, func
from dbconfig import init_db_engine, get_db_session,\
    Insumo, InsumoTipo, VentaPika, Pika, PikaInsumo, \
    Venta, VentaTipo, PrestockPika, StockPika, Alarma, \
    StockInsumo, MovStockPika, MovPrestockPika
import sys, datetime, itertools 

'''
El script general de gráficos tiene dos inputs:
La cantidad de días desde hoy hacia el pasado a tomar = D
Los ids de picas a mirar = Ps

El gráfico tiene un punto por cada día desde D hasta hoy
Cada punto muestra el prestock+stock-pedidos que había en ese momento
Por ende, hay que traer estos 3 datos

Prestock y stock provienen de sus respectivas tablas de movimiento
Pedidos hay que deducirlo de la tabla de ventas
Todo filtrado por los pikas ids que se seleccionaron

Dado un punto X en el gráfico (fecha), se mira
- el pre/stock con max(mov.fecha<=X)
- la venta con fecha_pedido <= X y fecha_venta[= None or > X]
'''


db = get_db_session()

days_totales = 60
dtnow = datetime.datetime.now()
dtstart = dtnow - datetime.timedelta(days=days_totales)
print(days_totales, dtnow, dtstart)

def grouperPika( item ): 
    return item.pika

movprestock = db.query(MovPrestockPika) \
    .filter(MovPrestockPika.fecha >= dtstart) \
    .order_by(MovPrestockPika.fecha) \
    .join(Pika) \
    .all()

l = [(pika,list(movs)) for pika, movs in itertools.groupby(movprestock, grouperPika)]
print(l)
sys.exit()



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

