import calendar
import time as _time
from datetime import datetime, time, timedelta

import bson
import bson.json_util
import pymongo
from bson import ObjectId
from flask import current_app

from tenjin.database.db import get_db
from tenjin.mongo_engine import Unit
from tenjin.execution.update import Update


# noinspection PyUnresolvedReferences
def get_start_end(index, factor=1):
    start = (index - 1) * current_app.groups_per_page * factor
    end = current_app.groups_per_page * factor
    return start, end


# noinspection PyUnresolvedReferences
def get_max_pages(count):
    max_pages = int(count / current_app.groups_per_page)
    if count % current_app.groups_per_page != 0:
        max_pages += 1
    return max_pages


# noinspection PyDefaultArgument
def get_project_index(
    projectId,
    group_id_list,
    nameFilter="",
    comboFilter=[],
    numericFilter=[],
    groupFilter=[],
    sampleFilter=[],
    experimentFilter=[],
    researchItemFilter=[],
    checkFilter=[],
    add_field_data_id_list=True,
    recent=False,
    index=1,
    include_linked="",
    date_filter=[],
    date_created=[],
    text_filter=[],
    displayed_categories=[],
    include_field_data=False,
    maxPage=None,
):
    filter_applied = check_if_filter_applied(
        nameFilter,
        comboFilter,
        numericFilter,
        groupFilter,
        sampleFilter,
        experimentFilter,
        researchItemFilter,
        checkFilter,
        date_filter,
        date_created,
        text_filter,
    )

    if not filter_applied:
        s = _time.time()
        groups = get_index_no_filter(
            project_id=projectId,
            group_id_list=group_id_list,
            recent=recent,
            include_field_data=include_field_data,
            displayed_categories=displayed_categories,
        )
        print("No filter", _time.time() - s)

    else:
        s = _time.time()
        if group_id_list:
            groups = get_filtered_index_with_group_id_list(
                projectId,
                group_id_list,
                nameFilter,
                comboFilter,
                numericFilter,
                groupFilter,
                sampleFilter,
                experimentFilter,
                researchItemFilter,
                checkFilter,
                recent,
                date_filter,
                date_created,
                text_filter,
                include_field_data=include_field_data,
                include_linked=include_linked,
                displayed_categories=displayed_categories,
            )
        else:
            return []
            # groups = get_filtered_index_without_group_id_list(projectId, nameFilter, comboFilter, groupFilter,
            #                                                   numericFilter,
            #                                                   sampleFilter, experimentFilter, researchItemFilter,
            #                                                   checkFilter, recent, date_filter, date_created,
            #                                                   text_filter,
            #                                                   include_field_data=include_field_data,
            #                                                   include_linked=include_linked,
            #                                                   displayed_categories=displayed_categories)
            print("filtered without group_id_list", _time.time() - s)

        print("filter", _time.time() - s)
    return groups


def get_index_no_filter(
    project_id, group_id_list, recent, include_field_data, displayed_categories
):
    # get top level groups
    # get subgroups
    # get exp, sample, resesearch item
    # build result list
    project_id = bson.ObjectId(project_id)
    group_id_list = [bson.ObjectId(g) for g in group_id_list]
    direction = pymongo.ASCENDING
    if recent:
        order_by = "Date"
        direction = pymongo.DESCENDING
    else:
        order_by = "NameLower"
    start, end = get_start_end(1)
    if not group_id_list:
        toplevel_groups = (
            get_db()
            .db["Group"]
            .find(
                {"ProjectID": project_id, "GroupID": None},
                {"_id": 1, "Name": 1, "GroupID": 1, "ShortID": 1},
            )
            .sort(order_by, direction)
            .skip(start)
            .limit(end)
        )
    else:
        toplevel_groups = (
            get_db()
            .db["Group"]
            .find(
                {"ProjectID": project_id, "_id": {"$in": group_id_list}},
                {"_id": 1, "Name": 1, "GroupID": 1, "ShortID": 1},
            )
            .sort(order_by, direction)
            .skip(start)
            .limit(end)
        )
    # toplevel_groups = Group.objects(
    #     ProjectID=project_id, GroupID=None).order_by(order_by)

    toplevel_groups = list(toplevel_groups)
    sub_group_id_list = get_subgroups(toplevel_groups)
    sub_groups = (
        get_db()
        .db["Group"]
        .find(
            {"_id": {"$in": sub_group_id_list}},
            {"_id": 1, "Name": 1, "GroupID": 1, "ShortID": 1},
        )
        .sort(order_by, direction)
        .skip(start)
        .limit(end)
    )
    groups = list(toplevel_groups)
    groups.extend(sub_groups)
    group_id_list = [g["_id"] for g in groups]

    group_item_mapping = {}

    if "Experiments" in displayed_categories or "all" in displayed_categories:
        exps = (
            get_db()
            .db["Experiment"]
            .find({"GroupIDList": {"$in": group_id_list}})
            .sort("Date", pymongo.DESCENDING)
        )
        # exps = Experiment.objects(GroupIDList__in=group_id_list).order_by("-Date")
        for exp in exps:
            add_item_to_groups_item_mapping(exp, group_item_mapping, "Experiments")
    else:
        exps = []

    if "Samples" in displayed_categories or "all" in displayed_categories:
        samples = (
            get_db()
            .db["Sample"]
            .find({"GroupIDList": {"$in": group_id_list}})
            .sort("Date", pymongo.DESCENDING)
        )
        # samples = Sample.objects(GroupIDList__in=group_id_list).order_by("-Date")
        for sample in samples:
            add_item_to_groups_item_mapping(sample, group_item_mapping, "Samples")
    else:
        samples = []

        # get categories
    categories = (
        get_db().db["ResearchCategory"].find({"ProjectID": project_id}).sort("Name")
    )
    # categories = ResearchCategory.objects(
    #     ProjectID=project_id).only("id", "Name").order_by("Name")
    category_mapping = {c["_id"]: c["Name"] for c in categories}
    cat_id_list = []
    for cat_id in category_mapping:
        cat_name = category_mapping[cat_id]
        if cat_name in displayed_categories or "all" in displayed_categories:
            cat_id_list.append(cat_id)

    researchitems = (
        get_db()
        .db["ResearchItem"]
        .find(
            {
                "GroupIDList": {"$in": group_id_list},
                "ResearchCategoryID": {"$in": cat_id_list},
            }
        )
        .sort("Date", pymongo.DESCENDING)
    )
    # researchitems = ResearchItem.objects(GroupIDList__in=group_id_list, ResearchCategoryID__in=cat_id_list).order_by(
    #     "-Date")

    for ri in researchitems:
        cat_id = ri["ResearchCategoryID"]
        if cat_id in category_mapping:
            add_item_to_groups_item_mapping(
                ri, group_item_mapping, category_mapping[cat_id]
            )

    # subgroups already included in groups => empty dict
    result_list = create_result_list(
        groups, subgroup_mapping={}, group_item_mapping=group_item_mapping
    )
    return result_list


