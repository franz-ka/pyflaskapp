from ._common import *

from enum import Enum, unique
@unique
class INSU_STOCK_CAUSA(Enum):
    INGRESO = 'ingreso'
    MANUAL = 'modificación manual'
    ABIERTO = 'consumible abierto'
    PRESTOCK = 'prestock pika'
    ARMADO = 'armado pika'
    VENTA = 'venta pika'

def inc_stock_insumo(insumo, stockinsumo, cantidad, date, causa):
    if type(cantidad) != int: cantidad = int(cantidad)

    return set_stock_insumo(insumo, stockinsumo, stockinsumo.cantidad + cantidad, date, causa)

def set_stock_insumo(insumo, stockinsumo, cantidad, date, causa):
    if type(causa) != INSU_STOCK_CAUSA: raise Exception('Causa no aceptada/inválida')

    if type(cantidad) != int: cantidad = int(cantidad)

    db = get_db()

    stockinsumo.cantidad = cantidad
    stockinsumo.fecha = date

    mov = MovStockInsumo(
        insumo = insumo,
        cantidad = stockinsumo.cantidad,
        fecha = stockinsumo.fecha,
        causa = causa.value)
    db.add(mov)
