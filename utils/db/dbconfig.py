import sys
from pathlib import Path
app_path = (Path(__file__).parent.parent.parent).absolute()
print('Usando path =', str(app_path))
sys.path.append(str(app_path / 'flask1'))

from models import Base, \
    Usuario, \
    Pika, Insumo, InsumoTipo, PikaInsumo, \
    PrestockPika, StockPika, StockInsumo, MovStockPika, MovStockInsumo, \
    VentaTipo, Venta, VentaPika, \
    StockPikaColor, StockInsumoColor, \
    Maquina, Gcode, Falla, Alarma, \
    FactorProductividad, PedidoUrgente

def init_db_engine():
    from sqlalchemy import create_engine
    __dbconnstr = 'sqlite:///' + str(app_path / 'instance' / 'flask1.db')
    print('Usando conn str =', __dbconnstr)
    return create_engine(__dbconnstr, echo=True)

def get_db_session(create_new=False):
    from sqlalchemy.orm import sessionmaker, scoped_session
    engine = init_db_engine()
    #Base.metadata.drop_all(engine)
    if create_new:
        Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    return DBSession()
