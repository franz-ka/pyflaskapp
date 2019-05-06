import click
from flask import current_app, g
from flask.cli import with_appcontext
from datetime import datetime

def init_db_engine(app):
    from sqlalchemy import create_engine
    return create_engine('sqlite:///' + app.config['DATABASE'], echo=True);


# Define and Access the Database - http://flask.pocoo.org/docs/1.0/tutorial/database/
def get_db():
    # g is a special object that is unique for each request.
    # It is used to store data that might be accessed by multiple functions during the request
    if 'db' not in g:
        g.db = current_app.DBSession
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def recreate_db():
    from sqlalchemy.orm import sessionmaker, scoped_session
    from .models import Base, Pieza, Impresion, ImpresionPieza, Articulo, Modelo, ModeloPieza, ModeloArticulo
    from .models import Pika, Insumo, PikaInsumo, StockPika, StockInsumo, MovStockPika, MovStockInsumo, Usuario, VentaTipo, Venta, VentaPika
    engine = init_db_engine(current_app)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    db = DBSession()
    '''db.add_all((
        Pieza(nombre='ojo baku', cantidad=10),
        Pieza(nombre='base baku', cantidad=20),
        Pieza(nombre='tapa baku', cantidad=20),
        Pieza(nombre='ojo coco', cantidad=20),
        Impresion(fecha=datetime(2019, 4, 1)),
        Impresion(fecha=datetime(2019, 4, 2)),
        Impresion(fecha=datetime(2019, 4, 3))
    ))
    piezs = db.query(Pieza)
    imps = db.query(Impresion)
    db.add_all((
        ImpresionPieza(
            impresion_id=imps.filter(Impresion.fecha == datetime(2019, 4, 1)).one().id,
            pieza_id=piezs.filter(Pieza.nombre == 'ojo baku').one().id,
            cantidad=50
        ),
        ImpresionPieza(
            impresion_id=imps.filter(Impresion.fecha == datetime(2019, 4, 2)).one().id,
            pieza_id=piezs.filter(Pieza.nombre == 'base baku').one().id,
            cantidad=2
        ),
        ImpresionPieza(
            impresion_id=imps.filter(Impresion.fecha == datetime(2019, 4, 2)).one().id,
            pieza_id=piezs.filter(Pieza.nombre == 'tapa baku').one().id,
            cantidad=2
        ),
        ImpresionPieza(
            impresion_id=imps.filter(Impresion.fecha == datetime(2019, 4, 3)).one().id,
            pieza_id=piezs.filter(Pieza.nombre == 'ojo baku').one().id,
            cantidad=20
        ),
        ImpresionPieza(
            impresion_id=imps.filter(Impresion.fecha == datetime(2019, 4, 3)).one().id,
            pieza_id=piezs.filter(Pieza.nombre == 'ojo coco').one().id,
            cantidad=30
        )
    ))
    db.commit()

    db.add_all((
        Articulo(nombre='iman grande', cantidad=10),
        Articulo(nombre='iman chico', cantidad=20),
        Articulo(nombre='gomita 3x2', cantidad=30)
    ))
    db.commit()
    arts = db.query(Articulo)
    modbak = Modelo(nombre='baku')
    modbak.piezas.append(ModeloPieza(pieza=piezs.filter(Pieza.nombre == 'base baku').one(), cantidad='1'))
    modbak.piezas.append(ModeloPieza(pieza=piezs.filter(Pieza.nombre == 'tapa baku').one(), cantidad='1'))
    modbak.piezas.append(ModeloPieza(pieza=piezs.filter(Pieza.nombre == 'ojo baku').one(), cantidad='2'))
    modbak.articulos.append(ModeloArticulo(articulo=arts.filter(Articulo.nombre == 'iman grande').one(), cantidad='1'))
    modbak.articulos.append(ModeloArticulo(articulo=arts.filter(Articulo.nombre == 'iman chico').one(), cantidad='2'))
    modbak.articulos.append(ModeloArticulo(articulo=arts.filter(Articulo.nombre == 'gomita 3x2').one(), cantidad='1'))
    db.add(modbak)
    db.commit()'''


    db.add_all((
        Pika(nombre='Baku'),
        Pika(nombre='Donn'),
        Pika(nombre='Koko'),
        Pika(nombre='Skup'),
        Pika(nombre='XL Baku'),
        Pika(nombre='XL Donn'),
        Pika(nombre='XL Koko'),
        Pika(nombre='XL Skup'),
        Insumo(nombre='ORing Pika'),
        Insumo(nombre='ORing XL'),
        Insumo(nombre='ORing Llav.'),
        Insumo(nombre='Iman Pika'),
        Insumo(nombre='Iman XL'),
        Insumo(nombre='Iman Llav.'),
        Insumo(nombre='PLA Rojo'),
        Insumo(nombre='PLA Blanco'),
        Insumo(nombre='PLA Negro')
    ))
    db.commit()
    pikas = db.query(Pika)
    insus = db.query(Insumo)
    db.add_all((
        PikaInsumo(
            pika_id=pikas.filter(Pika.nombre == 'Baku').one().id,
            insumo_id=insus.filter(Insumo.nombre == 'ORing Pika').one().id,
            cantidad=1
        ),
        PikaInsumo(
            pika_id=pikas.filter(Pika.nombre == 'Baku').one().id,
            insumo_id=insus.filter(Insumo.nombre == 'Iman Pika').one().id,
            cantidad=2
        ),
        PikaInsumo(
            pika_id=pikas.filter(Pika.nombre == 'Donn').one().id,
            insumo_id=insus.filter(Insumo.nombre == 'ORing Pika').one().id,
            cantidad=1
        ),
        PikaInsumo(
            pika_id=pikas.filter(Pika.nombre == 'Donn').one().id,
            insumo_id=insus.filter(Insumo.nombre == 'Iman Pika').one().id,
            cantidad=2
        )
    ))
    db.commit()
    for pika in pikas:
        db.add(StockPika(pika=pika, cantidad=10, fecha=datetime(2019, 5, 3)))
    for insu in insus:
        db.add(StockInsumo(insumo=insu, cantidad=20, fecha=datetime(2019, 5, 3)))
    db.commit()
    import hashlib
    hash123 = hashlib.sha256(b"123").hexdigest()
    db.add_all((
        Usuario(nombre='master', passhash=hash123, esadmin=True),
        Usuario(nombre='usu', passhash=hash123, esadmin=False)
    ))
    db.commit()

    #VentaTipo, Venta, VentaPika
    db.add_all((
        VentaTipo(nombre='Mayorista'),
        VentaTipo(nombre='Tienda'),
        VentaTipo(nombre='Otros')
    ))
    db.commit()
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
