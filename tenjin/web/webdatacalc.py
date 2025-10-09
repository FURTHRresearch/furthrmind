import json
import datetime

import bson
import flask
import requests
from flask import Blueprint
import random
import string

from tenjin.database.db import get_db
from tenjin.web.auth import createNewApiKey

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete

from .auth import login_required
from .helper.furthrHelper import ensureAccess
from tenjin.logic.spreadsheet_generator import SpreadsheetGenerator
from io import BytesIO
import openpyxl

bp = Blueprint('webdatacalc', __name__)


@bp.route('/webdatacalc/<fieldDataId>/run', methods=['POST'])
@login_required
def run_webdatacalc(fieldDataId):
    db = get_db().db
    fieldData = db.FieldData.find_one({"_id": bson.ObjectId(fieldDataId)})
    field = db.Field.find_one({'_id': fieldData['FieldID']})
    script = field["WebDataCalcScript"]
    if script is None:
        script = ""
    script = script.lower()
    response = {'error': '', 'stderr': '', 'stdout': ''}
    if field["CalculationType"] == "Spreadsheet":
        script_lower = script.replace("#spreadsheet", "")
        script_dict = json.loads(script_lower)
        result_dict = run_spreadsheet_calculation(script_dict, fieldData, flask.g.user)
        response.update({"stdout": json.dumps(result_dict)})

    elif script.startswith("#spreadsheet"):
        script_lower = script.replace("#spreadsheet", "")
        script_dict = json.loads(script_lower)
        exp_short_id = script_dict.get("exp-short-id")
        exp = db["Experiment"].find_one({"ShortID": exp_short_id})
        template_found = False
        if exp:
            spreadsheets = db["SpreadSheet"].find(
                {"ExperimentIDList": {"$in": [exp["_id"]]}})
            for spreadsheet in spreadsheets:
                if len(spreadsheet["ExperimentIDList"]) == 1:
                    template_found = True
                    script_dict["TemplateID"] = spreadsheet["_id"]
                    break
        if template_found:
            result_dict = run_spreadsheet_calculation(script_dict, fieldData, flask.g.user)
            response.update({"stdout": json.dumps(result_dict)})
    else:

        key = createNewApiKey(flask.g.user, 2, 'WebDataCalcKey', db)

        sample = None
        group = None
        research_item = None
        groupID = ""
        expID = ""
        sampleID = ""
        research_item_id = ""
        rawdataID = ""
        projectID = ""
        exp = db.Experiment.find_one(
            {'FieldDataIDList': {"$in": [bson.ObjectId(fieldDataId)]}})
        if exp is None:
            sample = db.Sample.find_one(
                {'FieldDataIDList': {"$in": [bson.ObjectId(fieldDataId)]}})
            if sample is None:
                research_item = db.ResearchItem.find_one(
                    {'FieldDataIDList': {"$in": [bson.ObjectId(fieldDataId)]}})
                if not research_item:
                    group = db.Group.find_one(
                        {'FieldDataIDList': {"$in": [bson.ObjectId(fieldDataId)]}})

        if exp:
            groupID = exp["GroupIDList"][0]
            rawdata = db.RawData.find_one({'ExpID': exp['_id']})
            if rawdata:
                rawdataID = str(rawdata["_id"])
            else:
                rawdataID = ""
            expID = exp["_id"]
        elif sample:
            expID = ""
            groupID = sample['GroupIDList'][0]
            rawdata = db.RawData.find_one({'SampleID': sample['_id']})
            if rawdata:
                rawdataID = str(rawdata["_id"])
            else:
                rawdataID = ""
            sampleID = sample["_id"]
        elif research_item:
            groupID = research_item['GroupIDList'][0]
            rawdata = db.RawData.find_one({'ResearchItemID': research_item['_id']})
            if rawdata:
                rawdataID = str(rawdata["_id"])
            else:
                rawdataID = ""
            research_item_id = research_item["_id"]
        elif group:
            groupID = group["_id"]

        group = db.Group.find_one(
            {'_id': groupID})
        if group:
            projectID = group["ProjectID"]

        CALLBACK_URL = flask.current_app.config.get("WEBDATACALC_CALLBACK_URL")
        if CALLBACK_URL is None:
            CALLBACK_URL = flask.current_app.config.get("CALLBACK_URL")
            if CALLBACK_URL is None:
                CALLBACK_URL = flask.current_app.config.get("ROOT_URL")

        ca_bundle_path = flask.current_app.config.get("REQUESTS_CA_BUNDLE")
        ca_bundle = "empty"
        use_ca_bundle = False
        if ca_bundle_path is not None:
            use_ca_bundle = True
            with open(ca_bundle_path, 'r') as f:
                ca_bundle = f.read()

        if field["CalculationType"] == "WebDataCalc":
            command = "python /furthr/main.pyc"
            image = "furthrresearch/furthrmind-coderunner-v1"
        else:
            command = "python /furthr/run_old_calc.pyc"
            image = "furthrresearch/furthrmind-coderunner-legacy-calc"
        runconfig = {
            "image": image,
            "payload": {
                "command": command,
                "language": "python",
                "files": [
                    {"name": "experiment.json", "content": json.dumps(
                        {'id': str(expID)})},
                    {"name": "group.json", "content": json.dumps(
                        {'id': str(groupID)})},
                    {"name": "project.json", "content": json.dumps(
                        {'id': str(projectID)})},
                    {"name": "fieldData.json", "content": json.dumps(
                        {'id': fieldDataId})},
                    {"name": "sample.json", "content": json.dumps(
                        {'id': str(sampleID)})},
                    {"name": "researchitem.json", "content": json.dumps(
                        {'id': str(research_item_id)})},
                    {"name": "field.json", "content": json.dumps(
                        {
                            'id': str(fieldData['FieldID']),
                            'calculationType': field.get('CalculationType', "Wrapper"),
                            'calculation-scriptID': {'id': str(field.get('RawDataCalcScriptFileID', ''))},
                        })},
                    {"name": "rawdata.json", "content": json.dumps(
                        {'id': str(rawdataID)})},
                    {"name": "config.json", "content": json.dumps(
                        {"callbackURL": CALLBACK_URL,
                         "X-API-KEY": key,
                         "USE-CA-BUNDLE": use_ca_bundle})},
                    {"name": "ca_bundle.pem", "content": ca_bundle},
                ]
            }}

        response = requests.post(f"{flask.current_app.config['WEBDATACALC_API']}/run", headers={
            'X-Access-Token': flask.current_app.config['WEBDATACALC_API_KEY']
        }, json=runconfig)
        response = response.json()
    result = None
    result_key_word = "/result:/"
    if result_key_word in response["stdout"]:
        index = response["stdout"].index(result_key_word)
        result = response["stdout"][index + len(result_key_word):]
        result = result.replace("\n", "")
        result = result.replace("\r", "")
        result = result.replace("\'", "\"")
        try:
            result = json.loads(result)
        except:
            pass
        

    return {
        'response': response,
        'result': result
    }


