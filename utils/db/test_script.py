from sqlalchemy import or_, func
from dbconfig import init_db_engine, get_db_session, \
    Insumo, InsumoTipo, VentaPika, Pika, PikaInsumo, \
    Venta, VentaTipo, PrestockPika, StockPika, Alarma, \
    StockInsumo, MovStockPika, MovPrestockPika
import sys, datetime, itertools 
from pprint import pprint
#get_db = get_db_session

db = get_db_session()
ventapikas = db.query(VentaPika).join(Venta)\
    .filter(Venta.fecha != None)\
    .order_by(Venta.fecha.desc(), Venta.id.desc())


pprint([vp.venta.ventapikas for vp in ventapikas.all()[:10]])
