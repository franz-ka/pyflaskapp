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
        pikas = get_pikas(),
        filtrado = hasquery(request.args)
    ))
    
@bp_ventas.route("/exportar/ventas.csv", methods=['GET'])
@login_required
def exportar_ventas():
    ventas = get_ventas(request.args)

    ex = CsvExporter('ventas.csv')
    ex.writeHeaders('Id,Fecha,Fecha pedido,Tipo,Comentario,Pika,Cantidad')
    last_venta_id = 0
    for vp in ventas:
        if last_venta_id != vp.venta_id:
            v = vp.venta
            vals = [
                v.id,
                v.fecha,
                v.fecha_pedido or '',
                v.ventatipo.nombre,
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
            comentario = request.form['comentario'] if 'comentario' in request.form else None
            vendido = 'vendido' in request.form
            
            warns = add_pedido(vendido, pikas, cants, tipo, comentario)
    
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

    