def get_subgroups(toplevel_groups):
    if not toplevel_groups:
        return []
    if isinstance(toplevel_groups[0], dict):
        toplevel_group_id_list = [g["_id"] for g in toplevel_groups]
    else:
        toplevel_group_id_list = toplevel_groups
    pipeline = [
        {"$match": {"GroupID": {"$in": toplevel_group_id_list}}},
        {
            "$graphLookup": {
                "from": "Group",
                "startWith": "$_id",
                "connectFromField": "_id",
                "connectToField": "GroupID",
                "as": "groups",
            }
        },
    ]
    sub_groups = get_db().db["Group"].aggregate(pipeline)
    sub_group_id_set = set()
    for g in sub_groups:
        sub_group_id_set.add(g["_id"])
        for sub in g["groups"]:
            sub_group_id_set.add(sub["_id"])

    return list(sub_group_id_set)


def get_groups_query_additional(field_data_query, name_query, date_created_query):
    result_group_id_list = []
    group_query = {}
    query_list = []

    if field_data_query:
        query_list.append(field_data_query)

    if name_query:
        query_list.append(name_query)

    if date_created_query:
        query_list.append(date_created_query)

    groups = (
        get_db()
        .db["Group"]
        .find({"$and": [group_query, date_created_query]}, {"_id": 1})
    )
    result_group_id_list.extend([g["_id"] for g in groups])

    query = {"GroupIDList": {"$in": result_group_id_list}}

    return query


def get_group_query_limiting(groups_filter):
    if not groups_filter:
        return {}
    group_list = [bson.ObjectId(g) for g in groups_filter]
    pipeline = [
        {"$match": {"_id": {"$in": group_list}}},
        {
            "$graphLookup": {
                "from": "Group",
                "startWith": "$_id",
                "connectFromField": "_id",
                "connectToField": "GroupID",
                "as": "groups",
            }
        },
    ]
    groups = get_db().db["Group"].aggregate(pipeline)
    group_id_list = []
    for g in groups:
        if g["_id"] in group_id_list:
            continue
        group_id_list.append(g["_id"])
        for sub in g["groups"]:
            if sub["_id"] in group_id_list:
                continue
            group_id_list.append(sub["_id"])

    group_query = {"GroupIDList": {"$in": group_id_list}}
    return group_query


def get_field_data_query_objects(
    combo_filter=None,
    numeric_filter=None,
    checks_filter=None,
    date_filter=None,
    text_filter=None,
):

    field_data_query = []

    if combo_filter:
        combo_query_dict = {}
        for filter in combo_filter:
            field = filter["field"]
            field_data = (
                get_db()
                .db["FieldData"]
                .find(
                    {
                        "$and": [
                            {"FieldID": bson.ObjectId(field)},
                            {
                                "Value": {
                                    "$in": [
                                        bson.ObjectId(i["id"]) for i in filter["values"]
                                    ]
                                }
                            },
                        ]
                    },
                    {"_id": 1},
                )
            )
            query = {"FieldDataIDList": {"$in": [fd["_id"] for fd in field_data]}}

            if field in combo_query_dict:
                combo_query_dict[field]["$or"].append(query)
            else:
                combo_query_dict[field] = {}
            combo_query_dict[field]["$or"] = [query]

            combined_combo_query = {"$and": []}
            for field in combo_query_dict:
                combined_combo_query["$and"].append(combo_query_dict[field])

            field_data_query.append(combined_combo_query)

    if checks_filter:
        check_query_dict = {}
        for check in checks_filter:
            field = check["field"]
            value = check["value"]
            if isinstance(value, str):
                if value.lower() == "true":
                    value = True
                else:
                    value = False
            if value is False:
                value_query = {"$or": [{"Value": False}, {"Value": None}]}
            else:
                value_query = {"Value": True}
            field_data = (
                get_db()
                .db["FieldData"]
                .find(
                    {"$and": [{"FieldID": bson.ObjectId(field)}, value_query]},
                    {"_id": 1},
                )
            )

            query = {"FieldDataIDList": {"$in": [fd["_id"] for fd in field_data]}}

            if field in check_query_dict:
                check_query_dict[field]["$or"].append(query)
            else:
                check_query_dict[field] = {}
            check_query_dict[field]["$or"] = [query]

        combined_check_query = {"$and": []}
        for field in check_query_dict:
            combined_check_query["$and"].append(check_query_dict[field])

        field_data_query.append(combined_check_query)

    if numeric_filter:
        numeric_query_dict = {}
        for nf in numeric_filter:
            field = nf["field"]

            field_dict = (
                get_db()
                .db["Field"]
                .find_one({"_id": bson.ObjectId(field)}, {"_id": 1, "Type": 1})
            )
            num_query = {"FieldID": bson.ObjectId(field)}
            range_query = {"FieldID": bson.ObjectId(field)}
            try:
                unitID = bson.ObjectId(nf["unit"])
                unit = Unit.objects.get(id=unitID)
                check, min_value = unit.unit_conversion_to_si(float(nf["min"]))
                min_value = float(nf["min"]) if not check else min_value
                check, max_value = unit.unit_conversion_to_si(float(nf["max"]))
                max_value = float(nf["max"]) if not check else max_value

                num_query["SIValue"] = {"$gte": min_value, "$lte": max_value}

                # noinspection PyTypedDict
                range_query["$or"] = [
                    {"SIValueMax": {"$gte": min_value}, "SIValue": {"$lte": max_value}},
                    {
                        "Value": None,
                        "SIValueMax": {"$gte": min_value, "$lte": max_value},
                    },
                    {
                        "ValueMax": None,
                        "SIValue": {"$gte": min_value, "$lte": max_value},
                    },
                ]
                index_to_be_used = "field_sivalue"

            except:
                min_value = None
                max_value = None
                try:
                    min_value = float(nf["min"])
                    max_value = float(nf["max"])
                except:
                    pass

                num_query["Value"] = {"$gte": min_value, "$lte": max_value}

                range_query["$or"] = [
                    {"ValueMax": {"$gte": min_value}, "Value": {"$lte": max_value}},
                    {"Value": None, "ValueMax": {"$gte": min_value, "$lte": max_value}},
                    {"ValueMax": None, "Value": {"$gte": min_value, "$lte": max_value}},
                ]
                index_to_be_used = "field_value"

            if field_dict["Type"] == "Numeric":
                query = num_query
            else:
                query = range_query

            field_data = (
                get_db().db["FieldData"].find(query, {"_id": 1}).hint(index_to_be_used)
            )

            query = {"FieldDataIDList": {"$in": [fd["_id"] for fd in field_data]}}

            if field in numeric_query_dict:
                numeric_query_dict[field]["$or"].append(query)
            else:
                numeric_query_dict[field] = {}
                numeric_query_dict[field]["$or"] = [query]

        combined_numeric_query = {"$and": []}
        for field in numeric_query_dict:
            combined_numeric_query["$and"].append(numeric_query_dict[field])

        field_data_query.append(combined_numeric_query)

    if date_filter:
        date_query_dict = {}
        for df in date_filter:
            custom_date = False
            if "option" in df:
                if df["option"].lower() == "custom":
                    custom_date = True
            else:
                custom_date = True
            if custom_date:
                try:
                    value_min = datetime.fromisoformat(df["min"])
                    value_max = datetime.fromisoformat(df["max"])
                except:
                    continue
            else:
                value_min, value_max = get_date_from_option_string(df["option"].lower())

            field_id = ObjectId(df["field"])
            query = {
                "FieldID": field_id,
                "Value": {"$gte": value_min, "$lte": value_max},
            }

            field_data = get_db().db["FieldData"].find(query, {"_id": 1})

            query = {"FieldDataIDList": {"$in": [fd["_id"] for fd in field_data]}}

            if field_id in date_query_dict:
                date_query_dict[field_id]["$or"].append(query)
            else:
                date_query_dict[field_id] = {}
                date_query_dict[field_id]["$or"] = [query]

        combined_date_query = {"$and": []}
        for field in date_query_dict:
            combined_date_query["$and"].append(date_query_dict[field])

        field_data_query.append(combined_date_query)

    if text_filter:
        text_query_dict = {}
        for tf in text_filter:
            value = tf["value"]
            field_id = ObjectId(tf["field"])
            query = {"FieldID": field_id, "ValueLower": {"$regex": value.lower()}}
            field_data = get_db().db["FieldData"].find(query, {"_id": 1})

            query = {"FieldDataIDList": {"$in": [fd["_id"] for fd in field_data]}}

            if field_id in text_query_dict:
                text_query_dict[field_id]["$or"].append(query)
            else:
                text_query_dict[field_id] = {}
                text_query_dict[field_id]["$or"] = [query]

        combined_text_query = {"$and": []}
        for field in text_query_dict:
            combined_text_query["$and"].append(text_query_dict[field])

        field_data_query.append(combined_text_query)

    if field_data_query:
        field_data_query = {"$and": field_data_query}
    else:
        field_data_query = {}
    return field_data_query


