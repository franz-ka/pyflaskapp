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

DROP TABLE IF EXISTS movstockpika;

CREATE TABLE movstockpika (
        id INTEGER NOT NULL, 
        pika_id INTEGER, 
        cantidad INTEGER NOT NULL, 
        fecha DATETIME, 
        causa VARCHAR(64) NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(pika_id) REFERENCES "_pika_old" (id)
);


PRAGMA foreign_keys=on;
'''.split(';') if len(l.strip())]

#print(list(engine.execute('select * from insumo')))

db = get_db_session()

print(list(engine.execute('select * from movstockpika')))

