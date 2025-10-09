from tenjin.database.db import get_db_async
from bson import ObjectId
from .filter_utils import (
    get_all_parent_groups,
    get_valid_categories,
    get_groups,
    filter_items,
    get_subgroups,
    check_if_filter_applied,
)
import asyncio
import pymongo
from flask import current_app


async def get_group_index(
    project_id,
    group_id_list,
    name_filter="",
    combo_filter=[],
    numeric_filter=[],
    group_filter=[],
    sample_filter=[],
    experiment_filter=[],
    research_item_filter=[],
    checks_filter=[],
    recent=False,
    date_filter=[],
    date_created=[],
    text_filter=[],
    displayed_categories=[],
    include_linked=False,
):

    filter_applied = check_if_filter_applied(
        name_filter,
        combo_filter,
        numeric_filter,
        group_filter,
        sample_filter,
        experiment_filter,
        research_item_filter,
        checks_filter,
        date_filter,
        date_created,
        text_filter,
    )

    top_level_group_id_list = group_id_list
    subgroup_ids = await get_subgroups(group_id_list)

    group_id_list = set(group_id_list)
    group_id_list.update(subgroup_ids)
    # group_id_list = list(group_id_list)

    db = get_db_async()

    groups_matches_filters = await get_groups(
        project_id,
        group_id_list,
        group_filter,
        name_filter,
        combo_filter,
        numeric_filter,
        checks_filter,
        date_filter,
        text_filter,
    )

    groups_to_be_checked = group_id_list - groups_matches_filters

    exp_coroutine = (
        db["Experiment"]
        .find(
            {
                "ProjectID": ObjectId(project_id),
                "GroupIDList": {"$in": list(groups_to_be_checked)},
            },
            {"_id": 1},
        )
        .to_list()
    )
    sample_coroutine = (
        db["Sample"]
        .find(
            {
                "ProjectID": ObjectId(project_id),
                "GroupIDList": {"$in": list(groups_to_be_checked)},
            },
            {"_id": 1},
        )
        .to_list()
    )
    research_item_coroutine = (
        db["ResearchItem"]
        .find(
            {
                "ProjectID": ObjectId(project_id),
                "GroupIDList": {"$in": list(groups_to_be_checked)},
            },
            {"_id": 1},
        )
        .to_list()
    )
    result = await asyncio.gather(
        exp_coroutine, sample_coroutine, research_item_coroutine
    )
    exp_ids = [e["_id"] for e in result[0]]
    sample_ids = [s["_id"] for s in result[1]]
    research_item_ids = [r["_id"] for r in result[2]]

    if filter_applied:
        filtered_item_id_set = await filter_items(
            project_id,
            exp_ids,
            sample_ids,
            research_item_ids,
            experiment_filter,
            sample_filter,
            research_item_filter,
            date_created,
            name_filter,
            combo_filter,
            numeric_filter,
            checks_filter,
            date_filter,
            text_filter,
            include_linked,
        )
    else:
        filtered_item_id_set = set(exp_ids + sample_ids + research_item_ids)

    cat_id_list, category_mapping = await get_valid_categories(
        project_id, displayed_categories
    )

    result_group_id_list, group_item_mapping = (
        await prepare_result_group_id_list_and_group_item_mapping(
            top_level_group_id_list,
            groups_matches_filters,
            filtered_item_id_set,
            category_mapping,
            cat_id_list,
            displayed_categories,
            filter_applied
        )
    )

    direction = pymongo.ASCENDING
    if recent:
        order_by = "Date"
        direction = pymongo.DESCENDING
    else:
        order_by = "NameLower"

    groups = await (
        db["Group"]
        .find(
            {"_id": {"$in": result_group_id_list}},
            {"_id": 1, "Name": 1, "GroupID": 1, "ShortID": 1},
        )
        .sort(order_by, direction)
        .to_list()
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


async def prepare_result_group_id_list_and_group_item_mapping(
    top_level_group_id_list,
    groups_matches_filters,
    filtered_item_id_set,
    category_mapping,
    cat_id_list,
    displayed_categories,
    filter_applied
):

    top_level_group_id_set = set(top_level_group_id_list)

    result_group_id_list = []
    group_item_mapping = {}

    db = get_db_async()

    coroutines = []
    exp = sample = False
    if "Experiments" in displayed_categories or "all" in displayed_categories:
        exp = True
        coroutines.append(
            db["Experiment"]
            .find(
                {
                    "$or": [
                        {"_id": {"$in": list(filtered_item_id_set)}},
                        {"GroupIDList": {"$in": list(groups_matches_filters)}},
                    ]
                },
                {"_id": 1, "GroupIDList": 1, "Name": 1, "ShortID": 1},
            )
            .sort("NameLower", pymongo.ASCENDING)
            .to_list()
        )

    if "Samples" in displayed_categories or "all" in displayed_categories:
        sample = True
        coroutines.append(
            db["Sample"]
            .find(
                {
                    "$or": [
                        {"_id": {"$in": list(filtered_item_id_set)}},
                        {"GroupIDList": {"$in": list(groups_matches_filters)}},
                    ]
                },
                {"_id": 1, "GroupIDList": 1, "Name": 1, "ShortID": 1},
            )
            .sort("NameLower", pymongo.ASCENDING)
            .to_list()
        )

    coroutines.append(
        db["ResearchItem"]
        .find(
            {
                "ResearchCategoryID": {"$in": cat_id_list},
                "$or": [
                    {"_id": {"$in": list(filtered_item_id_set)}},
                    {"GroupIDList": {"$in": list(groups_matches_filters)}},
                ],
            },
            {
                "_id": 1,
                "GroupIDList": 1,
                "Name": 1,
                "ShortID": 1,
                "ResearchCategoryID": 1,
            },
        )
        .sort("NameLower", pymongo.ASCENDING)
        .to_list()
    )

    results = await asyncio.gather(*coroutines)
    if exp:
        exps = results.pop(0)
    else:
        exps = []
    if sample:
        samples = results.pop(0)
    else:
        samples = []
    researchitems = results.pop(0)

    for exp in exps:
        result_group_id_list.extend(exp["GroupIDList"])
        add_item_to_groups_item_mapping(exp, group_item_mapping, "Experiments")

    for sample in samples:
        result_group_id_list.extend(sample["GroupIDList"])
        add_item_to_groups_item_mapping(sample, group_item_mapping, "Samples")

    for ri in researchitems:
        result_group_id_list.extend(ri["GroupIDList"])
        cat_name = category_mapping[ri["ResearchCategoryID"]]
        add_item_to_groups_item_mapping(ri, group_item_mapping, cat_name)

    maybe_not_parent_groups = set()
    for g in result_group_id_list:
        if g not in top_level_group_id_set:
            maybe_not_parent_groups.add(g)
    extra_groups_id_list = await get_all_parent_groups(maybe_not_parent_groups)
    result_group_id_list.extend(extra_groups_id_list)
    
    if not filter_applied:
        # If no filter is applied, we can add all top-level groups
        result_group_id_list.extend(top_level_group_id_set)
    
    sub_group_id_set = await get_subgroups(result_group_id_list)
    result_group_id_list.extend(list(sub_group_id_set))
    result_group_id_list = list(set(result_group_id_list))

    return result_group_id_list, group_item_mapping


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
