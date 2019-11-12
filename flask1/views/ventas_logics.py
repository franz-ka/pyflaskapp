from ._common import *

def get_ventatipos():
    db = get_db()   
    
    ventatipos = db.query(VentaTipo).order_by(VentaTipo.nombre).all()
    
    return ventatipos

def del_ventatipo(id): 
    db = get_db()   
    
    tipo = db.query(VentaTipo).get(id)
    ventas = db.query(Venta).filter(Venta.ventatipo==tipo)
    for v in ventas:
        db.query(VentaPika).filter(VentaPika.venta==v).delete()
    ventas.delete()
    db.query(VentaTipo).filter(VentaTipo.id==tipo.id).delete()

    db.commit()

def add_ventatipo(nombre): 
    db = get_db()   
    
    if db.query(VentaTipo).filter(VentaTipo.nombre==nombre).first():
        raise Exception('Ya existe un tipo de venta con ese nombre')
    tipo = VentaTipo(nombre=nombre)
    db.add(tipo)  

    db.commit()

def get_ventas(*args):    
    db = get_db()

    ventapikas = db.query(VentaPika).join(Venta).filter(Venta.fecha != None).order_by(Venta.fecha.desc(), Venta.id.desc())
    if len(args):
        filter_args = args[0]
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

        if filter_args.get('pika'):
            pikaid = int(filter_args['pika'])
            #ventas = ventas.join(VentaPika).filter(VentaPika.pika_id == pikaid)
            ventapikas = ventapikas.filter(VentaPika.pika_id == pikaid)

    ventapikas = ventapikas.all()
    
    return ventapikas

def get_ventas_format_select():  
    db = get_db()
    
    ventas = db.query(Venta).filter(Venta.fecha != None).order_by(Venta.fecha.desc()).all()
    ventasmodif = []
    for v in ventas:
        ventasmodif.append({
            'id': v.id,
            'fecha': v.fecha.strftime("%d/%m/%Y %H:%M"),
            'comentario': v.comentario
        })
        
    return ventasmodif

def del_venta(venta_id):    
    if not venta_id:
        raise Exception('Debe elegir una venta válida')
    
    db = get_db()

    venta = db.query(Venta).get(int(venta_id))
    dtnow = datetime.datetime.now()
    ventapikas = db.query(VentaPika).filter(VentaPika.venta == venta)

    for vp in ventapikas.all():
        #sumamos stock de pika
        pikacant = int(vp.cantidad)
        mov = MovStockPika(pika=vp.pika, cantidad=pikacant, fecha=dtnow)
        db.add(mov)

        stockpika = db.query(StockPika).get(vp.pika_id)
        stockpika.cantidad += pikacant
        stockpika.fecha = mov.fecha

    ventapikas.delete()
    db.query(Venta).filter(Venta.id == venta.id).delete()

    db.commit()

def get_pedidos():
    db = get_db()
    
    pedidos = db.query(VentaPika).join(Venta).filter(Venta.fecha_pedido != None).filter(Venta.fecha == None).order_by(Venta.fecha_pedido.asc())
    
    return pedidos

def get_pedidos_format_select():   
    db = get_db()

    pedidospikas = db.query(Venta).filter(Venta.fecha_pedido != None).filter(Venta.fecha == None).order_by(Venta.fecha_pedido.desc())
    pedidosmodif = []
    for v in pedidospikas:
        pedidosmodif.append({
            'id': v.id,
            'fecha': v.fecha_pedido.strftime("%d/%m/%Y %H:%M"),
            'comentario': v.comentario
        })
        
    return pedidospikas

def del_pedido(pedido_id):    
    if not pedido_id:
        raise Exception('Debe elegir un pedido válido')
    
    db = get_db()
    
    pedido = db.query(Venta).filter(Venta.id == int(pedido_id))
    ventapikas = db.query(VentaPika).filter(VentaPika.venta == pedido.one())
    ventapikas.delete()
    pedido.delete()
    
    db.commit()

