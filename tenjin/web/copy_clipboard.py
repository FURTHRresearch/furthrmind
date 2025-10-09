import flask
from .auth import login_required
import bson
from tenjin.database.db import get_db
from .helper.fieldsHelper import get_field_data_values
from .researchitems import get_linked_items
import json

bp = flask.Blueprint("copy_clipboard", __name__)


@bp.route(
    "/projects/<project_id>/<category>/<item_id>/copy-clipboard", methods=["POST"]
)
@login_required
def copy_item_clipboard_route(project_id, category, item_id):
    """
    Route to generate data for one item to be copied to clipboard
    data is in json format and has the following structure:
    {
        "decimalSeparator": str,
        "format": str,
        "elementsToCopy": list
    }
    elementsToCopy is a list of ids of the datatables to copy. It includes "metadata" if metadata is to be copied

    Parameters
    ----------
    project_id : str
        id of the project
    category : str
        the category of the item
    item_id : str
        id of the item

    Returns
    -------
    str
        string of the copied item in the format specified in data
    """

    if category == "experiments":
        category = "Experiment"
    elif category == "samples":
        category = "Sample"
    else:
        category = "ResearchItem"
    data = flask.request.get_json()

    decimal_separator = data["decimalSeparator"]
    output_format = data["format"]
    elements_to_copy = data["elementsToCopy"]

    metadata = False
    if "metadata" in elements_to_copy:
        metadata = True
    datatable_id_list = []

    for item in elements_to_copy:
        try:
            datatable_id_list.append(bson.ObjectId(item))
        except:
            pass

    item, new_linked_items, fielddata_mapping, datatables = get_data(
        category,
        bson.ObjectId(item_id),
        bson.ObjectId(project_id),
        datatable_id_list,
    )

    if output_format == "json":
        result_dict = prepare_json(
            item,
            new_linked_items,
            fielddata_mapping,
            datatables,
            metadata,
            decimal_separator,
        )
        string = json.dumps(result_dict)
    else:
        string = prepare_csv(
            item,
            new_linked_items,
            fielddata_mapping,
            datatables,
            metadata,
            output_format,
            decimal_separator,
        )
    return string


def get_data(
    category,
    item_id,
    project_id,
    datatable_id_list,
):
    """
    Get the data for the item to be copied to clipboard

    Parameters
    ----------
    category : str
        the category of the item, must be one of "Experiment", "Sample", "ResearchItem"
    item_id : bson.ObjectId
        the id of item as ObjectId
    project_id : bson.ObjectId
        the id of the project as ObjectId
    datatable_id_list : list[bson.ObjectId]
        ids of all the datatables to be copied as list of ObjectId

    Returns
    -------
    dict, list, dict, list
        item, linked_items, fielddata_mapping, datatables
        item is the item to be copied
        linked_items is the list of linked items
        fielddata_mapping is the mapping of field data ids to their values
        datatables is the list of datatables to be copied with all columns and values
    """
    assert category in ["Experiment", "Sample", "ResearchItem"]

    from tenjin.mongo_engine.Project import Project

    project_id_list, mapping = Project.check_permission([project_id], "read")
    if not project_id_list:
        flask.abort(403)
    db = get_db().db
    if category == "Experiment":
        item = db["Experiment"].find_one(
            {"_id": item_id},
            {"_id": 1, "Name": 1, "FieldDataIDList": 1, "GroupIDList": 1, "ShortID": 1},
        )
    elif category == "Sample":
        item = db["Sample"].find_one(
            {"_id": item_id},
            {"_id": 1, "Name": 1, "FieldDataIDList": 1, "GroupIDList": 1, "ShortID": 1},
        )
    else:
        item = db["ResearchItem"].find_one(
            {"_id": item_id},
            {
                "_id": 1,
                "Name": 1,
                "FieldDataIDList": 1,
                "GroupIDList": 1,
                "ShortID": 1,
                "ResearchCategoryID": 1,
            },
        )
        category = db["ResearchCategory"].find_one(
            {"_id": item["ResearchCategoryID"]}, {"_id": 1, "Name": 1}
        )["Name"]
    item["Category"] = category

    fielddata_id_list = []
    fielddata_id_list.extend(item["FieldDataIDList"])

    linked_items = get_linked_items(item_id)
    new_linked_items = []
    for linked in linked_items:
        linked_id = bson.ObjectId(linked["id"])
        linked_category = linked["Category"]
        if linked_category == "Experiment":
            linked_item = db["Experiment"].find_one(
                {"_id": linked_id},
                {
                    "_id": 1,
                    "Name": 1,
                    "FieldDataIDList": 1,
                    "GroupIDList": 1,
                    "ShortID": 1,
                },
            )

        elif linked_category == "Sample":
            linked_item = db["Sample"].find_one(
                {"_id": linked_id},
                {
                    "_id": 1,
                    "Name": 1,
                    "FieldDataIDList": 1,
                    "GroupIDList": 1,
                    "ShortID": 1,
                },
            )
        else:
            linked_item = db["ResearchItem"].find_one(
                {"_id": linked_id},
                {
                    "_id": 1,
                    "Name": 1,
                    "FieldDataIDList": 1,
                    "GroupIDList": 1,
                    "ShortID": 1,
                },
            )

        linked_item["Category"] = linked_category
        fielddata_id_list.extend(linked_item["FieldDataIDList"])
        new_linked_items.append(linked_item)

    fielddata_mapping = get_field_data_values(fielddata_id_list, [])

    datatables = get_datatables(datatable_id_list)

    return item, new_linked_items, fielddata_mapping, datatables


