FROM python:2.7-onbuild
EXPOSE 8000
CMD gunicorn -b 0.0.0.0:8000 main:app
