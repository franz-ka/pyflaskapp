import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path))


from dbconfig import init_db_engine, get_db_session, StockInsumo, MovStockInsumo

engine = init_db_engine()

[engine.execute(l.strip()) for l in '''
PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

DROP TABLE IF EXISTS movstockinsumo;

CREATE TABLE movstockinsumo (
        id INTEGER NOT NULL,
        insumo_id INTEGER,
        cantidad INTEGER NOT NULL,
        fecha DATETIME,
        causa VARCHAR(64) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(insumo_id) REFERENCES "_insumo_old" (id)
);


PRAGMA foreign_keys=on;
'''.split(';') if len(l.strip())]

#print(list(engine.execute('select * from insumo')))

db = get_db_session()

insutocks = db.query(StockInsumo).all()
for insutock in insutocks:
    mov = MovStockInsumo(
        insumo = insutock.insumo,
        cantidad = insutock.cantidad,
        fecha = insutock.fecha,
        causa = 'primer registro')
    db.add(mov)

db.commit()

print(db.query(MovStockInsumo).all())
