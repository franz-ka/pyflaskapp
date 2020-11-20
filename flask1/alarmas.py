from sqlalchemy import func
from flask import g
from flask1.models import Alarma, Insumo, StockInsumo, VentaPika, Venta, PikaInsumo
from datetime import datetime
import smtplib

_alarma_dias_intervalo = 1


def days_between(d1, d2):
    return abs((d2 - d1).days)

def _get_db_app_or_out():
    if g and g.db:
        return g.db
    else:
        from flask1.db import __dbconnstr
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from .models import Base
        engine = create_engine(__dbconnstr)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        return DBSession()

def check_alarma(insu):
    assert type(insu) == Insumo
    db = _get_db_app_or_out()

    alarma = db.query(Alarma).filter(Alarma.insumo == insu).first()

    if alarma:
        stock = db.query(StockInsumo).filter(StockInsumo.insumo == insu).first()

        q = db.query(func.sum(VentaPika.cantidad*PikaInsumo.cantidad).label('cant_insu_pedidos')) \
            .join(Venta) \
            .filter(Venta.fecha_pedido != None, Venta.fecha == None) \
            .join(PikaInsumo, VentaPika.pika_id == PikaInsumo.pika_id) \
            .filter(PikaInsumo.insumo_id == insu.id) \
            .group_by(PikaInsumo.insumo_id) \
            .all()

        if len(q):
            pedidos_cant = q[0].cant_insu_pedidos
        else:
            pedidos_cant = 0

        mando_mail = check_insumo_stock(alarma, stock, pedidos_cant)
        if mando_mail:
            print('check_alarma mail', insu)
            alarma.fecha_avisado = datetime.now()
            db.commit()


def check_alarmas():
    ################## TODO ERROR MAIL
    print('ALARMAS DESACTIVADAS')
    return
    ##################

    db = _get_db_app_or_out()

    alarmas_stocks = db.query(Alarma, StockInsumo).filter(StockInsumo.insumo_id == Alarma.insumo_id).all()

    for alarma, stock in alarmas_stocks:
        q = db.query(func.sum(VentaPika.cantidad*PikaInsumo.cantidad).label('cant_insu_pedidos')) \
            .join(Venta) \
            .filter(Venta.fecha_pedido != None, Venta.fecha == None) \
            .join(PikaInsumo, VentaPika.pika_id == PikaInsumo.pika_id) \
            .filter(PikaInsumo.insumo_id == stock.insumo_id) \
            .group_by(PikaInsumo.insumo_id) \
            .all()

        if len(q):
            pedidos_cant = q[0].cant_insu_pedidos
        else:
            pedidos_cant = 0

        mando_mail = check_insumo_stock(alarma, stock, pedidos_cant)
        if mando_mail:
            print('check_alarmas mail', stock.insumo)
            alarma.fecha_avisado = datetime.now()
            db.commit()


def check_insumo_stock(alarma, stock, pedidos_cant):
    if stock.cantidad - pedidos_cant <= alarma.cantidad and (not alarma.fecha_avisado or days_between(alarma.fecha_avisado, datetime.now()) >= _alarma_dias_intervalo):
        mandar_alarma(alarma.insumo.nombre, stock.cantidad, pedidos_cant, alarma.cantidad)
        return True
    return False


def mandar_alarma(nombre_insu, stock_insu, pedidos_cant, alarma_cant):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("stockcogonauts@gmail.com", "Markdijono1375$")
    message = (
            'Subject: Alarma stock bajo ({3}) de {0}\n'+
            'Hay {3} de stock para el insumo {0} ({1} stock real, {2} stock pedido).\n\n'+
            '(alarma configurada para stock igual o menor a {4})'
        ).format(nombre_insu, stock_insu, pedidos_cant, stock_insu - pedidos_cant, alarma_cant)
    s.sendmail("stockcogonauts@gmail.com", "cogonauts@gmail.com", message.encode('utf8'))
    s.quit()
