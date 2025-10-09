import json
import time

import bson
import flask
import pandas as pd
from bson.json_util import dumps as bson_dumps

from tenjin.database.db import get_db
from tenjin.execution.create import Create
from tenjin.execution.delete import Delete
from tenjin.execution.update import Update
from tenjin.web.helper.filterHelper import get_page_item_mapping_dashboard, get_page_item_mapping_dashboard
from .auth import login_required
from tenjin.web.researchitems import get_item_for_dashboard
import datetime
import dateutil.relativedelta

from .projects import page_group_mapping
from tenjin.web.helper.dashboard_item_mapping import get_dashboard_item_mapping

bp = flask.Blueprint('dataviews', __name__)


@bp.route('/dataviews/<dataviewid>', methods=['GET'])
@login_required
def get_dataview(dataviewid):
    db = get_db().db
    data = db.DataView.find_one({"_id": bson.ObjectId(dataviewid)})
    data["id"] = str(data["_id"])
    data["projectId"] = str(data["ProjectID"])
    data.pop('ProjectID')
    data.pop('_id')
    return bson_dumps(data)


@bp.route('/dataviews', methods=['POST'])
@login_required
def create_dataview():
    data = flask.request.get_json()
    db = get_db().db
    dataview_position = list(db.DataView.find(
        {'ProjectID': data['projectId']}).sort([('Row', -1), ('SizeY', -1)]).limit(1))
    create_dict = {
        "Name": data['name'],
        'FilterList': data['filterList'],
        'NameFilter': data['nameFilter'],
        'ProjectID': bson.ObjectId(data['projectId']),
        'DisplayedColumns': data['displayedColumns'],
        'IncludeLinked': data['includeLinked'],
        "ItemIDList": [],
        'DisplayedCategories': data['displayedCategories'],
        'SizeX': 2,
        'SizeY': 1,
        'Col': 0,
        'Row': 0 if not dataview_position else dataview_position[0]['Row'] + dataview_position[0]['SizeY'],
    }
    dataview_id = Create.create("DataView", create_dict)

    return {'id': str(dataview_id)}


@bp.route('/dataviews/<dataview_id>', methods=["DELETE"])
@login_required
def delete_dataview(dataview_id):
    Delete.delete("DataView", bson.ObjectId(dataview_id))
    return {'message': 'Done'}


@bp.route('/dataviews/<dataview_id>', methods=['POST'])
@login_required
def update_dataview(dataview_id):
    data = flask.request.get_json()
    # dataview_id = bson.ObjectId(dataview_id)
    if data.get("name"):
        dataview_id = Update.update("DataView", "Name", data.get("name"), dataview_id)
    if data.get("filterList") is not None:
        dataview_id = Update.update("DataView", "FilterList", data.get("filterList"), dataview_id)
    if data.get("nameFilter") is not None:
        dataview_id = Update.update("DataView", "NameFilter", data.get("nameFilter"), dataview_id)
    if data.get("displayedColumns") is not None:
        dataview_id = Update.update("DataView", "DisplayedColumns", data.get("displayedColumns"), dataview_id)
    if data.get("includeLinked") is not None:
        dataview_id = Update.update("DataView", "IncludeLinked", str(data.get("includeLinked")), dataview_id)
    if data.get("displayedCategories") is not None:
        dataview_id = Update.update("DataView", "DisplayedCategories", data.get("displayedCategories"), dataview_id)
    # id = db.DataView.update_one(
    #     {"_id": bson.ObjectId(dataview_id)},
    #     {"$set": {
    #         "Name": data.get('name'),
    #         'FilterList': data.get('filterList', []),
    #         'NameFilter': data.get('nameFilter', ""),
    #         "DisplayedColumns": data.get('displayedColumns', [])
    #     }})

    return {'id': str(dataview_id)}