def get_linked_items_recursive(
    include_linked, exp_id_list, sample_id_list, researchitem_id_list
):
    extra_exp_id_list = []
    extra_sample_id_list = []
    extra_researchitem_id_list = []

    # older versions saved a bool for include linked => false equals to "none", true equals to "direct"
    if include_linked is False:
        include_linked = "none"
    elif include_linked is True:
        include_linked = "direct"

    if include_linked.lower() == "none":
        return extra_exp_id_list, extra_sample_id_list, extra_researchitem_id_list

    if include_linked == "direct":
        extra_exp_id_list, extra_sample_id_list, extra_researchitem_id_list = (
            get_linked_items(exp_id_list, sample_id_list, researchitem_id_list)
        )
        return extra_exp_id_list, extra_sample_id_list, extra_researchitem_id_list

    if include_linked == "all":
        extra_exp_id_set = set(extra_exp_id_list)
        extra_sample_id_set = set(extra_sample_id_list)
        extra_researchitem_id_set = set(extra_researchitem_id_list)
        found_exp_id_list = list(exp_id_list)
        found_sample_id_list = list(sample_id_list)
        found_researchitem_id_list = list(researchitem_id_list)
        while True:
            temp_exp_id_list, temp_sample_id_list, temp_researchitem_id_list = (
                get_linked_items(
                    found_exp_id_list, found_sample_id_list, found_researchitem_id_list
                )
            )

            found_exp_id_list = list(set(temp_exp_id_list) - extra_exp_id_set)
            extra_exp_id_set.update(temp_exp_id_list)

            found_sample_id_list = list(set(temp_sample_id_list) - extra_sample_id_set)
            extra_sample_id_set.update(found_sample_id_list)

            found_researchitem_id_list = list(
                set(temp_researchitem_id_list) - extra_researchitem_id_set
            )
            extra_researchitem_id_set.update(found_researchitem_id_list)

            if (
                not found_exp_id_list
                and not found_sample_id_list
                and not found_researchitem_id_list
            ):
                break

        return (
            list(extra_exp_id_set),
            list(extra_sample_id_set),
            list(extra_researchitem_id_set),
        )


def get_linked_items(exp_id_list, sample_id_list, researchitem_id_list):
    id_list = []
    found_exp_id_set = set()
    found_sample_id_set = set()
    found_researchitem_id_set = set()

    if exp_id_list:
        id_list.extend(exp_id_list)

    if sample_id_list:
        id_list.extend(sample_id_list)

    if researchitem_id_list:
        id_list.extend(researchitem_id_list)

    links = (
        get_db()
        .db["Link"]
        .find(
            {
                "$or": [
                    {"DataID1": {"$in": id_list}},
                    {"DataID2": {"$in": id_list}},
                ]
            }
        )
    )
    id_set = set(id_list)
    for link in links:
        if link["DataID1"] in id_set:
            if link["Collection2"] == "Experiment":
                found_exp_id_set.add(link["DataID2"])
            elif link["Collection2"] == "Sample":
                found_sample_id_set.add(link["DataID2"])
            elif link["Collection2"] == "ResearchItem":
                found_researchitem_id_set.add(link["DataID2"])
        else:
            if link["Collection1"] == "Experiment":
                found_exp_id_set.add(link["DataID1"])
            elif link["Collection1"] == "Sample":
                found_sample_id_set.add(link["DataID1"])
            elif link["Collection1"] == "ResearchItem":
                found_researchitem_id_set.add(link["DataID1"])

    extra_exp_id_list = list(found_exp_id_set - set(exp_id_list))
    extra_sample_id_list = list(found_sample_id_set - set(sample_id_list))
    extra_researchitem_id_list = list(
        found_researchitem_id_set - set(researchitem_id_list)
    )

    return extra_exp_id_list, extra_sample_id_list, extra_researchitem_id_list


def add_item_to_groups_item_mapping(item, groups_item_mapping, category):
    for g_id in item["GroupIDList"]:
        if g_id not in groups_item_mapping:
            groups_item_mapping[g_id] = {}
        if category not in groups_item_mapping[g_id]:
            groups_item_mapping[g_id][category] = []
        groups_item_mapping[g_id][category].append(item)


def create_result_list(groups, subgroup_mapping, group_item_mapping):
    result_list = []
    for group in groups:
        group_node = {
            "id": str(group["_id"]),
            "name": group["Name"],
            "group_id": str(group["_id"]),
            "short_id": group["ShortID"],
            "parent": 0 if not group["GroupID"] else str(group["GroupID"]),
            "droppable": True,
            "expandable": True,
            "type": "Groups",
            "show_type": "groups",
            "visible": True,
            "text": group["Name"],
        }
        result_list.append(group_node)
        add_subgroup_nodes(
            group["_id"], subgroup_mapping, group_item_mapping, result_list
        )

        # if group["_id"] in subgroup_mapping:
        #     for subgroup in subgroup_mapping[group["_id"]]:
        #         sub_group_node = {
        #             "id": str(subgroup['_id']),
        #             "name": subgroup["Name"],
        #             "group_id": str(subgroup["_id"]),
        #             "short_id": subgroup['ShortID'],
        #             "parent": 0 if not subgroup["GroupID"] else str(subgroup["GroupID"]),
        #             "droppable": True,
        #             "expandable": True,
        #             "type": "Groups",
        #             "show_type": "groups",
        #             "visible": True,
        #             "text": subgroup["Name"],
        #         }
        #         result_list.append(sub_group_node)
        #
        #         add_cat_nodes(result_list, subgroup, group_item_mapping)

        add_cat_nodes(result_list, group, group_item_mapping)

    return result_list


