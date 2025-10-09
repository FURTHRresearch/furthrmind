import json
import time
import uuid

from bson.objectid import ObjectId

from tenjin.database.db import get_db
from tenjin.execution.append import Append
from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.file.file_storage import FileStorage
from tenjin.mongo_engine import Database, Document
from tenjin.tasks.rq_task import create_task


def getData(collection, findDict, findOne=False):
    db = get_db().db

    if findOne:
        result = db[collection].find_one(findDict)
    else:
        result = list(db[collection].find(findDict))

    return result


def copy(
    template_id,
    collection,
    project_id,
    user_id,
    group_id=None,
    include_fields=True,
    include_raw_data=False,
    include_files=False,
    include_exp=False,
    include_sample=False,
    include_researchitem=False,
    include_subgroup=False,
    do_linking=True,
    run_as_task=True,
):
    from tenjin.mongo_engine.ResearchCategory import ResearchCategory
    from tenjin.mongo_engine.Experiment import Experiment
    from tenjin.mongo_engine.Sample import Sample
    from tenjin.mongo_engine.Group import Group
    from tenjin.mongo_engine.ResearchItem import ResearchItem

    """
    param: templateID
            collection: collection of the template (Group, Experiment, Sample), string
            param: projectID, new projectID
            userID: executing user
    """

    cls_object, template_doc = Database.get_collection_class_and_document(
        collection, template_id
    )
    if not template_doc:
        return
    template_name = template_doc.Name

    data_dict = {
        "ProjectID": project_id,
    }

    subgroups_to_be_copied = []
    if collection in ["Sample", "Experiment"]:
        data_dict["GroupIDList"] = [group_id]
    elif collection == "ResearchItem":
        data_dict["GroupIDList"] = [group_id]
        template_cat = ResearchCategory.objects(
            id=template_doc.ResearchCategoryID.id
        ).first()
        cat = ResearchCategory.objects(
            ProjectID=project_id, Name=template_cat.Name
        ).first()
        if not cat:
            cat_dict = {"Name": template_cat.Name, "ProjectID": project_id}
            cat_id = Create.create("ResearchCategory", cat_dict)
        else:
            cat_id = cat.id
        data_dict["ResearchCategoryID"] = cat_id
    elif collection == "Group":
        # subgroup becomes subgroup in new
        # To avoid recursion, parent is set after subs are created
        # if template_doc.GroupID is not None:
        # data_dict["GroupID"] = group_id

        subgroups_to_be_copied = list(Group.objects(GroupID=template_id))

    number = -1
    while True:
        if number == -1:
            name = template_name
        elif number == 0:
            name = f"Copy of {template_name}"
        else:
            name = f"Copy of {template_name}_{number}"

        data_dict["Name"] = name

        doc = cls_object(**data_dict)
        try:
            doc.validate()
            break
        except:
            number += 1
            pass

    new_doc = Create.create(collection, data_dict, return_document=True)
    document_old_id_new_id_mapping = {template_id: new_doc.id}
    
    # to avoid that tasks create a new task for each copy, we can run the copy method directly, depending on the run_as_task flag
    # this is especially mandatory for copying many items with the same fields. If the items would be copied as tasks, the creation 
    # of the fields belonging to the items would be done in parallel, which could lead to conflicts
    if run_as_task:
        create_task(copy_method, collection, template_id, new_doc, document_old_id_new_id_mapping,
                    subgroups_to_be_copied, data_dict, project_id, user_id, group_id,
                    include_fields, include_raw_data, include_files, include_exp,
                    include_sample, include_researchitem, include_subgroup, do_linking)
    else:
        copy_method(
            collection, template_id, new_doc, document_old_id_new_id_mapping,
            subgroups_to_be_copied, data_dict, project_id, user_id, group_id,
            include_fields, include_raw_data, include_files, include_exp,
            include_sample, include_researchitem, include_subgroup, do_linking
        )
    return new_doc, document_old_id_new_id_mapping


def copy_method(
    collection: str,
    template_id: ObjectId,
    new_doc: Document,
    document_old_id_new_id_mapping: dict,
    subgroups_to_be_copied: list,
    data_dict: dict,
    project_id,
    user_id,
    group_id,
    include_fields,
    include_raw_data,
    include_files,
    include_exp,
    include_sample,
    include_researchitem,
    include_subgroup,
    do_linking,
):
    from tenjin.mongo_engine.ResearchCategory import ResearchCategory
    from tenjin.mongo_engine.Experiment import Experiment
    from tenjin.mongo_engine.Sample import Sample
    from tenjin.mongo_engine.Group import Group
    from tenjin.mongo_engine.ResearchItem import ResearchItem
    
    cls_object, template_doc = Database.get_collection_class_and_document(
        collection, template_id
    )
    template_name = template_doc.Name
    
    if collection == "Group":
        new_group_id = new_doc.id
        if include_exp:
            exps = Experiment.objects(GroupIDList__in=[template_id])
            for exp in exps:
                # do not run_as_task to avoid to a new task per item
                new_sub_doc, new_sub_document_id_mapping = copy(
                    exp.id,
                    "Experiment",
                    project_id,
                    user_id,
                    new_group_id,
                    include_fields,
                    include_raw_data,
                    include_files,
                    include_exp,
                    include_sample,
                    include_researchitem,
                    include_subgroup,
                    do_linking=False,
                    run_as_task=False,
                )
                document_old_id_new_id_mapping[exp.id] = new_sub_doc.id
                document_old_id_new_id_mapping.update(new_sub_document_id_mapping)

        if include_sample:
            samples = Sample.objects(GroupIDList__in=[template_id])
            for sample in samples:
                # do not run_as_task to avoid to a new task per item
                new_sub_doc, new_sub_document_id_mapping = copy(
                    sample.id,
                    "Sample",
                    project_id,
                    user_id,
                    new_group_id,
                    include_fields,
                    include_raw_data,
                    include_files,
                    include_exp,
                    include_sample,
                    include_researchitem,
                    include_subgroup,
                    do_linking=False,
                    run_as_task=False,
                )
                document_old_id_new_id_mapping[sample.id] = new_sub_doc.id
                document_old_id_new_id_mapping.update(new_sub_document_id_mapping)

        if include_researchitem:
            researchitems = ResearchItem.objects(GroupIDList__in=[template_id])
            for researchitem in researchitems:
                # do not run_as_task to avoid to a new task per item
                new_sub_doc, new_sub_document_id_mapping = copy(
                    researchitem.id,
                    "ResearchItem",
                    project_id,
                    user_id,
                    new_group_id,
                    include_fields,
                    include_raw_data,
                    include_files,
                    include_exp,
                    include_sample,
                    include_researchitem,
                    include_subgroup,
                    do_linking=False,
                    run_as_task=False,
                )
                document_old_id_new_id_mapping[researchitem.id] = new_sub_doc.id
                document_old_id_new_id_mapping.update(new_sub_document_id_mapping)

        if include_subgroup:
            # To avoid recursion, subgroups are found before new group is created
            for subgroup in subgroups_to_be_copied:
                # do not run_as_task to avoid to a new task per item
                new_sub_doc, new_sub_document_id_mapping = copy(
                    subgroup.id,
                    "Group",
                    project_id,
                    user_id,
                    new_group_id,
                    include_fields,
                    include_raw_data,
                    include_files,
                    include_exp,
                    include_sample,
                    include_researchitem,
                    include_subgroup,
                    do_linking=False,
                    run_as_task=False,
                )
                document_old_id_new_id_mapping[subgroup.id] = new_sub_doc.id
                document_old_id_new_id_mapping.update(new_sub_document_id_mapping)

        # Write Parent
        if template_doc.GroupID is not None:
            # To avoid name duplicates use a unique random name before setting the parent:
            unique_string = str(uuid.uuid4())
            Update.update("Group", "Name", unique_string, new_doc.id)

            # update parent group
            Update.update("Group", "GroupID", group_id, new_doc.id)

            # look for name and set it
            data_dict["GroupID"] = group_id
            # first check name before setting the parent group
            number = -1
            while True:
                if number == -1:
                    name = template_name
                elif number == 0:
                    name = f"Copy of {template_name}"
                else:
                    name = f"Copy of {template_name}_{number}"

                data_dict["Name"] = name

                doc = cls_object(**data_dict)
                try:
                    doc.validate()
                    break
                except:
                    number += 1
                    pass
            Update.update("Group", "Name", data_dict["Name"], new_doc.id)

        if do_linking:
            link_items(document_old_id_new_id_mapping)

    if include_fields:
        field_data_id_list = copyFieldData(template_id, collection, project_id, user_id)
        new_doc_id = Update.update(
            collection, "FieldDataIDList", field_data_id_list, new_doc.id
        )

    if collection in ["Experiment", "Sample", "ResearchItem"]:
        if include_files:
            create_task(
                copy_files,
                [f.id for f in template_doc.FileIDList],
                collection,
                new_doc.id,
            )
            # copy_files([f.id for f in template_doc.FileIDList], collection, new_doc.id)

        if include_raw_data:
            copy_data_table(template_id, new_doc, collection, project_id, user_id)