def get_page_item_index_from_database_internal(dataview_id):
    dataview_id = bson.ObjectId(dataview_id)
    db = get_db().db
    dataview = db.DataView.find_one({'_id': dataview_id})
    project_id = dataview['ProjectID']
    filterList = dataview['FilterList']
    nameFilter = dataview['NameFilter']
    include_linked = dataview['IncludeLinked']
    displayed_categories = dataview['DisplayedCategories']

    comboFilter = [f for f in filterList if f["type"] == 'combobox']
    for cf in comboFilter:
        cf["field"] = cf["id"]

    numericFilter = [f for f in filterList if f["type"] == 'numeric']
    for nf in numericFilter:
        nf["field"] = nf["id"]
        nf["min"] = nf["values"][0]["min"]
        nf["max"] = nf["values"][0]["max"]
        nf["unit"] = nf["values"][0]["unit"]

    dateFilter = [f for f in filterList if f["type"] == 'date']
    dateFilterNeu = []
    dateCreated = None
    for df in dateFilter:
        if df["id"] == "date_created":
            dateCreated = df
        else:
            dateFilterNeu.append(df)
    dateFilter = dateFilterNeu
    for df in dateFilter:
        df["field"] = df["id"]
        df["min"] = df["values"][0]["min"]
        df["max"] = df["values"][0]["max"]

    textFilter = [f for f in filterList if f["type"] == 'text']
    for tf in textFilter:
        tf["field"] = tf["id"]
        tf["value"] = tf["values"][0]["value"]

    checkFilter = [f for f in filterList if f["type"] == 'checkbox']
    for cf in checkFilter:
        cf["field"] = cf["id"]
        cf["value"] = cf["values"][0]["value"]

    group_filter = []
    group_filter_temp = [f for f in filterList if f["type"] == 'groups']
    if group_filter_temp:
        group_filter_temp = group_filter_temp[0]
        if group_filter_temp.get("values"):
            for value in group_filter_temp["values"]:
                if value and value.get("id"):
                    group_filter.append(value["id"])

    sample_filter = []
    sample_filter_temp = [f for f in filterList if f["type"] == 'samples']
    if sample_filter_temp:
        sample_filter_temp = sample_filter_temp[0]
        if sample_filter_temp.get("values"):
            for value in sample_filter_temp["values"]:
                if value and value.get("id"):
                    sample_filter.append(value["id"])

    exp_filter = []
    exp_filter_temp = [f for f in filterList if f["type"] == 'experiments']
    if exp_filter_temp:
        exp_filter_temp = exp_filter_temp[0]
        if exp_filter_temp.get("values"):
            for value in exp_filter_temp["values"]:
                if value and value.get("id"):
                    exp_filter.append(value["id"])

    item_filter = []
    item_filter_temp = [f for f in filterList if f["type"] == 'researchitems']
    if item_filter_temp:
        item_filter_temp = item_filter_temp[0]
        if item_filter_temp.get("values"):
            for value in item_filter_temp["values"]:
                if value and value.get("id"):
                    item_filter.append(value["id"])

    s = time.time()
    page_item_mapping = get_dashboard_item_mapping(dataview_id=dataview_id, project_id=project_id,
                                                        name_filter=nameFilter, combo_filter=comboFilter,
                                                        numeric_filter=numericFilter, group_filter=group_filter,
                                                        sample_filter=sample_filter, experiment_filter=exp_filter,
                                                        researchitem_filter=item_filter,
                                                        checks_filter=checkFilter, date_filter=dateFilter,
                                                        date_created=dateCreated,
                                                        text_filter=textFilter,
                                                        include_linked=include_linked,
                                                        displayed_categories=displayed_categories)

    return page_item_mapping

@bp.route('/dataviews/<dataview_id>/page-item-index-from-db', methods=['GET'])
@login_required
def get_page_item_index_from_database(dataview_id):
    page_item_mapping = get_page_item_index_from_database_internal(dataview_id)


def getItemValues(items, field_name_list, project_id):
    db = get_db().db
    field_name_list = [name.lower() for name in field_name_list]
    fields = list(db.Field.find({"NameLower": {"$in": field_name_list}, "ProjectID": project_id}, {"_id": 1, "Name": 1}))
    field_id_list = [f["_id"] for f in fields]
    field_mapping = {f["_id"]: f["Name"] for f in fields}
    field_data = db.FieldData.find({"FieldID": {"$in": field_id_list}},
                                   {"_id":1, 'FieldID': 1, "SIValue": 1})
    field_data_mapping = {fd['_id']: fd for fd in field_data}

    for i in items:
        for field_data_id in i['field_data_id_list']:
            field_data_id = bson.ObjectId(field_data_id)
            if field_data_id not in field_data_mapping:
                continue

            field_data = field_data_mapping[field_data_id]
            field_name = field_mapping[field_data["FieldID"]]
            i[field_name] = field_data['SIValue']
        i.pop('field_data_id_list')
    return items


