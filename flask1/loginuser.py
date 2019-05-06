from flask_login import UserMixin

# silly user model
#??????????
class User(UserMixin):
    def __init__(self, id, name, isadmin):
        self.id = id
        self.name = name
        self.isadmin = isadmin
        return None
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, str(self.isadmin))


#??????????
# create some users with ids 1 to 20
# users = [User(id) for id in range(1, 21)]