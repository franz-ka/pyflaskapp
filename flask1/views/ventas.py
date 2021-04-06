# coding=utf-8
from ._common import *

bp_ventas = Blueprint('ventas', __name__, url_prefix='/ventas')

'''menu_listadoventas
exportar_ventas
menu_agregelimtipoventa
menu_eliminarventa
menu_ingresarpedido
vender_pedido
'''
@bp_ventas.route("/listadoventas", methods=['GET'])
@login_required
def menu_listadoventas():

    return make_response(render_template(
        'menu/ventas/listadoventas.html',
        ventapikas = get_ventas(request.args),
        ventatipos = get_ventatipos(),
        clientes = get_clientes(),
        pikas = get_pikas(),
        filtrado = hasquery(request.args)
    ))

@bp_ventas.route("/exportar/ventas.csv", methods=['GET'])
@login_required
def exportar_ventas():
    ventas = get_ventas(request.args)

    ex = CsvExporter('ventas.csv')
    ex.writeHeaders('Id,Fecha,Fecha pedido,Tipo,Cliente,Comentario,Pika,Cantidad')
    last_venta_id = 0
    for vp in ventas:
        if last_venta_id != vp.venta_id:
            v = vp.venta
            vals = [
                v.id,
                v.fecha,
                v.fecha_pedido or '',
                v.ventatipo.nombre,
                v.cliente.nombre if v.cliente else '',
                v.comentario,
                '',
                ''
            ]
        vals[5] = vp.pika.nombre
        vals[6] = vp.cantidad
        ex.writeVals(vals)

    return ex.send()

@bp_ventas.route("/agregelimtipoventa", methods = ['GET', 'POST'])
@login_required
def menu_agregelimtipoventa():
    if request.method == "GET":

        return make_response(render_template(
            'menu/ventas/agregelimtipoventa.html',
            ventatipos = get_ventatipos()
        ))

    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            if request.form['operation'] == 'add':

                checkparams(request.form, ('nombretipoven',))
                add_ventatipo(request.form['nombretipoven'])

            elif request.form['operation'] == 'delete':

                checkparams(request.form, ('tipo',))
                del_ventatipo(int(request.form['tipo']))

            else:
                raise Exception('Operación inválida')
        except Exception as e:
            return str(e), 400

        return ''

@bp_ventas.route("/eliminarventa", methods=['GET', 'POST'])
@login_required
def menu_eliminarventa():
    if request.method == "GET":

        return make_response(render_template(
            'menu/ventas/eliminarventa.html',
            ventas = get_ventas_format_select(),
            pedidos = get_pedidos_format_select()
        ))

    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            operation = request.form['operation']

            if operation == 'delete_pedido':
                del_pedido(request.form.get('pedido'))
            elif operation == 'delete_venta':
                del_venta(request.form.get('venta'))
            else:
                raise Exception('Operación inválida')
        except Exception as e:
            return str(e), 400

        return ''

@bp_ventas.route("/ingresarpedido", methods = ['GET', 'POST'])
@login_required
def menu_ingresarpedido():
    if request.method == "GET":
        urgentes_all = get_urgentes()
        urgentes = {}
        for u in urgentes_all:
            urgentes[u.venta_id] = True

        return make_response(render_template(
            'menu/ventas/ingresarpedido.html',
            ventatipos = get_ventatipos(),
            clientes = get_clientes(),
            pikas = get_pikas(),
            ventapikas = get_pedidos(),
            urgentes = urgentes
        ))

    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('tipo', 'pika', 'cantidad'))

            pikas = request.form.getlist('pika')
            cants = request.form.getlist('cantidad')
            tipo = request.form['tipo']
            cliente = request.form['cliente']
            comentario = request.form['comentario'] if 'comentario' in request.form else None
            vendido = 'vendido' in request.form

            warns = add_pedido(vendido, pikas, cants, tipo, cliente, comentario)

            if warns:
                return 'La operación se realizó pero algunos pikas no van a tener stock para la venta:<br>- ' + '<br>- '.join(warns)
        except Exception as e:
            return str(e), 400

        return ''

@bp_ventas.route("/vender_pedido", methods = ['POST'])
@login_required
def menu_vender_pedido():
    print('post form:', request.form)

    try:
        checkparams(request.form, ('venta_id',))
        vender_pedido(request.form['venta_id'])
    except Exception as e:
        return str(e), 400

    return ''

@bp_ventas.route("/pedido_urgente", methods = ['POST'])
@login_required
def menu_pedido_urgente():
    print('post form:', request.form)

    try:
        checkparams(request.form, ('venta_id',))
        tog_urgente(request.form['venta_id'])
    except Exception as e:
        return str(e), 400

    return ''


@bp_ventas.route("/clientes", methods = ['GET', 'POST'])
@login_required
def menu_clientes():
    if request.method == "GET":
        db = get_db()
        clientes = db.query(Cliente).all()

        r = make_response(render_template(
            'menu/ventas/clientes.html',
            clientes=clientes
        ))
        return r
    else: #request.method == "POST":
        print('post form:',request.form)

        try:
            checkparams(request.form, ('operation',))

            operation = request.form['operation']

            if operation == 'agregar':
                checkparams(request.form, ('nombre',))
            elif operation == 'editar':
                checkparams(request.form, ('id','nombre'))
            elif operation == 'eliminar':
                checkparams(request.form, ('id',))
            else:
                return str('Operación inválida'), 400
        except Exception as e: return str(e), 400

        db = get_db()

        if operation == 'agregar':
            nombre = request.form['nombre'].strip()
            contacto = request.form['contacto'].strip()
            if db.query(Cliente).filter(Cliente.nombre==nombre).first():
                return 'Ya existe una máquina con ese nombre', 400
            cli = Cliente(nombre=nombre)
            if contacto:
                cli.contacto = contacto
            db.add(cli)
        elif operation == 'editar':
            id = int(request.form['id'].strip())
            nombre = request.form['nombre'].strip()
            contacto = request.form['contacto'].strip()
            cli = db.query(Cliente).get(id)
            cli.nombre = nombre
            cli.contacto = contacto
        elif operation == 'eliminar':
            id = int(request.form['id'].strip())
            db.query(Cliente).filter(Cliente.id==id).delete()

        db.commit()

        return ''
