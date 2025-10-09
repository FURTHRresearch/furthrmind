from tenjin.database.db import get_db_async
from bson import ObjectId
from .filter_utils import (
    get_all_parent_groups,
    get_groups,
    get_experiments,
    get_samples,
    get_research_items,
    compare_and_filter_items,
    get_valid_categories,
    check_if_filter_applied,
)
import asyncio
import pymongo
from flask import current_app
from tenjin.cache import Cache
from tenjin.tasks.rq_task import create_task
cache = Cache.get_cache()


async def get_page_group_mapping(
    project_id,
    name_filter="",
    combo_filter=[],
    numeric_filter=[],
    group_filter=[],
    sample_filter=[],
    experiment_filter=[],
    research_item_filter=[],
    check_filter=[],
    recent=False,
    date_filter=[],
    date_created=[],
    text_filter=[],
    displayed_categories=[],
    include_linked=False,
):
    import timeit
    start = timeit.default_timer()
    filter_applied = check_if_filter_applied(
        name_filter,
        combo_filter,
        numeric_filter,
        group_filter,
        sample_filter,
        experiment_filter,
        research_item_filter,
        check_filter,
        date_filter,
        date_created,
        text_filter,
    )

    if not filter_applied:
        return await get_not_filtered_page_group_mapping(
            project_id, recent, displayed_categories
        )


    result = await asyncio.gather(
        get_groups(
            project_id,
            None,
            group_filter,
            name_filter,
            combo_filter,
            numeric_filter,
            check_filter,
            date_filter,
            text_filter,
        ),
        get_groups_of_items(
            project_id,
            experiment_filter,
            sample_filter,
            research_item_filter,
            displayed_categories,
            date_created,
            name_filter,
            combo_filter,
            numeric_filter,
            check_filter,
            date_filter,
            text_filter,
            include_linked,
        ),
    )

    group_ids = result[0]
    group_ids.update(result[1])
    page_group_mapping = await prepare_group_mapping_data(group_ids, recent)
    print("get page group mapping", timeit.default_timer() - start)
    return page_group_mapping


async def get_not_filtered_page_group_mapping(project_id, recent, displayed_categories):
    direction = pymongo.ASCENDING
    if recent:
        order_by = "Date"
        direction = pymongo.DESCENDING
    else:
        order_by = "NameLower"

    db = get_db_async()
    toplevel_groups = await (
        db["Group"]
        .find({"ProjectID": project_id, "GroupID": None}, {"_id": 1})
        .sort(order_by, direction)
        .to_list()
    )

    group_id_list = [str(g["_id"]) for g in toplevel_groups]

    page_group_id_mapping = {}
    page = 1

    for i in range(0, len(group_id_list), current_app.groups_per_page):
        page_group_id_mapping[page] = group_id_list[i : i + current_app.groups_per_page]
        page += 1

    result_dict = {"maxPage": page - 1, "pageGroupMapping": page_group_id_mapping}

    return result_dict


