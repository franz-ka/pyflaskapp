import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path)) 


from dbconfig import get_db_session, PedidoUrgente
from datetime import datetime

# Crear la nueva tabla si no existe
db = get_db_session(create_new=True)

# Mostrar todas
print(db.query(PedidoUrgente).all())