def add_pedido(vendido, pikas, cants, tipo, comentario):
    warns = []     
       
    dtnow = datetime.datetime.now()
    
    db = get_db()
    
    vent = Venta(
        ventatipo=db.query(VentaTipo).filter(VentaTipo.id == tipo).one(),
        fecha_pedido=dtnow,
        comentario=comentario
    )
    
    if vendido:
        vent.fecha = dtnow
        tipoinsu_venta = db.query(InsumoTipo).filter(InsumoTipo.nombre=='Venta').one()
    
    db.add(vent)
    
    for i, pikaid in enumerate(pikas):
        if i<len(cants) and cants[i] and pikaid:
            pika = db.query(Pika).get(pikaid)
            pikacant = int(cants[i])
            stockpika = db.query(StockPika).get(pikaid)

            if stockpika.cantidad < pikacant:
                if vendido:
                    raise Exception('No hay suficiente stock del pika "{}" (hay {}, requiere {})'.format(pika.nombre, stockpika.cantidad, pikacant))
                else:
                    warns.append('Pika "{}" (hay {}, requiere {})'.format(pika.nombre, stockpika.cantidad, pikacant))

            #agregamos entrada de venta
            db.add(VentaPika(venta=vent, pika=pika, cantidad=pikacant))
            
            if vendido:
                pikainsus = db.query(PikaInsumo).join(Insumo).filter(PikaInsumo.pika==pika, Insumo.insumotipo==tipoinsu_venta)
                
                #restamos stock de insumos de venta
                for pikainsu in pikainsus:
                    stockinsu = db.query(StockInsumo).get(pikainsu.insumo_id)
                    if stockinsu.cantidad < pikainsu.cantidad*pikacant:
                        raise Exception('No hay suficiente stock de "{}" para el pika "{}" (hay {}, requiere {})'.format(pikainsu.insumo.nombre, pika.nombre, stockinsu.cantidad, pikainsu.cantidad*pikacant))

                    movinsu = MovStockInsumo(insumo=pikainsu.insumo, cantidad=pikainsu.cantidad, fecha=dtnow)
                    db.add(movinsu)
                    stockinsu.cantidad -= movinsu.cantidad*pikacant
                    stockinsu.fecha = movinsu.fecha
                    
                #restamos stock de pika
                mov = MovStockPika(pika=pika, cantidad=-int(cants[i]), fecha=dtnow)
                db.add(mov)
                stockpika.cantidad -= pikacant
                stockpika.fecha = mov.fecha

    db.commit()
    
    return warns

def vender_pedido(venta_id):    
    errors = []
    
    db = get_db()

    dtnow = datetime.datetime.now()
    
    venta = db.query(Venta).get(int(venta_id))
    venta.fecha=dtnow
    
    tipoinsu_venta = db.query(InsumoTipo).filter(InsumoTipo.nombre=='Venta').one()
    
    ventapikas = db.query(VentaPika).filter(VentaPika.venta_id==venta.id).all()
    for vpi in ventapikas:
        stockpika = db.query(StockPika).get(vpi.pika_id)

        if stockpika.cantidad < vpi.cantidad:
            errors.append('Requiere {} "{}", pero hay {}'.format(vpi.cantidad, vpi.pika.nombre, stockpika.cantidad))
        
        pikainsus = db.query(PikaInsumo).join(Insumo).filter(PikaInsumo.pika==vpi.pika, Insumo.insumotipo==tipoinsu_venta)
        
        #restamos stock de insumos de venta
        for pikainsu in pikainsus:
            stockinsu = db.query(StockInsumo).get(pikainsu.insumo_id)
            if stockinsu.cantidad < pikainsu.cantidad*vpi.cantidad:
                raise Exception('No hay suficiente stock de "{}" para el pika "{}" (hay {}, requiere {})'.format(pikainsu.insumo.nombre, vpi.pika.nombre, stockinsu.cantidad, pikainsu.cantidad*vpi.cantidad))
    
            movinsu = MovStockInsumo(insumo=pikainsu.insumo, cantidad=pikainsu.cantidad, fecha=dtnow)
            db.add(movinsu)
            stockinsu.cantidad -= movinsu.cantidad*vpi.cantidad
            stockinsu.fecha = movinsu.fecha
            
        #restamos stock de pika
        mov = MovStockPika(pika=vpi.pika, cantidad=-vpi.cantidad, fecha=dtnow)
        db.add(mov)
        stockpika.cantidad -= vpi.cantidad
        stockpika.fecha = mov.fecha
    
    if errors:
        # No commiteamos
        raise Exception('No hay suficiente stock:\n' + '\n'.join(errors))
    
    db.commit()
