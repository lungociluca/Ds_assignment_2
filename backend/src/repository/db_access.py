
def get(db):
    sql = 'select * from users'
    list = (db.engine.execute(sql))
    for el in list:
        print(el)


def get_user_by_id(db, id):
    sql = 'select * from users where id = %d' % id
    res = db.engine.execute(sql)
    return res


"""
class Users(db.Model):
    __tablename__ = 'users'

    ID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(32))
    role = db.Column(db.Integer)

    def __init__(self, id, username, password, role):
        self.ID = id
        self.username = username
        self.password = password
        self.role = role
"""