def add_subgroup_nodes(group_id, subgroup_mapping, group_item_mapping, result_list):
    if group_id in subgroup_mapping:
        for subgroup in subgroup_mapping[group_id]:
            sub_group_node = {
                "id": str(subgroup["_id"]),
                "name": subgroup["Name"],
                "group_id": str(subgroup["_id"]),
                "short_id": subgroup["ShortID"],
                "parent": 0 if not subgroup["GroupID"] else str(subgroup["GroupID"]),
                "droppable": True,
                "expandable": True,
                "type": "Groups",
                "show_type": "groups",
                "visible": True,
                "text": subgroup["Name"],
            }
            result_list.append(sub_group_node)
            add_cat_nodes(result_list, subgroup, group_item_mapping)
            add_subgroup_nodes(
                subgroup["_id"], subgroup_mapping, group_item_mapping, result_list
            )


def add_cat_nodes(result_list, group, group_item_mapping):
    if not group["_id"] in group_item_mapping:
        return
    for cat in group_item_mapping[group["_id"]]:
        cat_node = {
            "id": f"{str(group['_id'])}/sep/{cat}",
            "name": cat,
            "type": cat,
            "show_type": cat,
            "short_id": "",
            "parent": str(group["_id"]),
            "droppable": False,
            "expandable": True,
            "group_id": str(group["_id"]),
            "visible": True,
            "text": cat,
            "field_data_id_list": [],
        }
        result_list.append(cat_node)

        for item in group_item_mapping[group["_id"]][cat]:
            item_node = {
                "id": str(item["_id"]),
                "name": item["Name"],
                "type": cat,
                "show_type": cat,
                "short_id": item["ShortID"],
                "parent": str(cat_node["id"]),
                "droppable": False,
                "expandable": False,
                "group_id": str(group["_id"]),
                "visible": True,
                "text": item["Name"],
            }
            result_list.append(item_node)


def prepare_node(item_id, item_name, item_short_id, 
                 group_id, parent_id, category, droppable, 
                 expandable):  
    
    node = {
        "id": str(item_id),
        "name": item_name,
        "type": category,
        "show_type": category.lower(),
        "short_id": item_short_id,
        "parent": parent_id,
        "droppable": droppable,
        "expandable": expandable,
        "group_id": str(group_id),
        "visible": True,
        "text": item_name,
    }
    return node


def get_all_parent_groups(group_id_list: list):
    groups = list(
        get_db()
        .db["Group"]
        .find({"_id": {"$in": group_id_list}}, {"_id": 1, "GroupID": 1})
    )

    missing_group = True
    missing_group_id_list = []
    total_group_id_set = {g["_id"] for g in groups}
    groups_to_be_iterated = list(groups)
    extra_groups = []
    while missing_group:
        for group in groups_to_be_iterated:
            if not group["GroupID"]:
                continue
            if group["GroupID"] not in total_group_id_set:
                missing_group_id_list.append(group["GroupID"])
        if missing_group_id_list:
            new_groups = list(
                get_db()
                .db["Group"]
                .find({"_id": {"$in": missing_group_id_list}}, {"_id": 1, "GroupID": 1})
            )
            groups_to_be_iterated = new_groups
            extra_groups.extend(new_groups)
            for g in new_groups:
                total_group_id_set.add(g["_id"])
            missing_group_id_list = []
        else:
            missing_group = False

    return [g["_id"] for g in extra_groups]


def get_date_from_option_string(option_string):
    if option_string == "today":
        today = datetime.today().date()
        value_min = datetime.combine(today, time(0, 0))
        value_max = datetime.combine(today, time(23, 59))
    elif option_string == "yesterday":
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        value_min = datetime.combine(yesterday, time(0, 0))
        value_max = datetime.combine(yesterday, time(23, 59))
    elif option_string == "this week":
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        value_min = datetime.combine(start_of_week, time(0, 0))
        value_max = datetime.combine(end_of_week, time(23, 59))
    elif option_string == "last week":
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_last_week = start_of_week - timedelta(days=7)
        end_of_last_week = start_of_week - timedelta(days=1)
        value_min = datetime.combine(start_of_last_week, time(0, 0))
        value_max = datetime.combine(end_of_last_week, time(23, 59))
    elif option_string == "this month":
        today = datetime.today()
        start_of_month = datetime(today.year, today.month, 1)
        last_day_of_month = calendar.monthrange(today.year, today.month)[1]
        end_of_month = datetime(today.year, today.month, last_day_of_month)
        value_min = datetime.combine(start_of_month, time(0, 0))
        value_max = datetime.combine(end_of_month, time(23, 59))
    elif option_string == "last month":
        today = datetime.today()
        if today.month == 1:
            start_of_last_month = datetime(today.year - 1, 12, 1)
        else:
            start_of_last_month = datetime(today.year, today.month - 1, 1)
        last_day_of_last_month = calendar.monthrange(
            start_of_last_month.year, start_of_last_month.month
        )[1]
        end_of_last_month = datetime(
            start_of_last_month.year, start_of_last_month.month, last_day_of_last_month
        )
        value_min = datetime.combine(start_of_last_month, time(0, 0))
        value_max = datetime.combine(end_of_last_month, time(23, 59))
    elif option_string == "this year":
        today = datetime.today()
        start_of_year = datetime(today.year, 1, 1)
        end_of_year = datetime(today.year, 12, 31)
        value_min = datetime.combine(start_of_year, time(0, 0))
        value_max = datetime.combine(end_of_year, time(23, 59))
    else:
        raise ValueError("invalid option string")

    return value_min, value_max


# def get_filtered_index_without_group_id_list(project_id, name_filter, combo_filter,
#                                              numeric_filter, groups_filter,
#                                              samples_filter, experiments_filter, researchitems_filter,
#                                              checks_filter, recent, date_filter, date_created, text_filter,
#                                              include_field_data, include_linked, displayed_categories):
#     direction = pymongo.ASCENDING
#     if recent:
#         order_by = "Date"
#         direction = pymongo.DESCENDING
#     else:
#         order_by = "NameLower"
#
#     if name_filter or groups_filter or samples_filter or experiments_filter or researchitems_filter or date_created:
#         results = get_filtered_index_with_group_id_list(project_id, [], name_filter, combo_filter,
#                                                         numeric_filter, groups_filter,
#                                                         samples_filter, experiments_filter, researchitems_filter,
#                                                         checks_filter, recent, date_filter, date_created, text_filter,
#                                                         include_field_data, include_linked, displayed_categories,
#                                                         project_wide=True, limit_result_top_group_ids=100)
#         print(len(results))
#         return results
#
#     result_list = []
#     all_checked = False
#     counter = 1
#     factor = 8
#     max_number_groups = get_db().db["Group"].count_documents({"ProjectID": project_id, "GroupID": None})
#     found_top_level_groups = 0
#     while found_top_level_groups < current_app.groups_per_page and not all_checked:
#
#         start, end = get_start_end(counter, factor)
#         if end >= max_number_groups:
#             all_checked = True
#
#         # get certain amount of top level groups
#         toplevel_groups = get_db().db["Group"].find({"ProjectID": project_id, "GroupID": None}, {"_id": 1}).sort(
#             order_by, direction).skip(start).limit(end)
#
#         group_id_list = [g["_id"] for g in toplevel_groups]
#         results = get_filtered_index_with_group_id_list(project_id, group_id_list, name_filter, combo_filter,
#                                                         numeric_filter, groups_filter,
#                                                         samples_filter, experiments_filter, researchitems_filter,
#                                                         checks_filter, recent, date_filter, date_created, text_filter,
#                                                         include_field_data, include_linked, displayed_categories)
#         for r in results:
#             if r["parent"] == 0:
#                 if found_top_level_groups < current_app.groups_per_page:
#                     result_list.append(r)
#                 found_top_level_groups += 1
#             else:
#                 result_list.append(r)
#
#         counter += 1
#         print("Bla", counter, found_top_level_groups)
#     return result_list


