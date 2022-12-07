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


class AddressRepository:
    db = None

    def __init__(self, db):
        self.db = db

    def _insert(self, country, city):
        sql = "INSERT INTO addresses(country, city) VALUES('%s', '%s')" % (country, city)
        result = self.db.engine.execute(sql)
        return result

    def get_location_id(self, country, city):
        query = "SELECT id FROM addresses WHERE country = '%s' AND city = '%s'" % (country, city)
        result = self.db.engine.execute(query)
        for entry in result:
            return entry[0]
        return None

    def insert_if_not_exists(self, country, city):
        address_id = self.get_location_id(country, city)
        if address_id is not None:
            return address_id
        self._insert(country, city)
        address_id = self.get_location_id(country, city)
        return address_id
