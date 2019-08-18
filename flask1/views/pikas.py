# coding=utf-8
from ._common import *

bp_pikas = Blueprint('pikas', __name__, url_prefix='/pikas')

@bp_pikas.route("/armadopika", methods = ['GET', 'POST'])
@login_required
def menu_armadopika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/pikas/armadopika.html',
            pikas=pikas
        ))
        return r
    else: #request.method == "POST":
        print('post form:',request.form)

        try: checkparams(request.form, ('pika', 'cantidad'))
        except Exception as e: return str(e), 400

        db = get_db()

        pikas = request.form.getlist('pika')
        cants = request.form.getlist('cantidad')
        dtnow = datetime.datetime.now()
        for i, pikaid in enumerate(pikas):
            if i<len(cants) and cants[i] and pikaid:
                pika = db.query(Pika).get(pikaid)
                pikacant = int(cants[i])
                stockpika = db.query(StockPika).get(pikaid)
                pikainsus = db.query(PikaInsumo).filter(PikaInsumo.pika==pika)

                #restamos stock de insumos
                for pikainsu in pikainsus:
                    stockinsu = db.query(StockInsumo).get(pikainsu.insumo_id)
                    if stockinsu.cantidad < pikainsu.cantidad*pikacant:
                        return 'No hay suficiente stock de "{}" para el pika "{}" (hay {}, requiere {})'.format(pikainsu.insumo.nombre, pika.nombre, stockinsu.cantidad, pikainsu.cantidad*pikacant), 400

                    movinsu = MovStockInsumo(insumo=pikainsu.insumo, cantidad=pikainsu.cantidad, fecha=dtnow)
                    db.add(movinsu)
                    stockinsu.cantidad -= movinsu.cantidad*pikacant
                    stockinsu.fecha = movinsu.fecha

                #sumamos stock de pika
                mov = MovStockPika(pika=pika, cantidad=int(cants[i]), fecha=dtnow)
                db.add(mov)
                stockpika.cantidad += pikacant
                stockpika.fecha = mov.fecha

        db.commit()

        check_alarmas()

        return ''
    
    
@bp_pikas.route("/stockpikas", methods=['GET', 'POST'])
@login_required
def menu_stockpikas():
    if request.method == "GET":
        db = get_db()
        DATA = db.query(StockPika).join(Pika).order_by(Pika.nombre).all()

        r = make_response(render_template(
            'menu/pikas/stockpikas.html',
            DATA=DATA
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('PARAM1', 'PARAMN'))
        except Exception as e:
            return str(e), 400

        return redirect(url_for('main.menu_stockpikas'))

@bp_pikas.route("/exportar/stockpikas.csv", methods=['GET'])
@login_required
def exportar_stockpikas():
    db = get_db()
    stopik = db.query(StockPika).join(Pika).order_by(Pika.nombre).all()

    ex = CsvExporter('stockpikas.csv')
    ex.writeHeaders('Id,Nombre,Cantidad,Actualizado')
    for s in stopik:
        print(s)
        ex.writeVals([s.pika_id, s.pika.nombre, s.cantidad, s.fecha])
    return ex.send()

@bp_pikas.route("/agregelimpika", methods=['GET', 'POST'])
@login_required
def menu_agregelimpika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).all()

        r = make_response(render_template(
            'menu/pikas/agregelimpika.html',
            pikas=pikas
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        if request.form['operation'] == 'add':
            try:
                checkparams(request.form, ('nombrepika',))
            except Exception as e:
                return str(e), 400
        else:
            return str('Operación inválida'), 400
        '''elif request.form['operation'] == 'delete':
        try:
            checkparams(request.form, ('id'))
        except Exception as e:
            return str(e), 400'''

        db = get_db()

        if request.form['operation'] == 'add':
            if db.query(Pika).filter(Pika.nombre==request.form['nombrepika']).first():
                return str('Ya existe un pika con ese nombre'), 400
            # siempre al agregar un pika se debe agregar su StockPika en 0 sino después hay errores
            pika = Pika(nombre=request.form['nombrepika'])
            db.add(pika)
            db.add(StockPika(pika=pika, cantidad=0, fecha=datetime.datetime.now()))

        db.commit()

        return ''

@bp_pikas.route("/modificarstockpika", methods=['GET', 'POST'])
@login_required
def menu_modificarstockpika():
    if request.method == "GET":
        db = get_db()
        pikas = db.query(Pika).order_by(Pika.nombre).all()
        stocks = db.query(StockPika).all()

        r = make_response(render_template(
            'menu/pikas/modificarstockpika.html',
            pikas=pikas,
            stocks=stocks
        ))
        return r
    else:  # request.method == "POST":
        print('post form:', request.form)

        try:
            checkparams(request.form, ('pika', 'cantidadnueva'))
        except Exception as e:
            return str(e), 400

        db = get_db()

        pika = db.query(Pika).get(request.form['pika'])
        pikacant = int(request.form['cantidadnueva'])
        dtnow = datetime.datetime.now()

        # modificamos stock de pika
        mov = MovStockPika(pika=pika, cantidad=pikacant, fecha=dtnow)
        db.add(mov)

        stockpika = db.query(StockPika).get(request.form['pika'])
        stockpika.cantidad = pikacant
        stockpika.fecha = mov.fecha

        db.commit()

        return ''

