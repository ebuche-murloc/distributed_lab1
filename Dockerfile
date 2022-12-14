FROM python:3.10
#
WORKDIR /app

RUN pip install pipenv

COPY Pipfile.lock Pipfile.lock

RUN pipenv sync

EXPOSE 8000

COPY web /app
#копируем код после копирования зависимостей и их синхронизации чтобы при изменении кода всё быро было
CMD pipenv run uvicorn main:app --reload --host 0.0.0.0
#--host 0.0.0.0 делает приложение доступным по локалке

#(distributed_lab1) PS C:\Users\bda20\PycharmProjects\distributed_lab1>cd web переход в подпапку с кодом на питоне где сам app
#(distributed_lab1) PS C:\Users\bda20\PycharmProjects\distributed_lab1\web> uvicorn main:app --reload запускаем так чтобы при каждом изменении кода приложение перезапускалось
#(distributed_lab1) PS C:\Users\bda20\PycharmProjects\distributed_lab1\web> cd .. двигаемся на уровень вверх
#(distributed_lab1) PS C:\Users\bda20\PycharmProjects\distributed_lab1> docker build . делаем образ -t (тото-тото) называем контейнер
#(distributed_lab1) PS C:\Users\bda20\PycharmProjects\distributed_lab1> docker ps показывает запущенные контейнеры
#(distributed_lab1) PS C:\Users\bda20\PycharmProjects\distributed_lab1> docker run -p 8080:8000 distributed1  запускаем контейнер слева порт местный справа контейнера