def copyFieldData(template_id, collection, project_id, user_id):
    """
    param: templateID
    collection: collection of the template (Group, Experiment, Sample)
    param: projectID, new projectID
    userID: executing user
    newID: id of new item
    exp: bool, if newID refers to exp or not

    copies all fieldData from Template to new project
    - this method is recursive, that means all comboBox fields are searched in a nested way
    - creates all fields, that are found
        - if there is already a field with the same name in the new project, the type is compared. If type
        is different => conflict
    - creates all comboBoxEntries from the template project in the new project
        - Each comboBox entry will preserv it's fieldData. If there is already a comboBoxEntry with the
        same name in the new project belonging to the same field, the fieldData are not touched
    - creates all units and unit categories.
        - Add new units to new categories.
        - Already existing units and unit categories in the new project are not touched
    - Copy content of all notebook fields
        - That means files and images are duplicated and the old file
        and image ids are replaced by the new once

    The method also grabs all fields and units that are used in a nested way in a comboBoxEntry.
    """
    start = time.time()
    template = getData(collection, {"_id": template_id}, findOne=True)

    field_data_id_list = template["FieldDataIDList"]

    # Check for conflicted fields and all fields that needs to be created
    (
        conflictedFields,
        fieldList,
        toBeCreatedFieldList,
        existingFieldList,
        unitList,
        toBeCreatedUnitList,
        existingUnitList,
    ) = checkFieldAndUnitForFieldDataListFromForeignProject(
        field_data_id_list, project_id, user_id
    )
    if len(conflictedFields) > 0:
        return None
    print("Check everything", time.time() - start)

    # Create all fields in the new project, that needed to be created and return a list with the new fields
    newFieldList = createNewFields(toBeCreatedFieldList, project_id, user_id)
    # together with the existing fields in the new project, a total field list can be build
    totalNewFieldList = newFieldList
    totalNewFieldList.extend(existingFieldList)

    # create a mapping between original fieldID and the new fields. This is needed to create the fieldData later on
    originalFieldIDNewFieldMapping = {}
    for field in fieldList:
        for newField in totalNewFieldList:
            if field["Name"] == newField["Name"]:
                originalFieldIDNewFieldMapping[field["_id"]] = newField
                break

    # create all units in the new project, that needed to be created and return a list with the new units
    newUnitList = createNewUnits(toBeCreatedUnitList, project_id, user_id)
    totalNewUnitList = []
    for newUnit in newUnitList:
        totalNewUnitList.append(newUnit)
    for exitingUnit in existingUnitList:
        totalNewUnitList.append(exitingUnit)

    # create a mapping between original unitID and the new unit. This is needed to create the fieldData later on
    originalUnitIDNewUnitMapping = {}
    newUnitIDOriginalUnitMapping = {}
    for unit in unitList:
        for newUnit in totalNewUnitList:
            if unit["ShortName"] == newUnit["ShortName"]:
                originalUnitIDNewUnitMapping[unit["_id"]] = newUnit
                newUnitIDOriginalUnitMapping[newUnit["_id"]] = unit
                break
    updateUnitDefinitions(
        newUnitList, newUnitIDOriginalUnitMapping, originalUnitIDNewUnitMapping, user_id
    )
    # create all needed unit categories and update the new units
    createNewUnitCategoriesAndUpdateNewUnits(
        unitList, originalUnitIDNewUnitMapping, project_id, user_id
    )
    print("after unit task", time.time() - start)
    # Look for the fields of type "ComboBox" for the original and new field list
    originalComboFieldList = [
        field for field in fieldList if field["Type"] == "ComboBox"
    ]
    newComboFieldList = [
        field for field in totalNewFieldList if field["Type"] == "ComboBox"
    ]

    # create all comboBoxEntries and get all original fieldData per new comboBoxEntryID =>
    # mapping with newComboEntryID as key and original field_data_id_list as value
    # the newComboEntryID is needed, to attach the new fieldData (not created yet) to the right comboEntry
    comboEntryFieldDataMapping, originalComboIDNewComboIDMapping = (
        createNewComboEntries(originalComboFieldList, newComboFieldList, user_id, project_id)
    )

    print("Create combo", time.time() - start)

    # prepare an original field_data_id_list with all field Data that should be created in the new project, meaning the
    # one passed to the method + the one that needs to be created because they belong to comboBoxEntries
    totalFieldDataIDList = list(field_data_id_list)
    for _fieldDataIDList in comboEntryFieldDataMapping.values():
        totalFieldDataIDList.extend(_fieldDataIDList)

    # Getting the originalFieldDataList from the original field_data_id_list and create a dict with the _id as the key
    originalFieldDataList = getData(
        "FieldData",
        {"_id": {"$in": totalFieldDataIDList}},
    )
    originalFieldDataMapping = {
        fieldData["_id"]: fieldData for fieldData in originalFieldDataList
    }

    # sourceTargetNotebookIDMapperList is a mapping between old and new notebook entries. After all field data are created,
    # the notebook files and content will be copied
    sourceTargetNotebookIDMapperList = []
    # Start creating the new fieldData, 1. the one that were passed to the method and then the one for the comboBoxEntries
    newFieldDataIDList = []
    for fieldDataID in field_data_id_list:
        originalFieldData = originalFieldDataMapping[fieldDataID]
        originalFieldID = originalFieldData["FieldID"]
        newField = originalFieldIDNewFieldMapping[originalFieldID]
        newFieldDataID, notebookIDMapper = copyOneFieldData(
            originalFieldData,
            newField,
            originalComboIDNewComboIDMapping,
            originalUnitIDNewUnitMapping,
            project_id,
            user_id,
            get_db(),
        )
        newFieldDataIDList.append(newFieldDataID)
        if notebookIDMapper:
            sourceTargetNotebookIDMapperList.append(notebookIDMapper)

    print("Create field data", time.time() - start)

    copyFieldDataOfComboEntries(
        comboEntryFieldDataMapping,
        originalFieldDataMapping,
        originalFieldIDNewFieldMapping,
        originalComboIDNewComboIDMapping,
        originalUnitIDNewUnitMapping,
        project_id,
        user_id,
    )

    print("Create field data combo", time.time() - start)

    # taskQueue.enqueue(copyFieldDataOfComboEntries,comboEntryFieldDataMapping, originalFieldDataMapping, originalFieldIDNewFieldMapping,
    #                   originalComboIDNewComboIDMapping, originalUnitIDNewUnitMapping, projectID,
    #                   userID)
    # for comboBoxEntryID in comboEntryFieldDataMapping:
    #     field_data_id_list = comboEntryFieldDataMapping[comboBoxEntryID]
    #     newFieldDataIDList = []
    #     for fieldDataID in field_data_id_list:
    #         originalFieldData = originalFieldDataMapping[fieldDataID]
    #         originalFieldID = originalFieldData["FieldID"]
    #         newField = originalFieldIDNewFieldMapping[originalFieldID]
    #         newFieldDataID, notebookIDMapper = copyOneFieldData(originalFieldData, newField, originalComboIDNewComboIDMapping,
    #             originalUnitIDNewUnitMapping, projectID, userID)
    #         newFieldDataIDList.append(newFieldDataID)
    #         if notebookIDMapper:
    #             sourceTargetNotebookIDMapperList.append(notebookIDMapper)
    #
    #     db = get_db()
    #     Update.update(Collection.ComboBoxEntry, ComboBoxEntry.FieldDataIDList, newFieldDataIDList, comboBoxEntryID,
    #                   db, userID)

    # copy content of notebook fields
    if sourceTargetNotebookIDMapperList:
        copyContentAndFilesFromOneNotebookToAnother(
            sourceTargetNotebookIDMapperList, user_id, get_db()
        )

    print(newFieldDataIDList)
    print("Finish", time.time() - start)

    return newFieldDataIDList


