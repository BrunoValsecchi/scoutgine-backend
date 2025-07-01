#!/bin/bash
echo "BUILD START"
echo "Python version: $(python3 --version)"
pip3 install --upgrade pip
pip3 install -r requirements.txt
mkdir -p staticfiles_build
python3 manage.py collectstatic --noinput --clear
echo "BUILD END"
