import sys
import os

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)

# now we can import the module in the parent
# directory.

import model.models as models
import repository.device_repository as device_repository
import repository.consumption_repository as consumption_repository_package

class UserRepository:

    db = None

    def __init__(self, db):
        self.db = db

    def insert(self, username, password):
        sql = "INSERT INTO users(username, password) VALUES('%s', '%s')" % (username, password)
        result = self.db.engine.execute(sql)
        print(result)
        return result

    def insert_with_role(self, user: models.Users):
        sql = "INSERT INTO users(username, password, role) VALUES('%s', '%s', %d)" % (user.username, user.password, user.role)
        result = self.db.engine.execute(sql)
        return result

    def find_by_username(self, username):
        sql = "SELECT * FROM users WHERE username = '%s'" % username
        result_list, result = self.db.engine.execute(sql), None
        for el in result_list:
            result = models.Users(
                id=el[0],
                username=el[1],
                password=el[2],
                role=el[3]
            )
            break
        return result

    def get_users(self):
        sql = "SELECT * FROM users"
        result_list = self.db.engine.execute(sql)
        object_list = []
        for entry in result_list:
            object_list.append(models.Users(
                id=entry[0],
                username=entry[1],
                password=entry[2],
                role=entry[3]
            ))
        return object_list

    def find_by_id(self, id):
        sql = "SELECT * FROM users WHERE Id = %d" % id
        result_list, result = self.db.engine.execute(sql), None
        for el in result_list:
            result = models.Users(
                id=el[0],
                username=el[1],
                password=el[2],
                role=el[3]
            )
            break
        return result

    def update_user(self, user: models.Users):
        sql = "UPDATE users SET (username, password, role) = ('%s', '%s', %d) WHERE Id = %d" % \
              (user.username, user.password, user.role, user.ID)
        self.db.engine.execute(sql)

    def delete_user(self, user_id: int, device_repository: device_repository.DeviceRepository,
                    consumption_repository: consumption_repository_package.ConsumptionRepository):
        # delete all associated devices with that user
        id_of_devices = device_repository.get_devices_id_of_user(user_id)
        for id in id_of_devices:
            device_repository.delete_device(id, consumption_repository)

        query = "DELETE FROM users WHERE Id = %d" % user_id
        self.db.engine.execute(query)

    def users_join_devices_join_address(self):
        query = """
            SELECT username, description, city, country, max_hourly_consumption, devices.id FROM users 
            JOIN devices ON devices.owner_id = users.id 
            JOIN addresses ON addresses.id = devices.address_id 
            ORDER BY username;
        """
        return self.db.engine.execute(query)

    def users_join_devices_join_address_by_user_id(self, id):
        query = """
            SELECT username, description, city, country, max_hourly_consumption, devices.id FROM users 
            JOIN devices ON devices.owner_id = users.id 
            JOIN addresses ON addresses.id = devices.address_id 
            WHERE users.id = %d
            ORDER BY username
        """ % (id)
        return self.db.engine.execute(query)
