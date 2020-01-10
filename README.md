# pyflaskapp

Para el primer uso: 
1. en la raiz creamos un virtual env `python3 -m venv /venv`
2. activamos el venv `source venv/bin/activate`
3. instalamos dependencias `pip install -r requirements.txt`
4. setteamos la variable `export FLASK_APP=flask1`
5. `flask run` para hostear la app en http://127.0.0.1:5000
6. `flask init-db` para inicializar y cargar la db

Posteriormente solo hace falta hacer `flask run` para hostear o `python3 run.py`

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
