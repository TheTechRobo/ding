FROM python:3.11

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["sanic","server","--host=0.0.0.0","--port=8000","--single-process"]
