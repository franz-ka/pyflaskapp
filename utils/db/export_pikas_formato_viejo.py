# python3 ./utils/db/test_script.py | tail -n+3 > 'Cogosys - Pikas nuevo formato.csv'

from dbconfig import init_db_engine, get_db_session, \
    Usuario, \
    Pika, Insumo, InsumoTipo, PikaInsumo, \
    PrestockPika, StockPika, StockInsumo, MovPrestockPika, MovStockPika, MovStockInsumo

import sys, datetime, itertools
from pprint import pprint
from sqlalchemy import or_, func
db = get_db_session()

pikas = db.query(Pika).all()
#[pprint(vars(pika)) for pika in pikas]
#[pprint(pika.nombre) for pika in pikas]
print('id,nombre original,presentación,personaje')
for pika in pikas:
    presentacion = ''
    personaje = ''

    snom = pika.nombre.lower().strip()
    if snom.startswith('xl'):
        presentacion = 'XL'
    elif snom.startswith('cogo'):
        presentacion = 'Cogo'
    elif snom.startswith('mini'):
        presentacion = 'Mini'
    elif snom.startswith('mostrador'):
        presentacion = 'Mostrador'

    if presentacion:
        personaje = ' '.join(pika.nombre.split(' ')[1:])

    print(f'{pika.id},{pika.nombre},{presentacion},{personaje}')
