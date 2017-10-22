#!/bin/bash
kill -9 `ps -ef | grep manage.py | awk '{print $2}'`
/home/ubuntu/anaconda3/bin/python3 /var/www/django_hdm/manage.py runserver 0.0.0.0:8000 > /home/ubuntu/log_django/django.log&
