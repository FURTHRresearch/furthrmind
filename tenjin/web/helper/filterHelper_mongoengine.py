import calendar
from datetime import datetime, time, timedelta

import bson
import bson.json_util
from bson import ObjectId
from flask import current_app
from mongoengine import Q

from tenjin.mongo_engine import FieldData, Unit
from tenjin.mongo_engine import (Group, Experiment, Sample, ResearchItem,
                                 Link, ResearchCategory)


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
        groups = get_no_filter(project_id=projectId, recent=recent, index=index, include_field_data=include_field_data,
                               displayed_categories=displayed_categories)

    else:

        groups = get_filtered(projectId, nameFilter, comboFilter, numericFilter, groupFilter,
                              sampleFilter, experimentFilter, researchItemFilter,
                              checkFilter, recent, index, date_filter, date_created, text_filter,
                              include_field_data=include_field_data,
                              include_linked=include_linked, displayed_categories=displayed_categories)
    return groups


def get_no_filter(project_id, recent, index, include_field_data, displayed_categories):
    # get top level groups
    # get subgroups
    # get exp, sample, resesearch item
    # build result list

    if recent:
        order_by = "-Date"
    else:
        order_by = "NameLower"
    start, end = get_start_end(index)

    toplevel_groups = Group.objects(
        ProjectID=project_id, GroupID=None).order_by(order_by)
    toplevel_groups_count = toplevel_groups.count()
    max_pages = get_max_pages(toplevel_groups_count)

    toplevel_groups = list(toplevel_groups[start:end])
    sub_groups = get_subgroups(toplevel_groups)
    groups = list()
    groups.extend(toplevel_groups)
    groups.extend(sub_groups)
    group_id_list = [g.id for g in groups]

    group_item_mapping = {}

    if "Experiments" in displayed_categories or "all" in displayed_categories:
        exps = Experiment.objects(GroupIDList__in=group_id_list).order_by("-Date")
        for exp in exps:
            add_item_to_groups_item_mapping(exp, group_item_mapping, "Experiments")
    else:
        exps = []

    if "Samples" in displayed_categories or "all" in displayed_categories:
        samples = Sample.objects(GroupIDList__in=group_id_list).order_by("-Date")
        for sample in samples:
            add_item_to_groups_item_mapping(sample, group_item_mapping, "Samples")
    else:
        samples = []

        # get categories
    categories = ResearchCategory.objects(
        ProjectID=project_id).only("id", "Name").order_by("Name")
    category_mapping = {c.id: c.Name for c in categories}
    cat_id_list = []
    for cat_id in category_mapping:
        cat_name = category_mapping[cat_id]
        if cat_name in displayed_categories or "all" in displayed_categories:
            cat_id_list.append(cat_id)

    researchitems = ResearchItem.objects(GroupIDList__in=group_id_list, ResearchCategoryID__in=cat_id_list).order_by(
        "-Date")

    for ri in researchitems:
        cat_id = ri.ResearchCategoryID.id
        if cat_id in category_mapping:
            add_item_to_groups_item_mapping(ri, group_item_mapping, category_mapping[cat_id])

    # subgroups already included in groups => empty dict
    result_list = create_result_list(groups, subgroup_mapping={}, group_item_mapping=group_item_mapping,
                                     max_pages=max_pages, include_field_data=include_field_data)
    return result_list


def get_subgroups(toplevel_groups):
    pipeline = [
        {"$match": {"GroupID": {"$in": [g.id for g in toplevel_groups]}}},
        {"$graphLookup": {
            "from": "Group",
            "startWith": "$_id",
            "connectFromField": "_id",
            "connectToField": "GroupID",
            "as": "groups"}},
    ]
    sub_group_id_set = set()
    sub_groups = list(Group.objects.aggregate(pipeline))
    for g in sub_groups:
        sub_group_id_set.add(g["_id"])
        for sub in g["groups"]:
            sub_group_id_set.add(sub["_id"])

    subgroups = Group.objects(id__in=[g_id for g_id in sub_group_id_set])
    return list(subgroups)


