FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./app /app
