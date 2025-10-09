import io
import json
import os.path
import bson
import flask
import jwt
import requests
from tenjin.database.db import get_db
from tenjin.file.file_storage import FileStorage

from tenjin.logic.spreadsheet_generator import SpreadsheetGenerator
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete
from tenjin.authentication import Authentication

from .auth import login_required
from .helper.furthrHelper import ensureAccess

bp = flask.Blueprint('onlyoffice', __name__)

@bp.route('/onlyoffice/spreadsheets/<id_String>', methods=['GET'])
@login_required
def onlyoffice_spreadsheet(id_String):
    id_String = id_String.replace(" ", "")
    if "," in id_String:
        id_list = id_String.split(",")
        id_list = [bson.ObjectId(expID) for expID in id_list]
    else:
        id_list = [bson.ObjectId(id_String)]

    md5 = SpreadsheetGenerator.create_md5(id_list)

    findDict = {"$or": [
        {"ExperimentIDList": {"$in": id_list}},
        {"SampleIDList": {"$in": id_list}},
        {"ResearchItemIDList": {"$in": id_list}},
        {"DataViewID": {"$in": id_list}}
    ]}
    spreadsheetList = list(get_db().db["SpreadSheet"].find(findDict))

    if not spreadsheetList:
        return {"exists": False,
                "results": []}
    for spreadsheet in spreadsheetList:
        if spreadsheet["MD5"] == md5:
            return {"exists": True,
                    "results": [{"id": str(spreadsheet["_id"]), "name": ""}]}

    item_mapping = {}
    expList = list(get_db().db["Experiment"].find(
        {"_id": {"$in": id_list}}))
    item_mapping.update({exp["_id"]: exp for exp in expList})

    sampleList = list(get_db().db["Sample"].find(
        {"_id": {"$in": id_list}}))
    item_mapping.update({sample["_id"]: sample for sample in sampleList})

    researchItemList = list(get_db().db["ResearchItem"].find(
        {"_id": {"$in": id_list}}))
    item_mapping.update({ri["_id"]: ri for ri in researchItemList})

    dataviewList = list(get_db().db["Experiment"].find(
        {"_id": {"$in": id_list}}))
    item_mapping.update({dv["_id"]: dv for dv in dataviewList})

    returnList = []
    returnDict = {"exists": False,
                  "results": returnList}
    for spreadsheet in spreadsheetList:
        name = ""
        id_list = []
        id_list.extend(spreadsheet["ExperimentIDList"])
        id_list.extend(spreadsheet["SampleIDList"])
        id_list.extend(spreadsheet["ResearchItemIDList"])
        if spreadsheet["DataViewID"]:
            id_list.append(spreadsheet["DataViewID"])
        for _id in id_list:
            if _id in item_mapping:
                name += f"{item_mapping[_id]['Name']}, "
        name = name[:-2]
        returnList.append({"id": str(spreadsheet["_id"]), "name": name})
    return returnDict

