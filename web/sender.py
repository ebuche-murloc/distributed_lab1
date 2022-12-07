import os
import pika


def send_massage_to_queue(message: str):
    connection = pika.BlockingConnection(pika.URLParameters(os.environ.get("RABBITMQ_URL")))
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key=os.environ.get("RABBITMQ_QUEUE"), body=message.encode('utf-8'))
    channel.close()
    connection.close()
