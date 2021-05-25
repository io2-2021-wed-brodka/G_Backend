# to rebuild and run docker image
# $ docker build . -t salty-bikes
# $ docker run -tp 8080:8080 salty-bikes

FROM python:3.9.4

ENV PYTHONBUFFERED 1
ENV SECRET_KEY development-secret-key
ENV DEBUG 0

COPY requirements/main.txt /requirements/main.txt
RUN pip install -r /requirements/main.txt

COPY . .

RUN python manage.py migrate
RUN python manage.py loaddata fixtures/api-tests.json
