import pika
from backoffice.settings import QUEUE_URL, QUEUE_USER, QUEUE_PASSWORD, QUEUE_PORT, QUEUE_CONTEXT_ROOT

def send_message(queue_name, message):
    credentials = pika.PlainCredentials(QUEUE_USER, QUEUE_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(QUEUE_URL, QUEUE_PORT, QUEUE_CONTEXT_ROOT, credentials))
    channel = connection.channel()
    channel.basic_publish(exchange=queue_name,
                          routing_key='',
                          body=message)
    connection.close()
