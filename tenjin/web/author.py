import bson
import flask
import json

from tenjin.authentication import Authentication
from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete

from tenjin.database.db import get_db
from .auth import login_required


bp = flask.Blueprint('webauthor', __name__)



@bp.route("/author",methods=["GET"])
@login_required
def get_author():
	authors = get_db().find("Author",{})
	users = get_db().find("User",{})
	#for author in authors:
		#for user in users:
			# if author["UserID"] == user["_id"]:
			# 	name = ""
			# 	name += user["FirstName"] +" " if user.get("FirstName","") else ""
			# 	name += user["LastName"] if user.get("LastName","") else ""
			# 	author["Name"] = name
	return json.dumps([{"_id":str(a["_id"]),"name":a["Name"], "institution": a["Institution"]} for a in authors])


@bp.route("/author/<aid>",methods=["GET"])
@login_required
def get_author_name(aid):
	author = get_db().find_one("Author",{"_id":bson.ObjectId(aid)})
	if author["UserID"]:
		user = get_db().find_one("User",{"_id":author["UserID"]})
		if user:
			name = ""
			name += user["FirstName"] +" " if user.get("FirstName","") else ""
			name += user["LastName"] if user.get("LastName","") else ""
			author["Name"] = name
	return author["Name"]

@bp.route("/fielddata/setauthor",methods=["POST"])
@login_required
def set_author_fielddata():
	data = flask.request.get_json()
	fieldid = bson.ObjectId(data["fielddata"])
	authorid = bson.ObjectId(data["author"])
	Update.update("FieldData","AuthorID",authorid,fieldid, get_db(), flask.g.user)

	return "all good"



@bp.route("/author",methods=["POST"])
@login_required
def create_author():
	data = flask.request.get_json()
	potential_keys = ["UserID","Name","Institution"]
	parameter = {key:data[key.lower()] for key in potential_keys if key.lower() in data}
	result = Create.create("Author",parameter,get_db(),flask.g.user)
	return "all good"

@bp.route("/author/<resourceid>",methods=["POST"])
@login_required
def update_author(resourceid):
	data = flask.request.get_json()
	if not Authentication.hasAccess("Author", "write", bson.ObjectId(resourceid), flask.g.user, get_db()):
		flask.abort(403)
	potential_keys = ["UserID","Name","Institution"]
	parameter = {key:data[key.lower()] for key in potential_keys if key.lower() in data}
	for key,value in parameter.items():
		print(key, value)
		Update.update("Author",key,value,bson.ObjectId(resourceid),get_db(),flask.g.user)
	return "all good"

@bp.route("/author/<resourceid>/<newauthor>",methods=["DELETE"])
@login_required
def delete_author(resourceid, newauthor):

	#todo replace author id with successor
	if not Authentication.hasAccess("Author", "delete", bson.ObjectId(resourceid), flask.g.user, get_db()):
		flask.abort(403)
	result = Delete.delete("Author",bson.ObjectId(resourceid),get_db(),flask.g.user)
	return "all good"



