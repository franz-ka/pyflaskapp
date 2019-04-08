from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

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
    fecha = Column(String(64))
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


class Modelo(Base):
    __tablename__ = 'modelo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), nullable=False)
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