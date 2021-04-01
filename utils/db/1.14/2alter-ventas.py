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

ALTER TABLE venta RENAME TO _venta_old;

CREATE TABLE venta (
	id INTEGER NOT NULL,
	ventatipo_id INTEGER,
	cliente_id INTEGER,
	fecha DATETIME,
	comentario VARCHAR(128),
    fecha_pedido DATETIME,
	PRIMARY KEY (id),
	FOREIGN KEY(ventatipo_id) REFERENCES "_venta_old" (id)
	FOREIGN KEY(cliente_id) REFERENCES cliente (id)
);

INSERT INTO venta SELECT id,ventatipo_id,null,fecha,comentario,fecha_pedido FROM _venta_old;

DROP TABLE IF EXISTS _venta_old;

PRAGMA foreign_keys=on;
'''.split(';') if len(l.strip())]

print('Listo!')