def prepare_json(
    item, linked_items, fielddata_mapping, datatables, metadata, decimal_separator
):
    """
    Prepare the data for the item to be copied to clipboard in json format

    Parameters
    ----------
    item : dict
        the item to be copied
    linked_items : list[dict]
        list of linked items belonging to the item
    fielddata_mapping : dict
        mapping of field data ids to their values
    datatables : list[dict]
        list of datatables to be copied with all columns and values
    metadata : bool
        whether metadata is to be added to the json or not
    decimal_separator : str
        either "." or ",". All floats are converted to this separator

    Returns
    -------
    dict
        the data to be copied in json format
    """
    result_dict = {}
    if metadata:
        result_dict["name"] = item["Name"]
        result_dict["id"] = str(item["_id"])
        result_dict["shortId"] = item["ShortID"]
        result_dict["category"] = item["Category"]
        result_dict["fielddata"] = []
        for fielddata_id in item["FieldDataIDList"]:
            fielddata = fielddata_mapping[fielddata_id]
            result_fielddata_dict = prepare_json_fielddata(fielddata, decimal_separator)
            result_dict["fielddata"].append(result_fielddata_dict)

        result_list_linked_items = []
        for linked_item in linked_items:
            result_linked_item_dict = {}
            result_linked_item_dict["name"] = linked_item["Name"]
            result_linked_item_dict["id"] = str(linked_item["_id"])
            result_linked_item_dict["shortId"] = linked_item["ShortID"]
            result_linked_item_dict["category"] = linked_item["Category"]
            result_linked_item_dict["fielddata"] = []
            for fielddata_id in linked_item["FieldDataIDList"]:
                fielddata = fielddata_mapping[fielddata_id]
                result_fielddata_dict = prepare_json_fielddata(
                    fielddata, decimal_separator
                )
                result_linked_item_dict["fielddata"].append(result_fielddata_dict)
            result_list_linked_items.append(result_linked_item_dict)

        result_dict["linked_items"] = result_list_linked_items

    result_dict["datatables"] = []
    for datatable in datatables:
        result_dict["datatables"].append(
            prepare_json_datatable(datatable, decimal_separator)
        )
    return result_dict


def prepare_json_fielddata(fielddata, decimal_separator):
    """
    Method to prepare the field data for json format

    Parameters
    ----------
    fielddata : dict
        fielddata with its values
    decimal_separator : str
        either "." or ",". All floats are converted to this separator

    Returns
    -------
    dict
        field data in json format
    """
    fielddata_dict = {}
    fielddata_dict["field_name"] = fielddata["field_name"]
    fielddata_dict["type"] = fielddata["type"]
    fielddata_dict["value"] = fielddata["value"]
    fielddata_dict["unit"] = fielddata["unit"]
    fielddata_dict["si_value"] = fielddata["si_value"]
    fielddata_dict["value_max"] = None
    fielddata_dict["si_value_max"] = fielddata["si_value_max"]

    if fielddata_dict["type"] == "Numeric":
        fielddata_dict["value"] = fielddata["original_value"]
    elif fielddata_dict["type"] == "NumericRange":
        fielddata_dict["value"] = fielddata["original_value"][0]
        fielddata_dict["value_max"] = fielddata["original_value"][1]
    elif fielddata_dict["type"] in ["RawDataCalc", "WebDataCalc"]:
        fielddata_dict["value"] = fielddata["original_value"]

    for key, value in fielddata_dict.items():
        if value is not None:
            fielddata_dict[key] = convert_decimal_separator(value, decimal_separator)
    return fielddata_dict


