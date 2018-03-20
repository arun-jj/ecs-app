FROM ubuntu:16.04

EXPOSE 5000

RUN apt-get update && apt-get install -y supervisor python3-pip

RUN pip3 install flask>=0.10.1
RUN pip3 install uwsgi

RUN mkdir /app && mkdir -p /var/log/uwsgi && mkdir -p /var/www/flask

COPY src /app
COPY settings/uwsgi.ini /usr/local/etc/uwsgi/uwsgi.ini
COPY settings/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /app

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
