import json
import os
import sys

import pika
import requests

QUEUE_NAME = 'links'


def handle_message(ch, method, properties, body):
    #{"id":1,"url": "https://brbrbr.ru"}
    #decode json
    link_json = json.loads(body.decode("utf-8"))
    #2. fetch url
    response = requests.get(link_json["url"], timeout=10)
    status = response.status_code
    print(link_json["url"])
    web_url = f'{os.environ["WEB_BASE_URL"]}/links/{link_json["id"]}'
    web_request_body = {
        'status' : str(status),
    }
    print(status)
    web_response = requests.put(web_url, json=web_request_body, timeout=10)
    web_response.raise_for_status()

def main():
    connection = pika.BlockingConnection(pika.URLParameters(os.environ["RABBITMQ_URL"]))
    #amqp - протокол передачи сообшений, rabbit - имя хоста указанное в docker-compose
    channel = connection.channel()


    channel.queue_declare(queue=QUEUE_NAME) #объявляем очередь

    channel.basic_consume(queue=QUEUE_NAME,
                          auto_ack=True, #при получении сообщение сразу удаляется независимо обработано оно или нет
                          on_message_callback=handle_message) #при получении сообщения в эту очередь вызывается этот callback

    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
