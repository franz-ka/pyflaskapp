from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, event, Table
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

#######################
# https://stackoverflow.com/questions/8980735/how-can-i-verify-column-data-types-in-the-sqlalchemy-orm
def validate_int(value):
    if isinstance(value, str):
        value = int(value)
    else:
        assert isinstance(value, int)
    return value

def validate_string(value):
    assert isinstance(value, str)
    return value

def validate_datetime(value):
    assert isinstance(value, datetime.datetime)
    return value

validators = {
    Integer:validate_int,
    String:validate_string,
    DateTime:validate_datetime,
}

# this event is called whenever an attribute on a class is instrumented
@event.listens_for(Base, 'attribute_instrument')
def configure_listener(class_, key, inst):
    if not hasattr(inst.property, 'columns'):
        return
    # this event is called whenever a "set"
    # occurs on that instrumented attribute
    @event.listens_for(inst, "set", retval=True)
    def set_(instance, value, oldvalue, initiator):
        validator = validators.get(inst.property.columns[0].type.__class__)
        if validator:
            return validator(value)
        else:
            return value
##################################

# sqlalchemy Relationship Patterns - https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html
class Pieza(Base):
    __tablename__ = 'pieza'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), nullable=False)
    cantidad = Column(Integer)
    # Many-ImpresionPieza To One-Pieza Bidirectional
    impresionpieza = relationship("ImpresionPieza", back_populates="pieza")
    #gcodes = relationship("GCode", back_populates="pieza")
    def __repr__(self):
        return '<Pieza {} {}>'.format(self.id, self.nombre)

class Impresion(Base):
    __tablename__ = 'impresion'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime)
    # One-Impresion To Many-ImpresionPieza Bidirectional
    impresionpieza = relationship("ImpresionPieza", back_populates="impresion")
    def __repr__(self):
        return '<Impresion {} {}>'.format(self.pieza.nombre, self.fecha)

class ImpresionPieza(Base):
    __tablename__ = 'impresionpieza'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # One-Impresion To Many-ImpresionPieza Bidirectional
    impresion_id = Column(Integer, ForeignKey('impresion.id'))
    impresion = relationship("Impresion", back_populates="impresionpieza")
    # Many-ImpresionPieza To One-Pieza Bidirectional
    pieza_id = Column(Integer, ForeignKey('pieza.id'))
    pieza = relationship("Pieza", back_populates="impresionpieza")
    cantidad = Column(Integer)
    def __repr__(self):
        return '<ImpresionPieza impid={} piezid={} cant={}>'.format(self.impresion_id, self.pieza_id, self.cantidad)

class Articulo(Base):
    __tablename__ = 'articulo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), nullable=False)
    cantidad = Column(Integer)
    def __repr__(self):
        return '<Articulo {} {}>'.format(self.id, self.nombre)

'''assocModArt = Table('assocModArt', Base.metadata,
    Column('modelo_id', Integer, ForeignKey('modelo.id')),#left
    Column('articulo_id', Integer, ForeignKey('articulo.id'))#right
) 
assocModPie = Table('assocModPie', Base.metadata,
    Column('modelo_id', Integer, ForeignKey('modelo.id')),#left
    Column('pieza_id', Integer, ForeignKey('pieza.id'))#right
)'''
class ModeloPieza(Base):
    __tablename__ = 'modelopieza'
    modelo_id = Column(Integer, ForeignKey('modelo.id'), primary_key=True)
    pieza_id = Column(Integer, ForeignKey('pieza.id'), primary_key=True)
    cantidad = Column(Integer)
    pieza = relationship("Pieza")
    def __repr__(self):
        return '<ModeloPieza modid={} piezid={} cant={}>'.format(self.modelo_id, self.pieza_id, self.cantidad)
class ModeloArticulo(Base):
    __tablename__ = 'modeloarticulo'
    modelo_id = Column(Integer, ForeignKey('modelo.id'), primary_key=True)
    articulo_id = Column(Integer, ForeignKey('articulo.id'), primary_key=True)
    cantidad = Column(Integer)
    articulo = relationship("Articulo")
    def __repr__(self):
        return '<ModeloArticulo modid={} artid={} cant={}>'.format(self.modelo_id, self.articulo_id, self.cantidad)
