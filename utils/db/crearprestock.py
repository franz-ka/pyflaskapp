from dbconfig import Usuario, \
    Pika, Insumo, PikaInsumo, \
    PrestockPika, StockPika, StockInsumo, MovStockPika, MovStockInsumo, \
    VentaTipo, Venta, VentaPika, \
    Maquina, Gcode, Falla, Alarma, \
    get_db_session
from datetime import datetime

# esto crea la nueva tabla de PrestockPika
db = get_db_session(create_new=True)

#raise Exception()

'''prestocks = []
now = datetime.now()
for pika in db.query(Pika).all():
    prestocks.append(PrestockPika(pika=pika, cantidad=0, fecha=now))
    
print(prestocks)
print(db.add_all(prestocks))
db.commit()

print(db.query(PrestockPika).all())'''

dtnow = datetime.datetime.now()
for pika in db.query(Pika).all():
    prestockpika = db.query(PrestockPika).get(pika.id)
    if not prestockpika:
        db.add(PrestockPika(pika=pika, cantidad=0, fecha=dtnow))
        print('Agregado prestock a', pika.nombre)
db.commit()

