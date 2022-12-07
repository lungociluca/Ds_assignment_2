# publish.py
import pika, os, time, csv, sys, json

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
os.environ['CLOUDAMQP_URL'] = 'amqp://iyormxij:pmedFdFuNNyR_kNkCQ3vh9034hy1PcYG@rat.rmq2.cloudamqp.com/iyormxij'
url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel
channel.queue_declare(queue='hello') # Declare a queue



current_time = time.time()
device_id = int(sys.argv[1])
readings = []
with open('sensor.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\n')
    for value in csv_reader:
        as_json = json.dumps({ "timestamp": current_time,
                        "device_id": device_id,
                        "measurement_value": value[0]})
        readings.append(as_json)
        current_time += 10


message_number = 0

while True:

    time.sleep(1)

    print(readings[message_number])
    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body=readings[message_number])
    message_number += 1

    if message_number == len(readings):
        break

connection.close()