from bson import ObjectId
import calendar
from datetime import datetime, time, timedelta
from tenjin.database.db import get_db_async
import asyncio
import timeit
from tenjin.cache import Cache
cache = Cache.get_cache() 


async def get_groups(
    project_id,
    group_id_list,
    group_filter,
    name_filter,
    combo_filter,
    numeric_filter,
    checks_filter,
    date_filter,
    text_filter,
):
    """
    Method to find all groups for a certain set of filters. If group_id_list is None,
    the complete project is searched. Otherwise, only groups in groups_id_list
    are taken into account

    Parameters
    ----------
    project_id : _type_
        _description_
    group_id_list : _type_
        _description_
    group_filter : _type_
        _description_
    name_filter : _type_
        _description_
    combo_filter : _type_
        _description_
    numeric_filter : _type_
        _description_
    checks_filter : _type_
        _description_
    date_filter : _type_
        _description_
    text_filter : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if group_filter:
        group_filter = [ObjectId(g) for g in group_filter]
        if group_id_list:
            group_filter = [g for g in group_filter if g in group_id_list]
        parent_groups = await get_all_parent_groups(group_filter)
        return parent_groups

    fielddata_queries = get_field_data_query_objects(
        combo_filter, numeric_filter, checks_filter, date_filter, text_filter
    )
    coroutines = [name_query_coroutine("Group", group_id_list, name_filter, project_id)]
    coroutines.extend(
        [
            field_data_query_coroutine("Group", group_id_list, f, project_id)
            for f in fielddata_queries
        ]
    )
    results = await asyncio.gather(*coroutines)

    final_result = set()
    for result in results:
        if result is None:
            continue

        final_result.update(result)

    return final_result


async def get_experiments(
    project_id,
    exp_ids,
    date_created,
    name_filter,
    combo_filter,
    numeric_filter,
    checks_filter,
    date_filter,
    text_filter,
):
    result_dict = {"name_filter": set(), "date_created": set(), "field_data": []}

    fielddata_queries = get_field_data_query_objects(
        combo_filter, numeric_filter, checks_filter, date_filter, text_filter
    )
    coroutines = [
        direct_query_coroutine("Experiment", exp_ids, project_id),
        name_query_coroutine("Experiment", exp_ids, name_filter, project_id),
        date_query_coroutine("Experiment", exp_ids, date_created, project_id),
    ]
    
    coroutines.extend(
        [
            field_data_query_coroutine("Experiment", exp_ids, f, project_id)
            for f in fielddata_queries
        ]
    )
    results = await asyncio.gather(*coroutines)
    result_dict["direct"] = results[0]
    result_dict["name_filter"] = results[1]
    result_dict["date_created"] = results[2]
    if len(results) > 2:
        result_dict["field_data"] = results[3:]

    return result_dict


async def get_samples(
    project_id,
    sample_ids,
    date_created,
    name_filter,
    combo_filter,
    numeric_filter,
    checks_filter,
    date_filter,
    text_filter,
):

    result_dict = {"name_filter": set(), "date_created": set(), "field_data": []}

    fielddata_queries = get_field_data_query_objects(
        combo_filter, numeric_filter, checks_filter, date_filter, text_filter
    )
    coroutines = [
        direct_query_coroutine("Sample", sample_ids, project_id),
        name_query_coroutine("Sample", sample_ids, name_filter, project_id),
        date_query_coroutine("Sample", sample_ids, date_created, project_id),
    ]

    coroutines.extend(
        [
            field_data_query_coroutine("Sample", sample_ids, f, project_id)
            for f in fielddata_queries
        ]
    )
    results = await asyncio.gather(*coroutines)

    result_dict["direct"] = results[0]
    result_dict["name_filter"] = results[1]
    result_dict["date_created"] = results[2]
    if len(results) > 2:
        result_dict["field_data"] = results[3:]

    return result_dict


async def get_research_items(
    project_id,
    research_item_ids,
    date_created,
    name_filter,
    combo_filter,
    numeric_filter,
    checks_filter,
    date_filter,
    text_filter,
):

    result_dict = {"name_filter": set(), "date_created": set(), "field_data": []}

    fielddata_queries = get_field_data_query_objects(
        combo_filter, numeric_filter, checks_filter, date_filter, text_filter
    )
    coroutines = [
        direct_query_coroutine("ResearchItem", research_item_ids, project_id),
        name_query_coroutine(
            "ResearchItem", research_item_ids, name_filter, project_id
        ),
        date_query_coroutine(
            "ResearchItem", research_item_ids, date_created, project_id
        ),
    ]

    coroutines.extend(
        [
            field_data_query_coroutine("ResearchItem", research_item_ids, f, project_id)
            for f in fielddata_queries
        ]
    )
    results = await asyncio.gather(*coroutines)

    result_dict["direct"] = results[0]
    result_dict["name_filter"] = results[1]
    result_dict["date_created"] = results[2]
    if len(results) > 2:
        result_dict["field_data"] = results[3:]

    return result_dict


def get_field_data_query_objects(
    combo_filter=None,
    numeric_filter=None,
    checks_filter=None,
    date_filter=None,
    text_filter=None,
):
    from tenjin.mongo_engine import Unit, Field

    field_data_queries = []

    if combo_filter:

        for filter in combo_filter:
            values_str = [i["id"] for i in filter["values"]]
            values = []
            for v in values_str:
                try:
                    values.append(ObjectId(v))
                except:
                    pass
            field = filter["field"]
            query = {
                "FieldData": {
                    "$elemMatch": {
                        "FieldID": ObjectId(field),
                        "Value": {"$in": values},
                    }
                }
            }

            field_data_queries.append(query)

    if checks_filter:
        for check in checks_filter:
            field = check["field"]
            value = check["value"]
            if isinstance(value, str):
                if value.lower() == "true":
                    value = True
                else:
                    value = False
            if value is False:
                value_query = {
                    "$or": [{"FieldData.Value": False}, {"FieldData.Value": None}]
                }
            else:
                value_query = {"FieldData.Value": True}

            query = {"FieldData": {"$elemMatch": {"FieldID": ObjectId(field)}}}
            query["FieldData"]["$elemMatch"].update(value_query)

            field_data_queries.append(query)

    if numeric_filter:
        for nf in numeric_filter:
            field = nf["field"]

            num_query = {"FieldData": {"$elemMatch": {"FieldID": ObjectId(field)}}}
            range_query = {"FieldData": {"$elemMatch": {"FieldID": ObjectId(field)}}}

            try:
                unitID = ObjectId(nf["unit"])
                unit = Unit.objects.get(id=unitID)
                check, min_value = unit.unit_conversion_to_si(float(nf["min"]))
                min_value = float(nf["min"]) if not check else min_value
                check, max_value = unit.unit_conversion_to_si(float(nf["max"]))
                max_value = float(nf["max"]) if not check else max_value

                num_query["FieldData"]["$elemMatch"]["SIValue"] = {
                    "$gte": min_value,
                    "$lte": max_value,
                }

                # noinspection PyTypedDict
                range_query["FieldData"]["$elemMatch"]["$or"] = [
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

            except:
                min_value = None
                max_value = None
                try:
                    min_value = float(nf["min"])
                    max_value = float(nf["max"])
                except:
                    pass

                num_query["FieldData"]["$elemMatch"]["Value"] = {
                    "$gte": min_value,
                    "$lte": max_value,
                }

                range_query["FieldData"]["$elemMatch"]["$or"] = [
                    {"ValueMax": {"$gte": min_value}, "Value": {"$lte": max_value}},
                    {"Value": None, "ValueMax": {"$gte": min_value, "$lte": max_value}},
                    {"ValueMax": None, "Value": {"$gte": min_value, "$lte": max_value}},
                ]

            field_object = Field.objects(id=ObjectId(field)).only("Type").first()
            if field_object["Type"] == "Numeric":
                query = num_query
            else:
                query = range_query

            field_data_queries.append(query)

    if date_filter:
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
                "FieldData": {
                    "$elemMatch": {
                        "FieldID": field_id,
                        "Value": {"$gte": value_min, "$lte": value_max},
                    }
                }
            }

            field_data_queries.append(query)

    if text_filter:
        for tf in text_filter:
            value = tf["value"]
            field_id = ObjectId(tf["field"])
            query = {
                "FieldData": {
                    "$elemMatch": {
                        "FieldID": field_id,
                        "ValueLower": {"$regex": value.lower()},
                    }
                }
            }
            field_data_queries.append(query)

    return field_data_queries


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


async def get_all_parent_groups(group_ids: set):
    """
    Returns all parent groups of the given group_id_list
    If

    Parameters
    ----------
    group_id_list : list
        _description_

    Returns
    -------
    _type_
        _description_
    """
    db = get_db_async()
    subgroups = db["Group"].find(
        {"_id": {"$in": list(group_ids)}, "GroupID": {"$ne": None}},
        {"_id": 1, "GroupID": 1},
    )
    subgroups = await subgroups.to_list()
    subgroup_ids = set(subgroups)
    parent_groups = group_ids - subgroup_ids

    missing_group = True
    missing_group_id_list = []
    checked_group_id_set = {g["_id"] for g in subgroups}
    groups_to_be_iterated = list(subgroups)
    while missing_group:
        for group in groups_to_be_iterated:
            if not group["GroupID"]:
                parent_groups.add(group["_id"])
                continue
            if group["GroupID"] not in checked_group_id_set:
                missing_group_id_list.append(group["GroupID"])
        if missing_group_id_list:
            new_groups = db["Group"].find(
                {"_id": {"$in": missing_group_id_list}}, {"_id": 1, "GroupID": 1}
            )
            new_groups = await new_groups.to_list()
            groups_to_be_iterated = new_groups
            for g in new_groups:
                checked_group_id_set.add(g["_id"])
            missing_group_id_list = []
        else:
            missing_group = False

    return list(parent_groups)


async def get_subgroups(toplevel_groups):
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
    db = get_db_async()
    async with await db["Group"].aggregate(pipeline) as sub_groups:
        sub_group_id_set = set()
        async for g in sub_groups:
            sub_group_id_set.add(g["_id"])
            for sub in g["groups"]:
                sub_group_id_set.add(sub["_id"])

    return sub_group_id_set


async def direct_query_coroutine(collection, item_ids, project_id):

    if not item_ids:
        return set()
    if item_ids == "all":
        db = get_db_async()
        query = {"ProjectID": project_id}
        cursor = db[collection].find(query, {"_id": 1, "GroupIDList": 1})
        results = await cursor.to_list()
        cache_mapping = {f"{r['_id']}": r for r in results}
        cache.set_many(cache_mapping, timeout=3600*48)
        return {r["_id"] for r in results}
    else:
        return set(item_ids)


async def name_query_coroutine(
    collection, item_ids, name_filter, project_id, category_id_list=None
):
    if not name_filter:
        return None
    db = get_db_async()
    query = {"ProjectID": project_id, "NameLower": {"$regex": name_filter.lower()}}
    if category_id_list is not None:
        query["ResearchCategoryID"] = {"$in": category_id_list}
    if item_ids:
        query["_id"] = {"$in": list(item_ids)}
    name_cursor = db[collection].find(query, {"_id": 1, "GroupIDList": 1})
    name_results = await name_cursor.to_list()
    name_result_ids = {r["_id"] for r in name_results}
    cache_mapping = {f"{r['_id']}": r for r in name_results}
    cache.set_many(cache_mapping, timeout=3600*48)
    return name_result_ids


async def field_data_query_coroutine(
    collection, item_ids, field_query, project_id, category_id_list=None
):
    db = get_db_async()
    query = {"ProjectID": project_id}
    query.update(field_query)
    if category_id_list is not None:
        query["ResearchCategoryID"] = {"$in": category_id_list}
    if item_ids:
        query["_id"] = {"$in": list(item_ids)}
    fielddata_cursor = db[collection].find(query, 
                                           {"_id": 1, "GroupIDList": 1})
    fielddata_results = await fielddata_cursor.to_list()
    fielddata_result_ids = {f["_id"] for f in fielddata_results}
    cache_mapping = {f"{r['_id']}": r for r in fielddata_results}
    cache.set_many(cache_mapping, timeout=3600*48)
    return fielddata_result_ids


async def date_query_coroutine(
    collection, item_ids, date_created, project_id, category_id_list=None
):
    if not date_created:
        return None
    db = get_db_async()
    date_query = get_date_created_query(date_created)
    query = {"ProjectID": project_id}
    query.update(date_query)
    if category_id_list is not None:
        query["ResearchCategoryID"] = {"$in": category_id_list}
    if item_ids:
        query["_id"] = {"$in": list(item_ids)}
    date_cursor = db[collection].find(query, {"_id": 1, "GroupIDList": 1})
    date_results = await date_cursor.to_list()
    date_result_ids = {r["_id"] for r in date_results}
    cache_mapping = {f"{r['_id']}": r for r in date_results}
    cache.set_many(cache_mapping, timeout=3600*48)
    
    return date_result_ids


async def get_valid_categories(project_id, displayed_categories):
    displayed_categories = list(displayed_categories)
    if "Experiements" in displayed_categories:
        displayed_categories.remove("Experiments")
    if "Samples" in displayed_categories:
        displayed_categories.remove("Samples")
    if not displayed_categories:
        return [], {}

    db = get_db_async()
    categories = (
        db["ResearchCategory"]
        .find({"ProjectID": project_id}, {"_id": 1, "Name": 1})
        .sort("Name")
    )
    categories = await categories.to_list()
    category_mapping = {c["_id"]: c["Name"] for c in categories}
    cat_id_list = []
    for cat_id in category_mapping:
        cat_name = category_mapping[cat_id]
        if cat_name in displayed_categories or "all" in displayed_categories:
            cat_id_list.append(cat_id)

    return cat_id_list, category_mapping


async def get_linked_items(id_list):
    found_item_id_set = set()
    item_keys = [f"link_{i}" for i in id_list]
    cached_linked_items = cache.get_many(*item_keys)
    cached_linked_mapping = {}
    id_set = set(id_list)
    cached_id_set = set()
    for cached_items, item_id in zip(cached_linked_items, id_list):
        if cached_items is None:
            continue
        cached_linked_mapping[item_id] = cached_items
        cached_id_set.add(item_id)
    
    id_set = id_set - cached_id_set    
    id_list = list(id_set)
    id_list_original = id_list
    id_list_in_list = []
    chunk_number = 5000
    for i in range(0, len(id_list), chunk_number):
        if i + chunk_number > len(id_list):
            id_list_in_list.append(id_list[i:])
        else:
            id_list_in_list.append(id_list[i : i + chunk_number])
    
    db = get_db_async()
    coroutines = []
    for item_ids in id_list_in_list:
        coroutines.append(
            db["Link"]
            .find(
                {
                    "$or": [
                        {"DataID1": {"$in": item_ids}},
                        {"DataID2": {"$in": item_ids}},
                    ]
                }
            )
            .to_list()
        )
    results = await asyncio.gather(*coroutines)
    links = []
    for r in results:
        links.extend(r)
        
    id_set = set(id_list_original)
    linked_mapping = {}
    for link in links:
        if link["DataID1"] in id_set:
            found_item_id_set.add(link["DataID1"])
            if link["DataID1"] not in linked_mapping:
                linked_mapping[link["DataID1"]] = []
            linked_mapping[link["DataID1"]].append(link["DataID2"])
        else:
            found_item_id_set.add(link["DataID2"])
            if link["DataID2"] not in linked_mapping:
                linked_mapping[link["DataID2"]] = []
            linked_mapping[link["DataID2"]].append(link["DataID1"])

    extra_item_id_set = found_item_id_set - id_set
    if linked_mapping:
        cache_mapping = {f"link_{l}": linked_mapping[l] for l in linked_mapping}
        cache.set_many(cache_mapping, timeout=3600*48)
    for cached_item_id in cached_linked_mapping:
        cached_linked_items = cached_linked_mapping[cached_item_id]
        extra_item_id_set.update(set(cached_linked_items))
    linked_mapping.update(cached_linked_mapping)
    return extra_item_id_set, linked_mapping


async def get_linked_items_recursive(
    include_linked, item_id_list):
    import timeit
    extra_item_id_list = []
    final_mapping = {}

    # older versions saved a bool for include linked => false equals to "none", true equals to "direct"
    if include_linked is False:
        include_linked = "none"
    elif include_linked is True:
        include_linked = "direct"

    if include_linked.lower() == "none":
        return item_id_list, final_mapping

    if include_linked == "direct":
        extra_item_id_list, final_mapping = (
            await get_linked_items(item_id_list)
        )
        return extra_item_id_list, final_mapping

    number_of_layer = None
    try:
        number_of_layer = int(include_linked)
    except:
        pass
    total_linked_mapping = {}
    if include_linked == "all" or number_of_layer:
        extra_item_id_set = set()
        found_item_id_list = list(item_id_list)
        counter = 0
        while True:
            temp_item_id_list, linked_mapping = (
                await get_linked_items(found_item_id_list)
            )

            found_item_id_list = list(set(temp_item_id_list) - extra_item_id_set)
            extra_item_id_set.update(temp_item_id_list)
            total_linked_mapping.update(linked_mapping)

            if not found_item_id_list:
                break
            counter += 1
            if number_of_layer and counter >= number_of_layer:
                break
                  
        def add_sub_items(total_linked_mapping, parent_item_id, linked_item_id_list):
            for linked_item_id in linked_item_id_list:
                if parent_item_id not in total_linked_mapping:
                    total_linked_mapping[parent_item_id] = []
                if linked_item_id not in total_linked_mapping[parent_item_id]:
                    total_linked_mapping[parent_item_id].append(linked_item_id)
            new_linked_item_list = []
            for linked_item_id in linked_item_id_list:
                if linked_item_id not in total_linked_mapping:
                    continue
                if linked_item_id == parent_item_id:
                    continue
                for new_linked_item_id in total_linked_mapping[linked_item_id]:
                    if new_linked_item_id is parent_item_id:
                        continue
                    if new_linked_item_id in total_linked_mapping[parent_item_id]:
                        continue
                    new_linked_item_list.append(new_linked_item_id)
            if new_linked_item_list:
                add_sub_items(total_linked_mapping, parent_item_id, new_linked_item_list)
        
        for item_id in item_id_list:
            linked_item_id_list = total_linked_mapping.get(item_id)
            if not linked_item_id_list:
                continue
            add_sub_items(total_linked_mapping, item_id, linked_item_id_list)
        
        return (
            list(extra_item_id_set),
            total_linked_mapping
        )


async def compare_and_filter_items(
    exp_filter,
    sample_filter,
    researchitem_filter,
    name_filter,
    date_created,
    include_linked,
    results: list[dict],
):
    # results do have a structure like this:
    # results = [exp_results, sample_results, research_item_results]
    # each result has a structure like this:
    # {
    #     "name_filter": set(),
    #     "date_created": set(),
    #     "field_data": []  # list of sets
    # }'

    exp_results = results[0]
    sample_results = results[1]
    research_item_results = results[2]

    results = []
    if exp_filter or sample_filter or researchitem_filter:
        results.append(
            {
                "exps": exp_results["direct"],
                "samples": sample_results["direct"],
                "research_items": research_item_results["direct"],
            }
        )
    if name_filter:
        results.append(
            {
                "exps": exp_results["name_filter"],
                "samples": sample_results["name_filter"],
                "research_items": research_item_results["name_filter"],
            }
        )

    if date_created:
        results.append(
            {
                "exps": exp_results["date_created"],
                "samples": sample_results["date_created"],
                "research_items": research_item_results["date_created"],
            }
        )

    field_data_length = len(exp_results["field_data"])
    if len(sample_results["field_data"]) > field_data_length:
        field_data_length = len(sample_results["field_data"])
    if len(research_item_results["field_data"]) > field_data_length:
        field_data_length = len(research_item_results["field_data"])

    for i in range(field_data_length):
        results.append(
            {
                "exps": set(),
                "samples": set(),
                "research_items": set(),
            }
        )
        if i < len(exp_results["field_data"]):
            results[-1]["exps"] = exp_results["field_data"][i]
        if i < len(sample_results["field_data"]):
            results[-1]["samples"] = sample_results["field_data"][i]
        if i < len(research_item_results["field_data"]):
            results[-1]["research_items"] = research_item_results["field_data"][i]

    coroutines = []
    for r in results:
        item_ids = []
        item_ids.extend(r["exps"])
        item_ids.extend(r["samples"])
        item_ids.extend(r["research_items"])

        coroutines.append(
            get_linked_items_recursive(
                include_linked, item_ids)
        )

    extra_results = await asyncio.gather(*coroutines)
    final_result_set = []
    for result, extra_result in zip(results, extra_results):
        temp_result = set()
        temp_result.update(result["exps"])
        temp_result.update(result["samples"])
        temp_result.update(result["research_items"])

        extra_items = extra_result[0]
        temp_result.update(extra_items)
        final_result_set.append(temp_result)

    final_result = set()
    for result in final_result_set:
        final_result = final_result & result if final_result else result

    return final_result


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