@bp.route('/onlyoffice/<idString>/<spreadsheetID>', methods=['GET'])
@login_required
def onlyoffice_items(idString, spreadsheetID):
    idString = idString.replace(" ", "")
    if "," in idString:
        id_list = idString.split(",")
        id_list = [bson.ObjectId(expID) for expID in id_list]
    else:
        id_list = [bson.ObjectId(idString)]

    expList = list(get_db().db["Experiment"].find(
        {"_id": {"$in": id_list}}))
    sampleList = list(get_db().db["Sample"].find(
        {"_id": {"$in": id_list}}))
    researchItemList = list(get_db().db["ResearchItem"].find(
        {"_id": {"$in": id_list}}))

    expList = Authentication.filter_list_get("Experiment", expList, flask.g.user, get_db())
    sampleList = Authentication.filter_list_get("Sample", sampleList, flask.g.user, get_db())
    researchItemList = Authentication.filter_list_get("ResearchItem", researchItemList, flask.g.user, get_db())

    try:
        spreadsheetID = bson.ObjectId(spreadsheetID)
    except:
        spreadsheetID = None

    # Create spreadsheet / update spreadsheet  if data has changed. this leads to a change in s3key/chunkIDList which leads to a change in the key
    # we send to onlyoffice. Only if the key changes, a not cached document will be opened
    spreadsheet = SpreadsheetGenerator(exp_list=expList, sample_list=sampleList,
                                       research_item_list=researchItemList, dataview=None, user_id=flask.g.user,
                                       template_id=spreadsheetID).spreadsheet


    user = get_db().db["User"].find_one(
        {"_id": flask.g.user})
    email = user["Email"]

    fileID = spreadsheet["FileID"]
    file = get_db().db["File"].find_one({"_id": fileID})
    title = file["Name"]

    key = file["S3Key"]

    CALLBACK_URL = flask.current_app.config.get("ONLY_OFFICE_CALLBACK_URL")
    if CALLBACK_URL is None:
        CALLBACK_URL = flask.current_app.config.get("CALLBACK_URL")
        if CALLBACK_URL is None:
            CALLBACK_URL = flask.current_app.config.get("ROOT_URL")

    usertoken = jwt.encode(
        {'user': str(flask.g.user)}, flask.current_app.config['SECRET_KEY'], algorithm='HS256')
    config = {
        "document": {
            "fileType": "xlsx",
            "key": key,
            "title": title,
            "url": CALLBACK_URL + f"/web/onlyoffice/files/{fileID}/get?usertoken={usertoken}"
        },
        "documentType": "cell",
        "editorConfig": {
            "callbackUrl": CALLBACK_URL + f"/web/onlyoffice/files/{fileID}/track?usertoken={usertoken}",
            "customization": {"uiTheme": "theme-light"},
            "user": {
                "group": "nogroup",
                "id": f"{str(flask.g.user)}",
                "name": email
            }
        }
    }
    token = jwt.encode(
        config, flask.current_app.config['ONLY_OFFICE_JWT_SECRET'], algorithm='HS256')
    config['token'] = token
    return flask.render_template('onlyofficetest.html', configjson=json.dumps(config),server_url=flask.current_app.config.get("ONLY_OFFICE_DOC_SERVER"))

@bp.route('/onlyoffice/dataview/<dataview_id>', methods=['GET'])
@login_required
def onlyoffice_dataview(dataview_id):

    # Create spreadsheet / update spreadsheet  if data has changed. this leads to a change in s3key/chunkIDList which leads to a change in the key
    # we send to onlyoffice. Only if the key changes, a not cached document will be opened
    
    dataview_id = bson.ObjectId(dataview_id)
    find_dict = {"DataViewID": dataview_id}
    spreadsheet: dict = get_db().db["SpreadSheet"].find_one(find_dict)

    file_id = spreadsheet["FileID"]
    file = get_db().db["File"].find_one({"_id": file_id})
    title = file["Name"]

    user = get_db().db["User"].find_one(
        {"_id": flask.g.user})
    email = user["Email"]

    key = file["S3Key"]

    CALLBACK_URL = flask.current_app.config.get("ONLY_OFFICE_CALLBACK_URL")
    if CALLBACK_URL is None:
        CALLBACK_URL = flask.current_app.config.get("CALLBACK_URL")
        if CALLBACK_URL is None:
            CALLBACK_URL = flask.current_app.config.get("ROOT_URL")

    usertoken = jwt.encode(
        {'user': str(flask.g.user)}, flask.current_app.config['SECRET_KEY'], algorithm='HS256')
    config = {
        "document": {
            "fileType": "xlsx",
            "key": key,
            "title": title,
            "url": CALLBACK_URL + f"/web/onlyoffice/files/{file_id}/get?usertoken={usertoken}"
        },
        "documentType": "cell",
        "editorConfig": {
            "callbackUrl": CALLBACK_URL + f"/web/onlyoffice/files/{file_id}/track?usertoken={usertoken}",
            "customization": {"uiTheme": "theme-light"},
            "user": {
                "group": "nogroup",
                "id": f"{str(flask.g.user)}",
                "name": email
            }
        }
    }
    token = jwt.encode(
        config, flask.current_app.config['ONLY_OFFICE_JWT_SECRET'], algorithm='HS256')
    config['token'] = token
    return flask.render_template('onlyofficetest.html', configjson=json.dumps(config),server_url=flask.current_app.config.get("ONLY_OFFICE_DOC_SERVER"))

