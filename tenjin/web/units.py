from ast import Delete

import bson
import bson.json_util
import flask

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete
from tenjin.database.db import get_db

from .auth import login_required
from .helper.furthrHelper import ensureAccess
import click
from tenjin.database.unit_definition import getUnitList, getUnitCategory

bp = flask.Blueprint('webunits', __name__)

def init_app(app):
    app.cli.add_command(remove_duplicates)
    app.cli.add_command(add_unit_categories)

@bp.route('/units', methods=['GET'])
@login_required
def web_units():
    projid = flask.request.args.get('project', '')
    db = get_db().db
    selector = {'Predefined': True}
    if projid != '':
        ensureAccess("Project", "read", projid)
        selector = {
            '$or': [{'ProjectID': bson.ObjectId(projid)}, selector]}
    units = db.Unit.find(selector).sort("ShortName", 1)
    categories = list(db.UnitCategory.find())
    unitlist = [{
        "id": str(unit['_id']),
        "Name": unit['ShortName'],
        "editable": not (unit["Predefined"]),
        "category": next((cat['Name'] for cat in categories if (len(unit.get('UnitCategoryIDList', [])) > 0) and cat['_id'] == unit['UnitCategoryIDList'][0]), 'other'),
        "Definition": unit['Definition'],
    } for unit in units]

    return bson.json_util.dumps(unitlist)


@bp.route('/units/<id>', methods=['POST'])
@login_required
def update_unit(id):
    ensureAccess("Unit", "read", id)
    data = flask.request.get_json()
    userId = flask.g.user
    unitId = bson.ObjectId(id)
    if 'name' in data:
        Update.update("Unit", "ShortName",
                      data['name'], unitId, get_db(), userId)
        Update.update("Unit", "LongName",
                      data['name'], unitId, get_db(), userId)
    if 'definition' in data:
        definition = data['definition']
        definition = definition.replace(f'<u>{unitId}</u>', '')
        Update.update("Unit", "Definition",
                      definition, unitId, get_db(), userId)
    return 'all done'


@bp.route('/units/<id>', methods=['DELETE'])
@login_required
def delete_unit(id):
    ensureAccess("Unit", "delete", id)
    userId = flask.g.user
    Delete.delete("Unit", bson.ObjectId(id), get_db(), userId)
    return 'all done'


@bp.route('/projects/<projid>/units', methods=['POST'])
@login_required
def new_unit(projid):
    data = flask.request.get_json()
    userId = flask.g.user
    unitId = Create.create("Unit", {
        "LongName": data['name'],
        "ShortName": data['name'],
        "ProjectID": bson.ObjectId(projid),
        "Definition": data.get('definition', ''),
    }, get_db(), userId)
    ensureAccess("Unit", "write", unitId)

    return {
        'id': str(unitId),
        'Name': data['name'],
        'editable': True,
        'Definition': ''
    }

@click.command('remove-unit-duplicates')
@flask.cli.with_appcontext
def remove_duplicates():
    db = get_db().db
    unitList = getUnitList()
    for unit in unitList:
        found_unit_list = list(db["Unit"].find({"ShortName": unit['ShortName'], "Predefined": True}))
        if len(found_unit_list) > 1:
            first_unit = found_unit_list[0]
            second_unit = found_unit_list[1]
            db["FieldData"].update_many({"UnitID": first_unit["_id"]}, {"$set": {"UnitID": second_unit["_id"]}})
            db["Column"].update_many({"UnitID": first_unit["_id"]}, {"$set": {"UnitID": second_unit["_id"]}})
            db["Unit"].delete_one({"_id": first_unit["_id"]})
            print(unit['ShortName'], "new unit_id", second_unit["_id"], "old_unit_id", first_unit["_id"])
        predefined_unit = db["Unit"].find_one({"ShortName": unit['ShortName'], "Predefined": True})
        not_predefined_unit_list = list(db["Unit"].find({"ShortName": unit['ShortName'], "Predefined": False}))
        not_predefined_unit_list_id = [unit['_id'] for unit in not_predefined_unit_list]
        if not_predefined_unit_list_id:
            print("length of not_predefined_unit_list_id: ", len(not_predefined_unit_list_id), predefined_unit['_id'],
                  predefined_unit["ShortName"])
            db["FieldData"].update_many({"UnitID": {"$in": not_predefined_unit_list_id}}, {"$set": {"UnitID": predefined_unit["_id"]}})
            db["Column"].update_many({"UnitID": {"$in": not_predefined_unit_list_id}}, {"$set": {"UnitID": predefined_unit["_id"]}})
            db["Unit"].delete_many({"_id": {"$in": not_predefined_unit_list_id}})



@click.command('add-unit-categories')
@flask.cli.with_appcontext
def add_unit_categories():
    db = get_db().db
    db["UnitCategory"].delete_many({})
    db["Unit"].update_many({}, {"$set": {"UnitCategoryIDList": []}})
    categoryDict = getUnitCategory()
    for name in categoryDict.keys():
        id = db["UnitCategory"].insert_one(
            {"Date": None, "Owner": None, "ProjectIDList": [], "Name": name, "Predefined": True})
        db["Unit"].update_many({"ShortName": {"$in": categoryDict[name]}},
                                             {"$push": {"UnitCategoryIDList": id.inserted_id}})

