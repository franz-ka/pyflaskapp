from dbconfig import Usuario, \
    Pika, Insumo, PikaInsumo, \
    PrestockPika, StockPika, StockInsumo, MovStockPika, MovStockInsumo, \
    VentaTipo, Venta, VentaPika, \
    Maquina, Gcode, Falla, Alarma, \
    get_db_session
from datetime import datetime

# esto crea la nueva tabla de PrestockPika
db = get_db_session(create_new=True)

# no hace falta commit
#db.commit()

print('Hecho')