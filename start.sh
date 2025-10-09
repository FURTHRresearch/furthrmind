#!/bin/sh

echo 'Starting DB checks'
# for digital ocean app deployment
echo "$MONGODB_CERT" > mongodb.ca.crt
pipenv run flask s3-cors
pipenv run flask db-migrate

pipenv run gunicorn app:app
