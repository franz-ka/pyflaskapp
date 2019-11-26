import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path)) 


from dbconfig import get_db_session, MovStockPika

db = get_db_session()

# Borrar todas
db.query(MovStockPika).delete()
db.commit()

print(db.query(MovStockPika).all())