def get_filtered(project_id, name_filter, combo_filter, numeric_filter,
                 groups_filter, samples_filter, experiments_filter, researchitems_filter,
                 checks_filter, recent, index, date_filter, date_created, text_filter,
                 include_field_data, include_linked, displayed_categories):
    name_query = Q()
    if name_filter:
        name_query = Q(NameLower__contains=name_filter.lower())
    date_created_query = Q()
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
            date_created_query = Q(Date__gte=value_min, Date__lte=value_max)

    field_data_query = get_field_data_query_objects(
        combo_filter, numeric_filter, checks_filter, date_filter, text_filter)

    group_query_limiting = Q()
    if groups_filter:
        group_query_limiting = get_group_query_limiting(groups_filter)

    group_query_additional = get_groups_query_additional(field_data_query, name_query, date_created_query)

    exp_id_list = []
    sample_id_list = []
    researchitem_id_list = []

    if experiments_filter:
        exp_id_list.extend([bson.ObjectId(i) for i in experiments_filter])

    if samples_filter:
        sample_id_list.extend([bson.ObjectId(i) for i in samples_filter])

    if researchitems_filter:
        researchitem_id_list.extend([bson.ObjectId(i) for i in researchitems_filter])

    group_id_list = []
    group_item_mapping = {}  # Dict with dict for category with list of items

    project_query = Q(ProjectID=project_id)
    # get experiments and add groups_ids
    experiment_query = Q()
    if exp_id_list:
        experiment_query = Q(id__in=exp_id_list)
    if "Experiments" in displayed_categories or "all" in displayed_categories:
        exps = Experiment.objects(
            ((group_query_limiting & name_query & field_data_query & experiment_query & date_created_query) |
             group_query_additional) & project_query).only("id").order_by("-Date")
        exp_id_list = [e.id for e in exps]
    else:
        exps = []
        exp_id_list = []

    # get samples and add group_ids
    sample_query = Q()
    if sample_id_list:
        sample_query = Q(id__in=sample_id_list)
    if "Samples" in displayed_categories or "all" in displayed_categories:
        samples = Sample.objects(
            ((group_query_limiting & name_query & field_data_query & sample_query & date_created_query) |
             group_query_additional) & project_query).order_by("-Date").only("id", "GroupIDList")
        sample_id_list = [s.id for s in samples]
    else:
        samples = []
        sample_id_list = []

    # get categories
    categories = ResearchCategory.objects(
        project_query).only("id", "Name").order_by("Name")
    category_mapping = {c.id: c.Name for c in categories}

    # check if cat is in displayed categories
    cat_id_list = []
    for cat_id in category_mapping:
        cat_name = category_mapping[cat_id]
        if cat_name in displayed_categories or "all" in displayed_categories:
            cat_id_list.append(cat_id)
    cat_query = Q(ResearchCategoryID__in=cat_id_list)

    # get researchitems and add group_ids
    ri_query = Q()
    if researchitem_id_list:
        ri_query = Q(id__in=researchitem_id_list)

    researchitem_id_list = []
    researchitems = []
    if cat_id_list:
        researchitems = ResearchItem.objects(
            ((group_query_limiting & name_query & field_data_query & ri_query & date_created_query & cat_query) |
             group_query_additional) & project_query).order_by("-Date").only("id", "GroupIDList")
        researchitem_id_list = [ri.id for ri in researchitems]

    if include_linked:
        # exp_id_list, sample_id_list and researchitem_id_list include already all filtered items.
        # these id list will be extended by linked items
        exp_id_list, sample_id_list, researchitem_id_list = get_linked_items(
            exp_id_list, sample_id_list, researchitem_id_list
        )
        if "Experiments" in displayed_categories or "all" in displayed_categories:
            exps = Experiment.objects(id__in=exp_id_list).order_by("-Date").only("id", "GroupIDList")

        if "Samples" in displayed_categories or "all" in displayed_categories:
            samples = Sample.objects(id__in=sample_id_list).order_by("-Date").only("id", "GroupIDList", "ResearchCategoryID")

        researchitems = ResearchItem.objects(id__in=researchitem_id_list, ResearchCategoryID__in=cat_id_list).order_by(
            "-Date").only("id", "GroupIDList")

    for exp in exps:
        group_id_list.extend([g.id for g in exp.GroupIDList])
        add_item_to_groups_item_mapping(exp, group_item_mapping, "Experiments")
    for sample in samples:
        group_id_list.extend([g.id for g in sample.GroupIDList])
        add_item_to_groups_item_mapping(sample, group_item_mapping, "Samples")
    for ri in researchitems:
        cat_id = ri.ResearchCategoryID.id
        if cat_id in category_mapping:
            add_item_to_groups_item_mapping(ri, group_item_mapping, category_mapping[cat_id])
            group_id_list.extend([g.id for g in ri.GroupIDList])
    # get groups based on created group_id_list.
    # also add groups from groups_filter. If a group from groups_filter would be empty,
    # it would not be in the group List.

    query = (Q(id__in=group_id_list) | group_query_limiting) & project_query
    groups = list(Group.objects(query).only("id", "GroupID"))
    groups_mapping = {g.id: g for g in groups}
    groups, subgroup_mapping = get_all_parent_groups(groups)
    for g in groups:
        if g.id not in groups_mapping:
            groups_mapping[g.id] = g

    if recent:
        order_by = "-Date"
    else:
        order_by = "NameLower"
    start, end = get_start_end(index)

    # get certain amount of top level groups
    toplevel_groups = Group.objects(id__in=[g.id for g in groups], GroupID=None).order_by(order_by)
    toplevel_groups_count = toplevel_groups.count()
    max_pages = get_max_pages(toplevel_groups_count)
    toplevel_groups = toplevel_groups[start:end]
    result_list = create_result_list(toplevel_groups, subgroup_mapping, group_item_mapping,
                                     max_pages=max_pages, include_field_data=include_field_data)

    return result_list