def checkFieldAndUnitForFieldDataListFromForeignProject(
    fieldDataIDList, projectID, userID
):
    """
    param: fieldDataIDList
    param: projectID, new projectID
    database: mongo client, not our DatabaseClient.

    This method looks for all fields, that must be created in the new project by comparing fieldNames in the old
    and new project. If there is already with the same name in both projects, but from different field type, this
    field is added to a conflicted list.

    The method also grabs all fields and units that are used in a nested way in a comboBoxEntry.
    """

    # First we need all fields and units, that must be created in the new project. Also, all fields and units that are
    # referenced in comboBoxEntries must be found
    fieldList, unitList = getAllFieldAndUnitFromFieldDataIDListRecursive(
        fieldDataIDList, userID
    )

    conflictedFieldList, toBeCreatedFieldList, existingFieldList = checkFieldList(
        fieldList, projectID, userID
    )

    toBeCreatedUnitList, existingUnitList = checkUnitList(unitList, projectID, userID)

    return (
        conflictedFieldList,
        fieldList,
        toBeCreatedFieldList,
        existingFieldList,
        unitList,
        toBeCreatedUnitList,
        existingUnitList,
    )


def getAllFieldAndUnitFromFieldDataIDListRecursive(fieldDataIDList, userID):
    """
    In case field is a comboBox, all fieldData of the selected comboBoxEntry will be searched as well
    For units, also the needed units from definition strings will be searched and put on the list to be created.
    Both, fields and units search is treated recursively.
    """

    # Get all fields and units from the fieldDataList by searching for the fieldID and unitID
    fieldDataList = getData("FieldData", {"_id": {"$in": fieldDataIDList}})
    fieldIDList = [fieldData["FieldID"] for fieldData in fieldDataList]
    unitIDList = [fieldData["UnitID"] for fieldData in fieldDataList]

    fieldList = getData(
        "Field",
        {"_id": {"$in": fieldIDList}},
    )
    unitList = getData("Unit", {"_id": {"$in": unitIDList}})

    # getting all fields of type "ComboBox" and creating an id list of those
    comboFieldList = []
    comboFieldIDList = []
    # all comboBoxSyn fields must be checked for the reference comboField. Maybe this field is not yet in the
    # fieldList and thus must be queried
    comboReferenceFieldIDListToBeQueried = []
    for field in fieldList:
        if field["Type"] == "ComboBox":
            if field["_id"] not in comboFieldIDList:
                comboFieldIDList.append(field["_id"])
                comboFieldList.append(field)
        # for comboSynFields, we also must add the reference field to that list of fields that should be created
        elif field["Type"] == "ComboBoxSynonym":
            referenceComboFieldID = field["ComboBoxFieldID"]
            if referenceComboFieldID not in comboFieldIDList:
                if referenceComboFieldID not in fieldIDList:
                    comboReferenceFieldIDListToBeQueried.append(referenceComboFieldID)

    # get all field for the referenceComboFields for the ComboBoxSyn and add them to the fieldList and fieldIDList
    if comboReferenceFieldIDListToBeQueried:
        additionalFieldList = getData(
            "Field", {"_id": {"$in": comboReferenceFieldIDListToBeQueried}}
        )

        for additionalField in additionalFieldList:
            fieldList.append(additionalField)
            fieldIDList.append(additionalField["_id"])
            comboFieldList.append(additionalField)
            comboFieldIDList.append(additionalField["_id"])

    # getting all comboBoxEntries that are attached to the found fields of type "ComboBox"
    comboEntryList = getData("ComboBoxEntry", {"FieldID": {"$in": comboFieldIDList}})

    # Creating a new fieldDataIDList for all fieldData that are found in the comboBoxEntries
    comboFieldDataIDList = []
    for comboEntry in comboEntryList:
        comboFieldDataIDList.extend(comboEntry["FieldDataIDList"])

    # Calling this method again (recursion) to find the needed fields and units from the fieldDataList in the comboBoxEntries
    additionalFieldList = []
    additionalUnitList = []
    if comboFieldDataIDList:
        additionalFieldList, additionalUnitList = (
            getAllFieldAndUnitFromFieldDataIDListRecursive(comboFieldDataIDList, userID)
        )

    # The new fields from the comboBoxEntries are added to the fieldList if they are not already inside
    if additionalFieldList:
        for field in additionalFieldList:
            if field["_id"] not in fieldIDList:
                fieldList.append(field)
                fieldIDList.append(field["_id"])
    # The new units from the comboBoxEntries are added to the unitList if they are not already inside
    if additionalUnitList:
        for unit in additionalUnitList:
            if unit["_id"] not in unitIDList:
                unitList.append(unit)
                unitIDList.append(unit["_id"])

    # For units, we need to check the definition string if more units are necessary to be created in the new project
    # This will also be done recursively.
    additionalUnitListFromDefinition = getUnitListFromDefinitionRecursive(
        unitList, userID
    )
    # The newly found units from the definition strings will be added to the unitList if they are not yet part of it.
    for unit in additionalUnitListFromDefinition:
        if unit["_id"] in unitIDList:
            continue
        unitList.append(unit)
    return fieldList, unitList


