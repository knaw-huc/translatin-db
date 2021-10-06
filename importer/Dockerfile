FROM python:3.9-slim-buster

WORKDIR /code

RUN apt-get update && apt-get install -y \
    postgresql-client

COPY requirements.txt .
COPY config.ini .
COPY db.sh .

RUN pip install -r requirements.txt

COPY src/ .

CMD [ "python", "./import.py"]
