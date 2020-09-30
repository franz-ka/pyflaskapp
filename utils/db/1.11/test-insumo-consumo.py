import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path))

from dbconfig import init_db_engine, get_db_session, StockInsumo, MovStockInsumo, Insumo
import datetime
from pprint import pprint
import itertools, collections
from sqlalchemy import or_, not_, and_, func


db = get_db_session()

rango_tiempo_dias = 7
dtnow = datetime.datetime.now()
dtcomienzo = dtnow - datetime.timedelta(days=rango_tiempo_dias)
print(f'El parámetro de rango de días es {rango_tiempo_dias}. Tomando como fecha de inicio {dtcomienzo}')

# Traemos movimientos históricos de stock de insumos
movstocks = db.query(MovStockInsumo) \
    .filter(MovStockInsumo.fecha >= dtcomienzo) \
    .order_by(MovStockInsumo.insumo_id, MovStockInsumo.fecha.asc()) \
    .all()
print(f'Encontrados {len(movstocks)} movimientos de stock')

InsumoValores = collections.namedtuple('InsumoValores', 'consumo_total, stock_actual')
insumos_valores = {}

# Agrupamos movimientos por insumo
# itertools.groupby() in Python - https://www.geeksforgeeks.org/itertools-groupby-in-python/
key_func = lambda i: i.insumo_id
for insumo_id, insumo_movstocks in itertools.groupby(movstocks, key_func):

    # Viene como enumerador así que lo convertimos a lista
    insumo_movstocks = list(insumo_movstocks)
    primer_stock = insumo_movstocks[0]
    print(f'Analizando {len(insumo_movstocks)} movimientos de stock de insumo {insumo_id}')

    # Traemos el movimiento justo anterior al primer movimiento de nuestra lista
    # (si existe)
    pre_primer_stock = db.query(MovStockInsumo) \
        .filter(MovStockInsumo.insumo_id == insumo_id, MovStockInsumo.fecha < primer_stock.fecha) \
        .order_by(MovStockInsumo.fecha.desc()) \
        .first()

    # Si existe usarlo para calcular el primer (posible) consumo. Si no existe
    # el primer bucle del for va a estar de más pero no genera problemas.
    if pre_primer_stock:
        stock_inicial = pre_primer_stock.cantidad
    else:
        stock_inicial = primer_stock.cantidad

    consumo_total = 0
    last_stock = stock_inicial
    for movstock in insumo_movstocks:
        # Si el stock actual es menor al stock anterior, hubo consumo
        if movstock.cantidad < last_stock:
            consumo_total += last_stock - movstock.cantidad
        last_stock = movstock.cantidad

    # Guardamos valores
    insumos_valores[insumo_id] = InsumoValores(consumo_total=consumo_total, stock_actual=last_stock)

print(f'Valores de insumos:')
# Cargamos valores como campos "naturales" de insumos
insumos = db.query(Insumo).filter(Insumo.id.in_(insumos_valores.keys())).all()
for insumo in insumos:
    insumo_valores = insumos_valores[insumo.id]
    insumo.consumo_total = insumo_valores.consumo_total
    insumo.stock_actual = insumo_valores.stock_actual
    print(f'- {insumo.nombre}: consumo={insumo.consumo_total}, stock={insumo.stock_actual}')
