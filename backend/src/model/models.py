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

class Users:
    ID = None
    username = None
    password = None
    role = None

    def __init__(self, id, username, password, role):
        self.ID = id
        self.username = username
        self.password = password
        self.role = role

    def __repr__(self):
        return """
            ID = %d,
            username = %s,
            password = %s,
            role = %d
        """ % (self.ID, self.username, self.password, self.role)

    def to_tuple(self):
        return self.ID, self.username, self.password, self.role


class Device:
    ID = None
    description = None
    address_id = None
    max_hourly_consumption = None
    owner_id = None

    def __init__(self, id, description, address_id, max_hourly_consumption, owner_id):
        self.ID = id
        self.description = description
        self.address_id = address_id
        self.max_hourly_consumption = max_hourly_consumption
        self.owner_id = owner_id

    def __repr__(self):
        return """
            ID = %d
            description = %s
            address_id = %s
            max_h_cons = %s
            owner_id = %d
        """ % (self.ID, self.description, self.address_id, self.max_hourly_consumption, self.owner_id)

    def to_tuple(self):
        return self.ID, self.description, self.address_id, self.max_hourly_consumption, self.owner_id


class Address:
    ID = None
    city = None
    country = None

    def __init__(self, id, city, country):
        self.ID = id,
        self.city = city,
        self.country = country

    def __repr__(self):
        return f'{self.ID} {self.city} {self.country}'

    def to_tuple(self):
        return self.ID, self.city, self.country
