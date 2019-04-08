import os
from flask import Flask
from sqlalchemy.orm import sessionmaker

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

    ###### DB
    from . import db
    db.init_app(app)

    ###### LOGIN
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "/login"
    @login_manager.user_loader
    def load_user(userid):
        from .loginuser import User
        return User(userid)

    ###### ROUTES (y TEMPLATES)
    from . import routes
    app.register_blueprint(routes.bp)

    return app