def get_groups_query_additional(field_data_query, name_query, date_created_query):
    group_id_list = []
    groups = []
    if field_data_query:
        groups = Group.objects(field_data_query).only("id")
        group_id_list.extend([g.id for g in groups])
    if name_query:
        groups = Group.objects(name_query).only("id")
        group_id_list.extend([g.id for g in groups])
    if date_created_query:
        groups = Group.objects(date_created_query).only("id")
        group_id_list.extend([g.id for g in groups])

    if group_id_list:
        query = Q(GroupIDList__in=[g.id for g in groups])
    else:
        query = Q()

    return query


def get_group_query_limiting(groups_filter):
    if not groups_filter:
        return Q()
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
    groups = Group.objects.aggregate(pipeline)
    group_id_list = []
    for g in groups:
        if g["_id"] in group_id_list:
            continue
        group_id_list.append(g["_id"])
        for sub in g["groups"]:
            if sub["_id"] in group_id_list:
                continue
            group_id_list.append(sub["_id"])

    group_query = Q(GroupIDList__in=group_id_list)
    return group_query


def get_field_data_query_objects(combo_filter, numeric_filter, checks_filter, date_filter, text_filter):
    field_data_query = Q()

    if combo_filter:
        combo_query_dict = {}
        for filter in combo_filter:
            field = filter["field"]
            field_data = FieldData.objects(
                Value__in=[bson.ObjectId(i["id"]) for i in filter["values"]]).only("id")
            query = Q(FieldDataIDList__in=[fd.id for fd in field_data])
            if field in combo_query_dict:
                combo_query_dict[field] = combo_query_dict[field] | query
            else:
                combo_query_dict[field] = query

        combined_combo_query = Q()
        for field in combo_query_dict:
            combined_combo_query = combined_combo_query & (combo_query_dict[field])

        field_data_query = field_data_query & combined_combo_query

    if checks_filter:
        check_query_dict = {}
        for check in checks_filter:
            field = check["field"]
            field_data = FieldData.objects(FieldID=bson.ObjectId(check["field"]),
                                           Value=check["value"]).only("id")
            query = Q(FieldDataIDList__in=[fd.id for fd in field_data])
            if field in check_query_dict:
                check_query_dict[field] = check_query_dict[field] | query
            else:
                check_query_dict[field] = query

        combined_check_query = Q()
        for field in check_query_dict:
            combined_check_query = combined_check_query & (check_query_dict[field])

        field_data_query = field_data_query & combined_check_query

    if numeric_filter:

        numeric_query_dict = {}
        for nf in numeric_filter:
            field = nf["field"]
            query_object = Q(FieldID=bson.ObjectId(nf["field"]))
            num_query_object = query_object & Q(Type="Numeric")
            range_query_object = query_object & Q(Type="NumericRange")
            try:
                unitID = bson.ObjectId(nf["unit"])
                unit = Unit.objects.get(id=unitID)
                check, min_value = unit.unit_conversion_to_si(float(nf["min"]))
                min_value = float(nf["min"]) if not check else min_value
                check, max_value = unit.unit_conversion_to_si(float(nf["max"]))
                max_value = float(nf["max"]) if not check else max_value

                num_value_query = Q(SIValue__gte=min_value, SIValue__lte=max_value)
                num_query_object = num_query_object & num_value_query

                range_value_query = (Q(SIValueMax__gte=min_value, SIValue__lte=max_value) |
                                     Q(Value=None, SIValueMax__gte=min_value, SIValueMax__lte=max_value) |
                                     Q(ValueMax=None, SIValue__gte=min_value, SIValue__lte=max_value))

                range_query_object = range_query_object & range_value_query
                query = num_query_object | range_query_object

            except:
                min_value = float(nf["min"])
                max_value = float(nf["max"])

                num_value_query = Q(Value__gte=min_value, Value__lte=max_value)
                num_query_object = num_query_object & num_value_query

                range_value_query = (Q(ValueMax__gte=min_value, Value__lte=max_value) |
                                     Q(Value=None, ValueMax__gte=min_value, ValueMax__lte=max_value) |
                                     Q(ValueMax=None, Value__gte=min_value, Value__lte=max_value))

                range_query_object = range_query_object & range_value_query
                query = num_query_object | range_query_object

            field_data = FieldData.objects(query).only("id")

            query = Q(FieldDataIDList__in=[fd.id for fd in field_data])
            if field in numeric_query_dict:
                numeric_query_dict[field] = numeric_query_dict[field] | query
            else:
                numeric_query_dict[field] = query

        combined_numeric_query = Q()
        for field in numeric_query_dict:
            combined_numeric_query = combined_numeric_query & (numeric_query_dict[field])

        field_data_query = field_data_query & combined_numeric_query

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
            query_object = Q(FieldID=field_id, Type="Date", Value__gte=value_min, Value__lte=value_max)
            field_data = FieldData.objects(query_object).only("id")

            query = Q(FieldDataIDList__in=[fd.id for fd in field_data])
            if field_id in date_query_dict:
                date_query_dict[field_id] = date_query_dict[field_id] | query
            else:
                date_query_dict[field_id] = query

        combined_date_query = Q()
        for field_id in date_query_dict:
            combined_date_query = combined_date_query & date_query_dict[field_id]

        field_data_query = field_data_query & combined_date_query

    if text_filter:
        text_query_dict = {}
        for tf in text_filter:
            value = tf['value']
            field_id = ObjectId(tf['field'])
            query_object = Q(FieldID=field_id, Type="SingleLine", Value__icontains=value)
            field_data = FieldData.objects(query_object).only("id")

            query = Q(FieldDataIDList__in=[fd.id for fd in field_data])
            if field_id in text_query_dict:
                text_query_dict[field_id] = text_query_dict[field_id] | query
            else:
                text_query_dict[field_id] = query

        combined_text_query = Q()
        for field_id in text_query_dict:
            combined_text_query = combined_text_query & text_query_dict[field_id]

        field_data_query = field_data_query & combined_text_query

    return field_data_query


