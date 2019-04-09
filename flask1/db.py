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
    from .models import Base, Pieza, Impresion, ImpresionPieza
    engine = init_db_engine(current_app)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    db = DBSession()
    db.add_all((
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
    '''id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), nullable=False)
    articulos = relationship("Articulo", secondary=assocModArt)
    piezas = relationship("Pieza", secondary=assocModPie)'''
    db.add(Modelo(nombre='mod1'))

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