@bp.route("/webdatacalc/run-custom-script", methods=["POST"])
@login_required
def run_custom_script():
    """
    Structure of expected data: calculation-type currently not used. If more programming languages 
    supported, than it will be necessary
    
    for files, either the content can be submitted or the fileID. In both cases, the webdatacalc 
    server will save the content with the filename as specified under "filename"
    
    data["script"] = {
        "calculation-type": "custom-script-python",
        "content": "xxx"}
    data["files"] = [
        {"name": "xxx",  with file extension
         "content": "xxx",
         "format": "text", or "bytes"
         "id": "xxx"}
    data["config"] = {} , additional input parameter passed to the script
    
    """
    
    db = get_db().db
    data = flask.request.get_json()
    key = None
    CALLBACK_URL = None
    config = data.get("config")
    if config:
        key = config.get("X-API-KEY")

    if not key:
        key = createNewApiKey(flask.g.user, 2, 'WebDataCalcKey', db)

    CALLBACK_URL = flask.current_app.config.get("WEBDATACALC_CALLBACK_URL")
    if CALLBACK_URL is None:
        CALLBACK_URL = flask.current_app.config.get("CALLBACK_URL")
        if CALLBACK_URL is None:
            CALLBACK_URL = flask.current_app.config.get("ROOT_URL")

    ca_bundle_path = flask.current_app.config.get("REQUESTS_CA_BUNDLE")
    ca_bundle = "empty"
    use_ca_bundle = False
    if ca_bundle_path is not None:
        use_ca_bundle = True
        with open(ca_bundle_path, 'r') as f:
            ca_bundle = f.read()

    config = {"callbackURL": CALLBACK_URL,
              "X-API-KEY": key,
              "USE-CA-BUNDLE": use_ca_bundle}
    if "config" in data:
        config.update(data["config"])

    assert "script" in data, "script missing"
    if isinstance(data["script"], str):
        data["script"] = {
            "calculation-type": "custom-script-python",
            "content": data["script"]
        }
    runconfig = {
        "image": "furthrresearch/furthrmind-coderunner-v1",
        "payload": {
            "command": "python /furthr/run-custom-script.pyc",
            "language": "python",
            "files": [
                {"name": "script.py", "content": data["script"]["content"]},
                {"name": "files.txt", "content": json.dumps(data["files"])},
                {"name": "config.json", "content": json.dumps(config)},
                {"name": "ca_bundle.pem", "content": ca_bundle},
            ]
        }}
    response = requests.post(f"{flask.current_app.config['WEBDATACALC_API']}/run", headers={
        'X-Access-Token': flask.current_app.config['WEBDATACALC_API_KEY']
    }, json=runconfig)
    response = response.json()
    
    result = None
    result_key_word = "/result:/"
    if result_key_word in response["stdout"]:
        index = response["stdout"].index(result_key_word)
        result = response["stdout"][index + len(result_key_word):]
        result = result.replace("\n", "")
        result = result.replace("\r", "")
        result = result.replace("\'", "\"")
        try:
            result = json.loads(result)
        except:
            pass
    
    response["result"] = result
    return response