def get_filtered_index_with_group_id_list(
    project_id,
    top_level_group_id_list,
    name_filter,
    combo_filter,
    numeric_filter,
    groups_filter,
    samples_filter,
    experiments_filter,
    researchitems_filter,
    checks_filter,
    recent,
    date_filter,
    date_created,
    text_filter,
    include_field_data,
    include_linked,
    displayed_categories,
    project_wide=False,
):
    top_level_group_id_list = [bson.ObjectId(g) for g in top_level_group_id_list]

    cat_id_list, category_mapping = get_valid_categories(
        project_id, displayed_categories
    )

    (
        name_query_groups,
        show_as_empty_groups,
        exp_id_list,
        sample_id_list,
        researchitem_id_list,
    ) = get_filtered(
        project_id,
        top_level_group_id_list,
        name_filter,
        combo_filter,
        numeric_filter,
        groups_filter,
        samples_filter,
        experiments_filter,
        researchitems_filter,
        checks_filter,
        recent,
        date_filter,
        date_created,
        text_filter,
        displayed_categories,
        include_linked,
        project_wide,
        cat_id_list,
    )

    result_group_id_list, group_item_mapping = (
        prepare_result_group_id_list_and_group_item_mapping(
            top_level_group_id_list,
            name_query_groups,
            show_as_empty_groups,
            exp_id_list,
            sample_id_list,
            researchitem_id_list,
            category_mapping,
        )
    )
    direction = pymongo.ASCENDING
    if recent:
        order_by = "Date"
        direction = pymongo.DESCENDING
    else:
        order_by = "NameLower"

    groups = (
        get_db()
        .db["Group"]
        .find(
            {"_id": {"$in": result_group_id_list}},
            {"_id": 1, "Name": 1, "GroupID": 1, "ShortID": 1},
        )
        .sort(order_by, direction)
    )
    top_level_groups = []
    subgroup_mapping = {}

    for g in groups:
        if g["GroupID"] is None:
            top_level_groups.append(g)
        else:
            if g["GroupID"] not in subgroup_mapping:
                subgroup_mapping[g["GroupID"]] = []
            subgroup_mapping[g["GroupID"]].append(g)

    result_list = create_result_list(
        top_level_groups, subgroup_mapping, group_item_mapping
    )
    return result_list


def get_page_group_mapping(
    project_id,
    nameFilter="",
    comboFilter=[],
    numericFilter=[],
    groupFilter=[],
    sampleFilter=[],
    experimentFilter=[],
    researchItemFilter=[],
    checkFilter=[],
    recent=False,
    date_filter=[],
    date_created=[],
    text_filter=[],
    displayed_categories=[],
    include_linked=False,
):

    filter_applied = check_if_filter_applied(
        nameFilter,
        comboFilter,
        numericFilter,
        groupFilter,
        sampleFilter,
        experimentFilter,
        researchItemFilter,
        checkFilter,
        date_filter,
        date_created,
        text_filter,
    )
    project_id = bson.ObjectId(project_id)

    if not filter_applied:
        s = _time.time()
        page_group_mapping = get_not_filtered_page_group_mapping(
            project_id=project_id,
            recent=recent,
            displayed_categories=displayed_categories,
        )
        print("No filter page mapping", _time.time() - s)

    else:
        direction = pymongo.ASCENDING
        if recent:
            order_by = "Date"
            direction = pymongo.DESCENDING
        else:
            order_by = "NameLower"
        s = _time.time()
        toplevel_groups = (
            get_db()
            .db["Group"]
            .find({"ProjectID": project_id, "GroupID": None}, {"_id": 1})
            .sort(order_by, direction)
        )
        group_id_list = [g["_id"] for g in toplevel_groups]
        page_group_mapping = get_filtered_page_group_mapping(
            project_id,
            group_id_list,
            nameFilter,
            comboFilter,
            numericFilter,
            groupFilter,
            sampleFilter,
            experimentFilter,
            researchItemFilter,
            checkFilter,
            recent,
            date_filter,
            date_created,
            text_filter,
            displayed_categories=displayed_categories,
            include_linked=include_linked,
        )
        print("filtered page mapping", _time.time() - s)
    return page_group_mapping


def get_not_filtered_page_group_mapping(project_id, recent, displayed_categories):
    direction = pymongo.ASCENDING
    if recent:
        order_by = "Date"
        direction = pymongo.DESCENDING
    else:
        order_by = "NameLower"

    toplevel_groups = (
        get_db()
        .db["Group"]
        .find({"ProjectID": project_id, "GroupID": None}, {"_id": 1})
        .sort(order_by, direction)
    )

    group_id_list = [str(g["_id"]) for g in toplevel_groups]

    page_group_id_mapping = {}
    page = 1

    for i in range(0, len(group_id_list), current_app.groups_per_page):
        page_group_id_mapping[page] = group_id_list[i : i + current_app.groups_per_page]
        page += 1

    result_dict = {"maxPage": page - 1, "pageGroupMapping": page_group_id_mapping}

    return result_dict


def get_filtered_page_group_mapping(
    project_id,
    top_level_group_id_list,
    name_filter,
    combo_filter,
    numeric_filter,
    groups_filter,
    samples_filter,
    experiments_filter,
    researchitems_filter,
    checks_filter,
    recent,
    date_filter,
    date_created,
    text_filter,
    displayed_categories,
    include_linked,
):
    s = _time.time()

    cat_id_list, category_mapping = get_valid_categories(
        project_id, displayed_categories
    )

    project_wide = True
    (
        name_query_groups,
        show_as_empty_groups,
        exp_id_list,
        sample_id_list,
        researchitem_id_list,
    ) = get_filtered(
        project_id,
        top_level_group_id_list,
        name_filter,
        combo_filter,
        numeric_filter,
        groups_filter,
        samples_filter,
        experiments_filter,
        researchitems_filter,
        checks_filter,
        recent,
        date_filter,
        date_created,
        text_filter,
        displayed_categories,
        include_linked,
        project_wide,
        cat_id_list,
    )

    result_group_id_list, group_item_mapping = (
        prepare_result_group_id_list_and_group_item_mapping(
            top_level_group_id_list,
            name_query_groups,
            show_as_empty_groups,
            exp_id_list,
            sample_id_list,
            researchitem_id_list,
            category_mapping,
        )
    )

    direction = pymongo.ASCENDING
    if recent:
        order_by = "Date"
        direction = pymongo.DESCENDING
    else:
        order_by = "NameLower"

    toplevel_groups = (
        get_db()
        .db["Group"]
        .find({"_id": {"$in": result_group_id_list}, "GroupID": None}, {"_id": 1})
        .sort(order_by, direction)
    )

    group_id_list = [str(g["_id"]) for g in toplevel_groups]

    page_group_id_mapping = {}
    page = 0

    for i in range(0, len(group_id_list), current_app.groups_per_page):
        page += 1
        page_group_id_mapping[page] = group_id_list[i : i + current_app.groups_per_page]

    result_dict = {"maxPage": page, "pageGroupMapping": page_group_id_mapping}
    return result_dict


