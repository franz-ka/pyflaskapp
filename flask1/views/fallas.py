# coding=utf-8
from ._common import *

bp_fallas = Blueprint('fallas', __name__, url_prefix='/fallas')

@bp_fallas.route("/listadofallas", methods=['GET', 'POST'])
@login_required
def menu_listadofallas():
    if request.method == "GET":
        db = get_db()
        if not len(request.args):
            fallas = db.query(Falla)
            filtrado = False
        else:
            query = []
            for arg in request.args:
                k, v = arg, request.args[arg]
                if v:
                    if k=='maquina': query.append(Falla.maquina_id == v)
                    elif k=='descripcion': query.append(Falla.descripcion.ilike("%{}%".format(v)))
                    elif k=='gcode': query.append(Falla.gcode_id == v)
                    elif k=='fechadesde': query.append(Falla.fecha >= datetime.datetime.strptime(v,'%d/%m/%Y'))
                    elif k=='fechahasta': query.append(Falla.fecha <= datetime.datetime.strptime(v,'%d/%m/%Y') + datetime.timedelta(days=1))
            if query:
                from functools import reduce
                fallas = db.query(Falla).filter(reduce(lambda x, y: x&y, query))
                filtrado = True
            else:
                fallas = db.query(Falla)
                filtrado = False
            if request.args['pika']:
                pikaid = int(request.args['pika'])
                fallas = fallas.join(Gcode).filter(Gcode.pika_id == pikaid)
                filtrado = True
        fallas = fallas.order_by(Falla.fecha.desc()).all()

        maqs = db.query(Maquina).order_by(Maquina.nombre).all()
        gcods = db.query(Gcode).order_by(Gcode.nombre).all()
        pikas=[]
        for g in gcods:
            if g.pika and g.pika not in pikas:
                pikas.append(g.pika)
        def pika_sort_key(ele):
            print(ele)
            return ele.nombre
        print(pikas)
        pikas.sort(key=pika_sort_key)
        print(pikas)

        r = make_response(render_template(
            'menu/fallas/listadofallas.html',
            fallas=fallas,
            maqs=maqs,
            pikas=pikas,
            gcods=gcods,
            filtrado=filtrado
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        return redirect(url_for('main.menu_listadofallas'))

@bp_fallas.route("/exportar/fallas.csv", methods=['GET'])
@login_required
def exportar_fallas():
    db = get_db()

    if not len(request.args):
        fallas = db.query(Falla)
        filtrado = False
    else:
        query = []
        for arg in request.args:
            k, v = arg, request.args[arg]
            if v:
                if k=='maquina': query.append(Falla.maquina_id == v)
                elif k=='descripcion': query.append(Falla.descripcion.ilike("%{}%".format(v)))
                elif k=='gcode': query.append(Falla.gcode_id == v)
                elif k=='fechadesde': query.append(Falla.fecha >= v)
                elif k=='fechahasta': query.append(Falla.fecha <= v)
        if query:
            from functools import reduce
            fallas = db.query(Falla).filter(reduce(lambda x, y: x&y, query))
            filtrado = True
        else:
            fallas = db.query(Falla)
            filtrado = False
        if request.args['pika']:
            pikaid = int(request.args['pika'])
            fallas = fallas.join(Gcode).filter(Gcode.pika_id == pikaid)
            filtrado = True
    fallas = fallas.order_by(Falla.fecha.desc()).all()

    ex = CsvExporter('fallas.csv')
    ex.writeHeaders('Id,Fecha,Máquina,Pika,G-code,Descripción')
    for f in fallas:
        vals = [f.id, f.fecha, f.maquina.nombre, '', '', f.descripcion]
        if f.gcode:
            vals[4] = f.gcode.nombre
            if f.gcode.pika:
                vals[3] = f.gcode.pika.nombre
        ex.writeVals(vals)
    return ex.send()

@bp_fallas.route("/ingresarfalla", methods=['GET', 'POST'])
@login_required
def menu_ingresarfalla():
    if request.method == "GET":
        db = get_db()
        maqs = db.query(Maquina).order_by(Maquina.nombre).all()
        gcods = db.query(Gcode).order_by(Gcode.nombre).all()
        pikas=[]
        for g in gcods:
            if g.pika and g.pika not in pikas:
                pikas.append(g.pika)
        def pika_sort_key(ele):
            print(ele)
            return ele.nombre
        print(pikas)
        pikas.sort(key=pika_sort_key)
        print(pikas)

        r = make_response(render_template(
            'menu/fallas/ingresarfalla.html',
            maqs=maqs,
            pikas=pikas,
            gcods=gcods
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('maquina', 'descripcion'))
        except Exception as e:
            return str(e), 400

        db = get_db()
        dtnow = datetime.datetime.now()
        if request.form['gcode']:
            db.add(Falla(
                maquina=db.query(Maquina).filter(Maquina.id == request.form['maquina']).one(),
                gcode=db.query(Gcode).filter(Gcode.id == request.form['gcode']).one(),
                descripcion=request.form['descripcion'],
                fecha=dtnow
            ))
        else:
            db.add(Falla(
                maquina=db.query(Maquina).filter(Maquina.id == request.form['maquina']).one(),
                descripcion=request.form['descripcion'],
                fecha=dtnow
            ))

        db.commit()

        return ''

@bp_fallas.route("/agregelimmaquina", methods = ['GET', 'POST'])
@login_required
def menu_agregelimmaquina():
    if request.method == "GET":
        db = get_db()
        maqs = db.query(Maquina).order_by(Maquina.nombre).all()

        r = make_response(render_template(
            'menu/fallas/agregelimmaquina.html',
            maqs=maqs
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombremaqui',))
            except Exception as e:
                return str(e), 400
        elif request.form['operation'] == 'delete':
            try:
                checkparams(request.form, ('maquina',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400

        db = get_db()

        if request.form['operation'] == 'add':
            if db.query(Insumo).filter(Maquina.nombre==request.form['nombremaqui']).first():
                return 'Ya existe una máquina con ese nombre', 400
            maq = Maquina(nombre=request.form['nombremaqui'])
            db.add(maq)
        elif request.form['operation'] == 'delete':
            maq = db.query(Maquina).get(int(request.form['maquina']))
            db.query(Falla).filter(Falla.maquina==maq).delete()
            db.query(Maquina).filter(Maquina.id==maq.id).delete()

        db.commit()

        return ''

@bp_fallas.route("/agregelimgcode", methods = ['GET', 'POST'])
@login_required
def menu_agregelimgcode():
    if request.method == "GET":
        db = get_db()
        gcods = db.query(Gcode).order_by(Gcode.nombre).all()
        pikas = db.query(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/fallas/agregelimgcode.html',
            gcods=gcods,
            pikas=pikas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombregcode',))
            except Exception as e:
                return str(e), 400
        elif request.form['operation'] == 'delete':
            try:
                checkparams(request.form, ('gcode',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400

        db = get_db()

        if request.form['operation'] == 'add':
            if db.query(Gcode).filter(Gcode.nombre==request.form['nombregcode']).first():
                return 'Ya existe una g-code con ese nombre', 400
            if request.form['pika']:
                gcod = Gcode(nombre=request.form['nombregcode'],pika=db.query(Pika).get(int(request.form['pika'])))
            else:
                gcod = Gcode(nombre=request.form['nombre'])
            db.add(gcod)
        elif request.form['operation'] == 'delete':
            gcod = db.query(Gcode).get(int(request.form['gcode']))
            db.query(Falla).filter(Falla.gcode==gcod).delete()
            db.query(Gcode).filter(Gcode.id==gcod.id).delete()

        db.commit()

        return ''
