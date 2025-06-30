#!/bin/bash
echo "BUILD START"
python3.9 -m venv python3-virtualenv
source python3-virtualenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput --clear
echo "BUILD END"