def checkFieldList(fieldList, projectID, userID):
    """
    This method checks if there are conflicted fields, which fields must be created and which do exist already
    """

    # create a fieldNameList and a mapping with name as key and field as value
    fieldNameList = [field["Name"] for field in fieldList]
    fieldNameMapping = {field["Name"]: field for field in fieldList}

    # getting all new fields within the new project by asking for the fieldName and projectID
    newFieldList = getData(
        "Field", {"Name": {"$in": fieldNameList}, "ProjectID": projectID}
    )

    existingFieldList = []
    existingFieldIDList = []
    conflictedFieldList = []

    # if no new fields are found, all must be created
    if not newFieldList:
        toBeCreatedFieldList = fieldList
    else:
        # compare the original fields with the one in the new project. If the field type is equal, we do not have a
        # problem. But same name and different type is a conflict
        conflictedFieldList = []
        for newField in newFieldList:
            originalField = fieldNameMapping[newField["Name"]]
            if originalField["Type"] == newField["Type"]:
                # adding the fields to the existing list
                existingFieldIDList.append(originalField["_id"])
                existingFieldList.append(newField)
                continue
            # only if the type is different, this part will be reached
            conflictedFieldList.append(originalField)

        # create a fieldList of fields that must be created in the new project.
        toBeCreatedFieldList = [
            field for field in fieldList if field["_id"] not in existingFieldIDList
        ]

    return conflictedFieldList, toBeCreatedFieldList, existingFieldList


def createNewFields(fieldList, projectID, userID):
    """
    With this method all new fields will be created.
    All comboBoxSyn fields will be create at the end to ensure that the reference comboBox field is already present
    RawDataCalcScripts will be copied and the new fileID will be used
    TemplateSpreadsheet will be created if used in calculation
    """
    newFieldIDList = []
    comboBoxSynFieldList = []
    comboBoxOldNewIDMapper = {}
    for field in fieldList:

        # ComboBoxSyn fields must be created at the end, to ensure, that the reference comboBox fields are
        # already created
        if field["Type"] == "ComboBoxSynonym":
            comboBoxSynFieldList.append(field)
            continue

        # For script files, the file is copied and the new fileID will be used
        newRawDataCalcScriptFileID = None
        if field["RawDataCalcScriptFileID"] is not None:
            fs = FileStorage(get_db())
            newRawDataCalcScriptFileID = fs.copy(field["RawDataCalcScriptFileID"])

        webdatacalc_script = field["WebDataCalcScript"]
        if field["CalculationType"] == "Spreadsheet":
            script = field["WebDataCalcScript"]
            script_lower = script.replace("#spreadsheet", "")
            script_dict = json.loads(script_lower)
            spreadsheetTemplateID = script_dict.get("TemplateID")
            if spreadsheetTemplateID:
                spreadsheetTemplate = getData(
                    "SpreadSheet", {"_id": spreadsheetTemplateID}, findOne=True
                )
                if spreadsheetTemplate:
                    fs = FileStorage(get_db())
                    new_file_id = fs.copy(spreadsheetTemplate["FileID"])
                    spreadsheet_data_dict = {
                        "ProjectID": projectID,
                        "Template": True,
                        "TemplateName": spreadsheetTemplate["TemplateName"],
                        "FileID": new_file_id,
                    }
                    spreadsheet_id = Create.create("SpreadSheet", spreadsheet_data_dict)
                    script_dict["TemplateID"] = spreadsheet_id
                    webdatacalc_script = script_dict

        dataDict = {
            "Name": field["Name"],
            "Type": field["Type"],
            "ProjectID": projectID,
            "ComboBoxFieldID": field["ComboBoxFieldID"],
            "RawDataCalcScriptFileID": newRawDataCalcScriptFileID,
            "RawDataCalcOutputList": field["RawDataCalcOutputList"],
            "CalculationType": field["CalculationType"],
            "WebDataCalcScript": webdatacalc_script,
        }

        newFieldID = Create.create("Field", dataDict, get_db(), userID)
        newFieldIDList.append(newFieldID)

        # for the creation of the ComboBoxSyn field a mapper between old fieldID and new fieldID of all comboBox
        # fields is necessary
        if field["Type"] == "ComboBox":
            comboBoxOldNewIDMapper[field["_id"]] = newFieldID
            continue

    # Creating all comboBoxSyn field
    for field in comboBoxSynFieldList:
        # the new comboBoxFieldID is picked from the comboBoxOldNewIDMapper
        dataDict = {
            "Name": field["Name"],
            "Type": field["Type"],
            "ProjectID": [projectID],
            "ComboBoxFieldID": comboBoxOldNewIDMapper[field["ComboBoxFieldID"]],
            "RawDataCalcScriptFileID": None,
            "RawDataCalcOutputList": None,
            "CalculationType": None,
            "WebDataCalcScript": None,
        }

        newFieldID = Create.create("Field", dataDict, get_db(), userID)
        newFieldIDList.append(newFieldID)

    # To return not only the newFieldIDList, a query to get all new fields is Done
    if newFieldIDList:
        newFieldList = getData("Field", {"_id": {"$in": newFieldIDList}})
    else:
        newFieldList = []
    return newFieldList