@bp.route('/dataviews/<dataviewid>/page-item-index', methods=['GET'])
@login_required
async def get_dataview_page_item_index(dataviewid):
    from tenjin.mongo_engine.DataView import DataView
    dataviewid = bson.ObjectId(dataviewid)
    data_view = DataView.objects(id=dataviewid).first()
    dataview_list, _ = DataView.check_permission([data_view], 'read')
    if not dataview_list:
        return {
            "maxPage": 1,
            "pageItemMapping": {1: []}
        }

    project_id = data_view.ProjectID.id

    name_filter = flask.request.args.get('nameFilter', "")
    comboFilter = json.loads(
        flask.request.args.get('comboFieldValues', '[]'))
    numericFilter = json.loads(flask.request.args.get('numericFilter', '[]'))
    dateFilter = json.loads(flask.request.args.get('dateFilter', '[]'))
    dateFilterNeu = []
    dateCreated = None
    for df in dateFilter:
        if df["field"] == "date_created":
            dateCreated = df
        else:
            dateFilterNeu.append(df)
    dateFilter = dateFilterNeu
    textFilter = json.loads(flask.request.args.get('textFilter', '[]'))
    checkFilter = json.loads(flask.request.args.get('checkFilter', '[]'))

    groupFilter = json.loads(flask.request.args.get('groupFilter', '[]'))
    sampleFilter = json.loads(flask.request.args.get('sampleFilter', '[]'))
    experimentFilter = json.loads(flask.request.args.get('experimentFilter', '[]'))
    research_item_filter = json.loads(flask.request.args.get('researchItemFilter', '[]'))
    displayed_categories = json.loads(flask.request.args.get('displayedCategories', "[]"))
    include_linked = flask.request.args.get('includeLinked', "none")

    if include_linked == "false":
        include_linked = "none"

    page_item_mapping = await get_dashboard_item_mapping(dataviewid,
        project_id, name_filter=name_filter, combo_filter=comboFilter, numeric_filter=numericFilter,
        group_filter=groupFilter, sample_filter=sampleFilter, experiment_filter=experimentFilter,
        researchitem_filter=research_item_filter, checks_filter=checkFilter, date_filter=dateFilter,
        date_created=dateCreated, text_filter=textFilter, include_linked=include_linked,
        displayed_categories=displayed_categories)

    return page_item_mapping

@bp.route('/dataviews/<dataviewid>/items', methods=['GET'])
@login_required
def get_dataview_items(dataviewid):
    from tenjin.mongo_engine.DataView import DataView
    dataviewid = bson.ObjectId(dataviewid)
    data_view = DataView.objects(id=dataviewid).first()
    dataview_list, _ = DataView.check_permission([data_view], 'read')
    if not dataview_list:
        return {}

    project_id = data_view.ProjectID.id

    item_id_list = json.loads(flask.request.args.get('items', '[]'))

    items = get_item_for_dashboard(project_id, item_id_list)
    return items

@bp.route('/dataviews/<dataviewid>/data', methods=['GET'])
@login_required
def get_dataview_data_get(dataviewid):
    return get_dataview_data_internal(dataviewid)

@bp.route('/dataviews/<dataviewid>/data', methods=['POST'])
@login_required
def get_dataview_data_post(dataviewid):
    data = flask.request.get_json()
    page_item_mapping = {}
    if "pageItemMapping" in data:
        page_item_mapping = data["pageItemMapping"]

    return get_dataview_data_internal(dataviewid, page_item_mapping=page_item_mapping)


def get_dataview_data_internal(dataview_id, page_item_mapping=None):
    db = get_db().db
    dataview = db.DataView.find_one({'_id': bson.ObjectId(dataview_id)})
    chart = db.DataViewChart.find_one({'DataViewID': bson.ObjectId(dataview_id)})
    project_id = dataview['ProjectID']
    if not chart:
        return []

    x_axis = chart['XAxis']
    y_axis = chart['YAxis']
    field_name_list = [x_axis, y_axis]
    if None in field_name_list:
        return []

    item_id_list = dataview["ItemIDList"]
    items = get_item_for_dashboard(dataview["ProjectID"], item_id_list)

    items = getItemValues(items, field_name_list, project_id)
    Update.update("DataViewChart", "Data", items, chart['_id'], no_versioning=True)
    Update.update("DataViewChart", "DataUpdated", datetime.datetime.now(tz=datetime.UTC),
                  chart["_id"], no_versioning=True)
    df = pd.DataFrame(items)
    data = df.to_json(orient='records')
    return data

@bp.route('/dataviews/<dataviewid>/data_not_generated', methods=['GET'])
@login_required
def get_dataview_data_not_generated(dataviewid):
    db = get_db().db
    chart = db.DataViewChart.find_one({'DataViewID': bson.ObjectId(dataviewid)})
    if not chart:
        return ""
    if not chart["Data"]:
        return ""
    items = chart["Data"]
    df = pd.DataFrame(items)
    data = df.to_json(orient=flask.request.args.get('orient', 'records'))
    return data