def get_filtered(
    project_id,
    top_level_group_id_list,
    name_filter,
    combo_filter,
    numeric_filter,
    groups_filter,
    samples_filter,
    experiments_filter,
    researchitems_filter,
    checks_filter,
    recent,
    date_filter,
    date_created,
    text_filter,
    displayed_categories,
    include_linked,
    project_wide,
    cat_id_list,
):
    s = _time.time()
    (
        group_id_list_including_subgroups,
        name_query_groups,
        show_as_empty_groups,
        unfiltered_group_id_list_including_subgroups,
    ) = filter_groups(
        project_id,
        top_level_group_id_list,
        groups_filter,
        name_filter,
        combo_filter,
        numeric_filter,
        checks_filter,
        date_filter,
        date_created,
        text_filter,
        project_wide,
    )

    exp_id_list = []
    if not project_wide and (
        "Experiments" in displayed_categories or "all" in displayed_categories
    ):
        exps = (
            get_db()
            .db["Experiment"]
            .find(
                {"GroupIDList": {"$in": group_id_list_including_subgroups}}, {"_id": 1}
            )
        )
        exp_id_list = [e["_id"] for e in exps]
    sample_id_list = []
    if not project_wide and (
        "Samples" in displayed_categories or "all" in displayed_categories
    ):
        samples = (
            get_db()
            .db["Sample"]
            .find(
                {"GroupIDList": {"$in": group_id_list_including_subgroups}}, {"_id": 1}
            )
        )
        sample_id_list = [s["_id"] for s in samples]

    if project_wide:
        researchitem_id_list = []
    else:
        query = {
            "GroupIDList": {"$in": group_id_list_including_subgroups},
            "ResearchCategoryID": {"$in": cat_id_list},
        }
        researchitems = get_db().db["ResearchItem"].find(query, {"_id": 1})
        researchitem_id_list = [r["_id"] for r in researchitems]

    exp_id_list, sample_id_list, researchitem_id_list = filter_items(
        project_id,
        group_id_list_including_subgroups,
        unfiltered_group_id_list_including_subgroups,
        name_query_groups,
        exp_id_list,
        sample_id_list,
        researchitem_id_list,
        experiments_filter,
        samples_filter,
        researchitems_filter,
        name_filter,
        combo_filter,
        numeric_filter,
        checks_filter,
        date_filter,
        date_created,
        text_filter,
        include_linked,
        cat_id_list,
        project_wide,
        displayed_categories,
    )
    return (
        name_query_groups,
        show_as_empty_groups,
        exp_id_list,
        sample_id_list,
        researchitem_id_list,
    )


def prepare_result_group_id_list_and_group_item_mapping(
    top_level_group_id_list,
    name_query_groups,
    show_as_empty_groups,
    exp_id_list,
    sample_id_list,
    researchitem_id_list,
    category_mapping,
):
    top_level_group_id_set = set(top_level_group_id_list)

    result_group_id_list = []
    result_group_id_list.extend(name_query_groups)
    result_group_id_list.extend(show_as_empty_groups)

    group_item_mapping = {}
    if exp_id_list:
        exps = (
            get_db()
            .db["Experiment"]
            .find(
                {"_id": {"$in": exp_id_list}},
                {"_id": 1, "GroupIDList": 1, "Name": 1, "ShortID": 1},
            )
        )
        for exp in exps:
            result_group_id_list.extend(exp["GroupIDList"])
            add_item_to_groups_item_mapping(exp, group_item_mapping, "Experiments")

    if sample_id_list:
        samples = (
            get_db()
            .db["Sample"]
            .find(
                {"_id": {"$in": sample_id_list}},
                {"_id": 1, "GroupIDList": 1, "Name": 1, "ShortID": 1},
            )
        )
        for sample in samples:
            result_group_id_list.extend(sample["GroupIDList"])
            add_item_to_groups_item_mapping(sample, group_item_mapping, "Samples")

    if researchitem_id_list:
        researchitems = (
            get_db()
            .db["ResearchItem"]
            .find(
                {"_id": {"$in": researchitem_id_list}},
                {
                    "_id": 1,
                    "GroupIDList": 1,
                    "Name": 1,
                    "ShortID": 1,
                    "ResearchCategoryID": 1,
                },
            )
        )
        for ri in researchitems:
            result_group_id_list.extend(ri["GroupIDList"])
            cat_name = category_mapping[ri["ResearchCategoryID"]]
            add_item_to_groups_item_mapping(ri, group_item_mapping, cat_name)

    maybe_not_parent_groups = []
    for g in result_group_id_list:
        if g not in top_level_group_id_set:
            maybe_not_parent_groups.append(g)
    extra_groups_id_list = get_all_parent_groups(maybe_not_parent_groups)
    result_group_id_list.extend(extra_groups_id_list)

    return result_group_id_list, group_item_mapping


def filter_groups(
    project_id,
    group_id_list,
    groups_filter,
    name_filter,
    combo_filter,
    numeric_filter,
    checks_filter,
    date_filter,
    date_created,
    text_filter,
    project_wide=False,
):
    show_as_empty_groups = []
    name_query_groups = []
    unfiltered_group_id_list_including_subgroups = []
    unfiltered_group_id_list_including_subgroups.extend(group_id_list)
    subgroup_id_list = get_subgroups(group_id_list)
    unfiltered_group_id_list_including_subgroups.extend(subgroup_id_list)
    group_id_list_including_subgroups = []
    group_id_list_including_subgroups.extend(group_id_list)
    group_id_list_including_subgroups.extend(subgroup_id_list)

    if name_filter:
        if project_wide:
            name_query = {
                "ProjectID": project_id,
                "NameLower": {"$regex": name_filter.lower()},
            }
        else:
            name_query = {
                "_id": {"$in": group_id_list_including_subgroups},
                "NameLower": {"$regex": name_filter.lower()},
            }
        groups = get_db().db["Group"].find(name_query, {"_id": 1})
        group_id_list = [g["_id"] for g in groups]
        subgroup_id_list = get_subgroups(group_id_list)
        group_id_list_including_subgroups.extend(group_id_list)
        group_id_list_including_subgroups.extend(subgroup_id_list)
        name_query_groups.extend(group_id_list)
        name_query_groups.extend(subgroup_id_list)

    if groups_filter:
        if "all" not in groups_filter:
            groups_filter = [bson.ObjectId(g) for g in groups_filter]
            new_group_id_list = []
            for g_id in group_id_list_including_subgroups:
                if g_id in groups_filter:
                    new_group_id_list.append(g_id)
                    show_as_empty_groups.append(g_id)
            group_id_list_including_subgroups = new_group_id_list
        else:
            show_as_empty_groups.extend(group_id_list_including_subgroups)

    date_created_query = get_date_created_query(date_created)

    field_data_query = {}
    if combo_filter or numeric_filter or checks_filter or date_filter or text_filter:
        field_data_query = get_field_data_query_objects(
            combo_filter=combo_filter,
            numeric_filter=numeric_filter,
            checks_filter=checks_filter,
            date_filter=date_filter,
            text_filter=text_filter,
        )

    if field_data_query or date_created_query:
        query = {
            "$and": [
                {"_id": {"$in": group_id_list_including_subgroups}},
                field_data_query,
                date_created_query,
            ]
        }
        groups = get_db().db["Group"].find(query, {"_id": 1})
        show_as_empty_groups.extend([g["_id"] for g in groups])

    return (
        group_id_list_including_subgroups,
        name_query_groups,
        show_as_empty_groups,
        unfiltered_group_id_list_including_subgroups,
    )


