#!/bin/sh
echo "$MONGODB_CERT" > mongodb.ca.crt
pipenv run python start_worker.py