## Corriendo el sistema
Para el primer uso:
1. En la raíz del proyecto creamos un virtual env `python3 -m venv /venv`
2. Activamos el venv `source venv/bin/activate`
3. Instalamos dependencias `pip install -r requirements.txt`
4. Copiamos `instance/config.example.py` como `instance/config.py` y editamos a nuestro antojo.
5. Setteamos la variable `export FLASK_APP=flask1`
6. `flask run` para hostear la app en http://127.0.0.1:5000. Si lo anterior no funciona probar con `python3 run.py`
7. `flask init-db` para inicializar y cargar la BBDD (si es que no tienen ya una BBDD)

Para usos posteriores solo hace falta activar el virtual env y hacer `flask run` para hostear, o directamente `python3 run.py`.

Oneliner de desarrollo directo: `FLASK_APP=flask1 ./venv/bin/python3 run.py`

O: `source venv/bin/activate && FLASK_APP=flask1 TZ="America/Chicago" python3 run.py`

Nota: si tirar el error __ValueError: Timezone__ agregar variable `TZ="America/Chicago"`

## Estructura de carpetas
* `run.py` : Punto de entrada de la aplicación
* `flask1/` : Contiene la aplicación principal
  * `__init__.py` : Definición de contructor de la aplicación
  * `models.py` : Clases de la BBDD en SQL Alchemy
  * `routes.py` : Rutas generales de la aplicación (no de los menús)
  * `static/` : Archivos estáticos (o sea no procesador por el intérprete de python) como css, js e imágenes
  * `templates/` : HTMLs de la aplicación
    * `__base.html` y `_maingui.html` : HTMLs esqueleto
    * `_menu.html` : Ítems del menú principal (sidebar)
    * `_form.html` : Definición de funciones utilitarias para el armado de HTMLs
  * `views/` : Acá están las rutas de los menús y sus lógicas de BBDD
* `instance/` : Tiene archivos que no se suben al repositorio, como la BBDD y la configuración
* `logs/` : Logs del sistema, tampoco se suben al repositorio
* `utils/` : Contiene scripts utilitarios para el desarrollo
  * `modelcreator.py` : Sirve para crear modelos para SQL Alchemy a partir de arrays
  * `menuitemcreator.py` : Sirve para crear nuevas pantallas. Se usa pasándole 2 parámetros: el primero es bajo qué menú irá el nuevo ítem (pikas, insumos, etc.) y el segundo es el nombre del archivo que tendrá la nueva pantalla.
  * `db/test_script.py` : Sirve para testear funciones de SQL Alchemy sin necesidad de correr levantar site