@bp.route('/dataviews/<dataviewid>/charts', methods=['POST'])
@login_required
def add_dataview_chart(dataviewid):
    db = get_db().db
    data = flask.request.get_json()
    dataview = db.DataView.find_one({'_id': bson.ObjectId(dataviewid)})
    if not dataview:
        return {'error': 'Dataview not found'}, 404
    chart = db.DataViewChart.find_one({'DataViewID': bson.ObjectId(dataviewid)})
    if chart:
        chart_id = chart['_id']
        Update.update("DataViewChart", "Name", data.get("name"), chart_id)
        Update.update("DataViewChart", "XAxis", data.get("xAxis"), chart_id)
        Update.update("DataViewChart", "YAxis", data.get("yAxis"), chart_id)
        # db.DataViewChart.update_one(
        #     {'_id': bson.ObjectId(chart['_id'])},
        #     {'$set': {
        #      'Name': data.get('name'),
        #      'XAxis': data.get('xAxis'),
        #      'YAxis': data.get('yAxis'),
        #      }})
    else:
        data_dict = {
            'DataViewID': bson.ObjectId(dataviewid),
            'ProjectID': dataview['ProjectID'],
            'Name': data.get('name'),
            'XAxis': data.get('xAxis'),
            'YAxis': data.get('yAxis'),
        }
        chart_id = Create.create("DataViewChart", data_dict)
        # chart_id = db.DataViewChart.insert_one({
        #     'DataViewID': bson.ObjectId(dataviewid),
        #     'ProjectID': dataview['ProjectID'],
        #     'Name': data.get('name'),
        #     'XAxis': data.get('xAxis'),
        #     'YAxis': data.get('yAxis'),
        # }).inserted_id
    return {'id': str(chart_id)}


@bp.route('/projects/<projectId>/dataviews', methods=['GET'])
@login_required
def get_dataview_charts_project(projectId):
    db = get_db().db
    dataviews = list(db.DataView.find({"$and":
                                           [{'ProjectID': bson.ObjectId(projectId)},
                                            {'Name': {"$exists": True}},
                                            {"Name": {"$ne": ""}},
                                            {"Name": {"$ne": None}}]}))
    dataview_ids = [d["_id"] for d in dataviews]
    charts = list(db.DataViewChart.find({'DataViewID': {'$in': dataview_ids}}))
    dataview_chart_mapping = {chart['DataViewID']: chart for chart in charts}
    result_list = []
    for d in dataviews:
        chart = dataview_chart_mapping.get(d['_id'])
        if chart:
            chart_id = str(chart["_id"])
            chart_name = chart["Name"]
            x_axis = chart['XAxis']
            y_axis = chart['YAxis']
        else:
            chart_id = chart_name = x_axis = y_axis = None

        result_list.append({
            'id': str(d['_id']),
            'name': d['Name'],
            'xAxis': x_axis,
            'yAxis': y_axis,
            'chartId': chart_id,
            'chartName': chart_name,
            'sizeX': d['SizeX'],
            'sizeY': d['SizeY'],
            'col': d['Col'],
            'row': d['Row']
        })

    return json.dumps(result_list)


@bp.route('/projects/<projectId>/dataviews/positions', methods=['POST'])
@login_required
def set_dataview_positions(projectId):
    db = get_db().db
    data = flask.request.get_json()
    for chart in data:
        chart_id = bson.ObjectId(chart['id'])
        Update.update("DataView", "Col", chart['col'], chart_id)
        Update.update("DataView", "Row", chart['row'], chart_id)
        Update.update("DataView", "SizeX", chart['sizeX'], chart_id)
        Update.update("DataView", "SizeY", chart['sizeY'], chart_id)

        # db.DataView.update_one({'_id': bson.ObjectId(chart['id'])}, {
        #     '$set': {'Col': chart['col'], 'Row': chart['row'], 'SizeX': chart['sizeX'], 'SizeY': chart['sizeY']}})
    return 'OK'


@bp.route('/dataviews/<dataViewId>/charts', methods=['GET'])
@login_required
def get_dataview_charts(dataViewId):
    db = get_db().db
    chart = db.DataViewChart.find_one({'DataViewID': bson.ObjectId(dataViewId)})
    if chart:
        return json.dumps({
            'id': str(chart['_id']),
            'name': chart['Name'],
            'xAxis': chart['XAxis'],
            'yAxis': chart['YAxis']}
        )
    else:
        return {}

@bp.route('/dataviews/<dataview_id>/updated', methods=['GET'])
@login_required
def get_chart_update_time(dataview_id):
    db = get_db().db
    chart = db.DataViewChart.find_one({'DataViewID': bson.ObjectId(dataview_id)})
    if not chart:
        return ""

    dt1:datetime.datetime= chart["DataUpdated"]  # 1973-11-29 22:33:09
    if not dt1:
        return ""
    dt1 = dt1.replace(tzinfo=datetime.UTC)
    dt2 = datetime.datetime.now(tz=datetime.UTC)  # 1977-06-07 23:44:50
    rd = dateutil.relativedelta.relativedelta(dt2, dt1)
    if rd.days > 0:
        dt1.replace(microsecond=0)
        return dt1.isoformat()
    else:
        string = f"Hours: {rd.hours}, Minutes: {rd.minutes}, Seconds: {rd.seconds}"
        return string
