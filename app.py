import flask
from flask import Flask

import tenjin
import click
from tenjin.cache import Cache
from tenjin.tasks.rq_task import create_task

import json

app = Flask(__name__, instance_relative_config=True)
tenjin.create_app(app=app)
with app.app_context():
    from tenjin import web
    app.register_blueprint(web.bp)

    from tenjin.web import auth
    app.register_blueprint(auth.bp)

    from tenjin import api2
    app.register_blueprint(api2.bp, url_prefix="/api2")
    
    with open("tenjin/api2/openapi.yml", "w") as f:
        from tenjin.api2.spec import spec
        from tenjin.api2.resources.project import get, get_all, post, delete
        spec.path(view=get)
        spec.path(view=get_all)
        spec.path(view=post)
        spec.path(view=delete)
        f.write(spec.to_yaml())
    


@app.before_request
def check_maintenance_mode():
    from tenjin.cache import Cache
    cache = Cache.get_cache()

    @cache.cached(timeout=10)
    def _check_maintenance_mode():
        maintenance_mode = get_maintenance_mode()
        if maintenance_mode:
            flask.abort(503)
        return True
    _check_maintenance_mode()


def get_maintenance_mode():
    if app.config.get('MAINTENANCE_MODE'):
        return True
    if app.config.get("REDIS_QUEUE_ENABLED"):
        cache = Cache.get_cache()
        if cache.get("MaintenanceMode") == 1:
            return True
    return False


def enable_maintenance_mode():
    if app.config.get("REDIS_QUEUE_ENABLED"):
        cache = Cache.get_cache()
        cache.set("MaintenanceMode", 1, timeout=0)
        # set_to_redis("MaintenanceMode", 1)
    else:
        app.config["MAINTENANCE_MODE"] = True

@click.command("enable-maintenance-mode")
def enable_maintenance_mode_click():
    enable_maintenance_mode()
    print(f"Maintenance mode is enabled: {get_maintenance_mode()}")

def disable_maintenance_mode():
    if app.config.get("REDIS_QUEUE_ENABLED"):
        cache = Cache.get_cache()
        cache.set("MaintenanceMode", 0, timeout=0)
    else:
        app.config["MAINTENANCE_MODE"] = False

@click.command("disable-maintenance-mode")
def disable_maintenance_mode_click():
    disable_maintenance_mode()
    print(f"Maintenance mode is enabled: {get_maintenance_mode()}")

app.cli.add_command(enable_maintenance_mode_click)
app.cli.add_command(disable_maintenance_mode_click)

@app.route('/test-glitchtip')
def trigger_error():
    create_task(trigger_error_queue)
    division_by_zero = 1 / 0
    return division_by_zero

def trigger_error_queue():
    division_by_zero = 1 / 0
    return division_by_zero
