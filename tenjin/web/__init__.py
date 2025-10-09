import io
import os

import flask
import qrcode
from flask import Blueprint
from flask_cors import cross_origin

from . import (admin, apps, auth, copy_template, dataviews, fields, files, groups,
               ldap, notebooks, onlyoffice, projects, rawdata,
               researchitems, s3upload, tusupload, units, user, reseachcategory,
               webdatacalc, author, filter, copy_clipboard)
from .auth import login_required
from .helper.furthrHelper import ensureAccess

bp = Blueprint('web', __name__, template_folder='templates',
               static_folder='static', static_url_path='/web/static')

bp.register_blueprint(notebooks.bp, url_prefix="/web", name="notebook_web")
bp.register_blueprint(notebooks.bp, name="notebook_root")
bp.register_blueprint(auth.bp, url_prefix="/web", name="auth_web")
bp.register_blueprint(auth.bp, name="auth_root")
bp.register_blueprint(projects.bp, url_prefix="/web", name="projects_web")
bp.register_blueprint(projects.bp, name="projects_root")
bp.register_blueprint(groups.bp, url_prefix="/web", name="groups_web")
bp.register_blueprint(groups.bp, name="groups_root")
bp.register_blueprint(files.bp, url_prefix="/web", name="files_web")
bp.register_blueprint(files.bp, name="files_root")
bp.register_blueprint(researchitems.bp, url_prefix="/web", name="researchitems_web")
bp.register_blueprint(researchitems.bp, name="researchitems_root")
bp.register_blueprint(reseachcategory.bp, url_prefix="/web", name="reseachcategory_web")
bp.register_blueprint(reseachcategory.bp, name="reseachcategory_root")
bp.register_blueprint(author.bp,url_prefix="/web", name="author_web")
bp.register_blueprint(author.bp, name="author_root")
bp.register_blueprint(rawdata.bp, url_prefix="/web", name="raw_data_web")
bp.register_blueprint(rawdata.bp, name="raw_data_root")
bp.register_blueprint(fields.bp, url_prefix="/web", name="fields_web")
bp.register_blueprint(fields.bp, name="fields_root")
bp.register_blueprint(tusupload.bp, url_prefix="/web", name="tusupload_web")
bp.register_blueprint(tusupload.bp, name="tusupload_root")
bp.register_blueprint(webdatacalc.bp, url_prefix="/web", name="webdatacalc_web")
bp.register_blueprint(webdatacalc.bp, name="webdatacalc_root")
bp.register_blueprint(units.bp, url_prefix="/web", name="units_web")
bp.register_blueprint(units.bp, name="units_root")
bp.register_blueprint(s3upload.bp, url_prefix="/web", name="s3_web")
bp.register_blueprint(s3upload.bp, name="s3_root")

bp.register_blueprint(ldap.bp, url_prefix="/web")
bp.register_blueprint(user.bp, url_prefix="/web", name="user_web")
bp.register_blueprint(user.bp, name="user_root")
bp.register_blueprint(admin.bp, url_prefix="/web", name="admin_web")
bp.register_blueprint(admin.bp, name="admin_root")
bp.register_blueprint(dataviews.bp, url_prefix="/web", name="dataviews_web")
bp.register_blueprint(dataviews.bp, name="dataviews_root")
bp.register_blueprint(onlyoffice.bp, url_prefix="/web", name="onlyoffice_web")
bp.register_blueprint(onlyoffice.bp, name="onlyoffice_root")
bp.register_blueprint(copy_template.bp, url_prefix="/web", name="copy_template_web")
bp.register_blueprint(copy_template.bp, name="copy_template_root")
bp.register_blueprint(apps.bp, url_prefix="/web", name="apps_web")
bp.register_blueprint(apps.bp, name="apps_root")
bp.register_blueprint(filter.bp, url_prefix="/web", name="filter_web")
bp.register_blueprint(copy_clipboard.bp, url_prefix="/web", name="copy_clipboard")


@bp.route('/<path:path>', methods=['GET', "POST"])
def catch_all(path):
    # if "api2" in path and path[-1] == "/":
    #     path = f"/{path[:-1]}"
    #     return flask.redirect(path)
    # else:
    return flask.send_from_directory('tenjin/web/static', 'react/index.html')


@bp.route('/ldap-signup')
@bp.route('/chemical')
@bp.route('/projects/<id>/apps')
@bp.route('/inventory/batches/<id>')
@bp.route('/inventory')
@bp.route('/inventory/chemicals/<id>/batches')
@login_required
def project(id=None, page=None):
    return flask.send_from_directory('tenjin/web/static', 'react/index.html')


@bp.route('/')
@bp.route('/projects')
@login_required
def projects_preload():

    index = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                         'static', 'react', 'index.html')
    with open(index) as f:
        html = f.read()
    html = html.replace('</title>', '</title>' +
                        '<link rel="preload" href="/web/projects" as="fetch" crossorigin="anonymous" />')
    return html


@bp.route('/projects/<id>/data')
@login_required
def project_preload(id):
    index = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                         'static', 'react', 'index.html')
    with open(index) as f:
        html = f.read()
    # html = html.replace('</title>', '</title>' +
    #                     '<link rel="preload" href="/projects/' + id + '/groupindex" as="fetch" crossorigin="anonymous" />')
    return html



@bp.route('/web/allowed-signup-domain')
@bp.route('/allowed-signup-domain')
@cross_origin()
def allowed_signup_domain():
    return flask.current_app.config['ALLOWED_SIGNUP_DOMAIN']



@bp.route('/web/qrcode')
@login_required
def get_qrcode():
    img = qrcode.make(flask.request.args.get('data', ''))
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return flask.send_file(img_io, mimetype='image/png', as_attachment=True, attachment_filename='qrcode.png')


@bp.route("/web/current-version", methods=["GET"])
def current_version():
    return flask.current_app.config["SERVER_VERSION"]

@bp.route("/web/welcome-username-text", methods=["GET"])
def welcome_username_text():
    return flask.current_app.config["WELCOME_USERNAME_TEXT"]

@bp.route("/web/signup-text", methods=["GET"])
def signup_text():
    return flask.current_app.config["SIGNUP_TEXT"]
