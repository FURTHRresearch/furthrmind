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


# noinspection PyUnresolvedReferences
def get_start_end(index):
    start = (index - 1) * current_app.groups_per_page
    end = start + current_app.groups_per_page
    return start, end


# noinspection PyUnresolvedReferences
def get_max_pages(count):
    max_pages = int(count / current_app.groups_per_page)
    if count % current_app.groups_per_page != 0:
        max_pages += 1
    return max_pages


# noinspection PyDefaultArgument
def get_filtered_project_index(projectId, nameFilter='', comboFilter=[], numericFilter=[], groupFilter=[],
                               sampleFilter=[], experimentFilter=[], researchItemFilter=[],
                               checkFilter=[], add_field_data_id_list=True, recent=False,
                               index=1, include_linked=False, date_filter=[], date_created=[],
                               text_filter=[], displayed_categories=[],
                               include_field_data=False):
    filter_applied = (nameFilter or comboFilter or groupFilter or sampleFilter or experimentFilter or
                      researchItemFilter or comboFilter or numericFilter or date_filter or date_created or
                      text_filter)

    if not filter_applied:
        s = _time.time()
        groups = get_no_filter(project_id=projectId, recent=recent, index=index, include_field_data=include_field_data,
                               displayed_categories=displayed_categories)
        print("No filter", _time.time() - s)

    else:
        s = _time.time()
        groups = get_filtered(projectId, nameFilter, comboFilter, numericFilter, groupFilter,
                              sampleFilter, experimentFilter, researchItemFilter,
                              checkFilter, recent, index, date_filter, date_created, text_filter,
                              include_field_data=include_field_data,
                              include_linked=include_linked, displayed_categories=displayed_categories)
        print("filter", _time.time() - s)
    return groups


def get_no_filter(project_id, recent, index, include_field_data, displayed_categories):
    # get top level groups
    # get subgroups
    # get exp, sample, resesearch item
    # build result list
    project_id = bson.ObjectId(project_id)
    direction = pymongo.ASCENDING
    if recent:
        order_by = "Date"
        direction = pymongo.DESCENDING
    else:
        order_by = "NameLower"
    start, end = get_start_end(index)

    toplevel_groups = get_db().db["Group"].find({"ProjectID": project_id, "GroupID": None}).sort(order_by,
                                                                                                 direction).skip(
        start).limit(end)
    toplevel_groups_count = get_db().db["Group"].count_documents({"ProjectID": project_id, "GroupID": None})
    # toplevel_groups = Group.objects(
    #     ProjectID=project_id, GroupID=None).order_by(order_by)
    max_pages = get_max_pages(toplevel_groups_count)

    toplevel_groups = list(toplevel_groups)
    sub_groups = get_subgroups(toplevel_groups)
    groups = list()
    groups.extend(toplevel_groups)
    groups.extend(sub_groups)
    group_id_list = [g["_id"] for g in groups]

    group_item_mapping = {}

    if "Experiments" in displayed_categories or "all" in displayed_categories:
        exps = get_db().db["Experiment"].find({"GroupIDList": {"$in": group_id_list}}).sort("Date", pymongo.DESCENDING)
        # exps = Experiment.objects(GroupIDList__in=group_id_list).order_by("-Date")
        for exp in exps:
            add_item_to_groups_item_mapping(exp, group_item_mapping, "Experiments")
    else:
        exps = []

    if "Samples" in displayed_categories or "all" in displayed_categories:
        samples = get_db().db["Sample"].find({"GroupIDList": {"$in": group_id_list}}).sort("Date", pymongo.DESCENDING)
        # samples = Sample.objects(GroupIDList__in=group_id_list).order_by("-Date")
        for sample in samples:
            add_item_to_groups_item_mapping(sample, group_item_mapping, "Samples")
    else:
        samples = []

        # get categories
    categories = get_db().db["ResearchCategory"].find({"ProjectID": project_id}).sort("Name")
    # categories = ResearchCategory.objects(
    #     ProjectID=project_id).only("id", "Name").order_by("Name")
    category_mapping = {c["_id"]: c["Name"] for c in categories}
    cat_id_list = []
    for cat_id in category_mapping:
        cat_name = category_mapping[cat_id]
        if cat_name in displayed_categories or "all" in displayed_categories:
            cat_id_list.append(cat_id)

    researchitems = get_db().db["ResearchItem"].find(
        {"GroupIDList": {"$in": group_id_list},
         "ResearchCategoryID": {"$in": cat_id_list}}).sort("Date", pymongo.DESCENDING)
    # researchitems = ResearchItem.objects(GroupIDList__in=group_id_list, ResearchCategoryID__in=cat_id_list).order_by(
    #     "-Date")

    for ri in researchitems:
        cat_id = ri["ResearchCategoryID"]
        if cat_id in category_mapping:
            add_item_to_groups_item_mapping(ri, group_item_mapping, category_mapping[cat_id])

    # subgroups already included in groups => empty dict
    result_list = create_result_list(groups, subgroup_mapping={}, group_item_mapping=group_item_mapping,
                                     max_pages=max_pages, include_field_data=include_field_data)
    return result_list