## Templateo de HTML con Jinja2
Los template HTML utilizan la libería Jinja2. Las expresiones de Jinja2 están entre `{{ ... }}` o `{% ... %}`. Dentro de estos símbolos se puede usar un código similar a Python. Para leer datos de la aplicación principal mirar el apartado de [Manejo de requests](#manejo-de-requests).

Algunos usos básicos de Jinja2 son:

* `{{<expresión>}}` para insertar lo que devuelva la `<expresión>` directo al HTML final

* `{% set nombre_variable = <valor> %}` define y setea la variable `nombre_variable`

* `{% if <condición> %} ... {% else %} ... {% endif %}` el típico `if`

* `{% for <ele> in <colección> %} ... {% endfor %}` el típico `for`

**NOTA IMPORTANTE:** si define variables afuera del for, no las puede reasignar dentro del for! Para eso hay que hacer un workaround con arrays como se ve en [`prioridadimpresion.html`](flask1/templates/menu/prioridades/prioridadimpresion.html) con la variable `last_ventid`.

* `{{ forms.una_funcion(<parámetros>) }}` para insertar lo que devuelva la `forms.una_funcion(<parámetros>)` directo al HTML final

* `{% call forms.otra_funcion(<parámetros>) %} ... {% endcall %}` alternativa a comando anterior; en este caso el HTML que se encuentre entre los bloques `call`/`endcall` se le pasara al la función llamada, y esta podrá usar ese HTML llamando a `caller()`

## Acceso a la BBDD con SQL Alchemy
Para acceder a la BBDD se utiliza la librería SQL Alchemy. Los modelos, como ya mencionamos, están en el archivo `models.py`. La sesión de conexión a la BBDD se invoca de `db.py`.

Algunos usos básicos SQL Alchemy son los siguiente:

(por *registro* nos referimos a una fila de una tabla, que viene en forma de objeto de Python de tipo *Modelo*)

#### Consultar
* `db.query(<Modelo>).all()` traer todos los registros

* `db.query(<Modelo>).filter(<condición 1>, <condición N>).all()` traer todos los registros que cumplan con las condiciones pasadas (es un AND)

* `db.query(<Modelo>).filter(or_(<condición 1>, <condición N>)).all()` lo mismo que el anterior pero con OR

* `db.query(<Modelo>).filter(<Modelo>.<Campo>.in_(<array de valores>)).all()` traer todos los registros cuyo campo esté dentro de los valores de `<array de valores>` (sería como muchos OR)

* `db.query(<Modelo>).order_by(<Modelo>.<Campo>).all()` traer todos los registros ordenados ascendentemente por un campo. Si desea que el orden sea descendiente, agregarle `.desc()` al campo

* `db.query(<Modelo>).get(<id>)` traer un registro único según id de la tabla (si hay dos tira error)

* `db.query(<Modelo 1>).join(<Modelo 2>).all()` traer registros de dos tablas relacionadas (alguna tiene un campo con id de la otra)

Posteriormente para recorrer los registros utilice un `for` común y corriente. También puede pasarle directamente la colección a Jinja2 para recorrerlo en el template HTML.

#### Agregar
`db.add(<Instancia de modelo>)` agregar un registro

#### Eliminar
Para eliminar un registro puede usar cualquiera de las querys anteriores pero en vez de llamar `.all()` usar `.delete()`

También puede llamar `.delete()` directamente sobre un objeto de la BBDD

#### Modificar
Para modificar un registro simplemente asígnele un valor a alguno de sus campos. Por ejemplo:
```
mi_registro = db.query(<Modelo>).get(<id>)
mi_registro.nombre = '<nuevo nombre>'
```

**Recuerde** que si hace alguna modificacion de algún campo de algún registro, o agrega/elimina un registro entero, debe hacer `db.commit()` para efectuar los cambios.

## Manejo de requests

Las requests se reciben en las rutas definidas en `views/`.

Cada ruta corresponde a una función, y tiene un decorador del tipo:   
`@bp_<menú>.route(<url de ruta>, <métodos aceptados>)`

Por ejemplo:   
`@bp_fallas.route("/listadofallas", methods=['GET', 'POST'])`.

La `<url de ruta>` va a ser relativo al menú donde se encuentra dicha ruta. Si estamos en el menú `pikas`, y definimos la url de ruta como `/agregarpika`, la ruta final será `<url del site>/pikas/agregarpika`.

Los `<métodos aceptados>` es un array que puede contener `'GET'`, `'POST'`, o los dos.

Toda la información de una request será accesible desde dentro de la función de la ruta mediante la variable `request`.

Si estamos en un POST, la data del formulario se accede mediante `request.form['<nombre de campo>']`.

Si estamos en un GET, mediante `request.args['<nombre de campo>']`.

Tanto `request.form` como `request.args` se pueden recorrer con un `for`.

Para responder a una request utilizamos `return` y generalmente devolvemos rendereando un template HTML haciendo:
```
return make_response(render_template(
  '<path a HTML>',
   <variable 1>: <valor 1>,
   <variable N>: <valor 1>,
))
```
Donde la variables serán pasadas al template y podrán ser leídas por Jinja2.

## Lógica de la información
La información principal de la BBDD son _Pika_ e _Insumo_. Cada pika consume uno o más insumo en alguna parte del proceso de producción del pika. En qué parte del proceso de producción va a depender del _InsumoTipo_ que tenga el insumo, que puede ser: en el ingreso a prestock, en el armado, o en la venta. En cualquiera de esos 3 momentos por el que transite un pika se puede consumir un insumo. Qué insumo exactamente, vendra definido por los insumos que tenga asociado ese pika. Estas asociasiones estan en definidas en _PikaInsumo_.

Por otro lado tenemos los stocks de pikas e insumos en _StockPika_ y _StockInsumo_ respectivamente. Además, como los pikas primero entran en prestock y recién cuando se arman entran a stock, tenemos _PrestockPika_. Los movimientos de cada stock están en sus respectivas tablas: _MovPrestockPika_, _MovStockPika_ y _MovStockInsumo_ (sí, tendría que haber puesto todo en una misma tabla, pero me avive tarde!).

Cuando se ingresa un pedido o una venta se genera un registro _Venta_. Los tipos de venta están en _VentaTipo_. Como cada venta puede contener uno o más pikas, necesitamos una tabla aparte, que es _VentaPika_. Ahí se asocian qué pikas se vendieron en qué venta. Lo único que diferencia una venta de un pedido es que el pedido tiene el campo `fecha` vacío y una venta lo tiene populado con la fecha de venta.

## Accediendo directamente a la BBDD
Para mirar la información directamente de la BBDD deben instalar `sqlite3`. Posteriormente abrir la BBDD:

`sqlite3 instance/flask1.db`

Una vez adentro para ver las tablas ejecutar `.tables`.

Si desean ver la estructura de una tabla hacer `.schema <nombre de la tabla>`.

Y desde ahí pueden ejecutar cualquier comando SQL válido (terminando con `;`). Por ejemplo: `select * from pika;`.

Por defecto no se muestran los nombre de las columnas. Si quieren verlos hacer `.headers on`.

Finalmente, si se van a pasar mucho tiempo mirando la BBDD, pueden configurar que se vean más ordenados los registros haciendo `.mode columns`.