@bp.route('/fields/<fieldId>/webdatacalcscript', methods=['GET'])
@login_required
def get_webdatacalcscript(fieldId):
    ensureAccess("Field", "read", fieldId)
    field = get_db().db.Field.find_one({'_id': bson.ObjectId(fieldId)})
    return field['WebDataCalcScript']


@bp.route('/fields/<fieldDataId>/calculationresult', methods=['POST'])
@bp.route('/fields/<fieldDataId>/calculationresults', methods=['POST'])
@login_required
def set_calculationresults(fieldDataId):
    ensureAccess("FieldData", "read",
                 bson.ObjectId(fieldDataId))
    userId = flask.g.user
    data = flask.request.json

    set_calculationresult_method(fieldDataId, data, userId)
    # get_db().db['CalculationResult'].findOne({'FieldID': bson.ObjectId(fieldId)}, {
    #     '$set': {'CalculationResult': data}}, upsert=True)

    return "", 200


def set_calculationresult_method(fieldDataId, result_dict, userId):
    db = get_db()
    calculation = db.db["Calculation"].find_one(
        {"FieldDataID": bson.ObjectId(fieldDataId)})
    timeStamp = datetime.datetime.now(datetime.UTC)
    if calculation:
        Update.update("Calculation", "LastExecution", timeStamp,
                      calculation["_id"], db, userId)
        Update.update("Calculation", "UpToDate", True,
                      calculation["_id"], db, userId)
        Update.update("Calculation", "Output", result_dict,
                      calculation["_id"], db, userId)
    else:
        dataDict = {"FieldDataID": bson.ObjectId(fieldDataId),
                    "Output": result_dict,
                    "LastExecution": timeStamp,
                    "UpToDate": True}

        calculationID = Create.create(
            "Calculation", dataDict, db, userId)
        Update.update("FieldData", "Value", calculationID, bson.ObjectId(fieldDataId),
                      db, userId)


@bp.route('/fields/<fieldDataId>/triggerlist', methods=['POST'])
@login_required
def set_triggerlist(fieldDataId):
    ensureAccess("FieldData", "read", fieldDataId)
    userId = flask.g.user
    newTriggerList = flask.request.json
    newHashMapping = {hash(json.dumps(trigger))
                      : trigger for trigger in newTriggerList}
    for trigger in newTriggerList:
        if "Collection" not in trigger:
            trigger["Collection"] = None
        if "Attribute" not in trigger:
            trigger["Attribute"] = None
        if "DataID" not in trigger:
            trigger["DataID"] = None
        if "Value" not in trigger:
            trigger["Value"] = None

    db = get_db()
    calculation = db.db["Calculation"].find_one(
        {"FieldDataID": bson.ObjectId(fieldDataId)})

    if calculation:
        triggerIDList = calculation["TriggerIDList"]
        triggerList = db.db["Trigger"].find(
            {"_id": {"$in": triggerIDList}})
        existingHashMapping = {}
        existingHashIDMapping = {}
        for trigger in triggerList:
            triggerDict = {}
            for key in trigger.keys():
                if key not in ["Collection", "Attribute", "DataID",
                               "Value"]:
                    continue
                if isinstance(trigger[key], (bson.ObjectId, datetime.datetime)):
                    triggerDict[key] = str(trigger[key])
                else:
                    triggerDict[key] = trigger[key]
            existingHashMapping[hash(json.dumps(triggerDict))] = triggerDict
            existingHashIDMapping[hash(
                json.dumps(triggerDict))] = trigger["_id"]

        deleteTriggerIDList = []
        createTriggerList = []
        for existingHash in existingHashMapping.keys():
            if existingHash not in newHashMapping:
                deleteTriggerIDList.append(existingHashIDMapping[existingHash])

        for newHash in newHashMapping.keys():
            if newHash not in existingHashMapping:
                createTriggerList.append(newHashMapping[newHash])

        for deleteTriggerID in deleteTriggerIDList:
            Delete.delete("Trigger", deleteTriggerID, db, userId)
            triggerIDList.remove(deleteTriggerID)

        triggerIDList = []
        for createTrigger in createTriggerList:
            dataID = None
            if createTrigger["DataID"]:
                dataID = bson.ObjectId(createTrigger["DataID"])
            createDict = {"Collection": createTrigger["Collection"],
                          "DataID": dataID,
                          "Attribute": createTrigger["Attribute"],
                          "Value": createTrigger["Value"]}
            triggerID = Create.create(
                "Trigger", createDict, db, userId)
            triggerIDList.append(triggerID)

        Update.update("Calculation", "TriggerIDList", triggerIDList,
                      calculation["_id"], db, userId)

    return '', 200


