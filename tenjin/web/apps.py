
import json

import flask
from requests import get
from tenjin.web.auth import login_required

bp = flask.Blueprint('webapps', __name__)


def get_installed_apps():
    cfg = flask.current_app.config['ENABLED_APPS']
    if not cfg:
        return []
    apps = cfg.split(',')
    return apps


def get_app_data():
    apps = get_installed_apps()
    app_data = []
    for url in apps:
        data = None
        try:
            data = get(url + '/furthr-app.json').json()
        except:
            pass
        if not data:
            try:
                data = get(url + "/_/api/app-info")
                data = data.json()
            except:
                pass
        if not data:
            continue
        app = {"url": url}
        app['name'] = data.get('name', '')
        app['description'] = data.get('description', '')
        app['author'] = data.get('author', '')
        app['type'] = data.get('type', '')
        app['version'] = data.get('version', '')
        app_data.append(app)
    return app_data


@bp.route('/projects/<projectId>/apps', methods=['GET'])
@login_required
def get_apps(projectId):
    apps = get_app_data()
    return json.dumps(apps)

@bp.route('/webapp-callback', methods=['GET'])
@login_required
def get_callback():
    webapp_callback = flask.current_app.config.get('WEBAPP_CALLBACK_URL')
    if webapp_callback:
        return webapp_callback
    callback_url = flask.current_app.config.get('CALLBACK_URL')
    if callback_url:
        return callback_url
    root_url = flask.current_app.config.get('ROOT_URL')
    return root_url




# Not in use
# @bp.route('/web/projects/<projectId>/apps/<app>/content/<path:path>', methods=['GET'])
# def file(projectId, app, path):
#     apps = get_installed_apps()
#     res = get(apps.get(app)['url'] + '/' + path)
#     return flask.Response(res.content, mimetype=res.headers['Content-Type'])
