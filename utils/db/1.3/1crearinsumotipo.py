import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path)) 


from dbconfig import get_db_session, InsumoTipo
from datetime import datetime

# Crear la nueva tabla si no existe
db = get_db_session(create_new=True)

# Borrar viejas
db.query(InsumoTipo).delete()

# Insertar base
insus = [
    InsumoTipo(nombre='Prestock'),
    InsumoTipo(nombre='Armado'),
    InsumoTipo(nombre='Venta'),
    InsumoTipo(nombre='Consumible'),
]
    
print(insus)
print(db.add_all(insus))
db.commit()

# Mostrar todas
print(db.query(InsumoTipo).all())