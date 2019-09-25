from dbconfig import Usuario, \
    Pika, Insumo, PikaInsumo, \
    PrestockPika, StockPika, StockInsumo, MovStockPika, MovStockInsumo, \
    VentaTipo, Venta, VentaPika, \
    Maquina, Gcode, Falla, Alarma, \
    get_db_session
from datetime import datetime

db = get_db_session()

for i in db.query(PrestockPika).all():
    print(i, i.cantidad, i.fecha)