#!/bin/bash

# Upgrade pip and install packages to persistent location
/tmp/oryx/platforms/python/*/bin/python -m pip install --upgrade pip
/tmp/oryx/platforms/python/*/bin/python -m pip install -r requirements.txt --target /home/site/wwwroot/packages

# Set PYTHONPATH to include packages directory
export PYTHONPATH="/home/site/wwwroot/packages:$PYTHONPATH"

# Start the Django application
cd /home/site/wwwroot
gunicorn dmduproject.wsgi --bind 0.0.0.0:8000