class Modelo(Base):
    __tablename__ = 'modelo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), nullable=False)
    #piezas = relationship("Pieza", secondary=assocModPie)
    #articulos = relationship("Articulo", secondary=assocModArt)
    piezas = relationship("ModeloPieza")
    articulos = relationship("ModeloArticulo")
    def __repr__(self):
        return '<Modelo {} {}>'.format(self.id, self.nombre)


'''class GCode(Base):
    __tablename__ = 'gcode'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(64), nullable=False)
    # Many-GCode To One-Pieza Bidirectional
    pieza_id = Column(Integer, ForeignKey('pieza.id'))
    pieza = relationship("Pieza", back_populates="impresionpieza")
    cantidad = Column(Integer)
    def __repr__(self):
        return '<GCode {} {} {}>'.format(self.impresion.fecha, self.pieza.nombre, self.cantidad)


class ModeloPieza(Base):
    __tablename__ = 'modelopieza'
    # many_to_many_relationships https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_many_to_many_relationships.htm
    modelo_id = Column(Integer, ForeignKey('modelo.id'), primary_key = True)
    modelo = relationship(Modelo)
    pieza_id = Column(Integer, ForeignKey('pieza.id'), primary_key = True)
    pieza = relationship(Pieza)
    cantidad = Column(Integer)
    def __repr__(self):
        return '<ModeloPieza {} {} {}>'.format(self.modelo.nombre, self.pieza.nombre, self.cantidad)

'''


class Pika(Base):
    __tablename__ = 'pika'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), nullable=False)

    def __repr__(self): return '<Pika {}>'.format(self.id)


class Insumo(Base):
    __tablename__ = 'insumo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), nullable=False)

    def __repr__(self): return '<Insumo {}>'.format(self.id)


class PikaInsumo(Base):
    __tablename__ = 'pikainsumo'
    pika_id = Column(Integer, ForeignKey('pika.id'), primary_key=True)
    pika = relationship('Pika')
    insumo_id = Column(Integer, ForeignKey('insumo.id'), primary_key=True)
    insumo = relationship('Insumo')
    cantidad = Column(Integer, nullable=False)

    def __repr__(self): return '<PikaInsumo {}>'.format(self.pika_id)

class StockPika(Base):
    __tablename__ = 'stockpika'
    pika_id = Column(Integer, ForeignKey('pika.id'), primary_key=True)
    pika = relationship('Pika')
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime)

    def __repr__(self): return '<StockPika {}>'.format(self.id)


class StockInsumo(Base):
    __tablename__ = 'stockinsumo'
    insumo_id = Column(Integer, ForeignKey('insumo.id'), primary_key=True)
    insumo = relationship('Insumo')
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime)

    def __repr__(self): return '<StockInsumo {}>'.format(self.id)

class MovStockPika(Base):
    __tablename__ = 'movstockpika'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pika_id = Column(Integer, ForeignKey('pika.id'))
    pika = relationship('Pika')
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime)

    def __repr__(self): return '<MovStockPika {}>'.format(self.id)


class MovStockInsumo(Base):
    __tablename__ = 'movstockinsumo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    insumo_id = Column(Integer, ForeignKey('insumo.id'))
    insumo = relationship('Insumo')
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime)

    def __repr__(self): return '<MovStockInsumo {}>'.format(self.id)

class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(32), nullable=False)
    passhash = Column(String(64), nullable=False)
    esadmin = Column(Boolean, nullable=False)

    def __repr__(self): return '<Usuario {}>'.format(self.id)

class VentaTipo(Base):
    __tablename__ = 'ventatipo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), nullable=False)

    def __repr__(self): return '<VentaTipo {}>'.format(self.id)


class Venta(Base):
    __tablename__ = 'venta'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ventatipo_id = Column(Integer, ForeignKey('ventatipo.id'))
    ventatipo = relationship('VentaTipo')
    fecha = Column(DateTime)
    comentario = Column(String(128))
    ventapikas = relationship('VentaPika')

    def __repr__(self): return '<Venta {}>'.format(self.id)


class VentaPika(Base):
    __tablename__ = 'ventapika'
    id = Column(Integer, primary_key=True, autoincrement=True)
    venta_id = Column(Integer, ForeignKey('venta.id'))
    venta = relationship('Venta')
    pika_id = Column(Integer, ForeignKey('pika.id'))
    pika = relationship('Pika')
    cantidad = Column(Integer, nullable=False)

    def __repr__(self): return '<VentaPika {}>'.format(self.id)
