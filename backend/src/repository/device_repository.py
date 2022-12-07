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
import repository.consumption_repository as consumption_repository_package

class DeviceRepository:

    db = None

    def __init__(self, db):
        self.db = db

    def insert(self, device: models.Device):
        query = "INSERT INTO devices(description, address_id, max_hourly_consumption, owner_id) " \
                "VALUES('%s', %d, %d, %d)"\
                % (device.description, device.address_id, device.max_hourly_consumption, device.owner_id)
        result = self.db.engine.execute(query)
        return result

    def find_by_id(self, id):
        query = "SELECT * FROM devices WHERE Id = %d" % id
        result_list, result = self.db.engine.execute(query), None
        for el in result_list:
            result = models.Device(
                id=el[0],
                description=el[1],
                address_id=el[2],
                max_hourly_consumption=el[3],
                owner_id=el[4]
            )
            break
        return result

    def get_devices_id_of_user(self, user_id: int):
        query = "SELECT ID FROM devices WHERE owner_id = %d" % user_id
        tuple_list = self.db.engine.execute(query)
        result = [tuple[0] for tuple in tuple_list]
        return result

    def get_devices(self):
        query = "SELECT * FROM devices"
        result_list = self.db.engine.execute(query)
        object_list = []
        for entry in result_list:
            object_list.append(models.Device(
                id=entry[0],
                description=entry[1],
                address_id=entry[2],
                max_hourly_consumption=entry[3],
                owner_id=entry[4]
            ))
        return object_list

    def update_device(self, device: models.Device):
        query = "UPDATE devices SET (description, address_id, max_hourly_consumption) = " \
                "('%s', %d, %d) WHERE id = %d" \
                "" % (device.description, device.address_id, device.max_hourly_consumption, device.ID)
        self.db.engine.execute(query)

    def update_device_mapping(self, device_id, owner_id):
        query = "UPDATE devices SET owner_id = " \
                "%d WHERE id = %d" \
                "" % (owner_id, device_id)
        print(query)
        self.db.engine.execute(query)

    def delete_device(self, id, consumption_repository: consumption_repository_package.ConsumptionRepository):
        # first delete all the entries of the device in the 'consumption' table
        consumption_repository.delete_based_on_device_id(id)

        query = "DELETE FROM devices WHERE Id = %d" % id
        self.db.engine.execute(query)