async def get_groups_of_items(
    project_id,
    experiment_filter,
    sample_filter,
    research_item_filter,
    displayed_categories,
    date_created,
    name_filter,
    combo_filter,
    numeric_filter,
    checks_filter,
    date_filter,
    text_filter,
    include_linked,
):
    db = get_db_async()

    exp_ids = None
    sample_ids = None
    research_item_ids = None

    if experiment_filter or sample_filter or research_item_filter:
        if experiment_filter:
            if "all" in experiment_filter:
                exp_ids = "all"
            else:
                exp_ids = [ObjectId(e) for e in experiment_filter]
        else:
            exp_ids = []
        if sample_filter:
            if "all" in sample_filter:
                sample_ids = "all"
            else:
                sample_ids = [ObjectId(s) for s in sample_filter]
        else:
            sample_ids = []
        if research_item_filter:
            if "all" in research_item_filter:
                research_item_ids = "all"
            else:
                research_item_ids = [ObjectId(r) for r in research_item_filter]
        else:
            research_item_ids = []

    results = await asyncio.gather(
        get_experiments(
            project_id,
            exp_ids,
            date_created,
            name_filter,
            combo_filter,
            numeric_filter,
            checks_filter,
            date_filter,
            text_filter,
        ),
        get_samples(
            project_id,
            sample_ids,
            date_created,
            name_filter,
            combo_filter,
            numeric_filter,
            checks_filter,
            date_filter,
            text_filter,
        ),
        get_research_items(
            project_id,
            research_item_ids,
            date_created,
            name_filter,
            combo_filter,
            numeric_filter,
            checks_filter,
            date_filter,
            text_filter,
        ),
    )

    # results do have a structure like this:
    # results = [exp_results, sample_results, research_item_results]
    # each result has a structure like this:
    # {
    #     "name_filter": set(),
    #     "date_created": set(),
    #     "field_data": []  # list of sets

    filtered_item_id_set = await compare_and_filter_items(
        experiment_filter,
        sample_filter,
        research_item_filter,
        name_filter,
        date_created,
        include_linked,
        results,
    )

    item_keys = [str(i) for i in filtered_item_id_set]
    cached_items = cache.get_many(*item_keys)
    cached_items_id_set = {c["_id"] for c in cached_items if c is not None}
    coroutines = []
    
    item_ids = filtered_item_id_set - cached_items_id_set
    item_ids_list_in_list = []
    item_ids = list(item_ids)
    chunk_number = 5000
    for i in range(0,len(item_ids), chunk_number):
        if i + chunk_number > len(filtered_item_id_set):
            item_ids_list_in_list.append(item_ids[i:])
        else:
            item_ids_list_in_list.append(item_ids[i:i+chunk_number])

    
    if "Experiments" in displayed_categories or "all" in displayed_categories:
        for item_ids_list in item_ids_list_in_list:
            coroutines.append(
                db["Experiment"]
                .find(
                    {"_id": {"$in": item_ids_list}},
                    {"_id": 1, "GroupIDList": 1},
                )
                .to_list(),
            )

    if "Samples" in displayed_categories or "all" in displayed_categories:
        for item_ids_list in item_ids_list_in_list:
            coroutines.append(
                db["Sample"]
                .find(
                    {"_id": {"$in": item_ids_list}},
                    {"_id": 1, "GroupIDList": 1},
                )
                .to_list(),
            )

    cat_id_list, cat_mapping = await get_valid_categories(
        project_id, displayed_categories
    )

    for item_ids_list in item_ids_list_in_list:
        coroutines.append(
            db["ResearchItem"]
            .find(
                {
                    "_id": {"$in": item_ids_list},
                    "ResearchCategoryID": {"$in": cat_id_list},
                },
                {"_id": 1, "GroupIDList": 1},
            )
            .to_list(),
        )
    import timeit
    start = timeit.default_timer()
    results = await asyncio.gather(*coroutines)
    print("get all found items",timeit.default_timer() - start)
    group_ids = set()
    cache_mapping = {}
    for result in results:
        for r in result:
            group_ids.update(r["GroupIDList"])
            cache_mapping[str(r["_id"])] = r
    if cache_mapping:
        create_task(Cache.set_many, cache_mapping, timeout=3600*48)
    for item in cached_items:
        if item:
            group_ids.update(item["GroupIDList"])
    return group_ids


async def prepare_group_mapping_data(group_ids: set, recent):
    import time
    
    group_ids = list(group_ids)
    group_ids_list_in_list = []
    chunk_number = 5000
    for i in range(0,len(group_ids), chunk_number):
        if i + chunk_number > len(group_ids):
            group_ids_list_in_list.append(set(group_ids[i:]))
        else:
            group_ids_list_in_list.append(set(group_ids[i:i+chunk_number]))
    
    coroutines = []
    for group_ids in group_ids_list_in_list:
        coroutines.append(get_all_parent_groups(group_ids))
    
    results = await asyncio.gather(*coroutines)
    parent_group_ids = []
    for result in results:
        parent_group_ids.extend(result)

    reverse = False
    if recent:
        order_by = "Date"
        reverse = True
    else:
        order_by = "NameLower"

    db = get_db_async()
    
    parent_group_ids_list_in_list = []
    chunk_number = 5000
    for i in range(0, len(parent_group_ids), chunk_number):
        if i + chunk_number > len(parent_group_ids):
            parent_group_ids_list_in_list.append(parent_group_ids[i:])
        else:
            parent_group_ids_list_in_list.append(parent_group_ids[i : i + chunk_number])
    
    
    coroutines = []
    for parent_group_ids in parent_group_ids_list_in_list:
        coroutines.append(
            db["Group"]
            .find({"_id": {"$in": list(parent_group_ids)}, "GroupID": None}, {"_id": 1, order_by: 1})
            .to_list()
        )
    
    results = await asyncio.gather(*coroutines)
    groups = []
    for result in results:
        groups.extend(result)

    groups = sorted(groups, key=lambda x: x[order_by], reverse=reverse)
    group_id_list = [str(g["_id"]) for g in groups]

    page_group_id_mapping = {}
    page = 0

    for i in range(0, len(group_id_list), current_app.groups_per_page):
        page += 1
        page_group_id_mapping[page] = group_id_list[i : i + current_app.groups_per_page]
    result_dict = {"maxPage": page, "pageGroupMapping": page_group_id_mapping}

    return result_dict