def checkUnitList(unitList, projectID, userID):
    """
    This method checks all units and returns all units that must be created and the once that do exist already
    """

    # Unit stuff
    # create a unitNameList and a mapping with name as key and field as value
    unitNameList = [unit["ShortName"] for unit in unitList]
    unitNameMapping = {unit["ShortName"]: unit for unit in unitList}

    # getting all new fields within the new project by asking for the fieldName and projectID
    newUnitList = getData(
        "Unit",
        {
            "ShortName": {"$in": unitNameList},
            "$or": [{"ProjectID": projectID}, {"Predefined": True}],
        },
    )

    existingUnitList = []
    existingUnitIDList = []

    # if no new fields are found, all must be created
    if not newUnitList:
        toBeCreatedUnitList = unitList
    else:
        # compare the original units with the one in the new project.
        for newUnit in newUnitList:
            originalUnit = unitNameMapping[newUnit["ShortName"]]
            # adding the fields to the existing list
            existingUnitIDList.append(originalUnit["_id"])
            existingUnitList.append(newUnit)

        # create a fieldList of fields that must be created in the new project.
        toBeCreatedUnitList = [
            unit for unit in unitList if unit["_id"] not in existingUnitIDList
        ]
    return toBeCreatedUnitList, existingUnitList


def getUnitListFromDefinitionRecursive(unitList, userID):
    """
    Method to find all necessary units from the definition string. This method is recursively.
    """
    newUnitIDList = []
    # get all units found in the definition strings and create one list with all unitIDs
    for unit in unitList:
        definition = unit["Definition"]
        if definition is None or definition == "":
            continue
        unitIDList = findAllUnitIDInDefinition(definition)
        if unitIDList:
            for unitID in unitIDList:
                if unitID == unit["_id"]:
                    continue  # avoid deep recursion, endless loop
                if unitID not in newUnitIDList:
                    newUnitIDList.append(unitID)

    # Retrieve all units found in the definition strings
    if newUnitIDList:
        newUnitList = getData("Unit", {"_id": {"$in": newUnitIDList}})

        # Call this method again to get the units from definitions strings from the found units, recursion
        additionalUnitList = getUnitListFromDefinitionRecursive(newUnitList, userID)

        # add units to the newUnitIDList if they are not yet inside
        if additionalUnitList:
            for unit in additionalUnitList:
                if unit["_id"] in newUnitIDList:
                    continue
                newUnitList.append(unit)
        return newUnitList
    return []


def findAllUnitIDInDefinition(definition):
    """
    Seperate a definition string to a unitIDList
    """
    unitIDList = []
    index = definition.find("<u>")
    while index > -1:
        indexEnd = definition.find("</u>")
        indexEnd += 4
        unitTagString = definition[index:indexEnd]
        unitID = unitTagString[3:-4]
        unitID = ObjectId(unitID)
        if unitID not in unitIDList:
            unitIDList.append(unitID)
        definition = definition[indexEnd:]
        index = definition.find("<u>")
    return unitIDList


def createNewUnits(unitList, projectID, userID):
    """
    Method to create all new units, UnitCategory will be set later on.
    """
    newUnitIDList = []
    for unit in unitList:
        dataDict = {
            "ShortName": unit["ShortName"],
            "Definition": unit["Definition"],
            "LongName": unit["LongName"],
            "ProjectID": projectID,
            "UnitCategoryIDList": [],
        }

        newUnitID = Create.create("Unit", dataDict)
        newUnitIDList.append(newUnitID)

    newUnitList = getData("Unit", {"_id": {"$in": newUnitIDList}})
    return newUnitList


def updateUnitDefinitions(
    newUnitList, newUnitIDOriginalUnitMapping, originalUnitIDNewUnitMapping, userID
):
    database = get_db()

    for unit in newUnitList:
        originalUnit = newUnitIDOriginalUnitMapping[unit["_id"]]
        if originalUnit["Definition"] == "" or originalUnit["Definition"] is None:
            continue
        definition = originalUnit["Definition"]
        for unitID in originalUnitIDNewUnitMapping:
            definition.replace(str(unitID), str(originalUnitIDNewUnitMapping[unitID]))

        Update.update("Unit", "Definition", definition, unit["_id"], database, userID)


