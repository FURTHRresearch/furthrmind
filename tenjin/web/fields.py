import json
import os.path
from datetime import datetime

import bson
import bson.json_util
import flask

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete
from tenjin.database.db import get_db
from .auth import login_required
from .helper.fieldsHelper import createNewFieldOn, getFields
from .helper.furthrHelper import ensureAccess

bp = flask.Blueprint('webfields', __name__)


@bp.route('/projects/<projid>/fields', methods=['GET'])
@login_required
def get_fields(projid):
    db = get_db().db
    fields = [{
        'id': str(f['_id']),
        'name': f['Name'],
        'type': f['Type'],
    } for f in db.Field.find(
        {"ProjectID": bson.ObjectId(projid)}).sort("NameLower", 1)]
    return json.dumps(fields)


@bp.route('/projects/<projid>/fields', methods=['POST'])
@login_required
def field_create(projid):
    data = flask.request.get_json()
    userId = flask.g.user
    if not data['Type'] in ['ComboBox', 'Numeric', 'Notebook', 'SingleLine', 'CheckBox', 'RawDataCalc', 'MultiLine',
                            'ChemicalStructure', 'Date', "NumericRange"]:
        flask.abort(422)
    parameter = {
        "Type": data['Type'],
        "Name": data['Name'],
        "ProjectID": bson.ObjectId(projid),
    }
    fieldId = Create.create("Field", parameter, get_db(), userId)

    if data['Type'] == 'RawDataCalc':
        if data["spreadsheetTemplate"]:
            Update.update("Field", "CalculationType", "Spreadsheet", fieldId)
            root_folder = flask.current_app.root_path
            folder = os.path.join(root_folder, "tenjin", "web", "templates")
            with open(os.path.join(folder, "spreadsheet.py"), "r") as f:
                script = f.read()
                script = script.replace("<template_id>", data["spreadsheetTemplate"])
                script = script.replace("<cell>", data["cell"])
                Update.update("Field", "WebDataCalcScript", script, fieldId)
        else:
            root_folder = flask.current_app.root_path
            folder = os.path.join(root_folder, "tenjin", "web", "templates")
            Update.update("Field", "CalculationType", "WebDataCalc", fieldId)
            with open(os.path.join(folder, "webdatacalc_template.py"), "r") as f:
                script = f.read()
                Update.update("Field", "WebDataCalcScript", script, fieldId)

        # get_db().db.Field.update_one({'_id': fieldId}, {'$set': {'CalculationType': 'WebDataCalc', 'WebDataCalcScript': open(
        #     flask.current_app.config['WEBDATACALC_PATH'] + "/furthrapi/userCalc.py", "r").read()}})
    fieldDataId, value = createNewFieldOn(
        data['Type'], data['targetId'], data['targetType'], fieldId)

    return {
        'id': str(fieldDataId),
        'Name': data['Name'],
        'FieldID': str(fieldId),
        'Value': value,
        'UnitID': '--',
        'Type': data['Type'],
        'calculationType': 'WebDataCalc',
        "smiles": "",
        "cdxml": ""
    }


@bp.route('/comboboxentries/<combo_id>')
@login_required
def combobox_option_fields(combo_id):
    if combo_id == "-":
        return {}
    ensureAccess("ComboBoxEntry", "read", combo_id)
    db = get_db().db
    option = db.ComboBoxEntry.find_one({"_id": bson.ObjectId(combo_id)})
    fields = {
        "id": str(option['_id']),
        "name": option['Name'],
        "fields": getFields(option['FieldDataIDList'])}
    return bson.json_util.dumps(fields)


@bp.route('/comboboxentries/<entry_id>', methods=['POST'])
@login_required
def update_combo_option(entry_id):
    ensureAccess("ComboBoxEntry", "write", entry_id)
    data = flask.request.get_json()
    userId = flask.g.user
    entry_id = bson.ObjectId(entry_id)
    if 'name' in data:
        Update.update("ComboBoxEntry", "Name",
                      data['name'], entry_id, get_db(), userId)  # do we need more validation?
    return 'all done'


@bp.route('/comboboxentries/<field_id>/entries')
@login_required
def combobox_options(field_id):
    ensureAccess("Field", "read", field_id)
    db = get_db().db
    options = db.ComboBoxEntry.find({"FieldID": bson.ObjectId(field_id)}).sort("Name")
    optionslist = [{
        "id": str(option['_id']),
        "name": option['Name'],
        "fields": getFields(option['FieldDataIDList'])
    } for option in options]

    return bson.json_util.dumps(optionslist)


@bp.route('/comboboxentries/<field_id>/entries', methods=['POST'])
@login_required
def combobox_add_option(field_id):
    ensureAccess("Field", "write", field_id)
    fieldId = bson.ObjectId(field_id)
    userId = flask.g.user
    data = flask.request.get_json()
    if 'name' in data:
        parameter = {
            "Name": data['name'],
            "FieldID": fieldId
        }
        entryId = Create.create("ComboBoxEntry",
                                parameter, get_db(), userId)
        return {
            'id': str(entryId),
            'Name': data['name'],
        }


