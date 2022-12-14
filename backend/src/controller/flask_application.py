import json

from flask import Flask, url_for, session, flash, redirect
from flask import request, render_template
from flask_sqlalchemy import SQLAlchemy
import websockets
import asyncio
import threading
import logging 

from flask_sock import Sock

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
import service.service as service
import model.models as model
import constants.constants as constants

app = Flask(__name__)

app.config.update(
    SECRET_KEY='4681188652',
    SQLALCHEMY_DATABASE_URI='postgresql://postgres:4681188652@10.5.0.5:5432/postgres',
    # SQLALCHEMY_DATABASE_URI='postgresql://postgres:root@localhost/my_db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)
service_obj = service.Service(db)
sock = Sock(app)
lock = threading.Lock()

path_warnings = os.path.join(os.path.dirname(__file__), 'warnings')

users_to_notify = set()


@app.route('/get_status/<int:user_id>')
def get_status(user_id):

    to_return = 'Do nothing'
    lock.acquire()
    if user_id in users_to_notify:
        to_return = 'Refresh'
    lock.release()
    return to_return


@sock.route('/echo')
def echo(sock):
    data = sock.receive()
    sock.send(data)
    data = data.split()
    device_id, date = data[0], data[1]
    user_id = service_obj.get_device_by_id(device_id).owner_id
    lock.acquire()
    with open(os.path.join(path_warnings, f'{user_id}_{device_id}'), 'w') as fout:
        fout.write(date)
    global users_to_notify
    users_to_notify.add(int(user_id))
    lock.release()


def check_if_admin():
    if 'id' not in session:
        return False
    user = service_obj.get_user_by_id(session['id'])
    if user.role != 1:
        return False
    return True


@app.route('/', methods=['GET'])
def welcome():
    return render_template('welcome_page.html')


@app.route('/login/<int:sign_case>', methods=['GET', 'POST'])
def login(sign_case):
    if request.method == 'GET':
        return render_template('login.html', case=sign_case, flask=Flask)
    else:
        form = request.form
        result = None

        if sign_case == 0:
            # sign up
            result = service_obj.register(form.get('username'), form.get('psw'), form.get('psw-repeat'))
        else:
            # sign in
            result = service_obj.login(form.get('username'), form.get('psw'))

        # unsuccessful cases
        if result == constants.UNSUCCESSFUL:
            return render_template('login.html', case=sign_case, message='Wrong username or password.')
        if result == constants.NOT_ALLOWED_INPUT:
            return render_template('login.html', case=sign_case,
                                   message='Some of the characters used in username field are not allowed.')

        # successful cases
        session['id'] = service_obj.find_by_username(form.get('username')).ID
        if result == constants.ADMIN:
            return render_template('admin_main.html')
        if result == constants.USER:
            return user_page(None, None)


@app.route('/admin_display', methods=['GET'])
def admin_display():
    return render_template('admin_main.html')


@app.route('/admin<string:scenario>', methods=['POST'])
def admin_page(scenario):
    if not check_if_admin():
        return render_template('welcome_page.html')

    action = 'update'
    if scenario == 'user' and request.form.get('option_user') != 'update':
        action = 'delete' if request.form.get('option_user') == 'delete' else 'create'
    elif scenario == 'device' and request.form.get('option_devices') != 'update':
        action = 'delete' if request.form.get('option_devices') == 'delete' else 'create'
    elif scenario == 'mapping':
        # mappings can only be updates
        pass

    message = ''
    if action == 'delete':
        service_obj.delete_entry(request.form, scenario)
    elif action == 'update':
        service_obj.handle_admin_post(request.form, scenario)
    elif action == 'create':
        status = service_obj.insert_entry(request.form, scenario)
        if status == constants.UNSUCCESSFUL:
            message = 'Some fields were left empty for insert operation.'
        elif status == constants.USER_NOT_FOUND:
            message = 'The username you entered was not found.'
    return render_template('admin_main.html', message=message)


@app.route('/showUsers', methods=['GET'])
def get_users():
    if not check_if_admin():
        return render_template('welcome_page.html')
    fields, users_list = service_obj.get_users_as_tuple_list()
    if len(users_list) == 0:
        return '<p>There are no users</p>'
    return render_template('display_table.html', fields=fields, len_fields=len(fields), content=users_list,
                           content_len=len(users_list))


@app.route('/showDevices', methods=['GET'])
def get_devices():
    if not check_if_admin():
        return render_template('welcome_page.html')
    fields, device_list = service_obj.users_join_devices_join_address()
    if len(device_list) == 0:
        return '<p>There are no devices.</p>'
    return render_template('display_table.html', fields=fields, len_fields=len(fields), content=device_list,
                           content_len=len(device_list))


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/main_page/<int:month_int>/<int:year>', methods=['GET'])
def user_page(month_int, year):
    if 'id' not in session:
        return 'Must be logged in.'
    user = service_obj.get_user_by_id(session['id'])
    fields, devices = service_obj.get_devices_by_user_id(user.ID)

    if month_int is None or year is None:
        month_int, year = service.get_current_date()

    month = constants.month_int_to_string[month_int]
    days = service_obj.get_days_in_month(year, month)
    if days is None:
        return '<p>No data for this month</p>'
    print(days, month, year)

    warning = ''

    lock.acquire()
    files = os.listdir(path_warnings)

    global users_to_notify
    if session['id'] in users_to_notify:
        for file in files:
            if file.startswith(str(session['id'])):
                with open(os.path.join(path_warnings, file)) as fin:
                    device_id = file.split('_')[1]
                    warning = f'Device {device_id} has passed the allowed hourly consumption at {fin.read()}'

        # if the flag for our user was set, remove it, will not show the warning again if user refreshes
        users_to_notify.remove(session['id'])
    lock.release()
    return render_template('user_main.html',
                           days=days, month=month, year=year, month_int=month_int,
                           username=user.username, index_device_id=constants.index_device,
                           len_fields=len(fields), fields=fields, content_len=len(devices),
                           content=devices, warning=warning, user_id=session['id'])


@app.route('/chart/<int:day>/<string:month>/<int:year>', methods=['GET'])
def show_chart(day, month, year):
    if 'id' not in session:
        return 'Must be logged in.'
    devices = service_obj.get_devices_consumption_for_a_user_id(session['id'], day,
                                                                constants.month_string_to_int[month], year)
    data, labels = [], []
    for device_id, consumption in devices:
        labels.append(f'Device {device_id}')
        data.append(consumption)
    print(data, labels)

    return render_template('chart.html', day=day, month=month, year=year,
                           month_int=constants.month_string_to_int[month],
                           my_data=json.dumps(data), labels=json.dumps(labels))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
