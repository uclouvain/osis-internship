import pika
from backoffice.settings import QUEUE_URL, QUEUE_USER, QUEUE_PASSWORD, QUEUE_PORT, QUEUE_CONTEXT_ROOT
import json


def send_message(queue_name, message):
    """
    Send the message in the queue passed in parameter.

    :param queue_name: the name of the queue in which we have to send the JSON message.
    :param message: Must be a dictionnary !
    """
    credentials = pika.PlainCredentials(QUEUE_USER, QUEUE_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(QUEUE_URL, QUEUE_PORT, QUEUE_CONTEXT_ROOT, credentials))
    channel = connection.channel()
    channel.basic_publish(exchange=queue_name,
                          routing_key='',
                          body=json.dumps(message),
                          properties=pika.BasicProperties(content_type='application/json'))
    connection.close()
