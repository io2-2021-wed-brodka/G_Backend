# to rebuild and run docker image
# $ docker build . -t salty-bikes
# $ docker run -tp 8000:8000 salty-bikes

FROM python:3.9.4

ENV PYTHONBUFFERED 1
ENV DEBUG 0

COPY requirements/main.txt /requirements/main.txt
RUN pip install -r /requirements/main.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]