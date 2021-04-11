FROM python:3.9.4

ENV PYTHONBUFFERED 1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]