@bp.route('/fielddata/<id>', methods=['POST'])
@login_required
def field_update(id):
    ensureAccess("FieldData", "write", id)
    data = flask.request.get_json()
    userId = flask.g.user
    fieldDataId = bson.ObjectId(id)
    fieldData = get_db().db.FieldData.find_one({'_id': fieldDataId})
    if not fieldData:
        return ""
    field = get_db().db.Field.find_one({'_id': fieldData['FieldID']})
    if 'value' in data:
        value = data['value']
        if isinstance(value, list):
            if field['Type'] == 'NumericRange':
                value_min = value[0]
                value_max = value[1]
                if value_min != fieldData["Value"]:
                    try:
                        value_min = float(value_min)
                    except:
                        value_min = None
                    # do we need more validation?
                if value_max != fieldData["ValueMax"]:
                    try:
                        value_max = float(value_max)
                    except:
                        value_max = None

                value = [value_min, value_max]

                Update.update("FieldData", "InternalValueNumericRange", value, fieldDataId)

        else:
            skip = False
            if data['value'] == fieldData["Value"]:
                skip = True
            if not skip:
                if field['Type'] == 'Date':
                    value = data["value"]
                    if value == "":
                        value = None
                    else:
                        value = datetime.fromisoformat(data['value'])
                elif field['Type'] == 'Numeric':
                    value = None
                    try:
                        value = float(data['value'])
                    except:
                        pass
                    try:
                        value = float(data['value'])
                    except:
                        pass
                elif field["Type"] == "Numeric":
                    value = data["value"]
                    try:
                        value = float(value)
                    except:
                        value = None

                elif bson.objectid.ObjectId.is_valid(data['value']):
                    # hope the permission system validates this :)
                    value = bson.ObjectId(data['value'])

                elif field['Type'] == 'ComboBox' and data["value"] == "--":
                    value = None
                else:
                    value = data["value"]

                Update.update("FieldData", "Value", value, fieldDataId, get_db(),
                              userId)  # do we need more validation?

    if 'unitId' in data:
        unitID = None
        try:
            unitID = bson.ObjectId(data['unitId'])
        except:
            pass

        Update.update("FieldData", "UnitID", unitID, fieldDataId)
    return 'all done'


@bp.route('/fields/<id>', methods=['PATCH'])
@login_required
def field_update_name(id):
    ensureAccess("Field", "write", id)
    data = flask.request.get_json()
    userId = flask.g.user
    if 'name' in data:
        Update.update("Field", "Name", data['name'], bson.ObjectId(
            id), get_db(), userId)

    return 'all done'

@bp.route('/project/<project_id>/field/check', methods=['POST'])
@login_required
def check_field_name_create(project_id):
    data = flask.request.get_json()
    check = check_field_name(data["name"], project_id=project_id)
    if check:
        return "True"
    else:
        return "False"

@bp.route('/field/<field_id>/check', methods=['POST'])
@login_required
def check_field_name_update(field_id):
    data = flask.request.get_json()
    check = check_field_name(data["name"], field_id=field_id)
    if check:
        return "True"
    else:
        return "False"
    pass

def check_field_name(name, field_id=None, project_id=None):
    from tenjin.mongo_engine.Field import Field
    if field_id:
        field = Field.objects(id=bson.ObjectId(field_id)).first()
        field.Name = name
    else:
        param = {
            "Name": name,
            "Type": "Numeric",
            "ProjectID": project_id
        }
        field = Field(**param)
    try:
        field.validate()
        return True
    except:
        return False

@bp.route('/fields/<field_id>', methods=['DELETE'])
@login_required
def delete_field(field_id):
    ensureAccess("Field", "delete", field_id)
    Delete.delete("Field", bson.ObjectId(field_id))

    return 'all done'

@bp.route('/chemicalstructures/<id>')
@login_required
def get_chemicalstructure(id):
    db = get_db().db
    id = bson.ObjectId(id)
    s = db.ChemicalStructure.find_one({'_id': id})
    smiles = ""
    cdxml = ""
    if s["SmilesList"]:
        smiles = s["SmilesList"][0]
    if s["CDXML"]:
        cdxml = s["CDXML"]
    return {
        'smiles': smiles,
        "cdxml": cdxml
    }


@bp.route('/chemicalstructures/<id>', methods=['POST'])
@login_required
def update_chemicalstructure(id):
    ensureAccess("ChemicalStructure", "write", id)
    data = flask.request.get_json()
    id = bson.ObjectId(id)
    if "smiles" in data:
        smiles = data["smiles"]
        smiles_temp = smiles.replace(">>", ".")
        smiles_list = smiles_temp.split(".")
        Update.update("ChemicalStructure", "SmilesList",
                      smiles_list, id)
        Update.update("ChemicalStructure", "Smiles",
                      smiles, id)
    if "cdxml" in data:
        Update.update("ChemicalStructure", "CDXML",
                      data["cdxml"], id)

    return 'all good'



