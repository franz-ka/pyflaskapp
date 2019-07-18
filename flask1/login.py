from flask_login import UserMixin, LoginManager, login_user, logout_user
from flask1.db import get_db
from .models import Usuario

# silly user model
# ??????????
class User(UserMixin):
    def __init__(self, id, name, isadmin):
        self.id = id
        self.name = name
        self.isadmin = isadmin
        return None

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, str(self.isadmin))

def init_app(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "/login"

    @login_manager.user_loader
    def load_user(userid):
        db = get_db()
        usu = db.query(Usuario).get(userid)
        return User(usu.id, usu.nombre, usu.esadmin) if usu else None

def loginUserPass(user, passw):
    print('login try "{}" "{}"'.format(user, passw))
    db = get_db()
    usu = db.query(Usuario).filter(Usuario.nombre==user).one_or_none()
    if not usu:
        return False

    import hashlib
    if hashlib.sha256( passw.encode('utf-8') ).hexdigest() != usu.passhash:
        return False

    user = User(usu.id, usu.nombre, usu.esadmin)
    login_user(user)
    return True

def logoutUser():
    return logout_user()