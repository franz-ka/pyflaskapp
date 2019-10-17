from dbconfig import Usuario, \
    Pika, Insumo, PikaInsumo, \
    PrestockPika, StockPika, StockInsumo, MovStockPika, MovStockInsumo, \
    VentaTipo, Venta, VentaPika, \
    Maquina, Gcode, Falla, Alarma, \
    FactorProductividad, \
    get_db_session
from datetime import datetime

# esto crea la nueva tabla de FactorProductividad
db = get_db_session(create_new=True)

# no hace falta commit
#db.commit()

print('Hecho')

#raise Exception()
db.query(FactorProductividad).delete()

dtnow = datetime.now()
factores = []
for pika in db.query(Pika).all():
    prenombre = pika.nombre.split(' ')[0].lower()
    factor = FactorProductividad(pika=pika, fecha_actualizado=dtnow)
    if prenombre == 'cogo':
        factor.factor = 6
    elif prenombre == 'mini':
        factor.factor = 14
    elif prenombre == 'xl':
        factor.factor = 1
    else:
        continue
    factores.append(factor)

print(db.add_all(factores))
db.commit()

print(db.query(FactorProductividad).all())
