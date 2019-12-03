tables = {
    #'Pika': ['id','nombre,str64,nonull'] ,
    #'Insumo': ['id', 'InsumoTipo', 'nombre,str64,nonull'] ,
    #'PikaInsumo': ['Pika', 'Insumo', 'cantidad,int,nonull'] ,
    #'StockPika': ['Pika','cantidad,int,nonull', 'fecha,datetime'] ,
    #'StockInsumo': ['Insumo','cantidad,int,nonull', 'fecha,datetime'] ,
    'MovPrestockPika': ['id', 'Pika','cantidad,int,nonull', 'fecha,datetime'] ,
    #'MovStockInsumo': ['id', 'Insumo','cantidad,int,nonull', 'fecha,datetime'],
    #'Usuario': ['id','nombre,str32,nonull','passhash,str64,nonull','esadmin,bool,nonull'],
    #'VentaTipo': ['id', 'nombre,str64,nonull'],
    #'Venta': ['id', 'VentaTipo', 'fecha,datetime', 'comentario,str128', 'VentaPika,multiple'],
    #'VentaPika': ['id', 'Venta', 'Pika', 'cantidad,int,nonull']
    #'Maquina': ['id', 'nombre,str64,nonull'],
    #'Gcode': ['id', 'Pika', 'nombre,str128,nonull'],
    #'Falla': ['id', 'Maquina', 'Gcode', 'descripcion,str128,nonull', 'fecha,datetime']
    #'Alarma': ['id', 'Insumo', 'cantidad,int,nonull', 'fecha_avisado,datetime']
    #'PrestockPika': ['Pika','cantidad,int,nonull', 'fecha,datetime'] 
    #'StockPikaColor': ['Pika','cantidad_bajo,int', 'cantidad_medio,int'] ,
    #'StockInsumoColor': ['Insumo','cantidad_bajo,int', 'cantidad_medio,int'] ,
    #'FactorProductividad': ['Pika','factor,float,nonull', 'fecha_actualizado,datetime'] ,
    #'InsumoTipo': ['id', 'nombre,str64,nonull']
    #'PedidoUrgente': ['Venta']
}

txt=[]
for tname in tables:
    str = []
    str.append( "class {0}(Base):".format(tname) )
    str.append( "__tablename__ = '{0}'".format(tname.lower()) )

    fields = tables[tname]
    hasid = False
    if fields[0]=='id':
        str.append( "id = Column(Integer, primary_key=True, autoincrement=True)" )
        hasid = True
        del fields[0]
    for f in fields:
        fs = f.split(',')
        if f[0].isupper():
            if len(fs)==1:
                str.append( "{0}_id = Column(Integer, ForeignKey('{0}.id'){1})".format(f.lower(),'' if hasid else ', primary_key=True') )
                str.append( "{0} = relationship('{1}')".format(f.lower(), f) )
            else:
                if fs[1]=='multiple':
                    str.append("{0} = relationship('{1}')".format(fs[0].lower() + 's', fs[0]))
                else:
                    raise NotImplementedError()

        else:
            if len(fs)<2: raise Exception('campo {0} de tabla {1} tiene pocos argumentos ({2})'.format(f, tname, fs))

            if fs[1]=='int': type = 'Integer'
            elif fs[1][:3]=='str': type = 'String(' + fs[1][3:] + ')'
            elif fs[1]=='datetime': type = 'DateTime'
            elif fs[1]=='bool': type = 'Boolean'
            elif fs[1]=='float': type = 'Float'

            if 'nonull' in fs:
                nullstr=', nullable=False'
                fs.remove('nonull')
            else: nullstr=''

            str.append( "{0} = Column({1}{2})".format(fs[0], type, nullstr) )
    if fields[0]=='id':
        str.append( "def __repr__(self): return '<{0} {{}}>'.format(self.id)".format(tname) )
    else:
        str.append( "def __repr__(self): return '<{0} {{}}>'.format(self.{1})".format(tname, fields[0].lower() + '_id') )
    for i,l in enumerate(str):
        if i>0:
            str[i]='\t' + str[i]
    str.append( "" )
    txt.extend(str)

print('\n'.join(txt))