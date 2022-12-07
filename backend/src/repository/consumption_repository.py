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


class ConsumptionRepository:
    db = None

    def __init__(self, db):
        self.db = db

    def delete_based_on_device_id(self, device_id):
        sql = "DELETE FROM consumption WHERE device_id = %d" % device_id
        result = self.db.engine.execute(sql)
        return result

    def get_consumption_for_user_id_and_date(self, user_id, date):
        """
        Returns a list with the consumptions and ids for all devices of a certain user, in a certain day.
        :param user_id: integer
        :param date: string of type YYYY-MM-DD
        :return: list of tuples (device_id, consumption)
        """
        sql = "SELECT device_id, SUM(energy_consumption) / COUNT(*) as average " \
              "FROM consumption " \
              "JOIN devices on device_id = ID " \
              "WHERE owner_id = %d AND date(my_timestamp) = '%s'" \
              "GROUP BY device_id;" % (user_id, date)
        print(sql)
        result = self.db.engine.execute(sql)
        if not result:
            return []
        return [element for element in result]
