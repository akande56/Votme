#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip

pip install -r requirements/production.txt

python manage.py collectstatic --no-input
python manage.py migrate
