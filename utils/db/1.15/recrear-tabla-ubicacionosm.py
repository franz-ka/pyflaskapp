import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path))

from dbconfig import init_db_engine, get_db_session, UbicacionOSM

# drop
db = get_db_session()
UbicacionOSM.__table__.drop()

# recrear
db = get_db_session(create_new=True)

print('Listo!')
