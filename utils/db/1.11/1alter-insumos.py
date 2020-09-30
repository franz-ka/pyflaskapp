import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path))


from dbconfig import init_db_engine, get_db_session, Insumo, InsumoTipo

engine = init_db_engine()

[engine.execute(l.strip()) for l in '''
PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

ALTER TABLE insumo RENAME TO _insumo_old;

CREATE TABLE insumo (
    id INTEGER NOT NULL,
    insumotipo_id INTEGER,
    nombre VARCHAR(64) NOT NULL,
    delay_reposicion FLOAT NOT NULL,
    margen_seguridad FLOAT NOT NULL,
    ciclo_reposicion FLOAT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(insumotipo_id) REFERENCES "_insumo_old" (id)
);

INSERT INTO insumo SELECT id,insumotipo_id,nombre,1,1,4 FROM _insumo_old;

DROP TABLE IF EXISTS _insumo_old;

PRAGMA foreign_keys=on;
'''.split(';') if len(l.strip())]

print('Listo!')
