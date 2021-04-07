import sys
import os
app_path = os.path.abspath(__file__ + "/../../")
print('Usando path =', str(app_path))
sys.path.append(str(app_path))


from dbconfig import get_db_session, Venta, Cliente
from pprint import pprint

# Crear la nueva tabla si no existe
db = get_db_session()

ventas = db.query(Venta).all()

comentarios = []
for v in ventas:
	if v.comentario:
		# por frase completa
		#comentarios.append(v.comentario.strip().lower())
		# por primera palabra
		comentarios.append(v.comentario.strip().lower().split(' ')[0])

comentarios_unicos = {}
for c in comentarios:
	if not c in comentarios_unicos:
		comentarios_unicos[c] = 1
	else:
		comentarios_unicos[c] += 1

'''cmts = list(comentarios_unicos.keys())
cmts.sort()
print('\n'.join(cmts))
sys.exit(0)'''

#comentarios_top = {c:n for c,n in comentarios_unicos.items() if n > 5}
#https://www.askpython.com/python/dictionary/sort-a-dictionary-in-python
comentarios_top_sorted = {key: value for key, value in sorted(comentarios_unicos.items(), reverse=True, key=lambda item: item[1]) if value >= 6}

print('"Primera palabra en comentarios, 6 ocurrencias o más"')
print('cantidad, texto')
# tipo array
#[print(f'"{c}", ') for c in comentarios_top]
# texto plano
#print('\n'.join(comentarios_top))
# tipo csv
#[print(f'{c}, {n}') for n, c in comentarios_top.items()]
[print(f'{c}, {n.title()}') for n, c in comentarios_top_sorted.items()]


##########################
############ 2
##########################
# copiado de arriba
comentarios = []
for v in ventas:
	if v.comentario:
		# por frase completa
		#comentarios.append(v.comentario.strip().lower())
		# por primera palabra
		words = v.comentario.strip().lower().split(' ')
		if len(words):
			comentarios.append(len(words) >= 2 and words[0] + ' ' + words[1] or words[0])
comentarios_unicos = {}
for c in comentarios:
	if not c in comentarios_unicos:
		comentarios_unicos[c] = 1
	else:
		comentarios_unicos[c] += 1
print('\n"Primeras 2 palabras en comentarios, 4 ocurrencias o más"')
print('cantidad, texto')
comentarios_top_sorted = {key: value for key, value in sorted(comentarios_unicos.items(), reverse=True, key=lambda item: item[1]) if value >= 4}
[print(f'{c}, {n.title()}') for n, c in comentarios_top_sorted.items()]

#db.add(Cliente(nombre=''))

#db.commit()

# Mostrar todas
