# FURTHRmind 
FURTHRmind is a software tool for research and measurement data management (https://furthrmind.com)[https://furthrmind.com]. It is based on a flask server, in production served by gunicorn WSGI. As backend it uses a mongodb and is powered by the mongoengine framework.  


## Installation

Optionally add custom config in instance/config.py.
Install python enviroment with `pipenv install`

## Run for development

```
FLASK_ENV=development pipenv run flask run
npm start --prefix frontend
```


For local development of webdatacalc and spreadsheet editor, a localtunnel is recommended. 
```
npm install -g localtunnel
lt --port 5000 -s yourname
lt -p 5000 -s furthr --local-host "127.0.0.1"
```
Exposes the local port 5000 at https://yourname.loca.lt. See localtunnel.me.

## Docker
```
docker-compose build
docker-compose up

docker build . -f Dockerfile -t furthrresearch/furthrmind-server-v1 
docker push furthrresearch/furthrmind-server-v1      
```
An example docker file can be found under docker/docker-compose.yml


## Nginx configuration

/etc/nginx/vhost.d/tenjin.conf
```
server {
        listen 80;
        server_name furthr.*;

        location / {
                proxy_pass http://127.0.0.1:1337;
        }
}
```

HTTPS config: https://certbot.eff.org/
```
sudo certbot --nginx
```


## Command line interface

to run a click command:
```
pipenv run flask "command"
```

The following commands are available:
```
pipenv run flask db-migrate
pipenv run flask db-layout-check
pipenv run flask correct-si-values
pipenv run flask s3-cors
pipenv run flask migrate-files
pipenv run flask migrate-files-from-other-s3
pipenv run flask empty-queue
pipenv run flask check-missing-db-keys
pipenv run flask send-test-mail
```