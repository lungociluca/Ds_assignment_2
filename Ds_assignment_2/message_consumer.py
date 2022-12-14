#!/usr/bin/env python
import pika, sys, os, json, time, copy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import asyncio
import websockets
import threading

ip_backend = ''
path_ip_file = os.path.join(os.path.dirname(__file__), 'backend_ip.txt')
with open(path_ip_file) as fin:
    ip_backend = fin.read()
    print('File ', path_ip_file, ip_backend)

class MyThread(threading.Thread):
    def __init__(self, readings, app, db):
        threading.Thread.__init__(self)
        self.readings = readings
        self.app = app
        self.db = db

    def run(self):
        self.post_readings()

    async def test(self, message):
        async with websockets.connect('ws://%s:5000/echo' % ip_backend) as websocket:
            await websocket.send(str(message))
            response = await websocket.recv()
            print(response)

    def send_to_dabase(self, average):
        for key in average:
            with self.app.app_context():
                dt_object = datetime.fromtimestamp(time.time())
                sql = "INSERT INTO consumption values (%d, '%s', %f)" % (int(key), dt_object, average[key])
                self.db.engine.execute(sql)

                sql = f"SELECT max_hourly_consumption FROM devices WHERE id = {int(key)}"
                result = self.db.engine.execute(sql)

                for max_hourly_consumption in result:
                    print(max_hourly_consumption)
                    if max_hourly_consumption[0] < average[key] or True:
                        #send notification
                        asyncio.new_event_loop().run_until_complete(self.test(f'{key}  {dt_object}'))


    def post_readings(self):
        print("Post")

        measurements = {}
        measurements_count = {}
        average = {}
        for reading in self.readings:
            measurements[reading["device_id"]] = measurements.get(reading["device_id"], 0.0) + float(reading["measurement_value"])
            measurements_count[reading["device_id"]] = measurements_count.get(reading["device_id"], 0) + 1
        
        for key in measurements:
            average[key] = measurements[key] / measurements_count[key]
        
        print(average)
        self.send_to_dabase(average)







class Consumer(object):
    readings = None
    saved_timestamp = None
    app = None
    db = None

    def __init__(self) -> None:
        self.readings = []
        self.saved_timestamp = time.time()

        self.app = Flask(__name__)

        self.app.config.update(
            SECRET_KEY='4681188652',
            SQLALCHEMY_DATABASE_URI='postgresql://postgres:4681188652@10.5.0.5:5432/postgres',
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )
        self.db = SQLAlchemy(self.app)


    def callback(self, ch, method, properties, body):
        dictionary = json.loads(body)
        print(" [x] Received %s" % dictionary)
        self.readings.append(dictionary)

        current_time = time.time()
        if current_time - self.saved_timestamp >= 6:
            thread = MyThread(copy.copy(self.readings), self.app, self.db)
            thread.start()
            self.readings = []
            self.saved_timestamp = current_time
        

    def main(self):
        os.environ['CLOUDAMQP_URL'] = 'amqp://iyormxij:pmedFdFuNNyR_kNkCQ3vh9034hy1PcYG@rat.rmq2.cloudamqp.com/iyormxij'
        url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue='hello')

        channel.basic_consume(queue='hello', on_message_callback=self.callback, auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')

        while True:
            try:
                channel.start_consuming()
            except:
                print('Timeout')
                time.sleep(2)

    
if __name__ == '__main__':
    print('main')
    obj = Consumer()
    obj.main()