from sqlalchemy import or_, func
from dbconfig import init_db_engine, get_db_session,\
    Insumo, InsumoTipo, VentaPika, Pika, PikaInsumo, \
    Venta, VentaTipo, PrestockPika, StockPika, Alarma, \
    StockInsumo, MovStockPika, MovPrestockPika
import sys, datetime, itertools 
from pprint import pprint
get_db = get_db_session

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

class PikaData:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.movs_prestock = None
        self.movs_stock = None
        self.pedidos = None
        self.points = []
        self.points_data = []
        
    def print(self):
        print(f'Pika id={self.id}, nombre={self.nombre}')
        print(f'- movs_prestock:')
        pprint(self.movs_prestock)
        print(f'- movs_stock:')
        pprint(self.movs_stock)
        print(f'- pedidos:')
        pprint(self.pedidos)
        
    def print_points(self):
        print(f'Pika id={self.id}, nombre={self.nombre}')
        print(f'- points:')
        pprint(self.points)
        print(f'- points_data:')
        pprint(self.points_data)
        
pikas = {}

def grouperPikaId( item ): 
    if (hasattr(item, 'VentaPika')):
        return item.VentaPika.pika_id
    else:
        return item.pika_id

db = get_db()
a=db.query(MovPrestockPika).order_by(MovPrestockPika.fecha).limit(1).one()
print(a.fecha)
sys.exit()
#########################

# Parámetros iniciales
pika_ids = [14, 9, 12]#list(range(14))#
days_totales = 8#60
dtnow = datetime.datetime.now()
dtstart = dtnow - datetime.timedelta(days=days_totales)
print(f"Días totales={days_totales}, fecha actual={dtnow}, fecha comienzo={dtstart}")

# Traer data de pikas
pikas_sql = db.query(Pika).filter(Pika.id.in_(pika_ids)).all()

movprestock = db.query(MovPrestockPika) \
    .filter(MovPrestockPika.fecha >= dtstart, MovPrestockPika.pika_id.in_(pika_ids)) \
    .order_by(MovPrestockPika.pika_id, MovPrestockPika.fecha) \
    .all()

movstock = db.query(MovStockPika) \
    .filter(MovStockPika.fecha >= dtstart, MovStockPika.pika_id.in_(pika_ids)) \
    .order_by(MovStockPika.pika_id, MovStockPika.fecha) \
    .all()

pedidos = db.query(VentaPika, Venta) \
    .join(Venta) \
    .filter(
        Venta.fecha_pedido != None,
        Venta.fecha_pedido >= dtstart, # no queremos pedidos históricos, solo los del plazo
        or_(Venta.fecha == None, Venta.fecha > dtstart), # si se vendieron antes del comienzo del plazo no nos interesan (ya se contabilizan en los stocks)
        VentaPika.pika_id.in_(pika_ids)
    ) \
    .order_by(VentaPika.pika_id, Venta.fecha_pedido) \
    .all()

# Cargar data en objetos de pikas
for pika in pikas_sql:
    pikas[pika.id] = PikaData(pika.id, pika.nombre)
    
for pika_id, movs in itertools.groupby(movprestock, grouperPikaId):
    pikas[pika_id].movs_prestock = list(movs) 

for pika_id, movs in itertools.groupby(movstock, grouperPikaId):
    pikas[pika_id].movs_stock =  list(movs)

for pika_id, peds in itertools.groupby(pedidos, grouperPikaId):
    pikas[pika_id].pedidos =  list(peds)

# Reportar data de pikas cargada
for p in pikas.values():
    print('='*50, 'Pikas data')
    p.print()

# Calcular puntos de gráfico (+ 1 porque hay que contar el día de hoy)
print('@'*50, 'Days data')
for day in range(days_totales + 1):
    date = dtstart + datetime.timedelta(days=day)
    print(f"Day {day}, dtstart={dtstart}, date={date}")
    
    for pika in pikas.values():
        # Calculamos la última actualización de prestock antes (o igual) que la fecha del punto
        if pika.movs_prestock:
            for mov in pika.movs_prestock:
                if mov.fecha > date:
                    break
            prestock = mov.cantidad
        else:
            prestock = 0
            
        # Idem prestock
        if pika.movs_stock:
            for mov in pika.movs_stock:
                if mov.fecha > date:
                    break
            stock = mov.cantidad
        else:
            stock = 0
            
        # Calculamos pedido al día del punto
        pedido = 0
        if pika.pedidos:
            for venta_pika, venta in pika.pedidos:
                if venta.fecha_pedido > date:
                    break
                # Si no se vendió, todo ok, está como pedido pendiente
                # Si se vendió, pero después de la fecha del punto, estuvo como pedido en ese momento
                if not venta.fecha or venta.fecha > date:
                    pedido += venta_pika.cantidad
            
        stock_real = prestock + stock - pedido
        pika.points.append(stock_real)
        pika.points_data.append((prestock, stock, pedido))

# Reportar points
for p in pikas.values():
    print('#'*50, 'Points data')
    p.print_points()

