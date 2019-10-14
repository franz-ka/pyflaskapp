from dbconfig import Usuario, \
    Pika, Insumo, PikaInsumo, \
    PrestockPika, StockPika, StockInsumo, MovStockPika, MovStockInsumo, \
    VentaTipo, Venta, VentaPika, \
    Maquina, Gcode, Falla, Alarma, \
	StockPikaColor, \
    get_db_session
from datetime import datetime

# esto crea la nueva tabla de StockPikaColor y StockInsumoColor
db = get_db_session(create_new=True)

#raise Exception()
db.query(StockPikaColor).delete()

colores = []
for pika in db.query(Pika).all():
	prenombre = pika.nombre.split(' ')[0].lower()
	color = StockPikaColor(pika=pika)
	if prenombre == 'cogo':
		color.cantidad_bajo = 3
		color.cantidad_medio = 8
	elif prenombre == 'mini':
		color.cantidad_bajo = 10
		color.cantidad_medio = 26
	elif prenombre == 'xl':
		color.cantidad_bajo = 2
		color.cantidad_medio = 4
	else:
		continue
	colores.append(color)

print(db.add_all(colores))
db.commit()

print(db.query(StockPikaColor).all())