def get_subgroups(toplevel_groups):
    pipeline = [
        {"$match": {"GroupID": {"$in": [g["_id"] for g in toplevel_groups]}}},
        {"$graphLookup": {
            "from": "Group",
            "startWith": "$_id",
            "connectFromField": "_id",
            "connectToField": "GroupID",
            "as": "groups"}},
    ]
    sub_groups = get_db().db["Group"].aggregate(pipeline)
    sub_group_id_set = set()
    for g in sub_groups:
        sub_group_id_set.add(g["_id"])
        for sub in g["groups"]:
            sub_group_id_set.add(sub["_id"])

    subgroups = get_db().db["Group"].find({"_id": {"$in": [g_id for g_id in sub_group_id_set]}})
    return list(subgroups)


def get_filtered(project_id, name_filter, combo_filter, numeric_filter,
                 groups_filter, samples_filter, experiments_filter, researchitems_filter,
                 checks_filter, recent, index, date_filter, date_created, text_filter,
                 include_field_data, include_linked, displayed_categories):
    and_filter = []
    or_filter = []

    name_query = {}
    if name_filter:
        name_query = {"NameLowe": {"$regex": name_filter.lower()}}

    date_created_query = {}
    if date_created:
        value_min = value_max = None
        custom_date = False
        if "option" in date_created:
            if date_created["option"].lower() == "custom":
                custom_date = True
        else:
            custom_date = True
        if custom_date:
            try:
                value_min = datetime.fromisoformat(date_created['min'])
                value_max = datetime.fromisoformat(date_created['max'])
            except:
                pass
        else:
            value_min, value_max = get_date_from_option_string(date_created["option"].lower())
        if value_min and value_max:
            # date_created_query = {"$and": [
            #     {"Date": {"$gte": value_min}},
            #     {"Date": {"$lte": value_max}}
            # ]}

            date_created_query = {"Date": {"$gte": value_min, "$lte": value_max}}

    fd_exps, fd_samples, fd_researchitems = get_field_data_query_objects(
        combo_filter, numeric_filter, checks_filter, date_filter, text_filter)

    group_query_limiting = {}
    if groups_filter:
        group_query_limiting = get_group_query_limiting(groups_filter)

    # group_query_additional = get_groups_query_additional(field_data_query, name_query, date_created_query)

    exp_id_list = []
    sample_id_list = []
    researchitem_id_list = []
    if experiments_filter:
        exp_id_list.extend([bson.ObjectId(i) for i in experiments_filter])

    if samples_filter:
        sample_id_list.extend([bson.ObjectId(i) for i in samples_filter])

    if researchitems_filter:
        researchitem_id_list.extend([bson.ObjectId(i) for i in researchitems_filter])

    project_query = {"ProjectID": bson.ObjectId(project_id)}
    # get experiments and add groups_ids
    experiment_query = {}
    s = _time.time()
    if exp_id_list or sample_id_list or researchitem_id_list:
        experiment_query = {"_id": {"$in": exp_id_list}}
    if "Experiments" in displayed_categories or "all" in displayed_categories:
        # exps = get_db().db["Experiment"].find(
        #     {"$and": [
        #         project_query,
        #         {"$or": [
        #             {"$and": [group_query_limiting, name_query,
        #                       date_created_query]},
        #             # group_query_additional
        #         ]}
        #     ]}, {"_id": 1, "GroupIDList": 1}
        # )
        # exps = list(exps)
        exps =[]
    else:
        exps = []
    exps.extend(fd_exps)
    # get samples and add group_ids
    sample_query = {}
    if exp_id_list or sample_id_list or researchitem_id_list:
        sample_query = {"_id": {"$in": sample_id_list}}
    if "Samples" in displayed_categories or "all" in displayed_categories:
        # samples = get_db().db["Sample"].find(
        #     {"$and": [
        #         project_query,
        #         {"$or": [
        #             {"$and": [group_query_limiting, name_query, date_created_query]},
        #             # group_query_additional
        #         ]}]}, {"_id": 1, "GroupIDList": 1}
        # )
        samples = []
    else:
        samples = []
    samples.extend(fd_samples)
    # get categories
    categories = get_db().db["ResearchCategory"].find({"ProjectID": project_id}).sort("Name")
    # categories = ResearchCategory.objects(
    #     ProjectID=project_id).only("id", "Name").order_by("Name")
    category_mapping = {c["_id"]: c["Name"] for c in categories}
    cat_id_list = []
    for cat_id in category_mapping:
        cat_name = category_mapping[cat_id]
        if cat_name in displayed_categories or "all" in displayed_categories:
            cat_id_list.append(cat_id)
    cat_query = {"ResearchCategoryID": {"$in": cat_id_list}}

    # get researchitems and add group_ids
    ri_query = {}
    if exp_id_list or sample_id_list or researchitem_id_list:
        ri_query = {"_id": {"$in": researchitem_id_list}}

    researchitems = []
    if cat_id_list:
        pass
        # researchitems = get_db().db["ResearchItem"].find(
        #     {"$and": [
        #         project_query,
        #         cat_query,
        #         {"$or": [
        #             {"$and": [group_query_limiting, name_query, date_created_query]},
        #             # group_query_additional
        #         ]}
        #     ]}, {"_id": 1, "GroupIDList": 1}
        # )
        # researchitems = list(researchitems)

    researchitems.extend(fd_researchitems)

    group_id_list = []
    group_item_mapping = {}  # Dict with dict for category with list of items
    group_exp_mapping = {}
    group_sample_mapping = {}
    group_ri_mapping = {}
    for exp in exps:
        group_id_list.extend(exp["GroupIDList"])
        for group_id in exp["GroupIDList"]:
            if group_id not in group_exp_mapping:
                group_exp_mapping[group_id] = []
            group_exp_mapping[group_id].append(exp["_id"])
    for sample in samples:
        group_id_list.extend(sample["GroupIDList"])
        for group_id in sample["GroupIDList"]:
            if group_id not in group_sample_mapping:
                group_sample_mapping[group_id] = []
            group_sample_mapping[group_id].append(sample["_id"])
    for ri in researchitems:
        group_id_list.extend(ri["GroupIDList"])
        for group_id in ri["GroupIDList"]:
            if group_id not in group_ri_mapping:
                group_ri_mapping[group_id] = []
            group_ri_mapping[group_id].append(ri["_id"])

    # get groups based on created group_id_list.
    # also add groups from groups_filter. If a group from groups_filter would be empty,
    # it would not be in the group List.
    or_query = {"$or": [
        {"_id": {"$in": group_id_list}},
    ]}
    if groups_filter:
        or_query["$or"].append(group_query_limiting)
    query = {"$and":
        [
            project_query,
            or_query
        ]
    }

    groups = list(get_db().db["Group"].find(query, {"id": 1, "GroupID": 1}))
    groups, group_id_subgroup_id_list_mapping = get_all_parent_groups(groups)

    direction = pymongo.ASCENDING
    if recent:
        order_by = "Date"
        direction = pymongo.DESCENDING
    else:
        order_by = "NameLower"

    print("before final group", _time.time() - s)
    start, end = get_start_end(index)

    # get certain amount of top level groups
    toplevel_groups = list(get_db().db["Group"].find(
        {"_id": {"$in": [g["_id"] for g in groups]}, "GroupID": None}).
                           sort(order_by, direction).skip(start).limit(end))
    toplevel_groups_dict = {g["_id"]: g for g in toplevel_groups}
    toplevel_groups_count = get_db().db["Group"].count_documents(
        {"_id": {"$in": [g["_id"] for g in groups]}, "GroupID": None})
    max_pages = get_max_pages(toplevel_groups_count)

    sub_group_ids = []
    total_group_id_list = []
    for g in toplevel_groups:
        total_group_id_list.append(g["_id"])
        if g["_id"] in group_id_subgroup_id_list_mapping:
            sub_group_ids.extend(group_id_subgroup_id_list_mapping[g["_id"]])
            total_group_id_list.extend(sub_group_ids)

    sub_groups = get_db().db["Group"].find({"_id": {"$in": sub_group_ids}})
    subgroup_dict = {g["_id"]: g for g in sub_groups}

    subgroup_mapping = {}
    for group_id in group_id_subgroup_id_list_mapping:
        if group_id in toplevel_groups_dict:
            if group_id not in subgroup_mapping:
                subgroup_mapping[group_id] = []
            for subgroup_id in group_id_subgroup_id_list_mapping[group_id]:
                subgroup = subgroup_dict[subgroup_id]
                subgroup_mapping[group_id].append(subgroup)

    exp_id_list = []
    sample_id_list = []
    researchitem_id_list = []
    for group_id in total_group_id_list:
        if group_id in group_exp_mapping:
            exp_id_list.extend(group_exp_mapping[group_id])
        if group_id in group_sample_mapping:
            sample_id_list.extend(group_sample_mapping[group_id])
        if group_id in group_ri_mapping:
            researchitem_id_list.extend(group_ri_mapping[group_id])

    if include_linked:
        # exp_id_list, sample_id_list and researchitem_id_list include already all filtered items.
        # these id list will be extended by linked items
        extra_exp_id_list, extra_sample_id_list, extra_researchitem_id_list = get_linked_items(
            exp_id_list, sample_id_list, researchitem_id_list
        )
        exp_id_list.extend(extra_exp_id_list)
        sample_id_list.extend(extra_sample_id_list)
        researchitem_id_list.extend(extra_researchitem_id_list)

    exps = get_db().db["Experiment"].find({
        "_id": {"$in": exp_id_list}
    }).sort("Date", pymongo.DESCENDING)
    for exp in exps:
        add_item_to_groups_item_mapping(exp, group_item_mapping, "Experiments")

    samples = get_db().db["Sample"].find({
        "_id": {"$in": sample_id_list}
    }).sort("Date", pymongo.DESCENDING)
    for sample in samples:
        add_item_to_groups_item_mapping(sample, group_item_mapping, "Samples")

    r_items = get_db().db["ResearchItem"].find({
        "_id": {"$in": researchitem_id_list}
    }).sort("Date", pymongo.DESCENDING)
    for r_item in r_items:
        cat_id = r_item["ResearchCategoryID"]
        if cat_id in category_mapping:
            add_item_to_groups_item_mapping(r_item, group_item_mapping, category_mapping[cat_id])

    result_list = create_result_list(toplevel_groups, subgroup_mapping, group_item_mapping,
                                     max_pages=max_pages, include_field_data=include_field_data)

    return result_list