def prepare_json_datatable(datatable, decimal_separator):
    """
    Method to prepare the datatable for json format

    Parameters
    ----------
    datatable : dict
        datatable with its columns and values
    decimal_separator : str
        either "." or ",". All floats are converted to this separator

    Returns
    -------
    dict
        datatable in json format
    """
    result_dict = {}
    result_dict["name"] = datatable["Name"]
    result_dict["id"] = str(datatable["id"])
    result_dict["columns"] = []
    for column in datatable["Columns"]:
        column_dict = {}
        column_dict["name"] = column["Name"]
        column_dict["values"] = column["Values"]
        column_dict["values"] = [
            convert_decimal_separator(cell, decimal_separator)
            for cell in column_dict["values"]
        ]
        result_dict["columns"].append(column_dict)
    return result_dict


def prepare_csv(
    item,
    linked_items,
    fielddata_mapping,
    datatables,
    metadata,
    output_format,
    decimal_separator,
):
    """
    Prepare the data for the item to be copied to clipboard in csv format

    Parameters
    ----------
    item : dict
        the item to be copied
    linked_items : list[dict]
        list of linked items belonging to the item
    fielddata_mapping : dict
        mapping of field data ids to their values
    datatables : list[dict]
        list of datatables to be copied with all columns and values
    metadata : bool
        whether metadata is to be added to the csv or not
    output_format : str
        the format of the output, either ",", ";" or "\t"
    decimal_separator : str
        either "." or ",". All floats are converted to this separator

    Returns
    -------
    str
        Output string in csv format with the correct separator according to output_format
    """
    if metadata:
        rows = prepare_metadata_list(item, linked_items, fielddata_mapping)
    else:
        rows = []
    datable_rows = prepare_datatable_rows_for_csv(datatables)
    if datable_rows:
        if len(datable_rows) > len(rows):
            max_length = len(datable_rows)
            if metadata:
                for i in range(len(rows), max_length):
                    rows.append([""])
        elif len(rows) > len(datable_rows):
            column_number = len(datable_rows[0])
            for i in range(len(datable_rows), len(rows)):
                datable_rows.append([])
                for i in range(column_number):
                    datable_rows[-1].append("")

        if metadata:
            rows = add_empty_colums_before_datatables(rows)
            for row, data_table_row in zip(rows, datable_rows):
                row.extend(data_table_row)
        else:
            rows = datable_rows

    if output_format == ",":
        separator = ","
    elif output_format == ";":
        separator = ";"
    elif output_format == "\t":
        separator = "\t"
    string = ""
    for row in rows:
        row = [convert_decimal_separator(cell, decimal_separator) for cell in row]
        string += separator.join([str(cell) for cell in row]) + "\n"
    return string


def convert_decimal_separator(value, decimal_separator):
    """
    Method to convert the decimal separator of a value
    Only applied for floats

    Parameters
    ----------
    value : any
        The value to be converted
    decimal_separator : str
        either "." or ",". All floats are converted to this separator

    Returns
    -------
    any
       either string with converted decimal separator or the original value
    """
    if not value:
        return value
    if decimal_separator == ".":
        return value
    if isinstance(value, float):
        return str(value).replace(".", decimal_separator)
    return value


def prepare_metadata_list(item, linked_items, field_data_mapping):
    """
    Prepare the metadata for the item to be copied to clipboard

    Parameters
    ----------
    item : dict
        the item to be copied
    linked_items : list[dict]
        list of linked items belonging to the item
    field_data_mapping : dict
        mapping of field data ids to their values

    Returns
    -------
    list[list]
        list of rows with metadata. Each item in the list corresponds to one row. Each row is a list of strings
    """
    rows = []
    rows.append(["Name", item["Name"]])
    rows.append(["id", str(item["_id"])])
    rows.append(["shortId", item["ShortID"]])
    rows.append(["Category", item["Category"]])

    for fielddata_id in item["FieldDataIDList"]:
        fielddata = field_data_mapping[fielddata_id]
        field_data_list = prepare_field_data_rows_for_csv(fielddata)
        rows.append(field_data_list)

    if linked_items:
        rows.append([])
        rows.append(["Linked Items"])
        for linked_item in linked_items:
            rows.append(["Name", linked_item["Name"]])
            rows.append(["id", str(linked_item["_id"])])
            rows.append(["shortId", linked_item["ShortID"]])
            rows.append(["Category", linked_item["Category"]])
            for fielddata_id in linked_item["FieldDataIDList"]:
                fielddata = field_data_mapping[fielddata_id]
                field_data_list = prepare_field_data_rows_for_csv(fielddata)
                rows.append(field_data_list)
            rows.append([])

    return rows


def add_empty_colums_before_datatables(rows):
    """
    Add empty columns to the rows before the datatables start
    This is necessary to have the same number of columns in each row

    Parameters
    ----------
    rows : list[list]
        the rows to which the empty columns are added

    Returns
    -------
    list[list]
        rows with the empty columns added
    """
    total_columns = 10
    for row in rows:
        if len(row) < total_columns:
            for i in range(len(row), total_columns):
                row.append("")
    return rows


