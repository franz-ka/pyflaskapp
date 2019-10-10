from dbconfig import Usuario, \
    Pika, Insumo, PikaInsumo, \
    PrestockPika, StockPika, StockInsumo, MovStockPika, MovStockInsumo, \
    VentaTipo, Venta, VentaPika, \
    Maquina, Gcode, Falla, Alarma, \
    init_db_engine
    

engine = init_db_engine()

engine.execute('ALTER TABLE venta ADD column fecha_pedido DATETIME')