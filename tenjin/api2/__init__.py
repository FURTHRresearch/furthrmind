from functools import wraps
from bson import ObjectId
from mongoengine import ValidationError as MongoValidationError
from marshmallow import ValidationError
import flask
from sentry_sdk import capture_exception



from tenjin.database.db import get_db
from tenjin.web.webdatacalc import run_custom_script, set_calculationresults
from tenjin.authentication import Authentication
from tenjin.tasks.rq_task import create_task
from tenjin.logic.copy_template import copy

from tenjin.api2.schema.response_schema import (Response, 
                                                ResponseSchema, ResponseSchemaListValueStr)
from tenjin.api2.resources.project import bp as project_bp
from tenjin.api2.resources.group import bp as group_bp
from tenjin.api2.resources.exp_sample_ri import bp as exp_sample_ri_bp
from tenjin.api2.resources.fielddata import bp as fielddata_bp
from tenjin.api2.resources.field import bp as field_bp
from tenjin.api2.resources.datatable import bp as datatable_bp
from tenjin.api2.resources.column import bp as column_bp
from tenjin.api2.resources.research_category import bp as research_category_bp 
from tenjin.api2.resources.comboboxentry import bp as comboboxentry_bp
from tenjin.api2.resources.copy_item import bp as copy_item_bp
from tenjin.api2.resources.file import bp as file_bp
from tenjin.api2.resources.calculation_result import bp as calculation_result_bp
from tenjin.api2.resources.custom_script import bp as custom_script_bp
from tenjin.api2.resources.send_email import bp as send_email_bp
from tenjin.api2.resources.user import bp as user_bp
from tenjin.api2.resources.user_group import bp as user_group_bp


bp = flask.Blueprint('api2', __name__)

bp.register_blueprint(project_bp, url_prefix='/project')
bp.register_blueprint(project_bp, url_prefix='/projects', name='projects')
bp.register_blueprint(group_bp, url_prefix='/project')
bp.register_blueprint(group_bp, url_prefix='/projects', name='groups')
bp.register_blueprint(exp_sample_ri_bp, url_prefix='/project', name='project-experiment')
bp.register_blueprint(exp_sample_ri_bp, url_prefix='/projects', name='projects-experiment')
bp.register_blueprint(fielddata_bp, url_prefix='/project', name='fielddata-project')
bp.register_blueprint(fielddata_bp, url_prefix='/projects', name='fielddata-projects')
bp.register_blueprint(field_bp, url_prefix='/project', name='field-project')
bp.register_blueprint(field_bp, url_prefix='/projects', name='field-projects')
bp.register_blueprint(datatable_bp, url_prefix='/project', name='datatable-project')
bp.register_blueprint(datatable_bp, url_prefix='/projects', name='datatable-projects')
bp.register_blueprint(column_bp, url_prefix='/project', name='column-project')
bp.register_blueprint(column_bp, url_prefix='/projects', name='column-projects')
bp.register_blueprint(research_category_bp, url_prefix='/project', name='research-category-project')
bp.register_blueprint(research_category_bp, url_prefix='/projects', name='research-category-projects')
bp.register_blueprint(comboboxentry_bp, url_prefix='/project', name='comboboxentry-project')
bp.register_blueprint(comboboxentry_bp, url_prefix='/projects', name='comboboxentry-projects')


bp.register_blueprint(copy_item_bp, name='copy-item')
bp.register_blueprint(file_bp, name='file')
bp.register_blueprint(calculation_result_bp, name='calculation-result')
bp.register_blueprint(custom_script_bp, name='custom-script')
bp.register_blueprint(send_email_bp, name='send-email')
bp.register_blueprint(user_bp, name='user')
bp.register_blueprint(user_group_bp, name='user-group')


@bp.before_request
def authenticate_user():
    if not Authentication.authenticate_user():
        return ResponseSchema().dump(Response(status=False, message="You are not authorized")), 401

@bp.errorhandler(ValidationError)
def handle_marschmallow_error(e):
    print(e)
    return ResponseSchema().dump(Response(status=False, message=str(e))), 400

@bp.errorhandler(MongoValidationError)
def handle_mongoengine_error(e):
    try:
        message = e.errors["__all__"].args[0]
        print(e)
        return ResponseSchema().dump(Response(status=False, message=message)), 400
    except:
        print(e)
        return ResponseSchema().dump(Response(status=False, message=str(e))), 400

@bp.errorhandler(ValueError)
def handle_value_error(e):
    print(e)
    return ResponseSchema().dump(Response(status=False, message=str(e))), 400

@bp.errorhandler(PermissionError)
def handle_permission_error(e):
    print(e)
    return ResponseSchema().dump(Response(status=False, message=str(e))), 403

@bp.errorhandler(Exception)
def handle_generic_error(e):
    """
    Generic error handler for the API. It will return a 500 error with the error message.
    """
    if flask.current_app.config.get("TESTING", False):
        raise e  # In testing mode, raise the exception to see the traceback
    capture_exception(e)
    print(e)
    return ResponseSchema().dump(Response(status=False, message=str(e))), 500

@bp.route('/docs')
def docs():
    return flask.send_from_directory('tenjin/api2/static', 'redoc-static.html')
    

