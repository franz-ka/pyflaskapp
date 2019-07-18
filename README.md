**! ! EN PRODUCCIÓN ! !**

# pyflaskapp

Para el primer uso: 
1. en la raiz creamos un virtual env `python3 -m venv /venv`
2. activamos el venv `source venv/bin/activate`
3. instalamos dependencias `pip install -r requirements.txt`
4. setteamos la variable `export FLASK_APP=flask1`
5. `flask run` para hostear la app en http://127.0.0.1:5000
6. `flask init-db` para inicializar y cargar la db

Posteriormente solo hace falta hacer `flask run` para hostear o `python3 run.py`

Archivos principales:
* `routes.py` : Mapeo de urls a funciones y lógicas de get/post
* `models.py` : Clases de la base de datos
* `templates/__maingui.html` : Esqueleto html
* `templates/_menu.html` : Menu html
* `templates/menu/*.html` : Pantallas html
* `templates/_form.html` : Macros html de forms

Otros archivos:
* `__init__.py` : Creador de aplicación Flask
* `utils/modelcreator.py` : Crea las clases para models.py
* `utils/menuitemcreator.py` : Utilidad para crear nuevos items en el menú
* `db.py` : Definición de comandos db (como init-db)
* `login.py` : Modelos y lógica de login
* `csvexport.py` : Clase usada para exportar a .csv
* `instance/flask1.db` : Base de datos sqlite3

Unas screens:
![alt text](https://i.ibb.co/M2LJ83d/11.png)
![alt text](https://i.ibb.co/qWxDMsM/22.png)
