from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event, Column, Integer, String, DateTime, Boolean, ForeignKey
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

__ilegalchars = ['\'', '"', '\n', "<", "\\"]
def validate_string(value):
    assert isinstance(value, str)
    for c in __ilegalchars:
        assert c not in value
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

# sqlalchemy Relationship Patterns - https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html
# many_to_many_relationships https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_many_to_many_relationships.htm

class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(32), nullable=False)
    passhash = Column(String(64), nullable=False)
    esadmin = Column(Boolean, nullable=False)

    def __repr__(self): return '<Usuario {}>'.format(self.id)

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

    def __repr__(self): return '<StockPika {}>'.format(self.pika_id)

class StockInsumo(Base):
    __tablename__ = 'stockinsumo'
    insumo_id = Column(Integer, ForeignKey('insumo.id'), primary_key=True)
    insumo = relationship('Insumo')
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime)

    def __repr__(self): return '<StockInsumo {}>'.format(self.insumo_id)

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

class Maquina(Base):
    __tablename__ = 'maquina'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), nullable=False)

    def __repr__(self): return '<Maquina {}>'.format(self.id)

class Gcode(Base):
    __tablename__ = 'gcode'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pika_id = Column(Integer, ForeignKey('pika.id'))
    pika = relationship('Pika')
    nombre = Column(String(128), nullable=False)

    def __repr__(self): return '<Gcode {}>'.format(self.id)

class Falla(Base):
    __tablename__ = 'falla'
    id = Column(Integer, primary_key=True, autoincrement=True)
    maquina_id = Column(Integer, ForeignKey('maquina.id'))
    maquina = relationship('Maquina')
    gcode_id = Column(Integer, ForeignKey('gcode.id'))
    gcode = relationship('Gcode')
    descripcion = Column(String(128), nullable=False)
    fecha = Column(DateTime)

    def __repr__(self): return '<Falla {}>'.format(self.id)