def get_linked_items(experiment_filter, sample_filter, researchitem_filter):
    id_list = []
    exp_id_list = []
    sample_id_list = []
    researchitem_id_list = []

    if experiment_filter:
        id_list.extend([bson.ObjectId(i) for i in experiment_filter])
        exp_id_list.extend([bson.ObjectId(i) for i in experiment_filter])

    if sample_filter:
        id_list.extend([bson.ObjectId(i) for i in sample_filter])
        sample_id_list.extend([bson.ObjectId(i) for i in sample_filter])

    if researchitem_filter:
        id_list.extend([bson.ObjectId(i) for i in researchitem_filter])
        researchitem_id_list.extend([bson.ObjectId(i) for i in researchitem_filter])

    links = Link.objects(Q(DataID1__in=id_list) | Q(DataID2__in=id_list))

    for link in links:
        if link.DataID1 in id_list:
            if link.Collection2 == "Experiment":
                exp_id_list.append(link.DataID2)
            elif link.Collection2 == "Sample":
                sample_id_list.append(link.DataID2)
            elif link.Collection2 == "ResearchItem":
                researchitem_id_list.append(link.DataID2)
        else:
            if link.Collection1 == "Experiment":
                exp_id_list.append(link.DataID1)
            elif link.Collection1 == "Sample":
                sample_id_list.append(link.DataID1)
            elif link.Collection1 == "ResearchItem":
                researchitem_id_list.append(link.DataID1)

    return exp_id_list, sample_id_list, researchitem_id_list


