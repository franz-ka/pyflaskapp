import sys
from pathlib import Path
app_path = (Path(__file__).parent.parent).absolute()
print('Usando path =', str(app_path))
sys.path.append(str(app_path)) 


from dbconfig import init_db_engine
    
engine = init_db_engine()

[engine.execute(l.strip()) for l in '''
PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

ALTER TABLE insumo RENAME TO _insumo_old;

CREATE TABLE insumo
(
    id INTEGER NOT NULL, 
    insumotipo_id INTEGER, 
    nombre VARCHAR(64) NOT NULL, 
    PRIMARY KEY (id)
    FOREIGN KEY(insumotipo_id) REFERENCES insumotipo (id)
);

INSERT INTO insumo SELECT id,null,nombre FROM _insumo_old;

DROP TABLE IF EXISTS _insumo_old;

PRAGMA foreign_keys=on;
'''.split(';') if len(l.strip())]

print(list(engine.execute('select * from insumo')))