def createNewUnitCategoriesAndUpdateNewUnits(
    originalUnitList, originalUnitIDNewUnitMapping, projectID, userID
):
    """
    Method to create all new unit categories and assign the new units to the newly created unit categories
    """

    originalUnitCategoryIDList = []
    for originalUnit in originalUnitList:
        if originalUnit["UnitCategoryIDList"]:
            for unitCategoryID in originalUnit["UnitCategoryIDList"]:
                if unitCategoryID not in originalUnitCategoryIDList:
                    originalUnitCategoryIDList.append(unitCategoryID)
    if not originalUnitCategoryIDList:
        return

    # get the unit categories, including predefined
    originalUnitCategoryList = getData(
        "UnitCategory", {"_id": {"$in": originalUnitCategoryIDList}}
    )

    unitCategoryNameList = [
        unitCategory["Name"] for unitCategory in originalUnitCategoryList
    ]

    # get the existng categories, including predefined
    existingUnitCategoryList = getData(
        "UnitCategory",
        {
            "Name": {"$in": unitCategoryNameList},
            "$or": [{"ProjectID": projectID}, {"Predefined": True}],
        },
    )

    # build a mapping with categoryName as key and the category as value
    existingUnitCategoryNameMapping = {
        unitCategory["Name"]: unitCategory for unitCategory in existingUnitCategoryList
    }

    # find the unitCategories, that must be created and map the already existing one to the original ID,
    # this mapping is needed later
    toBeCreatedUnitCategoryList = []
    originalUnitCategoryIDNewUnitCategoryIDMapping = {}
    for originalUnitCategory in originalUnitCategoryList:
        categoryName = originalUnitCategory["Name"]
        # check if the original name exists in the newCategoryMapping (check for keys), if not => create,
        # otherwise add to originalUnitCategoryIDNewUnitCategoryIDMapping
        if categoryName not in existingUnitCategoryNameMapping:
            toBeCreatedUnitCategoryList.append(originalUnitCategory)
        else:
            originalUnitCategoryIDNewUnitCategoryIDMapping[
                originalUnitCategory["_id"]
            ] = existingUnitCategoryNameMapping[categoryName]["_id"]

    # get DatabaseClient needed for Create.create and Append.append
    db = get_db()

    # iterate toBeCreatedUnitCategoryList to create new categories and append to originalUnitCategoryIDNewUnitCategoryIDMapping
    if toBeCreatedUnitCategoryList:
        for unitCategory in toBeCreatedUnitCategoryList:
            unitCategoryDict = {
                "Name": unitCategory["Name"],
                "ProjectID": projectID,
            }
            newUnitCategoryID = Create.create("UnitCategory", unitCategoryDict)

            originalUnitCategoryIDNewUnitCategoryIDMapping[unitCategory["_id"]] = (
                newUnitCategoryID
            )

    # All categories are created. Now ensure, that the new categories are linked to the right new units
    for originalUnit in originalUnitList:
        newUnit = originalUnitIDNewUnitMapping[originalUnit["_id"]]
        newUnitCategoryIDList = newUnit["UnitCategoryIDList"]
        for originalUnitCategoryID in originalUnit["UnitCategoryIDList"]:
            newUnitCategoryID = originalUnitCategoryIDNewUnitCategoryIDMapping[
                originalUnitCategoryID
            ]
            if newUnitCategoryID not in newUnitCategoryIDList:
                Append.append(
                    "Unit",
                    "UnitCategoryIDList",
                    newUnit["_id"],
                    newUnitCategoryID,
                    db,
                    userID,
                )


def createNewComboEntries(originalComboFieldList, newComboFieldList, userID, project_id):
    """
    param: originalComboFieldList: All combo fields in the original projects
    param: newComboFieldList: All combo fields in the new project. These fields have been created already, that means
                                for every field in the original list should be an equivalent in the new List
    param: userID: userID of executing user

    return: mapping with new combobox entry as key and fieldData that need to be created
    return: mapping between old and new comboEntryID

    This method first gets all comboBoxEntries from the original project and also from the new Project. Then, these
    two lists are compared:
        - For every fieldName must be all comboBoxEntry in the original and new project. If there is none in the
            new project => it will be created
        - If there is already a comboEntry in the new Project, the fieldData are not touched. For new created Combobox
            entries, a list with original FieldData will be returned

    """

    # getting a dict for the original comboFields with the _id as key and a list with the comboFieldIDs only
    originalComboFieldIDMapping = {
        field["_id"]: field for field in originalComboFieldList
    }
    originalComboFieldIDList = [field["_id"] for field in originalComboFieldList]

    # getting 2 dicts for the new comboFields: 1. with the _id and a 2. with the fieldName as key
    # and getting a list with the comboFieldIDs only
    newComboFieldNameMapping = {field["Name"]: field for field in newComboFieldList}
    newComboFieldIDMapping = {field["_id"]: field for field in newComboFieldList}
    newComboFieldIDList = [field["_id"] for field in newComboFieldList]

    # getting all original comboEntries
    originalComboBoxEntryList = getData(
        "ComboBoxEntry", {"FieldID": {"$in": originalComboFieldIDList}}
    )
    # Create a mapping with the fieldName as value and the corresponding comboEntries in a list as the values
    originalComboBoxEntryFieldNameMapping = {}
    for comboEntry in originalComboBoxEntryList:
        fieldID = comboEntry["FieldID"]
        fieldName = originalComboFieldIDMapping[fieldID]["Name"]
        if fieldName not in originalComboBoxEntryFieldNameMapping:
            originalComboBoxEntryFieldNameMapping[fieldName] = []
        originalComboBoxEntryFieldNameMapping[fieldName].append(comboEntry)

    # getting all new comboEntries
    newComboBoxEntryList = getData(
        "ComboBoxEntry", {"FieldID": {"$in": newComboFieldIDList}}
    )
    newComboBoxEntryFieldNameMapping = {}
    # Create a mapping with the fieldName as value and the corresponding comboEntries in a list as the values
    for comboEntry in newComboBoxEntryList:
        fieldID = comboEntry["FieldID"]
        fieldName = newComboFieldIDMapping[fieldID]["Name"]
        if fieldName not in newComboBoxEntryFieldNameMapping:
            newComboBoxEntryFieldNameMapping[fieldName] = []
        newComboBoxEntryFieldNameMapping[fieldName].append(comboEntry)

    # Compare the two created mappings and create a new mapping for all comboEntries, that should be created
    # with fieldName as key and the original combo Entry in a list as value. Thus we know for every field name,
    # which comboEntries we must create
    toBeCreateComboEntryMapping = {}
    # Create a mapping between the old comboID and the new comboID. This will be needed later on
    originalComboIDNewComboIDMapping = {}
    for fieldName in originalComboBoxEntryFieldNameMapping:
        toBeCreateComboEntryMapping[fieldName] = []
        # if the fieldName is not in the newComboBoxEntryFieldNameMapping, the complete list must be created
        if fieldName not in newComboBoxEntryFieldNameMapping:
            toBeCreateComboEntryMapping[fieldName] = (
                originalComboBoxEntryFieldNameMapping[fieldName]
            )
        else:
            # the fieldName exists already: compare the comboBoxEntry names of the original and new combo entries.
            for originalComboEntry in originalComboBoxEntryFieldNameMapping[fieldName]:
                newComboFound = False
                for newComboEntry in newComboBoxEntryFieldNameMapping[fieldName]:
                    # There is already a comboEntry with the right name => do not create a new combo entry
                    if originalComboEntry["Name"] == newComboEntry["Name"]:
                        newComboFound = True
                        # add to originalComboIDNewComboIDMapping
                        originalComboIDNewComboIDMapping[originalComboEntry["_id"]] = (
                            newComboEntry["_id"]
                        )
                        break
                # there was no comboEntry found with the correct name => create
                if not newComboFound:
                    toBeCreateComboEntryMapping[fieldName].append(originalComboEntry)

    # In the next steps, the comboBox Entries will be created. Additionally, all fieldData that are attached to the
    # original combo entries must be created as well. Therefor we generate a map between the new comboEntryID and
    # the original fieldDataIDList

    toBeCreateFieldDataMapping = {}
    # with toBeCreateComboEntryMapping mapping all comboEntries can be created
    for fieldName in toBeCreateComboEntryMapping:
        newFieldID = newComboFieldNameMapping[fieldName]["_id"]
        for originalComboEntry in toBeCreateComboEntryMapping[fieldName]:
            comboDict = {
                "Name": originalComboEntry["Name"],
                "FieldID": newFieldID,
                "ProjectID": project_id
            }
            # the Create.create method works with the DatabaseClient only (Enums), thus we must get an instance of that client
            db = get_db()
            comboEntryID = Create.create("ComboBoxEntry", comboDict, db, userID)
            # add all original fieldDataIDList to the toBeCreateFieldDataMapping
            toBeCreateFieldDataMapping[comboEntryID] = originalComboEntry[
                "FieldDataIDList"
            ]
            # add to originalComboIDNewComboIDMapping
            originalComboIDNewComboIDMapping[originalComboEntry["_id"]] = comboEntryID

    return toBeCreateFieldDataMapping, originalComboIDNewComboIDMapping


