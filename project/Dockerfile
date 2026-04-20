FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/project

ENV DJANGO_SETTINGS_MODULE=project.settings

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "project.wsgi", "--bind", "0.0.0.0:8000"]