from dbconfig import init_db_engine, get_db_session, \
    Usuario, \
    Pika, Insumo, InsumoTipo, PikaInsumo, \
    PrestockPika, StockPika, StockInsumo, MovPrestockPika, MovStockPika, MovStockInsumo, \
    VentaTipo, Venta, VentaPika, \
    StockPikaColor, StockInsumoColor, \
    Maquina, Gcode, Falla, Alarma, \
    FactorProductividad, PedidoUrgente, \
    Valor, Cliente, \
    TipoCliente, TipoLocal, UbicacionOSM

import sys, datetime, itertools
from pprint import pprint
from sqlalchemy import or_, func
db = get_db_session()

clientes = db.query(Cliente).all()
#pprint(clientes)
#print(clientes[0])
#pprint(dir(clientes[0]))
#pprint(vars(clientes[0]))
#pprint(clientes[0].ventas)
#pprint(clientes[0].ventas[-1])
#pprint(dir(clientes[0].ventas[-1]))
'''pprint(clientes[0].ventas[-1].ventapikas)
pprint(clientes[0].ventas[-1].ventapikas[0])
pprint(vars(clientes[0].ventas[-1].ventapikas[0]))'''

#pprint(clientes[0].ventas[-1].fecha)
pv = clientes[0].ventas[0].fecha
uv = clientes[0].ventas[-1].fecha
diff = uv - pv
print(diff)
#pprint(dir(diff))
print(diff.total_seconds())
print(diff.days)

pikas_cogos = db.query(Pika).filter(Pika.nombre.ilike('cogo %')).all()
pprint(pikas_cogos)
pikas_cogos_ids = [pika.id for pika in pikas_cogos]
pprint(pikas_cogos_ids)

vp = db.query(VentaPika).first()
pprint(vars(vp))
'''ventapikas = db.query(VentaPika).join(Venta)\
    .filter(Venta.fecha != None)\
    .order_by(Venta.fecha.desc(), Venta.id.desc())
pprint([vp.venta.ventapikas for vp in ventapikas.all()[:10]])'''
