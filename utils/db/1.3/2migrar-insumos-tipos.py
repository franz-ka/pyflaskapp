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

#print(list(engine.execute('select * from insumo')))

db = get_db_session()

tipo_prestock = db.query(InsumoTipo).filter(InsumoTipo.nombre=='Prestock').one()
tipo_armado = db.query(InsumoTipo).filter(InsumoTipo.nombre=='Armado').one()
tipo_venta = db.query(InsumoTipo).filter(InsumoTipo.nombre=='Venta').one()
tipo_consumible = db.query(InsumoTipo).filter(InsumoTipo.nombre=='Consumible').one()

insus = db.query(Insumo).all()
for insu in insus:
    if insu.nombre.startswith(('X -','Y -','Z -','PLA ')):
        insu.insumotipo = tipo_consumible
    elif insu.nombre.startswith(('Packaging', 'Sticker')):
        insu.insumotipo = tipo_venta
    elif insu.nombre.startswith(('Imán', 'Argollas', 'Triangulito')):
        insu.insumotipo = tipo_armado
    elif insu.nombre.startswith('Oring'):
        insu.insumotipo = tipo_prestock
    
db.commit()

print(list(engine.execute('select * from insumo')))

