import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path))


from dbconfig import get_db_session, Valor

# Crear la nueva tabla si no existe
db = get_db_session(create_new=True)

db.add(Valor(nombre='insumos_stock_extendido_semanas', valor='10'))

db.commit()

# Mostrar todas
print(db.query(Valor).all())
