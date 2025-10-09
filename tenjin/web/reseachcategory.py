import bson
import flask
import json

from tenjin.authentication import Authentication
from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete

from tenjin.database.db import get_db
from .auth import login_required


bp = flask.Blueprint('webreseachcategories', __name__)



@bp.route("/projects/<projectid>/categories",methods=["GET"])
@login_required
def get_category(projectid):
	if not Authentication.hasAccess("Project", "read", bson.ObjectId(projectid), flask.g.user, get_db()):
		flask.abort(403)
	categories = get_db().find("ResearchCategory",{"ProjectID":bson.ObjectId(projectid)})
	required_keys = ["Name","Description","ProjectID"]
	a = [{key.lower(): str(c[key]) for key in required_keys} for c in categories]
	for i in range(len(a)):
		res = a[i]
		res['categoryid'] = str(categories[i]['_id'])

	return json.dumps(a)


@bp.route("/categories",methods=["POST"])
@login_required
def create_category():
	data = flask.request.get_json()
	potential_keys = ["Name","Description","ProjectID"]
	parameter = {key:data[key.lower()] for key in potential_keys if key.lower() in data}
	result = Create.create("ResearchCategory",parameter,get_db(),flask.g.user)
	return "All good"

@bp.route("/categories/<resourceid>",methods=["POST"])
@login_required
def update_category(resourceid):
	data = flask.request.get_json()
	if not Authentication.hasAccess("ResearchCategory", "write", bson.ObjectId(resourceid), flask.g.user, get_db()):
		flask.abort(403)
	potential_keys = ["Name","Description","ProjectID"]
	parameter = {key:data[key.lower()] for key in potential_keys if key.lower() in data}
	for key,value in parameter.items():
		Update.update("ResearchCategory",key,value,bson.ObjectId(resourceid),get_db(),flask.g.user)
	return "all good"

@bp.route("/categories/<resourceid>",methods=["DELETE"])
@login_required
def delete_category(resourceid):
	if not Authentication.hasAccess("ResearchCategory", "delete", bson.ObjectId(resourceid), flask.g.user, get_db()):
		flask.abort(403)
	result = Delete.delete("ResearchCategory",bson.ObjectId(resourceid),get_db(),flask.g.user)
	return "all good"



