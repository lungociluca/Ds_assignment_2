UNSUCCESSFUL = 0
ADMIN = 1
USER = 2
NOT_ALLOWED_INPUT = 3
INSERTED = 4
USER_NOT_FOUND = 5

index_device = 5

month_int_to_string = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

month_string_to_int = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

FORMS = {
    'user': ['user_id', 'username', 'password', 'role'],
    'device': ['device_id', 'description', 'address_id', 'max_hourly_consumption'],
    'mapping': ['user_id', 'device_id']
}

INTEGERS = ['user_id', 'device_id', 'role', 'address_id', 'max_hourly_consumption']
