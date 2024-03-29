import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path))


#from dbconfig import init_db_engine, get_db_session, Venta, Cliente
from dbconfig import init_db_engine

engine = init_db_engine()

# .schema TABLA para obtener CREATE
[engine.execute(l.strip()) for l in '''
PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

ALTER TABLE pika RENAME TO _pika_old;

CREATE TABLE pika (
    id INTEGER NOT NULL,
    nombre VARCHAR(64) NOT NULL,
    venta_diaria_manual FLOAT,
	oculto BOOLEAN NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO pika SELECT id,nombre,venta_diaria_manual,False FROM _pika_old;

DROP TABLE IF EXISTS _pika_old;

PRAGMA foreign_keys=on;
'''.split(';') if len(l.strip())]

print('Listo!')

input('\nPresioná <enter> para terminar ')