def get_groups_query_additional(field_data_query, name_query, date_created_query):
    group_id_list = []
    if field_data_query:
        groups = get_db().db["Group"].find(field_data_query, {"_id": 1})
        group_id_list.extend([g["_id"] for g in groups])
    if name_query:
        groups = get_db().db["Group"].find(name_query, {"_id": 1})
        group_id_list.extend([g["_id"] for g in groups])
    if date_created_query:
        groups = get_db().db["Group"].find(date_created_query, {"_id": 1})
        group_id_list.extend([g["_id"] for g in groups])

    query = {"GroupIDList": {"$in": group_id_list}}

    return query


def get_group_query_limiting(groups_filter):
    if not groups_filter:
        return {}
    group_list = [bson.ObjectId(g) for g in groups_filter]
    pipeline = [
        {"$match": {"_id": {"$in": group_list}}},
        {"$graphLookup": {
            "from": "Group",
            "startWith": "$_id",
            "connectFromField": "_id",
            "connectToField": "GroupID",
            "as": "groups"}},
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


def get_field_data_query_objects(combo_filter, numeric_filter, checks_filter, date_filter, text_filter):
    field_data_query = []

    if combo_filter:
        combo_query_dict = {}
        for filter in combo_filter:
            field = filter["field"]
            query = {"FieldID": bson.ObjectId(field),
                     "Value": {
                         "$in": [bson.ObjectId(i["id"]) for i in filter["values"]]}}

            # field_data = get_db().db["FieldData"].find({"FieldID": bson.ObjectId(field),
            #                                             "Value": {
            #                                                 "$in": [bson.ObjectId(i["id"]) for i in filter["values"]]}},
            #                                            {"_id": 1}
            #                                            )
            # query = {"FieldDataIDList": {"$in": [fd["_id"] for fd in field_data]}}

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
            field_data = get_db().db["FieldData"].find({"FieldID": bson.ObjectId(field), "Value": check["value"]},
                                                       {"_id": 1})

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
            num_query = {"FieldID": bson.ObjectId(field), "Type": "Numeric"}
            range_query = {"FieldID": bson.ObjectId(field), "Type": "NumericRange"}
            try:
                unitID = bson.ObjectId(nf["unit"])
                unit = Unit.objects.get(id=unitID)
                check, min_value = unit.unit_conversion_to_si(float(nf["min"]))
                min_value = float(nf["min"]) if not check else min_value
                check, max_value = unit.unit_conversion_to_si(float(nf["max"]))
                max_value = float(nf["max"]) if not check else max_value

                num_query["SIValue"] = {"$gte": min_value, "$lte": max_value}

                range_query["$or"] = [
                    {"SIValueMax": {"$gte": min_value}, "SIValue": {"$lte": max_value}},
                    {"Value": None, "SIValueMax": {"$gte": min_value, "$lte": max_value}},
                    {"ValueMax": None, "SIValue": {"$gte": min_value, "$lte": max_value}},
                ]

                query = {"$or": [num_query, range_query]}

            except:
                min_value = float(nf["min"])
                max_value = float(nf["max"])

                num_query["Value"] = {"$gte": min_value, "$lte": max_value}

                range_query["$or"] = [
                    {"ValueMax": {"$gte": min_value}, "Value": {"$lte": max_value}},
                    {"Value": None, "ValueMax": {"$gte": min_value, "$lte": max_value}},
                    {"ValueMax": None, "Value": {"$gte": min_value, "$lte": max_value}},
                ]

                query = {"$or": [num_query, range_query]}

            # field_data = get_db().db["FieldData"].find(query, {"_id": 1})
            #
            # query = {"FieldDataIDList": {"$in": [fd["_id"] for fd in field_data]}}

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
                    value_min = datetime.fromisoformat(df['min'])
                    value_max = datetime.fromisoformat(df['max'])
                except:
                    continue
            else:
                value_min, value_max = get_date_from_option_string(df["option"].lower())

            field_id = ObjectId(df['field'])
            query = {"FieldID": field_id,
                     "Type": "Date", "Value": {"$gte": value_min, "$lte": value_max}}

            # field_data = get_db().db["FieldData"].find(query, {"_id": 1})
            #
            # query = {"FieldDataIDList": {"$in": [fd["_id"] for fd in field_data]}}

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
            value = tf['value']
            field_id = ObjectId(tf['field'])
            query = {"FieldID": field_id, "Type": "SingleLine", "Value": {"$regex": value, '$options': 'i'}}
            # field_data = get_db().db["FieldData"].find(query, {"_id": 1})
            #
            # query = {"FieldDataIDList": {"$in": [fd["_id"] for fd in field_data]}}

            if field_id in text_query_dict:
                text_query_dict[field_id]["$or"].append(query)
            else:
                text_query_dict[field_id] = {}
                text_query_dict[field_id]["$or"] = [query]

        combined_text_query = {"$and": []}
        for field in text_query_dict:
            combined_text_query["$and"].append(text_query_dict[field])

        field_data_query.append(combined_text_query)

    item_dict = {"Experiment": [], "Sample": [], "ResearchItem": []}
    if field_data_query:
        field_data_query = {"$and": field_data_query}
        for item in item_dict:

            pipeline = [
                {"$match": field_data_query},
                {"$project": {"_id": 1}},
                {"$lookup": {
                    "from": item,
                    "localField": "_id",
                    "foreignField": "FieldDataIDList",
                    "as": item
                }},
                {"$project": {f"{item}._id": 1, f"{item}.GroupIDList": 1}}]
            field_data = get_db().db["FieldData"].aggregate(pipeline)
            field_data = list(field_data)
            for fd in field_data:
                item_dict[item].extend(fd[item])
    return item_dict["Experiment"], item_dict["Sample"], item_dict["ResearchItem"]



def get_linked_items(exp_id_list, sample_id_list, researchitem_id_list):
    id_list = []
    id_set = set()
    found_exp_id_set = set()
    found_sample_id_set = set()
    found_researchitem_id_set = set()

    if exp_id_list:
        id_list.extend(exp_id_list)

    if sample_id_list:
        id_list.extend(sample_id_list)

    if researchitem_id_list:
        id_list.extend(researchitem_id_list)
    id_set = set(id_list)
    links = get_db().db["Link"].find({"$or": [
        {"DataID1": {"$in": id_list}}, {"DataID2": {"$in": id_list}},
    ]})
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

    extra_id_list = list(found_exp_id_set - set(exp_id_list))
    extra_sample_id_list = list(found_sample_id_set - set(sample_id_list))
    extra_researchitem_id_list = list(found_researchitem_id_set - set(researchitem_id_list))
    return extra_id_list, extra_sample_id_list, extra_researchitem_id_list


def add_item_to_groups_item_mapping(item, groups_item_mapping, category):
    for g_id in item["GroupIDList"]:
        if g_id not in groups_item_mapping:
            groups_item_mapping[g_id] = {}
        if category not in groups_item_mapping[g_id]:
            groups_item_mapping[g_id][category] = []
        groups_item_mapping[g_id][category].append(item)


def create_result_list(groups, subgroup_mapping, group_item_mapping, max_pages, include_field_data):
    result_list = []
    for group in groups:
        group_node = {
            "id": str(group['_id']),
            "name": group["Name"],
            "group_id": str(group["_id"]),
            "short_id": group['ShortID'],
            'field_data_id_list': [str(field_data) for field_data in group['FieldDataIDList']] if include_field_data
            else [],
            "parent": 0 if not group["GroupID"] else str(group["GroupID"]),
            "droppable": True,
            "expandable": True,
            "type": "Groups",
            "show_type": "groups",
            "visible": True,
            "text": group["Name"],
            "pages": max_pages
        }
        result_list.append(group_node)
        if group["_id"] in subgroup_mapping:
            for subgroup in subgroup_mapping[group["_id"]]:
                sub_group_node = {
                    "id": str(subgroup['_id']),
                    "name": subgroup["Name"],
                    "group_id": str(subgroup["_id"]),
                    "short_id": subgroup['ShortID'],
                    'field_data_id_list': [str(field_data) for field_data in subgroup['FieldDataIDList']] if
                    include_field_data else [],
                    "parent": 0 if not subgroup["GroupID"] else str(subgroup["GroupID"]),
                    "droppable": True,
                    "expandable": True,
                    "type": "Groups",
                    "show_type": "groups",
                    "visible": True,
                    "text": subgroup["Name"],
                    "pages": max_pages
                }
                result_list.append(sub_group_node)

                add_cat_nodes(result_list, subgroup, group_item_mapping, max_pages, include_field_data)

        add_cat_nodes(result_list, group, group_item_mapping, max_pages, include_field_data)

    return result_list


def add_cat_nodes(result_list, group, group_item_mapping, max_pages, include_field_data):
    if not group["_id"] in group_item_mapping:
        return
    for cat in group_item_mapping[group["_id"]]:
        cat_node = {
            'id': f"{str(group['_id'])}/sep/{cat}",
            'name': cat,
            'type': cat,
            'show_type': cat,
            'short_id': "",
            'parent': str(group['_id']),
            "droppable": False,
            "expandable": True,
            "group_id": str(group["_id"]),
            "visible": True,
            "text": cat,
            "field_data_id_list": [],
            "pages": max_pages
        }
        result_list.append(cat_node)

        for item in group_item_mapping[group["_id"]][cat]:
            item_node = {
                'id': str(item['_id']),
                'name': item['Name'],
                'type': cat,
                'show_type': cat,
                'short_id': item["ShortID"],
                'parent': str(cat_node['id']),
                "droppable": False,
                "expandable": False,
                "group_id": str(group["_id"]),
                "visible": True,
                "text": item['Name'],
                "field_data_id_list": [str(field_data) for field_data in
                                       item['FieldDataIDList']] if include_field_data else [],
                "pages": max_pages
            }
            result_list.append(item_node)


def get_all_parent_groups(groups: list):
    missing_group = True
    missing_group_id_list = []
    total_group_id_set = {g["_id"] for g in groups}
    groups_to_be_iterated = list(groups)
    while missing_group:
        for group in groups_to_be_iterated:
            if not group["GroupID"]:
                continue
            if group["GroupID"] not in total_group_id_set:
                missing_group_id_list.append(group["GroupID"])
        if missing_group_id_list:
            new_groups = get_db().db["Group"].find({"_id": {"$in": missing_group_id_list}}, {"_id": 1, "GroupID": 1})
            groups_to_be_iterated = list(new_groups)
            groups.extend(groups_to_be_iterated)
            for g in new_groups:
                total_group_id_set.add(g["_id"])
            missing_group_id_list = []
        else:
            missing_group = False

    group_id_subgroup_id_list_mapping = {}
    for group in groups:
        if not group["GroupID"]:
            continue
        if group["GroupID"] not in group_id_subgroup_id_list_mapping:
            group_id_subgroup_id_list_mapping[group["GroupID"]] = []
        group_id_subgroup_id_list_mapping[group["GroupID"]].append(group["_id"])

    return groups, group_id_subgroup_id_list_mapping


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
        last_day_of_last_month = calendar.monthrange(start_of_last_month.year, start_of_last_month.month)[1]
        end_of_last_month = datetime(start_of_last_month.year, start_of_last_month.month,
                                     last_day_of_last_month)
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
