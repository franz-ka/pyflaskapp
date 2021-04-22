import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path))

from dbconfig import get_db_session, TipoCliente, TipoLocal

# Crear la nueva tabla si no existe
db = get_db_session(create_new=True)

db.add_all([TipoCliente(nombre='Distribuidor'), TipoCliente(nombre='Mayorista')])
db.add_all([TipoLocal(nombre='Físico'), TipoLocal(nombre='Virtual')])

db.commit()

# Mostrar todas
print(db.query(TipoCliente).all())
print(db.query(TipoLocal).all())

input('\nPresioná <enter> para terminar ')