# --------------------------------


@bp.route('/onlyoffice/files/<fileID>', methods=['GET'])
@login_required
def onlyoffice_files(fileID):
    ensureAccess("File", "read", bson.ObjectId(fileID))
    file = get_db().db["File"].find_one(
        {"_id": bson.ObjectId(fileID)})
    title = file["Name"]
    file_root, file_ext = os.path.splitext(title)
    file_type = file_ext[1:]

    documentType = None
    if file_type in ["doc", "docm", "docx", "docxf", "dot", "dotm", "dotx",
                     "epub", "fodt", "fb2", "htm", "html", "mht", "odt", "oform", "ott",
                     "oxps", "pdf", "rtf", "txt", "djvu", "xml", "xps"]:
        documentType ="word"

    elif file_type in ["csv", "fods", "ods", "ots", "xls", "xlsb", "xlsm", "xlsx", "xlt", "xltm", "xltx"]:
        documentType ="cell"

    elif file_type in ["fodp", "odp", "otp", "pot", "potm", "potx", "pps", "ppsm", "ppsx", "ppt", "pptm", "pptx"]:
        documentType ="slide"
    if documentType is None:
        return

    user = get_db().db["User"].find_one(
        {"_id": flask.g.user})
    email = user["Email"]

    key = file["S3Key"]

    CALLBACK_URL = flask.current_app.config.get("ONLY_OFFICE_CALLBACK_URL")
    if CALLBACK_URL is None:
        CALLBACK_URL = flask.current_app.config.get("CALLBACK_URL")
        if CALLBACK_URL is None:
            CALLBACK_URL = flask.current_app.config.get("ROOT_URL")

    usertoken = jwt.encode(
        {'user': str(flask.g.user)}, flask.current_app.config['SECRET_KEY'], algorithm='HS256')
    config = {
        "document": {
            "fileType": file_type,
            "key": key,
            "title": title,
            "url": CALLBACK_URL + f"/web/onlyoffice/files/{fileID}/get?usertoken={usertoken}"
        },
        "documentType": documentType,
        "editorConfig": {
            "callbackUrl": CALLBACK_URL + f"/web/onlyoffice/files/{fileID}/track?usertoken={usertoken}",
            "customization": {"uiTheme": "theme-light",
                              "forcesave": True},
            "user": {
                "group": "nogroup",
                "id": f"{str(flask.g.user)}",
                "name": email
            }
        }
    }
    token = jwt.encode(
        config, flask.current_app.config['ONLY_OFFICE_JWT_SECRET'], algorithm='HS256')
    config['token'] = token
    return flask.render_template('onlyofficetest.html', configjson=json.dumps(config), server_url=flask.current_app.config.get("ONLY_OFFICE_DOC_SERVER"))


@bp.route('/onlyoffice/files/<fileID>/get', methods=['GET'])
def onlyoffice_file_get(fileID):
    token = flask.request.args.get('usertoken')
    decoded = jwt.decode(
        token, flask.current_app.config['SECRET_KEY'], algorithms=['HS256'])
    flask.g.user = bson.ObjectId(decoded['user'])
    ensureAccess("File", "read", bson.ObjectId(fileID))
    fs = FileStorage(get_db())
    fileBytes = fs.get_file(fileID)
    file = get_db().db["File"].find_one(
        {"_id": bson.ObjectId(fileID)})
    fileName = file["Name"]
    return flask.send_file(
        io.BytesIO(fileBytes),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=fileName)


