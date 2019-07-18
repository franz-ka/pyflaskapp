import os
from flask import Flask
from sqlalchemy.orm import sessionmaker
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

DBSession = sessionmaker()

# Flask Mega Tutorial - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure
# The Application Factory - http://flask.pocoo.org/docs/1.0/tutorial/factory/
# Application Factories - http://flask.pocoo.org/docs/1.0/patterns/appfactories/
# Flask – Application Factory - https://excellencetechnologies.in/blog/flask-application-factory/
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'flask1.db'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Error Handling in Flask - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-error-handling
    if not app.debug:
        auth = (app.config['MAIL_FROM'], "wer987sdf654")
        secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_FROM'],
            toaddrs=app.config['MAIL_TO'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/cogosys.log', maxBytes=10240, backupCount=5)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

    ###### DB
    from . import db
    db.init_app(app)

    ###### LOGIN
    from . import login
    login.init_app(app)

    ###### ROUTES (y TEMPLATES)
    from . import routes
    app.register_blueprint(routes.bp)

    return app
