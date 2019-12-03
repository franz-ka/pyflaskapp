from ._common import *

def get_pikas():
    db = get_db()   
    
    pikas = db.query(Pika).order_by(Pika.nombre).all()
    
    return pikas

def inc_stock_pika(pika, stockpika, cantidad, date, causa):
    if type(cantidad) != int: cantidad = int(cantidad)
    
    return set_stock_pika(pika, stockpika, stockpika.cantidad + cantidad, date, causa)
    
def set_stock_pika(pika, stockpika, cantidad, date, causa):
    if type(cantidad) != int: cantidad = int(cantidad)
        
    db = get_db()
    
    stockpika.cantidad = cantidad
    stockpika.fecha = date
    
    mov = MovStockPika(
        pika = pika, 
        cantidad = stockpika.cantidad, 
        fecha = stockpika.fecha,
        causa = causa)
    db.add(mov)

def inc_prestock_pika(pika, prestockpika, cantidad, date, causa):
    if type(cantidad) != int: cantidad = int(cantidad)
    
    return set_prestock_pika(pika, prestockpika, prestockpika.cantidad + cantidad, date, causa)
    
def set_prestock_pika(pika, prestockpika, cantidad, date, causa):
    if type(cantidad) != int: cantidad = int(cantidad)
        
    db = get_db()
    
    prestockpika.cantidad = cantidad
    prestockpika.fecha = date
    
    mov = MovPrestockPika(
        pika = pika, 
        cantidad = prestockpika.cantidad, 
        fecha = prestockpika.fecha,
        causa = causa)
    db.add(mov)

'''def add_ventatipo(nombre): 
    db = get_db()   
    
    if db.query(VentaTipo).filter(VentaTipo.nombre==nombre).first():
        raise Exception('Ya existe un tipo de venta con ese nombre')
    tipo = VentaTipo(nombre=nombre)
    db.add(tipo)  

def del_ventatipo(id): 
    db = get_db()   
    
    tipo = db.query(VentaTipo).get(id)
    ventas = db.query(Venta).filter(Venta.ventatipo==tipo)
    for v in ventas:
        db.query(VentaPika).filter(VentaPika.venta==v).delete()
    ventas.delete()
    db.query(VentaTipo).filter(VentaTipo.id==tipo.id).delete()

def get_ventas(filter_args):    
    db = get_db()

    ventapikas = db.query(VentaPika).join(Venta).filter(Venta.fecha != None).order_by(Venta.fecha.desc(), Venta.id.desc())
    if len(filter_args):
        query = []
        for arg in filter_args:
            k, v = arg, filter_args[arg]
            if v:
                if k=='tipo': query.append(Venta.ventatipo_id == v)
                elif k=='comentario': query.append(Venta.comentario.ilike("%{}%".format(v)))
                elif k=='fechadesde': query.append(Venta.fecha >= datetime.datetime.strptime(v,'%d/%m/%Y'))
                elif k=='fechahasta': query.append(Venta.fecha <= datetime.datetime.strptime(v,'%d/%m/%Y') + datetime.timedelta(days=1))
        if query:
            from functools import reduce
            ventapikas = ventapikas.filter(reduce(lambda x, y: x&y, query))

        if filter_args['pika']:
            pikaid = int(filter_args['pika'])
            #ventas = ventas.join(VentaPika).filter(VentaPika.pika_id == pikaid)
            ventapikas = ventapikas.filter(VentaPika.pika_id == pikaid)

    ventapikas = ventapikas.all()
    
    return ventapikas'''