def filter_items(
    project_id,
    group_id_list_including_subgroups,
    unfiltered_group_id_list_including_subgroups,
    name_query_groups,
    exp_id_list,
    sample_id_list,
    researchitem_id_list,
    exp_filter,
    sample_filter,
    researchitem_filter,
    name_filter,
    combo_filter,
    numeric_filter,
    checks_filter,
    date_filter,
    date_created,
    text_filter,
    include_linked,
    category_id_list,
    project_wide,
    displayed_categories,
):
    """
    Filters various items such as experiments, samples, and research items based on multiple filter criteria.

    Parameters:
        unfiltered_group_id_list_including_subgroups (list): List of group IDs that are not filtered yet. Include all subgroups.
        name_query_groups: groups that have been found due to a name query => all items of this group will be included

    """

    s = _time.time()

    # check if filter applied except of group filter, since that one is already checked
    filter_applied = check_if_filter_applied(
        name_filter=name_filter,
        combo_filter=combo_filter,
        numeric_filter=numeric_filter,
        samples_filter=sample_filter,
        experiments_filter=exp_filter,
        researchitems_filter=researchitem_filter,
        checks_filter=checks_filter,
        date_filter=date_filter,
        groups_filter=[],
        date_created=date_created,
        text_filter=text_filter,
    )

    if not filter_applied:
        if project_wide:
            # exp_id_list etc. still empty: get all items belonging to group_id_list_including_subgroups
            if "Experiments" in displayed_categories or "all" in displayed_categories:
                exps = (
                    get_db()
                    .db["Experiment"]
                    .find(
                        {"GroupIDList": {"$in": group_id_list_including_subgroups}},
                        {"_id": 1},
                    )
                )
                exp_id_list = [e["_id"] for e in exps]

            if "Samples" in displayed_categories or "all" in displayed_categories:
                samples = (
                    get_db()
                    .db["Sample"]
                    .find(
                        {"GroupIDList": {"$in": group_id_list_including_subgroups}},
                        {"_id": 1},
                    )
                )
                sample_id_list = [s["_id"] for s in samples]
            if category_id_list:
                query = {
                    "GroupIDList": {"$in": group_id_list_including_subgroups},
                    "ResearchCategoryID": {"$in": category_id_list},
                }
                researchitems = get_db().db["ResearchItem"].find(query, {"_id": 1})
                researchitem_id_list = [r["_id"] for r in researchitems]

        return exp_id_list, sample_id_list, researchitem_id_list

    # name filter is applied on the unfiltered groups, since items from groups that have not been found will be shown anyway
    if name_filter:
        if project_wide:
            name_query = {
                "$or": [
                    {
                        "ProjectID": project_id,
                        "NameLower": {"$regex": name_filter.lower()},
                    },
                    {"GroupIDList": {"in": name_query_groups}},
                ]
            }
            index_to_be_used = "project_namelower"
        else:
            name_query = {
                "$or": [
                    {
                        "GroupIDList": {
                            "$in": unfiltered_group_id_list_including_subgroups
                        },
                        "NameLower": {"$regex": name_filter.lower()},
                    },
                    {"GroupIDList": {"in": name_query_groups}},
                ]
            }
            index_to_be_used = "group_namelower"
        if "Experiments" in displayed_categories or "all" in displayed_categories:
            exps = (
                get_db()
                .db["Experiment"]
                .find(name_query, {"_id": 1})
                .hint(index_to_be_used)
            )
            exp_id_list = [e["_id"] for e in exps]

        if "Samples" in displayed_categories or "all" in displayed_categories:
            samples = get_db().db["Sample"].find(name_query, {"_id": 1})
            sample_id_list = [s["_id"] for s in samples]

        if category_id_list:
            query = {
                "$and": [{"ResearchCategoryID": {"$in": category_id_list}}, name_query]
            }
            researchitems = get_db().db["ResearchItem"].find(query, {"_id": 1})
            researchitem_id_list = [ri["_id"] for ri in researchitems]

    if exp_filter or sample_filter or researchitem_filter:
        if project_wide:
            if "all" in exp_filter:
                if not exp_id_list:
                    if (
                        "Experiments" in displayed_categories
                        or "all" in displayed_categories
                    ):
                        exps = (
                            get_db()
                            .db["Experiment"]
                            .find({"ProjectID": project_id}, {"_id": 1})
                        )
                        exp_id_list = [e["_id"] for e in exps]
            else:
                if not exp_id_list:
                    exp_id_list = [bson.ObjectId(e) for e in exp_filter]

            if "all" in sample_filter:
                if not sample_id_list:
                    if (
                        "Samples" in displayed_categories
                        or "all" in displayed_categories
                    ):
                        samples = (
                            get_db()
                            .db["Sample"]
                            .find({"ProjectID": project_id}, {"_id": 1})
                        )
                        sample_id_list = [s["_id"] for s in samples]
            else:
                if not sample_id_list:
                    sample_id_list = [bson.ObjectId(s) for s in sample_filter]

            if "all" in researchitem_filter:
                if not researchitem_id_list:
                    if category_id_list:
                        researchitems = (
                            get_db()
                            .db["ResearchItem"]
                            .find(
                                {
                                    "ProjectID": project_id,
                                    "ResearchCategoryID": {"$in": category_id_list},
                                },
                                {"_id": 1},
                            )
                        )
                        researchitem_id_list = [r["_id"] for r in researchitems]
            else:
                if not researchitem_id_list:
                    researchitem_id_list = [
                        bson.ObjectId(r) for r in researchitem_filter
                    ]

        if "all" not in exp_filter:
            exp_filter = [bson.ObjectId(e) for e in exp_filter]
            new_exp_id_list = []
            for e_id in exp_id_list:
                if e_id in exp_filter:
                    new_exp_id_list.append(e_id)
            exp_id_list = new_exp_id_list

        if "all" not in sample_filter:
            sample_filter = [bson.ObjectId(s) for s in sample_filter]
            new_sample_id_list = []
            for s_id in sample_id_list:
                if s_id in sample_filter:
                    new_sample_id_list.append(s_id)
            sample_id_list = new_sample_id_list

        if "all" not in researchitem_filter:
            researchitem_filter = [bson.ObjectId(r) for r in researchitem_filter]
            new_researchitem_id_list = []
            for ri_id in researchitem_id_list:
                if ri_id in researchitem_filter:
                    new_researchitem_id_list.append(ri_id)
            researchitem_id_list = new_researchitem_id_list

    date_created_query = get_date_created_query(date_created)
    field_data_query = {}
    if combo_filter or numeric_filter or checks_filter or date_filter or text_filter:
        field_data_query = get_field_data_query_objects(
            combo_filter=combo_filter,
            numeric_filter=numeric_filter,
            checks_filter=checks_filter,
            date_filter=date_filter,
            text_filter=text_filter,
        )

    if date_created_query or field_data_query:
        if project_wide:
            query = {
                "$and": [
                    {"ProjectID": project_id},
                    date_created_query,
                    field_data_query,
                ]
            }
            if "Experiments" in displayed_categories or "all" in displayed_categories:
                exps = get_db().db["Experiment"].find(query, {"_id": 1})
                exp_id_list = [item["_id"] for item in exps]

            if "Samples" in displayed_categories or "all" in displayed_categories:
                samples = get_db().db["Sample"].find(query, {"_id": 1})
                sample_id_list = [item["_id"] for item in samples]

            if category_id_list:
                query["$and"].append({"ResearchCategoryID": {"$in": category_id_list}})
                # query.update({"ResearchCategoryID": {"$in": category_id_list}})
                researchitems = get_db().db["ResearchItem"].find(query, {"_id": 1})
                researchitem_id_list = [item["_id"] for item in researchitems]

        else:
            item_id_list = []
            query = {
                "$and": [
                    {"_id": {"$in": item_id_list}},
                    date_created_query,
                    field_data_query,
                ]
            }
            if exp_id_list:
                item_id_list.extend(exp_id_list)
                exps = get_db().db["Experiment"].find(query, {"_id": 1})
                exp_id_list = [item["_id"] for item in exps]
            if sample_id_list:
                item_id_list.clear()
                item_id_list.extend(sample_id_list)
                samples = get_db().db["Sample"].find(query, {"_id": 1})
                sample_id_list = [item["_id"] for item in samples]
            if researchitem_id_list:
                item_id_list.clear()
                item_id_list.extend(researchitem_id_list)
                researchitems = get_db().db["ResearchItem"].find(query, {"_id": 1})
                researchitem_id_list = [item["_id"] for item in researchitems]

    # if name_query_exps:
    #     exp_id_list.extend(name_query_exps)
    # if name_query_samples:
    #     sample_id_list.extend(name_query_samples)
    # if name_query_researchitems:
    #     researchitem_id_list.extend(name_query_researchitems)

    extra_exp_id_list, extra_sample_id_list, extra_researchitem_id_list = (
        get_linked_items_recursive(
            include_linked, exp_id_list, sample_id_list, researchitem_id_list
        )
    )

    if "Experiments" in displayed_categories or "all" in displayed_categories:
        exp_id_list.extend(extra_exp_id_list)
    if "Samples" in displayed_categories or "all" in displayed_categories:
        sample_id_list.extend(extra_sample_id_list)
    if extra_researchitem_id_list and category_id_list:
        query = {
            "_id": {"$in": extra_researchitem_id_list},
            "ResearchCategoryID": {"$in": category_id_list},
        }
        extra_items = get_db().db["ResearchItem"].find(query, {"_id": 1})
        researchitem_id_list.extend(e["_id"] for e in extra_items)

    return exp_id_list, sample_id_list, researchitem_id_list