@bp.route('/webdatacalc/<id>', methods=['POST'])
@login_required
def update_webdatacalc(id):
    ensureAccess("Field", "read", id)
    data = flask.request.get_json()
    field = get_db().db["Field"].find_one({"_id": bson.ObjectId(id)})
    if field["RawDataCalcScriptFileID"]:
        return "all good"
    userID = flask.g.user
    Update.update("Field", "WebDataCalcScript", data["code"], bson.ObjectId(id), get_db(),
                  userID)
    return "all good"


def run_spreadsheet_calculation(script_dict: dict, fielddata, userID):
    template_id = script_dict.get("TemplateID")
    if not template_id:
        template_id = script_dict.get("TemplateID".lower())
        if not template_id:
            template_id = script_dict.get("template_id")
    assert template_id, ValueError("TemplateID not found")

    current_item = False
    if template_id == "current_item":
        current_item = True
    else:
        template_id = bson.ObjectId(template_id)

    result_cell = script_dict.get("Cell")
    if not result_cell:
        result_cell = script_dict.get("Cell".lower())

    db = get_db().db
    exp_list = []
    sample_list = []
    item_list = []
    exp = sample = item = None
    exp = db.Experiment.find_one(
        {'FieldDataIDList': {"$in": [bson.ObjectId(fielddata["_id"])]}})
    if not exp:
        sample = db.Sample.find_one(
            {'FieldDataIDList': {"$in": [bson.ObjectId(fielddata["_id"])]}})
        if not sample:
            item = db.ResearchItem.find_one(
                {'FieldDataIDList': {"$in": [bson.ObjectId(fielddata["_id"])]}})
    if exp:
        exp_list.append(exp)
    if sample:
        sample_list.append(sample)
    if item:
        item_list.append(item)
    if current_item:
        spreadsheet_gen_instance = SpreadsheetGenerator(exp_list, sample_list=sample_list, research_item_list=item_list,
                                                        dataview=None,
                                                        user_id=flask.g.user)
    else:
        spreadsheet_gen_instance = SpreadsheetGenerator(exp_list, sample_list=sample_list, research_item_list=item_list,
                                                        dataview=None,
                                                        user_id=flask.g.user, template_id=template_id,
                                                        force_template=True,
                                                        save=False)
    spreadsheet_bytes = spreadsheet_gen_instance.outputBytes

    spreadsheet_calculator_url = flask.current_app.config.get("SPREADSHEET_CALCULATOR_URL")
    spreadsheet_calculator_access_key = flask.current_app.config.get("SPREADSHEET_CALCULATOR_ACCESS_KEY")
    header = {"ACCESS-KEY": spreadsheet_calculator_access_key}
    data = spreadsheet_bytes
    response = requests.request("GET", f"{spreadsheet_calculator_url}/evaluate", headers=header, data=data)
    spreadsheet_bytes = response.content

    spreadsheet_bytes = BytesIO(spreadsheet_bytes)
    wb = openpyxl.load_workbook(spreadsheet_bytes, data_only=True)
    sheets = wb.sheetnames
    if "Your workspace" not in sheets:
        result = {"Result": "'Your workspace' sheet not found"}
        set_calculationresult_method(fielddata["_id"], result, userID)
        return

    sheet = wb["Your workspace"]
    # noinspection PyUnresolvedReferences
    result = sheet[result_cell].value
    result_dict = {"Result": result}
    set_calculationresult_method(fielddata["_id"], result_dict, userID)
    return result_dict
