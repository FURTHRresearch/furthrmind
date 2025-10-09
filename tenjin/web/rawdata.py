import time

from .helper.furthrHelper import ensureAccess
import flask

from .auth import login_required
from tenjin.database.db import get_db
import bson

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete
from tenjin.file.s3_storage import S3Storage
import pandas as pd
import iteration_utilities
import datetime

bp = flask.Blueprint('webrawdata', __name__)

import json

@bp.route('/rawdata/<id>')
@login_required
def rawdata(id):
    ensureAccess("RawData", "read", id)
    db = get_db().db
    start = time.time()
    data = db.RawData.find_one({"_id": bson.ObjectId(id)})
    columns_cursor = db.Column.find(
        {"_id": {"$in": data['ColumnIDList']}},{
            "_id":1,"Name":1, "Data": 1, "UnitID": 1, "Type": 1})
    column_mapping = {c["_id"]: c for c in columns_cursor}
    columns = []
    for column_id in data['ColumnIDList']:
        if column_id not in column_mapping:
            continue
        column = column_mapping[column_id]
        column["id"] = str(column["_id"])
        if column["UnitID"]:
            column["UnitID"] = str(column["UnitID"])
        column.pop("_id")
        if column["Type"] == "Date":
            column["Data"] = list(map(convert_datetime_to_iso, column["Data"]))
        columns.append(column)
    return_data = {'columns': columns,
                   "name": data["Name"]}
    json_data = json.dumps(return_data)
    return json_data

def convert_datetime_to_iso(value):
    if isinstance(value, datetime.datetime):
        value = value.isoformat()
    return value

@bp.route('/columns/<id>', methods=['POST'])
@login_required
def column_update(id):
    ensureAccess("Column", "write", id)
    data = flask.request.get_json()
    userId = flask.g.user
    colId = bson.ObjectId(id)
    # do we need more validation?
    Update.update("Column", "Data",
                  data, colId, get_db(), userId)
    return 'all done'

@bp.route("/rawdata/<item_type>/<item_id>", methods=['Post'])
@login_required
def create_rawdata(item_type, item_id):
    start = time.time()
    exp_id = sample_id = researchitem_id = None
    if item_type.lower() == 'experiments':
        collection = "Experiment"
        exp_id = bson.ObjectId(item_id)
    elif item_type.lower() == 'samples':
        collection = "Sample"
        sample_id = bson.ObjectId(item_id)
    else:
        collection = "ResearchItem"
        researchitem_id = bson.ObjectId(item_id)

    ensureAccess(collection, "write", item_id)
    data = flask.request.get_json()
    column_id_list = []
    for pos, column in enumerate(data['columns']):
        column_data = column["data"]
        if iteration_utilities.all_isinstance(column_data, (float, type(None))):
            column_type = "Numeric"
        else:
            try:
                column_data = list(map(convert_to_float, data))
            except:
                pass
            if iteration_utilities.all_isinstance(column_data, (float, type(None))):
                column_type = "Numeric"
            else:
                column_type = "Text"

        data_dict = {
            "Name": str(column['name']),
            "Data": column_data,
            "Type": column_type

        }
        column_id = Create.create("Column", data_dict)
        column_id_list.append(column_id)
    data_dict = {
        "ExpID": exp_id,
        "SampleID": sample_id,
        "ResearchItemID": researchitem_id,
        "ColumnIDList": column_id_list,
        "Name": data["name"]
    }
    rawdata_id = Create.create("RawData", data_dict)
    return str(rawdata_id)

def convert_to_float(value):
    if not value:
        return None
    float_value = float(value)
    return float_value


@bp.route("/rawdata/<rawdata_id>", methods=['Delete'])
@login_required
def delete_rawdata(rawdata_id):
    Delete.delete("RawData", bson.ObjectId(rawdata_id))
    return "all done"

@bp.route("/rawdata/<rawdata_id>/csv", methods=['GET'])
@login_required
def create_csv(rawdata_id):
    start = time.time()
    from tenjin.mongo_engine.RawData import RawData
    from tenjin.mongo_engine.Column import Column
    rawdata = RawData.objects(id=bson.ObjectId(rawdata_id)).first()
    rawdata_list, rawdata_mapping = rawdata.check_permission([rawdata], "read")
    if not rawdata_list:
        return ""
    if not rawdata:
        return ""
    column_id_list = [c.id for c in rawdata.ColumnIDList]
    columns = Column.objects(id__in=column_id_list)
    column_mapping = {c.id: c for c in columns}

    column_dict = {}
    column_name_list = []
    for c_id in column_id_list:
        c = column_mapping[c_id]
        column_name = c.Name
        column_name_list.append(column_name)
        column_values = c.Data
        column = {column_name: column_values}
        column_dict.update(column)

    df = pd.DataFrame({ key:pd.Series(value) for key, value in column_dict.items() })
    # save as csv:
    df_csv = pd.DataFrame.to_csv(df, index=False)

    blob = df_csv.encode("utf-8")

    exp = rawdata.ExpID.fetch()
    exp_name = exp.Name

    if not rawdata.Name:
        file_name = f"{exp_name}_Data_table.csv"
    else:
        file_name = f"{exp_name}_{rawdata.Name}.csv"

    s3_storage = S3Storage(get_db())
    file_id = s3_storage.put(blob, fileName=file_name)
    return str(file_id)

@bp.route('/rawdata/<rawdata_id>', methods=['POST'])
@login_required
def rawdata_update(rawdata_id):
    ensureAccess("RawData", "write", rawdata_id)
    data = flask.request.get_json()
    Update.update("RawData", "Name", data['name'], bson.ObjectId(rawdata_id))
    return 'all done'