def copyFieldDataOfComboEntries(
    comboEntryFieldDataMapping,
    originalFieldDataMapping,
    originalFieldIDNewFieldMapping,
    originalComboIDNewComboIDMapping,
    originalUnitIDNewUnitMapping,
    projectID,
    userID,
):
    database = get_db()
    sourceTargetNotebookIDMapperList = []
    for comboBoxEntryID in comboEntryFieldDataMapping:
        fieldDataIDList = comboEntryFieldDataMapping[comboBoxEntryID]
        newFieldDataIDList = []
        for fieldDataID in fieldDataIDList:
            originalFieldData = originalFieldDataMapping[fieldDataID]
            originalFieldID = originalFieldData["FieldID"]
            newField = originalFieldIDNewFieldMapping[originalFieldID]
            newFieldDataID, notebookIDMapper = copyOneFieldData(
                originalFieldData,
                newField,
                originalComboIDNewComboIDMapping,
                originalUnitIDNewUnitMapping,
                projectID,
                userID,
                database,
            )
            newFieldDataIDList.append(newFieldDataID)
            if notebookIDMapper:
                sourceTargetNotebookIDMapperList.append(notebookIDMapper)

        Update.update(
            "ComboBoxEntry",
            "FieldDataIDList",
            newFieldDataIDList,
            comboBoxEntryID,
            database,
            userID,
        )

    copyContentAndFilesFromOneNotebookToAnother(
        sourceTargetNotebookIDMapperList, userID, database
    )


def copyOneFieldData(
    fieldData,
    newField,
    originalComboIDNewComboIDMapping,
    originalUnitIDNewUnitMapping,
    projectID,
    userID,
    database,
):
    """
    Method to copy one fieldData.
    """

    fieldID = newField["_id"]
    fieldType = newField["Type"]
    notebookIDMapper = {}
    if fieldType == "MultiLine":
        notebookDict = {
            "Content": "",
            "ImageFileIDList": [],
            "FileIDList": [],
            "ProjectID": projectID,
        }

        newNotebookID = Create.create("Notebook", notebookDict)
        notebookIDMapper["Source"] = fieldData["Value"]
        notebookIDMapper["Target"] = newNotebookID

        dataDict = {
            "FieldID": fieldID,
            "Value": newNotebookID,
            "UnitID": None,
            "ProjectID": projectID,
        }

    elif fieldType == "ComboBox":

        originalComboBoxID = fieldData["Value"]
        if originalComboBoxID is None:
            newComboBoxID = None
        else:
            newComboBoxID = originalComboIDNewComboIDMapping[originalComboBoxID]
        dataDict = {
            "FieldID": fieldID,
            "Value": newComboBoxID,
            "UnitID": None,
            "ProjectID": projectID,
        }

    elif fieldType == "Numeric":
        originalUnitID = fieldData["UnitID"]
        newUnitID = None
        if originalUnitID is not None:
            newUnitID = originalUnitIDNewUnitMapping[originalUnitID]["_id"]
        dataDict = {
            "FieldID": fieldID,
            "Value": fieldData["Value"],
            "UnitID": newUnitID,
            "ProjectID": projectID,
        }

    elif fieldType == "Link":
        value = None
        fieldDataLinkID = fieldData["Value"]
        if fieldDataLinkID is not None:
            fieldDataLink = getData(
                "FieldDataLink",
                {"_id": fieldDataLinkID},
            )

            linkDataDict = {
                "TargetID": fieldDataLink["TargetID"],
                "FieldID": fieldID,
            }
            newLinkID = Create.create("FieldDataLink", linkDataDict)
            value = newLinkID

        dataDict = {
            "FieldID": fieldID,
            "Value": value,
            "UnitID": None,
            "ProjectID": projectID,
        }

    else:
        dataDict = {
            "FieldID": fieldID,
            "Value": fieldData["Value"],
            "UnitID": fieldData["UnitID"],
            "ProjectID": projectID,
        }

    fieldDataID = Create.create("FieldData", dataDict)

    return fieldDataID, notebookIDMapper


def copyContentAndFilesFromOneNotebookToAnother(
    sourceTargetNotebookIDMapperList, userID, database
):
    sourceNotebookIDList = []
    targetNotebookIDList = []
    for sourceTargetNotebookIDMapper in sourceTargetNotebookIDMapperList:
        sourceNotebookID = sourceTargetNotebookIDMapper["Source"]
        targetNotebookID = sourceTargetNotebookIDMapper["Target"]
        if None in [sourceNotebookID, targetNotebookID]:
            continue
        sourceNotebookIDList.append(sourceNotebookID)
        targetNotebookIDList.append(targetNotebookID)

    totalNotebookIDList = sourceNotebookIDList
    totalNotebookIDList.extend(targetNotebookIDList)

    totalNotebookList = getData("Notebook", {"_id": {"$in": totalNotebookIDList}})
    totalNotebookMapping = {notebook["_id"]: notebook for notebook in totalNotebookList}

    for sourceTargetNotebookIDMapper in sourceTargetNotebookIDMapperList:
        sourceNotebookID = sourceTargetNotebookIDMapper["Source"]
        targetNotebookID = sourceTargetNotebookIDMapper["Target"]

        sourceNotebook = totalNotebookMapping[sourceNotebookID]

        sourceContent = sourceNotebook["Content"]
        if not sourceContent:
            continue
        sourceImageFileIDList = sourceNotebook["ImageFileIDList"]
        sourceFileIDList = sourceNotebook["FileIDList"]

        targetContent = sourceContent

        targetImageFileIDList = []
        for imageFileID in sourceImageFileIDList:
            newImageFileID, targetContent = copyOneFileAndReplaceID(
                imageFileID, targetContent, database
            )
            targetImageFileIDList.append(newImageFileID)

        targetFileIDList = []
        for fileID in sourceFileIDList:
            newFileID, targetContent = copyOneFileAndReplaceID(
                fileID, targetContent, database
            )
            targetFileIDList.append(newFileID)

        Update.update(
            "Notebook",
            "Content",
            targetContent,
            targetNotebookID,
            database,
            userID,
        )
        if targetImageFileIDList:
            Update.update(
                "Notebook",
                "ImageFileIDList",
                targetImageFileIDList,
                targetNotebookID,
                database,
                userID,
            )
        if targetFileIDList:
            Update.update(
                "Notebook",
                "FileIDList",
                targetFileIDList,
                targetNotebookID,
                database,
                userID,
            )


