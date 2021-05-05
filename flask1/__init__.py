import os, sys
from flask import Flask
from flask import __version__ as flask__version__
from sqlalchemy.orm import sessionmaker
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

DBSession = sessionmaker()

# Flask Mega Tutorial - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure
# The Application Factory - http://flask.pocoo.org/docs/1.0/tutorial/factory/
# Application Factories - http://flask.pocoo.org/docs/1.0/patterns/appfactories/
# Flask - Application Factory - https://excellencetechnologies.in/blog/flask-application-factory/
def create_app(test_config=None):
    print('Py version {}.{}'.format(*sys.version_info[:2]))
    print('Flask version', flask__version__)
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
        auth = (app.config['MAIL_USU'], app.config['MAIL_PASS'])
        secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_FROM'],
            toaddrs=app.config['MAIL_TO_ERRORS'], subject='Cogosys - Error',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/errors.log', maxBytes=51200, backupCount=5)
        file_handler.setFormatter(logging.Formatter('\n%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

    # guardar static path
    static_path = str(os.path.abspath(__file__ + "/../static"))
    print('Usando static path =', static_path)
    app._static_path = static_path

    ###### DB
    from . import db
    db.init_app(app)

    ###### LOGIN
    from . import login
    login.init_app(app)

    ###### ROUTES (y TEMPLATES)
    from . import routes
    app.register_blueprint(routes.bp)
    from .views import menu_bps
    for menu_bp in menu_bps:
        app.register_blueprint(menu_bp)

    ###### REQUESTS LOGGER
    if not os.path.exists('logs'):
        os.mkdir('logs')
    app._request_logger = logging.getLogger("requests")
    app._request_logger.setLevel(logging.DEBUG)
    req_file_handler = RotatingFileHandler('logs/requests.log', maxBytes=102400, backupCount=5)
    req_file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
    req_file_handler.setLevel(logging.DEBUG)
    app._request_logger.addHandler(req_file_handler)
    @app.before_request
    def log_request_info():
        from flask import request
        r = request
        if r.endpoint != None and r.endpoint != 'static':
            log_vals = []
            if len(r.values):
                for key,val in r.values.items():
                    if key == 'password':
                        sanit_val = '*' * len(val)
                    else:
                        sanit_val = val.replace('"',r'\"')
                    log_vals.append(f'{key}="{sanit_val}"')
            app._request_logger.debug('%s, %s, %s, (%s), %s, %s',
                     r.method,
                     r.path,
                     r.endpoint,
                     ';'.join(log_vals),
                     r.remote_addr,
                     r.headers.get('USER_AGENT','--Sin USER_AGENT--'))

    return app
