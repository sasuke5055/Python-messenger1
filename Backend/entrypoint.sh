#!/bin/sh

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuserwithpassword \
        --username admin \
        --password admin \
        --email admin@example.org \
        --preserve
