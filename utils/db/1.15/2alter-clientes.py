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

ALTER TABLE cliente RENAME TO _cliente_old;

CREATE TABLE cliente (
	id INTEGER NOT NULL,
	nombre VARCHAR(128) NOT NULL,
	nombre_de_contacto VARCHAR(128),
	telefono VARCHAR(64),
	mail VARCHAR(64),
	tipo_cliente_id INTEGER,
	tipo_local_id INTEGER,
	ubicacion_osm_id INTEGER,
	ubicacion VARCHAR(128),
	PRIMARY KEY (id),
	FOREIGN KEY(tipo_cliente_id) REFERENCES tipocliente (id),
	FOREIGN KEY(tipo_local_id) REFERENCES tipolocal (id),
	FOREIGN KEY(ubicacion_osm_id) REFERENCES ubicacionosm (id)

);

INSERT INTO cliente SELECT id,nombre,null,contacto,null,null,null,null,null FROM _cliente_old;

DROP TABLE IF EXISTS _cliente_old;

PRAGMA foreign_keys=on;
'''.split(';') if len(l.strip())]

print('Listo!')

input('\nPresioná <enter> para terminar ')
