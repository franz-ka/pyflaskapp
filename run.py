from flask1 import create_app
app = create_app()
app.run(debug=app.config['DEBUG_FLASK'], host=app.config['APP_HOST'], port=app.config['APP_PORT'])