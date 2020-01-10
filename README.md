## Corriendo el sistema
Para el primer uso: 
1. en la raiz creamos un virtual env `python3 -m venv /venv`
2. activamos el venv `source venv/bin/activate`
3. instalamos dependencias `pip install -r requirements.txt`
4. setteamos la variable `export FLASK_APP=flask1`
5. `flask run` para hostear la app en http://127.0.0.1:5000
6. `flask init-db` para inicializar y cargar la db

Para usos posteriores solo hace falta activar el virtual env y hacer `flask run` para hostear o directamente `python3 run.py`

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
Los template HTML utilizan la libería Jinja2. Las expresiones de Jinja2 están entre `{{ ... }}` o `{% ... %}`. Dentro de estos símbolos se puede usar un código similar a Python.

Algunos usos básicos de Jinja2 son:

* `{{<expresión>}}` para insertar lo que devuelva la `<expresión>` directo al html final

* `{% set nombre_variable = <valor> %}` define y setea la variable `nombre_variable`

* `{% if <condición> %} ... {% else %} ... {% endif %}` el típico `if`

* `{% for <ele> in <colección> %} ... {% endfor %}` el típico `for`

**NOTA IMPORTANTE:** si define variables afuera del for, no las puede reasignar dentro del for! Para eso hay que hacer un workaround con arrays como se ve en [`prioridadimpresion.html`](flask1/templates/menu/prioridades/prioridadimpresion.html) con la variable `last_ventid`.

* `{{ forms.una_funcion(<parámetros>) }}` para insertar lo que devuelva la `forms.una_funcion(<parámetros>)` directo al html final

* `{% call forms.otra_funcion(<parámetros>) %} ... {% endcall %}` alternativa a comando anterior; en este caso el html que se encuentre entre los bloques `call`/`endcall` se le pasara al la función llamada, y esta podrá usar ese html llamando a `caller()`

## Acceso a la BBDD con SQL Alchemy
Para acceder a la BBDD se utiliza la librería SQL Alchemy. Los modelos, como ya mencionamos, están en el archivo `models.py`. La sesión de conexión a la BBDD se invoca de `db.py`. 

Algunos usos básicos SQL Alchemy son los siguiente:

(por *registro* nos referimos a una fila de una tabla, que viene en forma de objeto de Python de tipo *Modelo*)

* `db.query(<Modelo>).all()` traer todos los registros

* `db.query(<Modelo>).filter(<condición 1>, <condición N>).all()` traer todos los registros que cumplan con las condiciones pasadas (es un AND)

* `db.query(<Modelo>).filter(or_(<condición 1>, <condición N>)).all()` lo mismo que el anterior pero con OR

* `db.query(<Modelo>).order_by(<Modelo>.<Campo>).all()` traer todos los registros ordenados ascendentemente por un campo. Si desea que el orden sea descendiente, agregarle `.desc()` al campo

* `db.query(<Modelo>).get(<id>)` traer un registro único según id de la tabla (si hay dos tira error)

* `db.query(<Modelo 1>).join(<Modelo 2>).all()` traer registros de dos tablas relacionadas (alguna tiene un campo con id de la otra)

* `db.add(<Instancia de modelo>)` agregar un registro

Para eliminar un registro puede usar cualquiera de las querys anteriores pero en vez de llamar `.all()` usar `.delete()`

También puede llamar `.delete()` directamente sobre un objeto de la BBDD

Recuerde que si hace alguna modificacion de algún campo de algún registro, o agrega/elimina uno entero, debe hacer `db.commit()` para efectuar los cambios.
