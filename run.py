from flask1 import create_app
app = create_app()
app.run(debug=True, host='127.0.0.1')
#app.run(debug=True, host='192.168.0.92', port=54321)