def add_item_to_groups_item_mapping(item, groups_item_mapping, category):
    for g in item.GroupIDList:
        if g.id not in groups_item_mapping:
            groups_item_mapping[g.id] = {}
        if category not in groups_item_mapping[g.id]:
            groups_item_mapping[g.id][category] = []
        groups_item_mapping[g.id][category].append(item)


def create_result_list(groups, subgroup_mapping, group_item_mapping, max_pages, include_field_data):
    result_list = []
    for group in groups:
        group_node = {
            "id": str(group['id']),
            "name": group["Name"],
            "group_id": str(group.id),
            "short_id": group['ShortID'],
            'field_data_id_list': [str(field_data.id) for field_data in group['FieldDataIDList']] if include_field_data
            else [],
            "parent": 0 if not group["GroupID"] else str(group["GroupID"].id),
            "droppable": True,
            "expandable": True,
            "type": "Groups",
            "show_type": "groups",
            "visible": True,
            "text": group["Name"],
            "pages": max_pages
        }
        result_list.append(group_node)
        if group.id in subgroup_mapping:
            for subgroup in subgroup_mapping[group.id]:
                sub_group_node = {
                    "id": str(subgroup['id']),
                    "name": subgroup["Name"],
                    "group_id": str(subgroup.id),
                    "short_id": subgroup['ShortID'],
                    'field_data_id_list': [str(field_data.id) for field_data in subgroup['FieldDataIDList']] if
                    include_field_data else [],
                    "parent": 0 if not subgroup["GroupID"] else str(subgroup["GroupID"].id),
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
    if not group.id in group_item_mapping:
        return
    for cat in group_item_mapping[group.id]:
        cat_node = {
            'id': f"{str(group['id'])}/sep/{cat}",
            'name': cat,
            'type': cat,
            'show_type': cat,
            'short_id': "",
            'parent': str(group['id']),
            "droppable": False,
            "expandable": True,
            "group_id": str(group["id"]),
            "visible": True,
            "text": cat,
            "field_data_id_list": [],
            "pages": max_pages
        }
        result_list.append(cat_node)

        for item in group_item_mapping[group.id][cat]:
            item_node = {
                'id': str(item['id']),
                'name': item['Name'],
                'type': cat,
                'show_type': cat,
                'short_id': item.ShortID,
                'parent': str(cat_node['id']),
                "droppable": False,
                "expandable": False,
                "group_id": str(group["id"]),
                "visible": True,
                "text": item['Name'],
                "field_data_id_list": [str(field_data.id) for field_data in
                                       item['FieldDataIDList']] if include_field_data else [],
                "pages": max_pages
            }
            result_list.append(item_node)


def get_all_parent_groups(groups: list):
    missing_group = True
    missing_group_id_list = []
    total_group_id_set = {g.id for g in groups}
    groups_to_be_iterated = list(groups)
    while missing_group:
        for group in groups_to_be_iterated:
            if not group.GroupID:
                continue
            if group.GroupID.id not in total_group_id_set:
                missing_group_id_list.append(group.GroupID.id)
        if missing_group_id_list:
            new_groups = Group.objects(id__in=missing_group_id_list)
            groups_to_be_iterated = list(new_groups)
            groups.extend(list(new_groups))
            for g in new_groups:
                total_group_id_set.add(g.id)
            missing_group_id_list = []
        else:
            missing_group = False
    subgroup_mapping = {}
    for group in groups:
        if not group.GroupID:
            continue
        if group.GroupID.id not in subgroup_mapping:
            subgroup_mapping[group.GroupID.id] = []
        subgroup_mapping[group.GroupID.id].append(group)

    return groups, subgroup_mapping


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
        last_day_of_last_month = calendar.monthrange(start_of_last_month.year, today.month)[1]
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