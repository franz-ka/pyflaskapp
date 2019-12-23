from sqlalchemy import or_, func
from dbconfig import init_db_engine, get_db_session, \
    Insumo, InsumoTipo, VentaPika, Pika, PikaInsumo, \
    Venta, VentaTipo, PrestockPika, StockPika, Alarma, \
    StockInsumo, MovStockPika, MovPrestockPika
import sys, datetime, itertools 
from pprint import pprint
get_db = get_db_session

db = get_db_session()
# esto devuelve un array de listas de 4 elementos [0]=Pika [1]=PrestockPika [2]=StockPika
pedidos_query = db.query(VentaPika.pika_id, func.sum(VentaPika.cantidad).label('pedidos')) \
    .join(Venta) \
    .filter(Venta.fecha_pedido != None) \
    .filter(Venta.fecha == None) \
    .group_by(VentaPika.pika_id) \
    .subquery()
pprint('#############')
pprint(dir(pedidos_query.columns))
    
DATA = db.query(Pika, PrestockPika, StockPika, pedidos_query.columns.pedidos) \
    .join(PrestockPika) \
    .join(StockPika) \
    .join(pedidos_query, Pika.id == pedidos_query.columns.pika_id, isouter=True) \
    .order_by(Pika.nombre) \
    .all()

pprint(dir(DATA[0]))
pprint(DATA)
