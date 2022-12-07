import json
import os
import sys
from typing import Optional

import pika
import requests
import redis

QUEUE_NAME = 'links'
cache = redis.Redis(host=os.environ["CACHE_HOST"], decode_responses=True) #решение проблемы с 'b200' статусом, байтовая строка возвращалась, decode_responses=True переводит сразу в utf-8
                                                                          #если там реально какие-то бинарные веши хранятся, то лучше после get запроса из redis сразу декодировать

def fetch_status_from_internet(url) -> int:
    response = requests.get(url, timeout=10)
    status = response.status_code
    print(str(status) + " fetch_status_from_internet", flush=True)
    return status

def get_from_cache(cache_key: str) -> Optional[int]:
    value = cache.get(cache_key)
    print(str(value) + " get_from_cache", flush=True)
    return value

def set_cache(cache_key: str, status_code: int) -> None:
    cache.set(cache_key, status_code, ex=120)

def get_status(url) -> int:
    cache_key = f"url-{url}"
    status_code = get_from_cache(cache_key)

    if status_code is None:
        status_code = fetch_status_from_internet(url)
        set_cache(cache_key, status_code)
    print(str(status_code) + " get_status", flush=True)
    return status_code

def handle_message(ch, method, properties, body):
    link_json = json.loads(body.decode("utf-8"))

    status = get_status(link_json["url"])
    print(str(status) + " handle_message", flush=True)
    web_url = f'{os.environ["WEB_BASE_URL"]}/links/{link_json["id"]}'
    web_request_body = {
        'status' : str(status),
    }
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
