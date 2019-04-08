from flask_login import UserMixin

# silly user model
#??????????
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        return None
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


#??????????
# create some users with ids 1 to 20
users = [User(id) for id in range(1, 21)]