from tenjin.database.db import get_db_async
from bson import ObjectId
from .filter_utils import (
    filter_items,
    get_valid_categories,
    check_if_filter_applied,
)
import asyncio
from flask import current_app
from tenjin.execution.update import Update

async def get_dashboard_item_mapping(
    dataview_id,
    project_id,
    name_filter,
    combo_filter,
    numeric_filter,
    group_filter,
    sample_filter,
    experiment_filter,
    researchitem_filter,
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
        group_filter,
        sample_filter,
        experiment_filter,
        researchitem_filter,
        checks_filter,
        date_filter,
        date_created,
        text_filter,
    )

    exp_id_list = []
    sample_id_list = []
    research_item_id_list = []
    if not filter_applied:
        return {"maxPage": 1, "pageItemMapping": {1: []}}

    db = get_db_async()
    if group_filter:
        if "all" in group_filter:
            if not (experiment_filter or sample_filter or researchitem_filter):
                experiment_filter.append("all")
                sample_filter.append("all")
                researchitem_filter.append("all")
        else:
            group_id_list = [ObjectId(g) for g in group_filter]
            coroutines = []
            for c in ["Experiment", "Sample", "ResearchItem"]:
                coroutines.append(
                    db[c]
                    .find({"GroupIDList": {"$in": group_id_list}}, {"_id": 1})
                    .to_list()
                )
            results = await asyncio.gather(*coroutines)
            exp_id_list = [doc["_id"] for doc in results[0]]
            sample_id_list = [doc["_id"] for doc in results[1]]
            research_item_id_list = [doc["_id"] for doc in results[2]]

    filtered_item_id_set = await filter_items(
        project_id,
        exp_id_list,
        sample_id_list,
        research_item_id_list,
        experiment_filter,
        sample_filter,
        researchitem_filter,
        date_created,
        name_filter,
        combo_filter,
        numeric_filter,
        checks_filter,
        date_filter,
        text_filter,
        include_linked,
    )

    coroutines = []
    exp_position = None
    sample_position = None
    researchitem_position = None
    if "all" in displayed_categories or "Experiments" in displayed_categories:
        coroutines.append(
            db["Experiment"]
            .find({"_id": {"$in": list(filtered_item_id_set)}}, {"_id": 1, "Date": 1})
            .to_list()
        )
        exp_position = 0
    if "all" in displayed_categories or "Samples" in displayed_categories:
        coroutines.append(
            db["Sample"]
            .find({"_id": {"$in": list(filtered_item_id_set)}}, {"_id": 1, "Date": 1})
            .to_list()
        )
        if exp_position is None:
            sample_position = 0
        else:
            sample_position = 1

    cat_id_list, category_mapping = await get_valid_categories(
        project_id, displayed_categories
    )
    if cat_id_list:
        coroutines.append(
            db["ResearchItem"]
            .find(
                {
                    "_id": {"$in": list(filtered_item_id_set)},
                    "ResearchCategoryID": {"$in": cat_id_list},
                },
                {"_id": 1, "Date": 1},
            )
            .to_list()
        )
        if sample_position is None and exp_position is None:
            researchitem_position = 0
        elif sample_position is None:
            researchitem_position = 1
        elif exp_position is None:
            researchitem_position = 1
        else:
            researchitem_position = 2
            
    results = await asyncio.gather(*coroutines)
    exps = []
    samples = []
    researchitems = []
    if exp_position is not None:
        exps = results[exp_position]
    if sample_position is not None:
        samples = results[sample_position]
    if researchitem_position is not None:
        researchitems = results[researchitem_position]

    if not exps and not samples and not researchitems:
        return {"maxPage": 1, "pageItemMapping": {1: []}}

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