def copyOneFileAndReplaceID(fileID, content, database):
    fs = FileStorage(database)
    newFileID = fs.copy(fileID)
    newContent = content.replace(str(fileID), str(newFileID))
    return newFileID, newContent


def link_items(document_old_id_new_id_mapping):
    from tenjin.mongo_engine.Link import Link

    old_ids = list(document_old_id_new_id_mapping.keys())

    # find all links where id1 and id2 are in old_ids
    links = Link.objects(DataID1__in=old_ids, DataID2__in=old_ids)
    for link in links:
        new_id_1 = document_old_id_new_id_mapping[link.DataID1]
        new_id_2 = document_old_id_new_id_mapping[link.DataID2]
        data_dict = {
            "DataID1": new_id_1,
            "DataID2": new_id_2,
            "Collection1": link.Collection1,
            "Collection2": link.Collection2,
        }
        Create.create("Link", data_dict)


def copy_data_table(template_id, new_doc, collection, project_id, user_id):
    from tenjin.mongo_engine.RawData import RawData
    from tenjin.mongo_engine.Column import Column

    new_exp_id = new_sample_id = new_ri_id = None
    if collection == "Experiment":
        rawdata = RawData.objects(ExpID=template_id)
        new_exp_id = new_doc.id
    elif collection == "Sample":
        rawdata = RawData.objects(SampleID=template_id)
        new_sample_id = new_doc.id
    elif collection == "ResearchItem":
        rawdata = RawData.objects(ResearchItemID=template_id)
        new_ri_id = new_doc.id
    else:
        rawdata = []

    unitIDList = []
    column_id_list = []
    for rd in rawdata:
        column_id_list.extend([c.id for c in rd.ColumnIDList])
    columns = Column.objects(id__in=column_id_list)
    column_id_mapping = {c.id: c for c in columns}
    for c in columns:
        if c.UnitID:
            unitIDList.append(c.UnitID.id)

    unitList = getData("Unit", {"_id": {"$in": unitIDList}})
    originalUnitIDNewUnitMapping = createAllNewUnitsRawData(
        unitList, user_id, project_id
    )

    for rd in rawdata:
        create_task(
            copy_one_data_table,
            rd,
            column_id_mapping,
            originalUnitIDNewUnitMapping,
            project_id,
            new_exp_id,
            new_sample_id,
            new_ri_id,
        )


def copy_one_data_table(
    rd,
    column_id_mapping,
    originalUnitIDNewUnitMapping,
    project_id,
    new_exp_id,
    new_sample_id,
    new_ri_id,
):
    new_column_id_list = []
    for column_lazy in rd.ColumnIDList:
        column_id = column_lazy.id
        if column_id not in column_id_mapping:
            continue
        column = column_id_mapping[column_id]
        new_unit_id = None
        if column.UnitID:
            if column.UnitID.id in originalUnitIDNewUnitMapping:
                new_unit_id = originalUnitIDNewUnitMapping[column.UnitID.id]["_id"]
        data_dict = {
            "Name": column.Name,
            "Type": column.Type,
            "Data": column.Data,
            "Default": column.Default,
            "UnitID": new_unit_id,
            "ProjectID": project_id,
        }
        new_column_id = Create.create("Column", data_dict)
        new_column_id_list.append(new_column_id)

    rd_data_dict = {
        "Name": rd.Name,
        "ExpID": new_exp_id,
        "SampleID": new_sample_id,
        "ResearchItemID": new_ri_id,
        "ColumnIDList": new_column_id_list,
        "ProjectID": project_id,
    }
    new_rd_id = Create.create("RawData", rd_data_dict)


def createAllNewUnitsRawData(unitList, user_id, project_id):
    unitIDList = [u["_id"] for u in unitList]
    # For units, we need to check the definition string if more units are necessary to be created in the new project
    # This will also be done recursively.
    additionalUnitListFromDefinition = getUnitListFromDefinitionRecursive(
        unitList, user_id
    )
    # The newly found units from the definition strings will be added to the unitList if they are not yet part of it.
    for unit in additionalUnitListFromDefinition:
        if unit["_id"] in unitIDList:
            continue
        unitList.append(unit)
    toBeCreatedUnitList, existingUnitList = checkUnitList(unitList, project_id, user_id)

    # create all units in the new project, that needed to be created and return a list with the new units
    newUnitList = createNewUnits(toBeCreatedUnitList, project_id, user_id)
    totalNewUnitList = []
    for newUnit in newUnitList:
        totalNewUnitList.append(newUnit)
    for exitingUnit in existingUnitList:
        totalNewUnitList.append(exitingUnit)

    # create a mapping between original unitID and the new unit. This is needed to create the fieldData later on
    originalUnitIDNewUnitMapping = {}
    newUnitIDOriginalUnitMapping = {}
    for unit in unitList:
        for newUnit in totalNewUnitList:
            if unit["ShortName"] == newUnit["ShortName"]:
                originalUnitIDNewUnitMapping[unit["_id"]] = newUnit
                newUnitIDOriginalUnitMapping[newUnit["_id"]] = unit
                break

    # create all needed unit categories and update the new units
    createNewUnitCategoriesAndUpdateNewUnits(
        unitList, originalUnitIDNewUnitMapping, project_id, user_id
    )

    return originalUnitIDNewUnitMapping


def copy_files(fileIDList, collection, new_doc_id):
    fs = FileStorage(get_db())
    new_file_id_list = []
    for file_id in fileIDList:
        new_file_id = fs.copy(file_id)
        new_file_id_list.append(new_file_id)
    Update.update(collection, "FileIDList", new_file_id_list, new_doc_id)
