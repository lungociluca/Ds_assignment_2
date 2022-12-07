import sys, os, hashlib
import datetime

# getting the name of the directory
# where the this file is present.
import model.models

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
import repository.users_repository as user_repository
import repository.device_repository as device_repository
import repository.consumption_repository as consumption_repository
import repository.calendar_repository as calendar_repository
import repository.address_repository as address_repository
import string
import constants.constants as constants


def md5_of_string(text):
    return hashlib.md5(text.encode()).hexdigest()


def get_current_date():
    current_time = datetime.datetime.now()
    return current_time.month, current_time.year


class Service:
    user_repository = None
    device_repository = None
    consumption_repository = None
    calendar_repository = None
    address_repository = None
    allowed_input = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + '._ ')

    def __init__(self, db):
        self.user_repository = user_repository.UserRepository(db)
        self.device_repository = device_repository.DeviceRepository(db)
        self.consumption_repository = consumption_repository.ConsumptionRepository(db)
        self.calendar_repository = calendar_repository.CalendarRepository(db)
        self.address_repository = address_repository.AddressRepository(db)

    def _test_strings_for_not_allowed_characters(self, string_list):
        """
        Takes a list of strings and returns True if there is a string not respecting the format
        specified in 'allowed_input'
        :param string_list: list of strings to check for potential injection
        :return: boolean
        """
        for s in string_list:
            if not set(s) <= self.allowed_input:
                return True
        return False

    def get_days_in_month(self, year: int, month):
        return self.calendar_repository.get_days_of_month(year, month)

    def insert_user(self, user, password):
        return self.user_repository.insert(user, password)

    def find_by_username(self, username):
        return self.user_repository.find_by_username(username)

    def register(self, username, password, confirm_password):
        input_list = [username]
        if self._test_strings_for_not_allowed_characters(input_list):
            return constants.NOT_ALLOWED_INPUT

        # if passwords don't match or the username is already taken => return unsuccessful status
        if password != confirm_password or self.user_repository.find_by_username(username):
            return constants.UNSUCCESSFUL

        # hash the password
        password = md5_of_string(password)

        self.user_repository.insert(username, password)
        return constants.USER

    def login(self, username, password):
        input_list = [username]
        if self._test_strings_for_not_allowed_characters(input_list):
            return constants.NOT_ALLOWED_INPUT

        result = self.user_repository.find_by_username(username)

        # hash the password
        password = md5_of_string(password)

        if not result:
            return constants.UNSUCCESSFUL
        if result.password == password:
            if result.role == 1:
                return constants.ADMIN
            else:
                return constants.USER
        else:
            return constants.UNSUCCESSFUL

    def get_users(self):
        return self.user_repository.get_users()

    def get_users_as_tuple_list(self):
        object_list = self.get_users()
        tuple_list = []
        for obj in object_list:
            tuple_list.append(obj.to_tuple())
        fields = ['ID', 'Username', 'Password', 'Role']
        return fields, tuple_list

    def get_user_by_id(self, user_id):
        return self.user_repository.find_by_id(user_id)

    def handle_admin_post(self, form, scenario):
        if scenario not in ['user', 'device', 'mapping']:
            print("Wrong scenario argument in service: " + scenario)
            return constants.UNSUCCESSFUL

        id_entry_to_change = None
        if scenario == 'user' or scenario == 'mapping':
            if not form.get('current_username'):
                return constants.UNSUCCESSFUL
            id_entry_to_change = self.user_repository.find_by_username(form.get('current_username')).ID
            if not id_entry_to_change:
                return constants.UNSUCCESSFUL
        else:
            id_entry_to_change = int(form.get('device_id'))

        if scenario == 'user':
            user: models.Users = self.user_repository.find_by_id(id_entry_to_change)
            if form.get('new_username'):
                user.username = form.get('new_username')
            if form.get('password'):
                user.password = md5_of_string(form.get('password'))
            if form.get('role'):
                user.role = int(form.get('role'))
            self.user_repository.update_user(user)
        elif scenario == 'device':
            device: models.Device = self.device_repository.find_by_id(id_entry_to_change)
            country, city = None, None

            if form.get('description'):
                device.description = form.get('description')
            if form.get('max_hourly_consumption'):
                device.max_hourly_consumption = int(form.get('max_hourly_consumption'))
            if form.get('city'):
                city = form.get('city')
            if form.get('country'):
                country = form.get('country')

            address_id = self.address_repository.insert_if_not_exists(country, city)
            if device.address_id != address_id:
                device.address_id = address_id

            print(device)
            self.device_repository.update_device(device)
        elif scenario == 'mapping':
            if form.get('device_id'):
                self.device_repository.update_device_mapping(int(form.get('device_id')), id_entry_to_change)
            else:
                print('Error in service')

    def insert_entry(self, form, scenario):
        if scenario == 'user':
            if form.get('new_username') and form.get('password') and form.get('role'):
                user = models.Users(id=None, username=form.get('new_username'), password=md5_of_string(form.get('password')),
                                    role=int(form.get('role')))
                self.user_repository.insert_with_role(user)
            else:
                return constants.UNSUCCESSFUL
        elif scenario == 'device':
            if form.get('description') and form.get('city') and form.get('country') \
                    and form.get('max_hourly_consumption') and form.get('owner'):
                owner = self.user_repository.find_by_username(form.get('owner'))
                if not owner:
                    return constants.USER_NOT_FOUND
                self._insert_device(user_id=owner.ID, description=form.get('description'), city=form.get('city'),
                                    country=form.get('country'),
                                    max_hourly_consumption=int(form.get('max_hourly_consumption')))
            else:
                return constants.UNSUCCESSFUL
        return constants.INSERTED

    def _insert_device(self, user_id: int, description: str, city: str, country: str, max_hourly_consumption: int):
        address_id = self.address_repository.insert_if_not_exists(country, city)
        device = models.Device(None, description=description,
                               address_id=address_id, max_hourly_consumption=max_hourly_consumption, owner_id=user_id)
        self.device_repository.insert(device)

    def delete_entry(self, form, scenario):
        id = None
        if scenario == 'user' and form.get('current_username'):
            id = self.user_repository.find_by_username(form.get('current_username')).ID
        if scenario == 'device' and form.get('device_id'):
            id = int(form.get('device_id'))

        if scenario == 'user':
            self._delete_user(id)
        if scenario == 'device':
            self._delete_device(id)

    def _delete_user(self, id):
        self.user_repository.delete_user(id, self.device_repository, self.consumption_repository)

    def _delete_device(self, device_id):
        self.device_repository.delete_device(device_id, self.consumption_repository)

    def users_join_devices_join_address(self):
        fields_list = ['username', 'description', 'city', 'country', 'max hourly consumption', 'device_id']
        db_result, devices = self.user_repository.users_join_devices_join_address(), []
        for result in db_result:
            devices.append(result)
        return fields_list, devices

    def get_devices_by_user_id(self, user_id):
        fields_list = ['username', 'description', 'city', 'country', 'max hourly consumption', 'device_id']
        db_result, devices = self.user_repository.users_join_devices_join_address_by_user_id(user_id), []
        for result in db_result:
            devices.append(result)
        return fields_list, devices

    def get_devices_consumption_for_a_user_id(self, user_id, day: int, month: int, year: int):
        """
        Returns a list of tuples (device_id, average_daily_consumption)
        :param year:
        :param month:
        :param day:
        :param user_id:
        :return:
        """

        # get a date string of format YYYY-MM-DD
        day = str(day) if day > 9 else f'0{day}'
        month = str(month) if month > 9 else f'0{month}'
        year = str(year)
        date = f'{year}-{month}-{day}'

        result = self.consumption_repository.get_consumption_for_user_id_and_date(user_id, date)
        for e in result:
            print(str(e))

        return result

    def get_device_by_id(self, id):
        return self.device_repository.find_by_id(int(id))


    def add_address(self, city, country):
        address_id = self.address_repository.insert_if_not_exists(city, country)
        print(address_id)
        return address_id