@bp.route('/onlyoffice/files/<fileID>/track', methods=['GET', 'POST'])
def onlyoffice_track(fileID):
    data = flask.request.json
    token = data.get('token')
    if not token:
        token = flask.request.headers.get('Authorization')[len('Bearer '):]
    decoded = jwt.decode(
        token, flask.current_app.config['ONLY_OFFICE_JWT_SECRET'], algorithms=['HS256'])
    status = data.get('status')

    if status == 2 or status == 6:
        usertoken = flask.request.args.get('usertoken')
        userId = jwt.decode(
            usertoken, flask.current_app.config['SECRET_KEY'], algorithms=['HS256'])['user']
        flask.g.user = bson.ObjectId(userId)
        blob = requests.get(decoded.get('url')).content

        fs = FileStorage(get_db())
        fs.put(blob, fileID)
    return {'error': 0}

@bp.route('/onlyoffice/<project_id>/spreadsheet_templates')
@login_required
def get_spreadsheet_templates(project_id):

    from tenjin.mongo_engine import SpreadSheet
    templates = SpreadSheet.objects(ProjectID=project_id, Template=True)
    returnList = []
    exists = templates.count() > 0
    for template in templates:
        name = template["TemplateName"]
        returnList.append({"id": str(template.id),
                          "name": name})
    return {"exists": exists,
            "results": returnList}

@bp.route('/onlyoffice/<project_id>/create_template/<collection>/<_id>', methods=["POST"])
@login_required
def create_spreadsheet_template(collection, _id, project_id):
    db = get_db()
    data = flask.request.json
    name = data.get("name")
    user_id = flask.g.user
    spreadsheet = None
    if collection == "Experiment":
        attr = "ExperimentIDList"
    elif collection == "Sample":
        attr = "SampleIDList"
    else:
        attr = "ResearchItemIDList"
    spreadsheet_list = db.db["SpreadSheet"].find({attr: {"$in": [bson.ObjectId(_id)]}})
    for s in spreadsheet_list:
        if {bson.ObjectId(_id)} == set(s[attr]):
            spreadsheet = s
            break
    if spreadsheet is None:
        return "Spreadsheet not found"
    spreadsheet_id = spreadsheet["_id"]
    Update.update("SpreadSheet", "Template", True, bson.ObjectId(spreadsheet_id), db,
                  user_id)
    Update.update("SpreadSheet", "TemplateName", name, bson.ObjectId(spreadsheet_id), db, user_id)
    return "All done"

@bp.route('/onlyoffice/delete_template/<spreadsheet_id>', methods=["DELETE"])
@login_required
def delete_spreadsheet_template(spreadsheet_id):
    user_id = flask.g.user
    db = get_db()
    ensureAccess("SpreadSheet", "write", bson.ObjectId(spreadsheet_id))
    Update.update("SpreadSheet", "Template", False, bson.ObjectId(spreadsheet_id), db,
                  user_id)

    Update.update("SpreadSheet", "TemplateName", None, bson.ObjectId(spreadsheet_id), db, user_id)
    return "All done"


@bp.route('/onlyoffice/update_template/<spreadsheet_id>', methods=["POST"])
@login_required
def update_spreadsheet_template_name(spreadsheet_id):
    user_id = flask.g.user
    db = get_db()
    data = flask.request.json

    Update.update("SpreadSheet", "TemplateName", data['name'], bson.ObjectId(spreadsheet_id), db,
                  user_id)
    return "All done"


@bp.route('/onlyoffice/delete_spreadsheet/<collection>/<item_id>', methods=["DELETE"])
@login_required
def delete_spreadsheet(collection, item_id):
    if collection.lower() == "sample":
        attr = "SampleIDList"
    elif collection.lower() == "experiment":
        attr = "ExperimentIDList"
    else:
        attr = "ResearchItemIDList"

    user_id = flask.g.user
    db = get_db()
    spreadsheet = None
    spreadsheet_list = db.db["SpreadSheet"].find(
        {attr: {"$in": [bson.ObjectId(item_id)]}})
    for s in spreadsheet_list:
        if len(s[attr]) == 1:
            spreadsheet = s
            break
    if spreadsheet is None:
        return "Spreadsheet not found"
    spreadsheet_id = spreadsheet["_id"]
    Delete.delete("SpreadSheet", spreadsheet_id, db, user_id)
    return "All done"
