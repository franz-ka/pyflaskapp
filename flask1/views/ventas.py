# coding=utf-8
from ._common import *

bp_ventas = Blueprint('ventas', __name__, url_prefix='/ventas')

@bp_ventas.route("/listadoventas", methods=['GET', 'POST'])
@login_required
def menu_listadoventas():
    if request.method == "GET":
        db = get_db()

        ventapikas = db.query(VentaPika).join(Venta).filter(Venta.fecha != None).order_by(Venta.fecha.desc(), Venta.id.desc())
        filtrado = False
        if len(request.args):
            query = []
            for arg in request.args:
                k, v = arg, request.args[arg]
                if v:
                    if k=='tipo': query.append(Venta.ventatipo_id == v)
                    elif k=='comentario': query.append(Venta.comentario.ilike("%{}%".format(v)))
                    elif k=='fechadesde': query.append(Venta.fecha >= datetime.datetime.strptime(v,'%d/%m/%Y'))
                    elif k=='fechahasta': query.append(Venta.fecha <= datetime.datetime.strptime(v,'%d/%m/%Y') + datetime.timedelta(days=1))
            if query:
                from functools import reduce
                ventapikas = ventapikas.filter(reduce(lambda x, y: x&y, query))
                filtrado = True

            if request.args['pika']:
                pikaid = int(request.args['pika'])
                #ventas = ventas.join(VentaPika).filter(VentaPika.pika_id == pikaid)
                ventapikas = ventapikas.filter(VentaPika.pika_id == pikaid)
                filtrado = True

        ventapikas = ventapikas.all()
        ventatipos = db.query(VentaTipo).order_by(VentaTipo.nombre).all()
        pikas = db.query(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/ventas/listadoventas.html',
            ventapikas=ventapikas,
            ventatipos=ventatipos,
            pikas=pikas,
            filtrado=filtrado
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        from flask import send_file
        return send_file('/home/franzisca/PycharmProjects/pyflaskapp/flask1/models.py', attachment_filename='db.py', as_attachment=True)

@bp_ventas.route("/exportar/ventas.csv", methods=['GET'])
@login_required
def exportar_ventas():
    db = get_db()

    if not len(request.args):
        ventas = db.query(Venta)
        filtrado = False
    else:
        query = []
        for arg in request.args:
            k, v = arg, request.args[arg]
            if v:
                if k=='tipo': query.append(Venta.ventatipo_id == v)
                elif k=='comentario': query.append(Venta.comentario.ilike("%{}%".format(v)))
                elif k=='fechadesde': query.append(Venta.fecha >= datetime.datetime.strptime(v,'%d/%m/%Y'))
                elif k=='fechahasta': query.append(Venta.fecha <= datetime.datetime.strptime(v,'%d/%m/%Y') + datetime.timedelta(days=1))
        if query:
            from functools import reduce
            ventas = db.query(Venta).filter(reduce(lambda x, y: x&y, query))
            filtrado = True
        else:
            ventas = db.query(Venta)
            filtrado = False
        if request.args['pika']:
            pikaid = int(request.args['pika'])
            ventas = ventas.join(VentaPika).filter(VentaPika.pika_id == pikaid)
            filtrado = True
    ventas = ventas.order_by(Venta.fecha.desc()).all()

    ex = CsvExporter('ventas.csv')
    ex.writeHeaders('Id,Fecha,Tipo,Comentario,Pika,Cantidad')
    for v in ventas:
        vals = [v.id, v.fecha, v.ventatipo.nombre, v.comentario, '', '']
        if len(v.ventapikas):
            for vpi in v.ventapikas:
                vals[4] = vpi.pika.nombre
                vals[5] = vpi.cantidad
                ex.writeVals(vals)
        else:
            ex.writeVals(vals)
    return ex.send()

@bp_ventas.route("/agregelimtipoventa", methods = ['GET', 'POST'])
@login_required
def menu_agregelimtipoventa():
    if request.method == "GET":
        db = get_db()
        ventatipos = db.query(VentaTipo).order_by(VentaTipo.nombre).all()

        r = make_response(render_template(
            'menu/ventas/agregelimtipoventa.html',
            ventatipos=ventatipos
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombretipoven',))
            except Exception as e:
                return str(e), 400
        elif request.form['operation'] == 'delete':
            try:
                checkparams(request.form, ('tipo',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400

        db = get_db()

        if request.form['operation'] == 'add':
            if db.query(VentaTipo).filter(VentaTipo.nombre==request.form['nombretipoven']).first():
                return 'Ya existe un tipo de venta con ese nombre', 400
            tipo = VentaTipo(nombre=request.form['nombretipoven'])
            db.add(tipo)
        elif request.form['operation'] == 'delete':
            tipo = db.query(VentaTipo).get(int(request.form['tipo']))
            ventas = db.query(Venta).filter(Venta.ventatipo==tipo)
            for v in ventas:
                db.query(VentaPika).filter(VentaPika.venta==v).delete()
            ventas.delete()
            db.query(VentaTipo).filter(VentaTipo.id==tipo.id).delete()

        db.commit()

        return ''

@bp_ventas.route("/eliminarventa", methods=['GET', 'POST'])
@login_required
def menu_eliminarventa():
    if request.method == "GET":
        db = get_db()
        ventas = db.query(Venta).order_by(Venta.fecha.desc()).all()
        ventasmodif = []
        for v in ventas:
            ventasmodif.append({
                'id': v.id,
                'fecha': v.fecha.strftime("%d/%m/%Y %H:%M"),
                'comentario': v.comentario
            })

        r = make_response(render_template(
            'menu/ventas/eliminarventa.html',
            ventas=ventasmodif
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('venta',))
        except Exception as e:
            return str(e), 400

        db = get_db()

        venta = db.query(Venta).get(int(request.form['venta']))
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

        return ''

@bp_ventas.route("/ingresarpedido", methods = ['GET', 'POST'])
@login_required
def menu_ingresarpedido():
    if request.method == "GET":
        db = get_db()
        ventatipos = db.query(VentaTipo).order_by(VentaTipo.nombre).all()
        pikas = db.query(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/ventas/ingresarpedido.html',
            ventatipos=ventatipos,
            pikas=pikas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('tipo', 'pika', 'cantidad'))
        except Exception as e:
            return str(e), 400
        
        warns = []

        db = get_db()
        pikas = request.form.getlist('pika')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        vent = Venta(
            ventatipo=db.query(VentaTipo).filter(VentaTipo.id == request.form['tipo']).one(),
            fecha_pedido=dtnow,
            comentario=request.form['comentario'] if 'comentario' in request.form else None
        )
        db.add(vent)
        for i, pikaid in enumerate(pikas):
            if i<len(cants) and cants[i] and pikaid:
                pika = db.query(Pika).get(pikaid)
                pikacant = int(cants[i])
                stockpika = db.query(StockPika).get(pikaid)

                if stockpika.cantidad < pikacant:
                    warns.append('Pika "{}" (hay {}, requiere {})'.format(pika.nombre, stockpika.cantidad, pikacant))

                #agregamos entrada de venta
                db.add(VentaPika(venta=vent, pika=pika, cantidad=pikacant))

        #db.commit()

        if warns:
            return 'La operación se realizó pero algunos pikas no van a tener stock para la venta:<br>- ' + '<br>- '.join(warns)
        else:
            return ''


