import click
from flask import current_app, g
from flask.cli import with_appcontext
from datetime import datetime

__dbconnstr = None

def init_db_engine(app):
    global __dbconnstr
    from sqlalchemy import create_engine
    __dbconnstr = 'sqlite:///' + app.config['DATABASE']
    return create_engine(__dbconnstr, echo=app.config['DEBUG_SQL'])


# Define and Access the Database - http://flask.pocoo.org/docs/1.0/tutorial/database/
def get_db():
    # g is a special object that is unique for each request.
    # It is used to store data that might be accessed by multiple functions during the request
    if 'db' not in g:
        g.db = current_app.DBSession
        #print(f'Fetch DB #{ id(g.db) }')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def recreate_db():
    return
    from sqlalchemy.orm import sessionmaker, scoped_session
    from .models import Base, \
        Usuario, \
        Pika, Insumo, PikaInsumo, \
        StockPika, StockInsumo, MovStockPika, MovStockInsumo, \
        VentaTipo, Venta, VentaPika, \
        Maquina, Gcode, Falla, Alarma
    engine = init_db_engine(current_app)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)

    db = DBSession()

    # Usuarios
    import hashlib
    hashMark = hashlib.sha256(b"markdijono").hexdigest()
    hash123 = hashlib.sha256(b"4321").hexdigest()
    db.add_all((
        Usuario(nombre='admin', passhash=hashMark, esadmin=True),
        Usuario(nombre='nacho', passhash=hash123, esadmin=False),
        Usuario(nombre='rama', passhash=hash123, esadmin=False),
        Usuario(nombre='sosa', passhash=hash123, esadmin=False),
        Usuario(nombre='tomi', passhash=hash123, esadmin=False),
        Usuario(nombre='dani', passhash=hash123, esadmin=False),
        Usuario(nombre='augusto', passhash=hash123, esadmin=False)
    ))

    ######################
    ##### Pikas e Insumos
    ## CUIDADO QUE SI AGREGAS PIKA ASÍ SÍ O SÍ TENÉS QUE AGREGARLE STOCK SINO ERROR
    db.add_all((
        Pika(nombre='Baku'),
        Pika(nombre='Donn'),
        Pika(nombre='Koko'),
        Pika(nombre='Skup'),
        Pika(nombre='XL Baku'),
        Pika(nombre='XL Donn'),
        Pika(nombre='XL Koko'),
        Pika(nombre='XL Skup')
        #Insumo(nombre='ORing Pika'),
        #Insumo(nombre='ORing XL'),
        #Insumo(nombre='ORing Llav.'),
        #Insumo(nombre='Iman Pika'),
        #Insumo(nombre='Iman XL'),
        #Insumo(nombre='Iman Llav.'),
        #Insumo(nombre='PLA Rojo'),
        #Insumo(nombre='PLA Blanco'),
        #Insumo(nombre='PLA Negro')
    ))

    ######################
    ##### Pikas <> Insumos
    pikas = db.query(Pika)

    ## END
    db.commit()
    return
    #insus = db.query(Insumo)
    db.add_all((
        PikaInsumo(
            pika=pikas.filter(Pika.nombre == 'Baku').one(),
            insumo=insus.filter(Insumo.nombre == 'ORing Pika').one(),
            cantidad=1
        ),
        PikaInsumo(
            pika=pikas.filter(Pika.nombre == 'Baku').one(),
            insumo=insus.filter(Insumo.nombre == 'Iman Pika').one(),
            cantidad=2
        ),
        PikaInsumo(
            pika=pikas.filter(Pika.nombre == 'Donn').one(),
            insumo=insus.filter(Insumo.nombre == 'ORing Pika').one(),
            cantidad=1
        ),
        PikaInsumo(
            pika=pikas.filter(Pika.nombre == 'Donn').one(),
            insumo=insus.filter(Insumo.nombre == 'Iman Pika').one(),
            cantidad=2
        )
    ))

    ######################
    ##### Stocks
    for pika in pikas:
        db.add(StockPika(pika=pika, cantidad=10, fecha=datetime(2019, 5, 3)))
    for insu in insus:
        db.add(StockInsumo(insumo=insu, cantidad=20, fecha=datetime(2019, 5, 3)))

    ######################
    ##### Ventas
    db.add_all((
        VentaTipo(nombre='Mayorista'),
        VentaTipo(nombre='Tienda'),
        VentaTipo(nombre='Otros')
    ))

    ventips = db.query(VentaTipo)
    vents = [
        Venta(
            ventatipo=ventips.filter(VentaTipo.nombre == 'Mayorista').one(),
            fecha=datetime.now(),
            comentario='Niño Grow'
        ),
        Venta(
            ventatipo=ventips.filter(VentaTipo.nombre == 'Tienda').one(),
            fecha=datetime.now(),
            comentario='Promo 2, pedro'
        )
    ]
    db.add_all(vents)
    db.add_all((
        VentaPika(venta=vents[0], pika=pikas.filter(Pika.nombre == 'Baku').one(), cantidad=5),
        VentaPika(venta=vents[0], pika=pikas.filter(Pika.nombre == 'Donn').one(), cantidad=3),
        VentaPika(venta=vents[1], pika=pikas.filter(Pika.nombre == 'Koko').one(), cantidad=6),
        VentaPika(venta=vents[1], pika=pikas.filter(Pika.nombre == 'Skup').one(), cantidad=2)
    ))

    ######################
    ##### Fallas
    # Maquina, Gcode, Falla
    db.add_all((
        Maquina(nombre='MK2A'),
        Maquina(nombre='MK2B'),
        Maquina(nombre='MK3A'),
        Maquina(nombre='MK3B')
    ))
    db.add_all((
        Gcode(nombre='Piezas blancas x23', pika=pikas.filter(Pika.nombre == 'Baku').one()),
        Gcode(nombre='Piezas rojas x11', pika=pikas.filter(Pika.nombre == 'Donn').one()),
        Gcode(nombre='Piezas negras x54') #pika=None
    ))
    maqs = db.query(Maquina)
    gcods = db.query(Gcode)
    db.add_all((
        Falla(
            maquina=maqs.filter(Maquina.nombre == 'MK2A').one(),
            gcode=gcods.filter(Gcode.nombre == 'Piezas blancas x23').one(),
            descripcion='MinTemp', fecha=datetime(2019, 5, 3)),
        Falla(
            maquina=maqs.filter(Maquina.nombre == 'MK2B').one(),
            gcode=gcods.filter(Gcode.nombre == 'Piezas negras x54').one(),
            descripcion='MaxTemp', fecha=datetime(2019, 5, 3)),
        Falla(
            maquina=maqs.filter(Maquina.nombre == 'MK2A').one(),
            #gcode=None,
            descripcion='ExploTo', fecha=datetime(2019, 5, 3))
    ))

    ## END
    db.commit()

@click.command('init-db')
@with_appcontext
def recreate_db_command():
    recreate_db()
    click.echo('Initialized the database.')


def init_app(app):
    # function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # adds a new command that can be called with 'flask init-db' command line
    app.cli.add_command(recreate_db_command)

    from sqlalchemy.orm import sessionmaker, scoped_session
    from .models import Base
    engine = init_db_engine(app)
    Base.metadata.bind = engine
    session_factory = sessionmaker(bind=engine)
    app.DBSession = scoped_session(session_factory)
