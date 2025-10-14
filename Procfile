web: python manage.py migrate && gunicorn Ztionsec.wsgi:application --log-file -
worker: python manage.py rqworker default
release: python manage.py migrate
