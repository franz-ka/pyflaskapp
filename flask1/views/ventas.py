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
        texto_filtrado = 'filtro' in request.args and request.args['filtro']
        mas_datos = 'mas_datos' in request.args and request.args['mas_datos'] == 'si'
        ordenar_por = 'ordenar_por' in request.args and request.args['ordenar_por']

        db = get_db()

        pikas_cogos = db.query(Pika).filter(Pika.nombre.ilike('cogo %')).all()
        pikas_cogos_ids = [pika.id for pika in pikas_cogos]

        if not texto_filtrado:
            clientes = db.query(Cliente).order_by(Cliente.nombre).all()
        else:
            clientes = db.query(Cliente).order_by(Cliente.nombre).filter(or_(
                Cliente.nombre.ilike("%{}%".format(texto_filtrado)),
                Cliente.nombre_de_contacto.ilike("%{}%".format(texto_filtrado)),
            )).all()

        if mas_datos:
            for cli in clientes:
                cli.ventas_reales_totales = 0
                cli.ultima_venta_real = None
                ventas_cantidad_cogos = 0
                primera_fecha_venta_cogo = None
                ultima_fecha_venta_cogo = None

                # por cada venta real (no pedido) del cliente revisamos los pikas
                # vendidos y si hay versiones "cogo" los contamos
                for ven in cli.ventas:
                    if not ven.fecha is None:
                        cli.ventas_reales_totales += 1
                        cli.ultima_venta_real = ven
                        # chequear si hay pikas "cogo" en la venta
                        for vp in ven.ventapikas:
                            if vp.pika_id in pikas_cogos_ids:
                                if not primera_fecha_venta_cogo:
                                    primera_fecha_venta_cogo = ven.fecha
                                ventas_cantidad_cogos += vp.cantidad
                                ultima_fecha_venta_cogo = ven.fecha

                if ventas_cantidad_cogos and primera_fecha_venta_cogo != ultima_fecha_venta_cogo:
                    date_diff = ultima_fecha_venta_cogo - primera_fecha_venta_cogo
                    days_diff = date_diff.days
                    if days_diff <= 30:
                        cli.ventas_mensuales = ventas_cantidad_cogos
                    else:
                        cli.ventas_mensuales = (ventas_cantidad_cogos / days_diff) * 30
                else:
                    cli.ventas_mensuales = None

            if ordenar_por:
                print(f'Ordenando por: {ordenar_por}')
                # Key Functions - https://docs.python.org/3/howto/sorting.html#key-functions
                if ordenar_por == 'ventas_totales':
                    clientes.sort(key=lambda cli: cli.ventas_reales_totales or 0, reverse=True)
                elif ordenar_por == 'ventas_mensuales':
                    clientes.sort(key=lambda cli: cli.ventas_mensuales or 0, reverse=True)
                elif ordenar_por == 'ultima_venta':
                    fecha_min = datetime.datetime(1900,1,1)
                    clientes.sort(key=lambda cli: cli.ultima_venta_real.fecha if cli.ultima_venta_real else fecha_min, reverse=True)

        tipoclientes = db.query(TipoCliente).all()
        tipolocales = db.query(TipoLocal).all()
        ubicacionesosm = db.query(UbicacionOSM).all()

        r = make_response(render_template(
            'menu/ventas/clientes.html',
            clientes=clientes,
            tipoclientes=tipoclientes,
            tipolocales=tipolocales,
            ubicacionesosm=ubicacionesosm,
            filtrado=texto_filtrado and True or False,
            mas_datos=mas_datos
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


        if operation == 'eliminar':
            id = int(request.form['id'].strip())
            cli_query = db.query(Cliente).filter(Cliente.id==id)
            cli = cli_query.first()

            if cli.ubicacion_osm:
                db.query(UbicacionOSM).filter(UbicacionOSM.id==cli.ubicacion_osm_id).delete()

            cli_query.delete()
        elif operation == 'agregar' or operation == 'editar':
            nombre = request.form['nombre'].strip()
            nombre_de_contacto = request.form.get('nombre_de_contacto', '').strip()
            telefono = request.form.get('telefono', '').strip()
            mail = request.form.get('mail', '').strip()
            tipo_cliente_id = request.form.get('tipo_cliente')
            tipo_local_id = request.form.get('tipo_local')
            ubicacion_osm_data = request.form.get('ubicacion_osm_data')
            ubicacion = request.form.get('ubicacion', '').strip()

            if operation == 'agregar':
                if db.query(Cliente).filter(Cliente.nombre==nombre).first():
                    return 'Ya existe un cliente con ese nombre', 400
                cli = Cliente()
                db.add(cli)
            elif operation == 'editar':
                id = int(request.form['id'].strip())
                cli = db.query(Cliente).get(id)

            cli.nombre = nombre
            if nombre_de_contacto: cli.nombre_de_contacto = nombre_de_contacto
            if telefono: cli.telefono = telefono
            if mail: cli.mail = mail

            if tipo_cliente_id:
                cli.tipo_cliente = db.query(TipoCliente).get(tipo_cliente_id)
            if tipo_local_id:
                cli.tipo_local = db.query(TipoLocal).get(tipo_local_id)

            if ubicacion_osm_data:
                osm_data = json.loads(ubicacion_osm_data)

                # el campo _id solo viene cuando se edita un cliente y no se
                # toca el campo de ubicación osm (nunca se invalida)
                if '_id' not in osm_data:
                    ubicacion_osm = UbicacionOSM(
                        lat = osm_data["lat"],
                        lon = osm_data["lon"],
                        display_name = osm_data["display_name"],
                        road = osm_data["address"].get("road"),
                        house_number = osm_data["address"].get("house_number"),
                        postcode = osm_data["address"].get("postcode"),
                        # datos de tipo state
                        state = osm_data["address"].get("state"),
                        state_district = osm_data["address"].get("state_district"),
                        town = osm_data["address"].get("town"),
                        # datos de tipo city
                        city = osm_data["address"].get("city"),
                        city_district = osm_data["address"].get("city_district"),
                        suburb = osm_data["address"].get("suburb"),
                    )
                    # si había una ubicación previamente cargada borrarla
                    if cli.ubicacion_osm:
                        db.query(UbicacionOSM).filter(UbicacionOSM.id==cli.ubicacion_osm_id).delete()
                    cli.ubicacion_osm = ubicacion_osm

                cli.ubicacion = None
            elif ubicacion:
                cli.ubicacion = ubicacion
                cli.ubicacion_osm = None
            #endif
        #endif

        db.commit()

        return ''

@bp_ventas.route("/ubicacionOsmData", methods = ['GET'])
@login_required
def get_ubicacionosm_data():
    ubicacion_osm_id = int(request.args['id'])

    db = get_db()

    ubicacion_osm = db.query(UbicacionOSM).get(ubicacion_osm_id)

    ubicacion_osm_json = jsonify(
        _id = ubicacion_osm.id,
        lat = ubicacion_osm.lat,
        lon = ubicacion_osm.lon,
        display_name = ubicacion_osm.display_name,
        road = ubicacion_osm.road,
        house_number = ubicacion_osm.house_number,
        postcode = ubicacion_osm.postcode,
        state = ubicacion_osm.state,
        state_district = ubicacion_osm.state_district,
        town = ubicacion_osm.town,
        city = ubicacion_osm.city,
        city_district = ubicacion_osm.city_district,
        suburb = ubicacion_osm.suburb,
    )

    return ubicacion_osm_json
