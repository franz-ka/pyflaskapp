import sys, re
path=sys.argv[1]

f=open(path,'r+')
lastl=''
selfound=0
full_file = f.readlines()
f.seek(0)
#f=open(path,'w')
full_file_iter=iter(full_file)
for line in full_file_iter:
	#search for select
	if '<select class' in line:
		#guardamos parámetro col
		data_name = re.search('name="(\w+)"', line).groups()[0]
		data_cols = re.search('col-sm-(\d+)', lastl).groups()[0]
		data_required = '1' if 'required' in line else '0'
		ln=line
		#continue till close select
		while '</select' not in ln:
			ln=next(full_file_iter)
		#skip close select
		ln=next(full_file_iter)
		#skip empty lines
		while not ln:
			ln=next(full_file_iter)
		#msg div (inside current div)?
		data_msg=''
		if '<div' in ln and 'invalid-feedback' in ln:
			while 1:
				ln=next(full_file_iter)
				if '</div' not in ln:
					data_msg += ln.strip()
				else:
					break
			#skip close msg div
			ln=next(full_file_iter)
			#skip empty lines
			while not ln:
				ln=next(full_file_iter)
		#continue till close first div
		while '</div' not in ln:
			ln=next(full_file_iter)
		#skip close first div
		ln=next(full_file_iter)
		
		print(path, f'{{{{ forms.input_select({data_cols}, "{data_msg}") }}}}')
		f.write(f'    {{{{ forms.input_select({data_cols}, "{data_name}", "{data_msg}", required={data_required}) }}}}\n')
		
		# puntero quedó en el prox a </div, así que lo asignamos a lastl
		# en prox iteración se escribirá
		lastl = ln
		# eskipeamos sino se escribiría el opening div parent del select (igual lo acabamos de pisar con la línea anterior)
		continue
	if lastl:
		f.write(lastl)
	lastl = line
# escribimos última línea
f.write(line)	
# truncamos (borramos todo después de nuestro write, que equivale al archivo viejo)
f.truncate()
f.close()