def get_datatables(datatable_id_list):
    """
    Method to get the datatables to be copied
    iterates all columns for each datatable and looks for the longest column and stores the length 
    adds empty values if necessary, to have all columns the same length

    Parameters
    ----------
    datatable_id_list : list
        list with ids of the datatables to be copied

    Returns
    -------
    list[dict]
        list of datatables as dicts with all columns and values
    """
    from tenjin.mongo_engine.RawData import RawData
    from tenjin.mongo_engine.Column import Column

    datatables = RawData.objects(id__in=datatable_id_list).order_by("Name")
    datatable_mapping = {d.id: d for d in datatables}
    result_list = []
    for datatable_id in datatable_id_list:
        datatable = datatable_mapping.get(datatable_id)
        if not datatable:
            continue
        result_dict = {}
        result_dict["Name"] = datatable.Name
        result_dict["id"] = datatable.id
        result_dict["MaxRows"] = 0
        column_id_list = [c.id for c in datatable.ColumnIDList]
        columns = Column.objects(id__in=column_id_list)
        column_mapping = {c.id: c for c in columns}

        column_list = []
        for c_id in column_id_list:
            column_dict = {}
            c = column_mapping[c_id]
            column_dict["Name"] = c.Name
            column_values = c.Data
            for pos, v in enumerate(column_values):
                if v is None:
                    column_values[pos] = ""

            if result_dict["MaxRows"] < len(column_values):
                result_dict["MaxRows"] = len(column_values)
            column_dict["Values"] = column_values
            column_list.append(column_dict)

        result_dict["Columns"] = column_list
        result_list.append(result_dict)

    max_length = 0
    for datatable in result_list:
        if max_length < datatable["MaxRows"]:
            max_length = datatable["MaxRows"]

    for datatable in result_list:
        for column in datatable["Columns"]:
            if len(column["Values"]) < max_length:
                column["Values"].extend([""] * (max_length - len(column["Values"])))

    return result_list


def prepare_datatable_rows_for_csv(datatables):
    """
    Method to prepare the datatables for the clipboard for csv format. Creates for each row one list with all values

    Parameters
    ----------
    datatables : list[dict]
        list of datatables with all columns and values

    Returns
    -------
    list[list]
        list of rows with the datatables. Each row is a list of strings
    """
    if not datatables:
        return []
    rows = []
    max_length = 0
    for datatable in datatables:
        if max_length < datatable["MaxRows"]:
            max_length = datatable["MaxRows"]
    for i in range(max_length + 1):
        rows.append([])

    for datatable in datatables:
        rows[0].append(f"Name: {datatable['Name']}")
        for row in range(1, max_length + 1):
            rows[row].append("")

        for row in range(0, max_length):
            for column in datatable["Columns"]:
                if row == 0:
                    rows[row].append(column["Name"])
                rows[row + 1].append(column["Values"][row])

    return rows


def prepare_field_data_rows_for_csv(fielddata):
    """
    Method to prepare the field data for the clipboard for csv format. Creates one list with all values

    Parameters
    ----------
    fielddata : dict
        fielddata with its values

    Returns
    -------
    list
        list of strings with the field data
    """
    field_data_list = [fielddata["field_name"], fielddata["type"]]
    if not fielddata["value"]:
        field_data_list.append("--")
    else:
        if fielddata["type"] == "Numeric":
            field_data_list.append(fielddata["original_value"])
            if not fielddata["unit"]:
                unit = "--"
            else:
                unit = fielddata["unit"]
            field_data_list.append(unit)
            if fielddata["si_value"]:
                field_data_list.append("SI Value")
                field_data_list.append(fielddata["si_value"])
        elif fielddata["type"] == "NumericRange":
            field_data_list.extend(fielddata["original_value"])
            if not fielddata["unit"]:
                unit = "--"
            else:
                unit = fielddata["unit"]
            field_data_list.append(unit)
            if fielddata["si_value"]:
                field_data_list.append("SI Value")
                field_data_list.append(fielddata["si_value"])
            if fielddata["si_value_max"]:
                field_data_list.append("SI Value Max")
                field_data_list.append(fielddata["si_value_max"])
        elif fielddata["type"] in ["RawDataCalc", "WebDataCalc"]:
            if fielddata["original_value"]:
                if isinstance(fielddata["original_value"], dict):
                    for key, value in fielddata["original_value"].items():
                        field_data_list.append(key)
                        field_data_list.append(value)
        elif fielddata["type"] == "MultiLine":
            field_data_list.append(fielddata["value"])
        elif fielddata["type"] == "ComboBox":
            field_data_list.append(fielddata["value"])
        elif fielddata["type"] == "Date":
            field_data_list.append(fielddata["value"])
    return field_data_list