def get_date_created_query(date_created):
    date_created_query = {}
    if not date_created:
        return date_created_query
    value_min = value_max = None
    custom_date = False
    if "option" in date_created:
        if date_created["option"].lower() == "custom":
            custom_date = True
    else:
        custom_date = True
    if custom_date:
        try:
            value_min = datetime.fromisoformat(date_created["min"])
            value_max = datetime.fromisoformat(date_created["max"])
        except:
            pass
    else:
        value_min, value_max = get_date_from_option_string(
            date_created["option"].lower()
        )
    if value_min and value_max:
        date_created_query["Date"] = {"$gte": value_min, "$lte": value_max}
    return date_created_query


def get_valid_categories(project_id, displayed_categories):
    displayed_categories = list(displayed_categories)
    if "Experiements" in displayed_categories:
        displayed_categories.remove("Experiments")
    if "Samples" in displayed_categories:
        displayed_categories.remove("Samples")
    if not displayed_categories:
        return [], {}

    categories = (
        get_db()
        .db["ResearchCategory"]
        .find({"ProjectID": project_id}, {"_id": 1, "Name": 1})
        .sort("Name")
    )
    category_mapping = {c["_id"]: c["Name"] for c in categories}
    cat_id_list = []
    for cat_id in category_mapping:
        cat_name = category_mapping[cat_id]
        if cat_name in displayed_categories or "all" in displayed_categories:
            cat_id_list.append(cat_id)

    return cat_id_list, category_mapping


def get_page_item_mapping_dashboard(
    dataview_id,
    project_id,
    name_filter,
    combo_filter,
    numeric_filter,
    groups_filter,
    samples_filter,
    experiments_filter,
    researchitems_filter,
    checks_filter,
    date_filter,
    date_created,
    text_filter,
    include_linked,
    displayed_categories,
):

    filter_applied = check_if_filter_applied(
        name_filter,
        combo_filter,
        numeric_filter,
        groups_filter,
        samples_filter,
        experiments_filter,
        researchitems_filter,
        checks_filter,
        date_filter,
        date_created,
        text_filter,
    )
    if not filter_applied:
        return {"maxPage": 1, "pageItemMapping": {1: []}}

    cat_id_list, category_mapping = get_valid_categories(
        project_id, displayed_categories
    )

    project_wide = True
    toplevel_groups = (
        get_db()
        .db["Group"]
        .find({"ProjectID": project_id, "GroupID": None}, {"_id": 1})
    )
    top_level_group_id_list = [g["_id"] for g in toplevel_groups]

    (
        name_query_groups,
        show_as_empty_groups,
        exp_id_list,
        sample_id_list,
        researchitem_id_list,
    ) = get_filtered(
        project_id,
        top_level_group_id_list,
        name_filter,
        combo_filter,
        numeric_filter,
        groups_filter,
        samples_filter,
        experiments_filter,
        researchitems_filter,
        checks_filter,
        False,
        date_filter,
        date_created,
        text_filter,
        displayed_categories,
        include_linked,
        project_wide,
        cat_id_list,
    )

    exps = list(
        get_db()
        .db["Experiment"]
        .find({"_id": {"$in": exp_id_list}}, {"_id": 1, "Date": 1})
    )
    samples = list(
        get_db()
        .db["Sample"]
        .find({"_id": {"$in": sample_id_list}}, {"_id": 1, "Date": 1})
    )
    researchitems = list(
        get_db()
        .db["ResearchItem"]
        .find({"_id": {"$in": researchitem_id_list}}, {"_id": 1, "Date": 1})
    )

    items = []
    items.extend(exps)
    items.extend(samples)
    items.extend(researchitems)

    sorted_items = sorted(items, key=lambda x: x["Date"], reverse=True)

    page_item_mapping = {}
    page = 1
    items_per_page = current_app.groups_per_page
    item_id_list = []
    for i in range(0, len(sorted_items), items_per_page):
        start = i
        end = i + items_per_page
        items = [str(i["_id"]) for i in sorted_items[start:end]]
        item_id_list.extend(items)
        page_item_mapping[page] = items
        page += 1

    Update.update(
        "DataView", "ItemIDList", item_id_list, dataview_id, no_versioning=True
    )

    result_dict = {"maxPage": page - 1, "pageItemMapping": page_item_mapping}
    return result_dict


def check_if_filter_applied(
    name_filter,
    combo_filter,
    numeric_filter,
    groups_filter,
    samples_filter,
    experiments_filter,
    researchitems_filter,
    checks_filter,
    date_filter,
    date_created,
    text_filter,
):

    if (
        name_filter
        or combo_filter
        or groups_filter
        or samples_filter
        or experiments_filter
        or researchitems_filter
        or numeric_filter
        or date_filter
        or date_created
        or text_filter
        or checks_filter
    ):
        return True
    else:
        return False
