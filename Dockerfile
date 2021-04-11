FROM python:3.9.4

ENV PYTHONBUFFERED 1

COPY requirements/main.txt /requirements/main.txt
RUN pip install -r /requirements/main.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]