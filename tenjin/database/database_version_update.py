import datetime
import random
import string

import bson
import flask
import click
from flask.cli import with_appcontext
from tenjin.execution.delete import Delete
from flask import current_app


class DatabaseVersionUpdate:

    def __init__(self, db, currentDatabaseVersion, softwareVersion):

        self.localRenewed = False
        self.versionList = [
            "1.26.4",
            "1.26.5",
            "1.26.6",
            "1.26.7",
            "1.26.8",
            "1.26.9",
            "1.26.10",
            "1.26.11",
            "1.26.12",
            "1.26.13",
            "1.26.14",
            "1.26.15",
            "1.26.16",
            "1.26.17",
            "1.26.18",
            "1.26.19",
            "1.26.21",
            "1.26.23",
            "1.26.24",
            "1.26.25",
            "1.26.26",
            "1.26.28",
            "1.27.0",
            "1.28.0",
            "1.28.1",
            "1.28.2",
            "1.28.3",
            "1.29.0",
            "1.29.1",
            "1.29.2",
            "1.29.3",
            "1.30.0",
        ]

        self.versionMethodDict = {
            "1.26.4": self.update_1_26_4,
            "1.26.5": self.update_1_26_5,
            "1.26.6": self.update_1_26_6,
            "1.26.7": self.update_1_26_7,
            "1.26.8": self.update_1_26_8,
            "1.26.9": self.update_1_26_9,
            "1.26.10": self.update_1_26_10,
            "1.26.11": self.update_1_26_11,
            "1.26.12": self.update_1_26_12,
            "1.26.13": self.update_1_26_13,
            "1.26.14": self.update_1_26_14,
            "1.26.15": self.update_1_26_15,
            "1.26.16": self.update_1_26_16,
            "1.26.17": self.update_1_26_17,
            "1.26.18": self.update_1_26_18,
            "1.26.19": self.update_1_26_19,
            "1.26.21": self.update_1_26_21,
            "1.26.23": self.update_1_26_23,
            "1.26.24": self.update_1_26_24,
            "1.26.25": self.update_1_26_25,
            "1.26.26": self.update_1_26_26,
            "1.26.28": self.update_1_26_28,
            "1.27.0": self.update_1_27_0,
            "1.28.0": self.update_1_28_0,
            "1.28.1": self.update_1_28_1,
            "1.28.2": self.update_1_28_2,
            "1.28.3": self.update_1_28_3,
            "1.29.0": self.update_1_29_0,
            "1.29.1": self.update_1_29_1,
            "1.29.2": self.update_1_29_2,
            "1.29.3": self.update_1_29_3,
            "1.30.0": self.update_1_30_0,
        }

        self.versionCollectionDict = {
            "1.26.4": [],
            "1.26.5": [],
            "1.26.6": [],
            "1.26.7": [],
            "1.26.8": [],
            "1.26.9": [],
            "1.26.10": [],
            "1.26.11": [],
            "1.26.12": [],
            "1.26.13": [],
            "1.26.14": [],
            "1.26.15": [],
            "1.26.16": [],
            "1.26.17": [],
            "1.26.18": [],
            "1.26.19": [],
            "1.26.21": [],
            "1.26.23": [],
            "1.26.24": [],
            "1.26.25": [],
            "1.26.26": [],
            "1.26.28": [],
            "1.27.0": [],
            "1.28.0": [],
            "1.28.1": [],
            "1.28.2": [],
            "1.28.3": [],
            "1.29.0": [],
            "1.29.1": [],
            "1.29.2": [],
            "1.29.3": [],
            "1.30.0": [],
        }

        self.dataBase = db
        self.databaseVersion = currentDatabaseVersion
        self.softwareVersion = softwareVersion
        self.skippedVersion = self.determineUpdates()

    def compareVersionStrings(self, oldVersion, newVersion):

        currentVersion = oldVersion.split(".")
        possibleNewVersion = newVersion.split(".")

        for index in range(0, 3):

            if int(possibleNewVersion[index]) > int(currentVersion[index]):
                return True

            if int(possibleNewVersion[index]) < int(currentVersion[index]):
                return False

        return True

    def determineUpdates(self):

        skippedVersionList = []

        for version in self.versionList:

            if not self.compareVersionStrings(version, self.databaseVersion) and self.compareVersionStrings(version,
                                                                                                            self.softwareVersion):
                skippedVersionList.append(version)

        return skippedVersionList

    def createCollectionBackUp(self, collection):

        if isinstance(collection, str):
            collectionName = collection
        else:
            collectionName = collection.name
        allEntry = self.dataBase.db[collectionName].find({})

        for entry in allEntry:
            entry["_idBackUp"] = entry.pop("_id")
            self.dataBase.db[(collectionName + "BackUp")].insert_one(entry)

        print("BackUpDone")

    def resetCollectionToBackUp(self, collection):
        if isinstance(collection, str):
            collectionName = collection
        else:
            collectionName = collection.name

        self.dataBase.db[collectionName].drop()

        allEntry = self.dataBase.db[collectionName + "BackUp"].find({})
        for entry in allEntry:
            entry["_id"] = entry.pop("_idBackUp")
            self.dataBase.db[collectionName].insert_one(entry)

        self.dataBase.db[collectionName + "BackUp"].drop()

        print("BackUpRestored")

    def deleteBackUp(self, collection):
        if isinstance(collection, str):
            collectionName = collection
        else:
            collectionName = collection.name

        self.dataBase.db[collectionName + "BackUp"].drop()

        print("BackUpDeleted")

    def checkForBackUp(self, collection):

        if isinstance(collection, str):
            collectionName = collection
        else:
            collectionName = collection.name
        if collectionName + "BackUp" in self.dataBase.db.list_collection_names():
            print("BackUpFound")
            return True
        else:
            return False

    def performDBUpdate(self):

        for version in self.skippedVersion:

            changedCollections = self.versionCollectionDict[version]

            for collection in changedCollections:

                if self.checkForBackUp(collection):
                    self.resetCollectionToBackUp(collection)

                self.createCollectionBackUp(collection)

            method = self.versionMethodDict[version]
            method()

            for collection in changedCollections:
                self.deleteBackUp(collection)

            print(version)
            self.dataBase.db.SoftwareVersion.insert_one(
                {"Version": version, "Date": datetime.datetime.now()})

        print(self.skippedVersion)
        if not self.softwareVersion in self.skippedVersion:
            self.dataBase.db.SoftwareVersion.insert_one({"Version": self.softwareVersion,
                                                         "Date": datetime.datetime.now()})



    def update_1_26_4(self):
        collections = self.dataBase.db.list_collection_names()
        for c in collections:
            self.dataBase.db[c].update_many({"MySQLID": {"$exists": True}}, {"$unset": {"MySQLID": 1}})

        """ remove TargetCollection"""
        collections = ["Field", "Notebook", "Unit"]
        for c in collections:
            items = list(self.dataBase.db[c].find({"TargetCollection": {"$in": ["Batch", "Chemical"]}}))
            item_id_list = [i["_id"] for i in items]
            if c == "Field":
                self.dataBase.db["FieldData"].delete_many({"FieldID": {"$in": item_id_list}})
                self.dataBase.db["ComboBoxEntry"].delete_many({"FieldID": {"$in": item_id_list}})
            elif c == "Unit":
                self.dataBase.db["FieldData"].delete_many({"UnitID": {"$in": item_id_list}})
                self.dataBase.db["Column"].delete_many({"UnitID": {"$in": item_id_list}})
            elif c == "Notebook":
                self.dataBase.db["FieldData"].delete_many({"Value": {"$in": item_id_list}})

            self.dataBase.db[c].update_many({}, {"$unset": {"TargetCollection": 1}})

        """ Correct MultiLine Values """

        field_data = self.dataBase.db["FieldData"].find({"Type": "MultiLine"})
        for fd in field_data:
            value = fd["Value"]
            if value is None:
                continue
            if isinstance(value, str):
                if value == "None":
                    value = None
                else:
                    try:
                        value = bson.ObjectId(value)
                    except:
                        value = None
                self.dataBase.db["FieldData"].update_one({"_id": fd["_id"]}, {"$set": {"Value": value}})

        """ Remove FieldDataIDList from RawData """
        self.dataBase.db["RawData"].update_many({}, {"$unset": {"FieldDataIDList": 1}})

        # Database.check_database()

    def update_1_26_5(self):
        self.dataBase.db["Project"].update_many({}, {"$set": {"Archived": True}})

    def update_1_26_6(self):
        self.dataBase.db["RawData"].update_many({"Sample": {"$exists": True}}, {"$rename": {"Sample": "SampleID"}})
        self.dataBase.db["RawData"].update_many({"SampleID": {"$exists": False}}, {"$set": {"SampleID": None}})

    def update_1_26_7(self):
        # combobox entries:
        duplicates_check_list = [
            {"name": "ComboBoxEntry", "name_attribute": "Name", "compare_attribute": "NameLower",
             "unique_key": "FieldID"},
            {"name": "DataView", "name_attribute": "Name", "compare_attribute": "NameLower", "unique_key": "ProjectID"},
            {"name": "Experiment", "name_attribute": "Name", "compare_attribute": "NameLower",
             "unique_key": "ProjectID"},
            {"name": "Field", "name_attribute": "Name", "compare_attribute": "NameLower", "unique_key": "ProjectID"},
            {"name": "Group", "name_attribute": "Name", "compare_attribute": "NameLower", "unique_key": "ProjectID"},
            {"name": "Project", "name_attribute": "Name", "compare_attribute": "NameLower", "unique_key": None},
            {"name": "ResearchCategory", "name_attribute": "Name", "compare_attribute": "NameLower",
             "unique_key": "ProjectID"},
            {"name": "ResearchItem", "name_attribute": "Name", "compare_attribute": "NameLower",
             "unique_key": "ResearchCategoryID"},
            {"name": "Sample", "name_attribute": "Name", "compare_attribute": "NameLower", "unique_key": "ProjectID"},
            {"name": "Unit", "name_attribute": None, "compare_attribute": "ShortName", "unique_key": "ProjectID"},
            {"name": "UserGroup", "name_attribute": "Name", "compare_attribute": "NameLower", "unique_key": None},
            {"name": "Author", "name_attribute": "Name", "compare_attribute": "NameLower", "unique_key": None},
        ]

        for d in duplicates_check_list:
            self.check_name_lower_duplicates(d["name"], d["name_attribute"], d["compare_attribute"], d["unique_key"])

    def check_name_lower_duplicates(self, collection, name_attribute, compare_attribute, unique_key):
        db = self.dataBase.db
        item_list = list(db[collection].find({}))
        compare_dict = {}
        compare_list = [item.get(compare_attribute) for item in item_list]
        for item in item_list:
            unique_key_value = item.get(unique_key)
            compare_value = item.get(compare_attribute)
            if compare_value not in compare_list:
                continue
            if compare_value not in compare_dict:
                compare_dict[compare_value] = {}
            if unique_key_value not in compare_dict[compare_value]:
                compare_dict[compare_value][unique_key_value] = []
            compare_dict[compare_value][unique_key_value].append(item)

        for compare_value in compare_dict:
            for unique_id in compare_dict[compare_value]:
                if len(compare_dict[compare_value][unique_id]) > 1:
                    items = compare_dict[compare_value][unique_id][1:]
                    count = 1
                    for item in items:

                        if name_attribute:
                            name = f"{item[name_attribute]}_{count}"
                            db[collection].update_one({"_id": item["_id"]},
                                                      {"$set": {name_attribute: name}
                                                       })
                        value = f"{compare_value}_{count}"
                        db[collection].update_one({"_id": item["_id"]},
                                                  {"$set": {compare_attribute: value}
                                                   })
                        count += 1
                        print(f"renamed {item[compare_attribute]}")

        return compare_dict

    def update_1_26_8(self):
        self.dataBase.db["Project"].update_many({}, {"$set": {"Archived": False}})

    def update_1_26_9(self):
        users = self.dataBase.db["User"].find({})
        for user in users:
            author = self.dataBase.db["Author"].find_one({"UserID": user["_id"]})
            if not author:
                data = {"Name": user["Email"],
                        "NameLower": user["Email"].lower(),
                        "UserID": user["_id"],
                        "Institution": None,
                        "Date": datetime.datetime.now(datetime.UTC),
                        "OwnerID": user["_id"]}
                self.dataBase.db["Author"].insert_one(data)

    def update_1_26_10(self):
        from tenjin.mongo_engine import Database
        Database.check_missing_db_keys()

    def update_1_26_11(self):
        cs_list = self.dataBase.db["ChemicalStructure"].find({})
        for cs in cs_list:
            if cs.get("SmilesList"):
                smiles = cs["SmilesList"][0]
            else:
                smiles = ""
            self.dataBase.db["ChemicalStructure"].update_one({"_id": cs["_id"]},
                                                             {"$set": {"Smiles": smiles}})

        for cs in cs_list:
            if cs.get("Smiles"):
                self.dataBase.db["ChemicalStructure"].update_one({"_id": cs["_id"]}, {"$set": {"SmilesList": [cs["Smiles"]]}})
            else:
                self.dataBase.db["ChemicalStructure"].update_one({"_id": cs["_id"]}, {"$set": {"SmilesList": []}})

        self.dataBase.db["ChemicalStructure"].update_many({}, {"$set": {"CDXML": None}})

    def update_1_26_12(self):
        from tenjin.mongo_engine.Column import Column

        columns = Column.objects(Name="Neglect")
        flask.g.no_access_check = True
        for column in columns:
            Delete.delete("Column", column.id)

        columns = Column.objects()
        for column in columns:
            if column.Data:
                if isinstance(column.Data[0], list):
                    new_data = []
                    for data_list in column.Data:
                        new_data.extend(data_list)
                    # Versioning not necessary => use direct db entry
                    self.dataBase.db["Column"].update_one({"_id": column.id},
                                                          {"$set": {"Data": new_data}})

        flask.g.no_access_check = False

    def update_1_26_13(self):
        self.dataBase.db["RawData"].update_many({}, {"$set": {"Name": "Data table"}})

    def update_1_26_14(self):
        self.dataBase.db["RawData"].update_many({}, {"$set": {"Name": "Data table"}})
        from tenjin import create_app
        app = create_app(minimal=True)
        with app.app_context():

            from tenjin.mongo_engine.FieldData import FieldData
            flask.g.no_access_check = True
            field_data_list = FieldData.objects(Type="Numeric")
            for fd in field_data_list:
                fd.update_si_value()
            flask.g.no_access_check = False

    def update_1_26_15(self):
        collections = self.dataBase.db.list_collection_names()
        for c in collections:
            self.dataBase.db[c].update_many({"CreateFlag": {"$exists": True}}, {"$unset": {"CreateFlag": 1}})

        usedShortIDs = []
        allEntries = self.dataBase.db["ResearchItem"].find({})
        for entry in allEntries:
            while True:
                shortID = ''.join(random.choice(
                    string.ascii_lowercase + string.digits) for i in range(6))
                if not shortID in usedShortIDs:
                    usedShortIDs.append(shortID)
                    break
            self.dataBase.db["ResearchItem"].update_one(
                {"_id": entry["_id"]}, {"$set": {"ShortID": "rtm-" + shortID}})

    def update_1_26_16(self):
        self.dataBase.db["RawData"].update_many({}, {"$set":{"SampleID": None,
                                                             "ResearchItemID": None}})

    def update_1_26_17(self):
        field_data_list = self.dataBase.db["FieldData"].find({"Type": "MultiLine",
                                                              "Value": None})
        for fd in field_data_list:
            project_id = fd["ProjectID"]
            data = {"Content": "",
                    "ProjectID": project_id,
                    "FileIDList": [],
                    "ImageFileIDList": []}
            notebook_id = self.dataBase.db["Notebook"].insert_one(data).inserted_id
            self.dataBase.db["FieldData"].update_one({"_id": fd["_id"]},
                                                     {"$set": {"Value": notebook_id}})

        self.dataBase.db["Notebook"].update_many({"Content": None},
                                                 {"$set": {"Content": ""}})
        db = self.dataBase.db
        collections = db.list_collection_names()
        for c in collections:
            db[c].drop_indexes()

    def update_1_26_18(self):
        from tenjin.mongo_engine.Link import Link
        exps = self.dataBase.db["Experiment"].find({})
        for exp in exps:
            for sample_id in exp["UsedSampleIDList"]:
                link_data = {"DataID1": exp["_id"],
                             "Collection1": "Experiment",
                             "DataID2": sample_id,
                             "Collection2": "Sample"}
                link = Link(**link_data)
                link.save()

            for item_id in exp["ResearchItemIDList"]:
                link_data = {"DataID1": exp["_id"],
                             "Collection1": "Experiment",
                             "DataID2": item_id,
                             "Collection2": "ResearchItem"}
                link = Link(**link_data)
                link.save()
        self.dataBase.db["Experiment"].update_many({}, {"$unset":{"UsedSampleIDList": 1, "ResearchItemIDList": 1}})

    def update_1_26_19(self):
        from tenjin.mongo_engine.User import User
        from tenjin.mongo_engine.UserGroup import UserGroup

        user_groups = self.dataBase.db["UserGroup"].find({})
        for ug in user_groups:
            new_user_id_list = []
            print(ug["UserIDList"])
            for user_id in ug["UserIDList"]:
                user = User.objects(id=user_id).first()
                if user:
                    new_user_id_list.append(user_id)
            print(new_user_id_list)
            self.dataBase.db["UserGroup"].update_one({"_id": ug["_id"]}, {"$set": {"UserIDList": new_user_id_list}})

        ug = UserGroup.objects(Name="everybody").first()
        if ug:
            user_id_list = [u.id for u in ug["UserIDList"]]
            user = User.objects()
            for u in user:
                if u.id in user_id_list:
                    continue
                user_id_list.append(u.id)
            self.dataBase.db["UserGroup"].update_one({"_id": ug.id}, {"$set": {"UserIDList": user_id_list}})

    def update_1_26_21(self):
        from tenjin.mongo_engine.Column import Column
        columns = Column.objects()
        for column in columns:
            if column.Type == "Numeric":
                continue
            data = list(column.Data)
            if all(isinstance(item, (float, int, type(None))) for item in data):
                column.update(Type="Numeric")
                print(f"{column.id} updated")
        restore_falsy_deleted_notebooks()

    def update_1_26_23(self):
        users = self.dataBase.db["User"].find({})
        for user in users:
            email = user["Email"]
            if not email:
                continue
            email_lower = email.lower()
            if email_lower != email:
                try:
                    self.dataBase.db["User"].update_one({"_id": user["_id"]}, {"$set": {"Email": email_lower}})
                    print(f"updated {email} to {email_lower}")
                except:
                    pass

    def update_1_26_24(self):
        from tenjin.mongo_engine.File import File
        from tenjin.mongo_engine import Database
        Database.set_no_access_check(True)
        self.dataBase.db["File"].update_many({}, {"$set": {"IsThumbnail": False}})

        files = File.objects(Name__contains="thumbnail_thumbnail_thumbnail").only("id")
        to_be_deleted = [file.id for file in files]
        self.dataBase.db["File"].delete_many({"_id": {"$in": to_be_deleted}})
        self.dataBase.db["File"].update_many({"ThumbnailFileID": {"$in": to_be_deleted}},
                                             {"$set": {"ThumbnailFileID": None}})

        thumbnail_file_id_list = [file.id for file in files]
        files = File.objects()
        for file in files:
            if file.ThumbnailFileID:
                thumbnail_file_id_list.append(file.ThumbnailFileID.id)
        self.dataBase.db["File"].update_many({"_id": {"$in": thumbnail_file_id_list}}, {"$set": {"IsThumbnail": True}})
        Database.set_no_access_check(False)


    def update_1_26_25(self):
        self.dataBase.db["FieldData"].update_many({}, {"$set": {"ValueMax": None, "SIValueMax": None,
                                                                "InternalValueNumericRange": None}})
        self.dataBase.db["Experiment"].update_many({}, {"$set": {"Protected": False}})
        self.dataBase.db["Sample"].update_many({}, {"$set": {"Protected": False}})
        self.dataBase.db["ResearchItem"].update_many({}, {"$set": {"Protected": False}})

    def update_1_26_26(self):
        self.dataBase.db["DataView"].update_many({}, {"$set": {"IncludeLinked": False}})

    def update_1_26_28(self):
        self.dataBase.db["DataView"].update_many({}, {"$set": {"DisplayedCategories": ["all"]}})
        self.dataBase.db["Filter"].update_many({}, {"$set": {"DisplayedCategories": ["all"]}})

    def update_1_27_0(self):
        self.dataBase.db["Filter"].update_many({"IncludeLinked": True},
                                               {"$set": {"IncludeLinked": "direct"}})
        self.dataBase.db["Filter"].update_many({"IncludeLinked": False},
                                               {"$set": {"IncludeLinked": "none"}})

        self.dataBase.db["DataView"].update_many({"IncludeLinked": True},
                                               {"$set": {"IncludeLinked": "direct"}})
        self.dataBase.db["DataView"].update_many({"IncludeLinked": False},
                                               {"$set": {"IncludeLinked": "none"}})

    def update_1_28_0(self):
        import time
        s = time.time()
        self.dataBase.db["FieldData"].update_many({},
                                                 {"$set": {"ValueLower": None}})
        field_data = self.dataBase.db["FieldData"].find({})
        counter = 0
        for fd in field_data:
            counter += 1
            if isinstance(fd["Value"], str):
                self.dataBase.db["FieldData"].update_one({"_id": fd["_id"]},
                                                         {"$set": {"ValueLower": fd["Value"].lower()}})
            if counter % 10000 == 0:
                print(f"{counter} updated", time.time() - s)

    def update_1_28_1(self):
        try:
            self.dataBase.db["FieldData"].drop_index("FieldID_1")
            self.dataBase.db["FieldData"].drop_index("Value_1")
            self.dataBase.db["FieldData"].drop_index("ValueLower_1")
            self.dataBase.db["FieldData"].drop_index("Type_1")
            self.dataBase.db["FieldData"].drop_index("FieldID_1_SIValue_1_SIValueMax_1_Type_1")
            self.dataBase.db["FieldData"].drop_index("FieldID_1_Value_1_ValueMax_1_Type_1")
            self.dataBase.db["FieldData"].drop_index("FieldID_1_ValueLower_1_Type_1")
            self.dataBase.db["FieldData"].drop_index("FieldID_1_Value_1_Type_1")
        except:
            pass

        exp_indexes_to_be_dropped = ["GroupIDList_1", "NameLower_1_ProjectID_1", "NameLower_1_GroupIDList_1",
                                     "ProjectID_1"]
        for name in exp_indexes_to_be_dropped:
            try:
                self.dataBase.db["Experiment"].drop_index(name)
            except:
                print("index not dropped", name)

    def update_1_28_2(self):

        field_data_indexes_to_be_dropped = ["FieldID_1_SIValue_1_SIValueMax_1_Type_1", "FieldID_1_Value_1_ValueMax_1_Type_1",
                                            "FieldID_1_ValueLower_1_Type_1","FieldID_1", "Value_1", "ValueLower_1",
                                            "Type_1","FieldID_1_Value_1_Type_1","FieldID_1_SIValue_1", "FieldID_1_Value_1"]
        for name in field_data_indexes_to_be_dropped:
            try:
                self.dataBase.db["FieldData"].drop_index(name)
            except:
                print("index not dropped", name)

    def update_1_28_3(self):
        collections = ["FieldData", "Experiment"]
        for c in collections:
            self.dataBase.db[c].drop_indexes()

    def update_1_29_0(self):
        self.dataBase.db["DataView"].update_many({}, {"$set": {"ItemIDList": []}})

    def update_1_29_1(self):
        self.dataBase.db["DataView"].update_many({}, {"$set": {"ItemIDListUpdated": None}})

    def update_1_29_2(self):
        self.dataBase.db["DataViewChart"].update_many({}, {"$set": {"Data": None}})
        self.dataBase.db["DataViewChart"].update_many({}, {"$set": {"DataUpdated": None}})

    def update_1_29_3(self):
        with current_app.app_context():
            from tenjin.web.dataviews import get_dataview_data_internal, get_page_item_index_from_database_internal
            from tenjin.mongo_engine import Database
            self.dataBase.db["DataView"].update_many({}, {"$set": {"ItemIDList": []}})
            self.dataBase.db["DataViewChart"].update_many({}, {"$set": {"Data": []}})
            dataviews = list(self.dataBase.db["DataView"].find({}))
            Database.set_no_access_check(True)
            for dv in dataviews:
                pass
                page_item_index = get_page_item_index_from_database_internal(dv["_id"])
                data = get_dataview_data_internal(dv["_id"])
            Database.set_no_access_check(False)
            
    def update_1_30_0(self):
        # from tenjin import create_app
        # app = create_app(minimal=True)
        with current_app.app_context():
            
            experiments = self.dataBase.db["Experiment"].find({})
            for item in experiments:
                fielddata_id_list = item["FieldDataIDList"]
                attribute_list = ["_id", "FieldID", "Value", "ValueMax", "SIValue", "SIValueMax", "Type", "ValueLower"]
                fielddata = self.dataBase.db["FieldData"].find({"_id": {"$in": fielddata_id_list}})
                data = []
                for fd in fielddata:
                    fd_data = {}
                    for attribute in attribute_list:
                        fd_data[attribute] = fd[attribute]
                    data.append(fd_data)
                self.dataBase.db["FieldData"].update_many({"_id": {"$in": fielddata_id_list}}, {"$set": {"ParentCollection": "Experiment",
                                                                                                         "ParentDataID": item["_id"]}})
                self.dataBase.db["Experiment"].update_one({"_id": item["_id"]}, {"$set": {"FieldData": data}})

            samples = self.dataBase.db["Sample"].find({})
            for item in samples:
                fielddata_id_list = item["FieldDataIDList"]
                attribute_list = ["_id", "FieldID", "Value", "ValueMax", "SIValue", "SIValueMax", "Type", "ValueLower"]
                fielddata = self.dataBase.db["FieldData"].find({"_id": {"$in": fielddata_id_list}})
                data = []
                for fd in fielddata:
                    fd_data = {}
                    for attribute in attribute_list:
                        fd_data[attribute] = fd[attribute]
                    data.append(fd_data)
                self.dataBase.db["FieldData"].update_many({"_id": {"$in": fielddata_id_list}}, {"$set": {"ParentCollection": "Sample",
                                                                                                         "ParentDataID": item["_id"]}})
                self.dataBase.db["Sample"].update_one({"_id": item["_id"]}, {"$set": {"FieldData": data}})
            
            comboboxentries = self.dataBase.db["ComboBoxEntry"].find({})
            for item in comboboxentries:
                fielddata_id_list = item["FieldDataIDList"]
                attribute_list = ["_id", "FieldID", "Value", "ValueMax", "SIValue", "SIValueMax", "Type", "ValueLower"]
                fielddata = self.dataBase.db["FieldData"].find({"_id": {"$in": fielddata_id_list}})
                data = []
                for fd in fielddata:
                    fd_data = {}
                    for attribute in attribute_list:
                        fd_data[attribute] = fd[attribute]
                    data.append(fd_data)
                self.dataBase.db["FieldData"].update_many({"_id": {"$in": fielddata_id_list}}, {"$set": {"ParentCollection": "ComboBoxEntry",
                                                                                                         "ParentDataID": item["_id"]}})
                self.dataBase.db["ComboBoxEntry"].update_one({"_id": item["_id"]}, {"$set": {"FieldData": data}})

            researchitems = self.dataBase.db["ResearchItem"].find({})
            for item in researchitems:
                fielddata_id_list = item["FieldDataIDList"]
                if fielddata_id_list is None:
                    fielddata_id_list = []
                attribute_list = ["_id", "FieldID", "Value", "ValueMax", "SIValue", "SIValueMax", "Type", "ValueLower"]
                fielddata = self.dataBase.db["FieldData"].find({"_id": {"$in": fielddata_id_list}})
                data = []
                for fd in fielddata:
                    fd_data = {}
                    for attribute in attribute_list:
                        fd_data[attribute] = fd[attribute]
                    data.append(fd_data)
                self.dataBase.db["FieldData"].update_many({"_id": {"$in": fielddata_id_list}}, {"$set": {"ParentCollection": "ResearchItem",
                                                                                                         "ParentDataID": item["_id"]}})
                self.dataBase.db["ResearchItem"].update_one({"_id": item["_id"]}, {"$set": {"FieldData": data}})

            groups = self.dataBase.db["Group"].find({})
            for item in groups:
                fielddata_id_list = item["FieldDataIDList"]
                attribute_list = ["_id", "FieldID", "Value", "ValueMax", "SIValue", "SIValueMax", "Type", "ValueLower"]
                fielddata = self.dataBase.db["FieldData"].find({"_id": {"$in": fielddata_id_list}})
                data = []
                for fd in fielddata:
                    fd_data = {}
                    for attribute in attribute_list:
                        fd_data[attribute] = fd[attribute]
                    data.append(fd_data)
                self.dataBase.db["FieldData"].update_many({"_id": {"$in": fielddata_id_list}}, {"$set": {"ParentCollection": "Group",
                                                                                                         "ParentDataID": item["_id"]}})
                self.dataBase.db["Group"].update_one({"_id": item["_id"]}, {"$set": {"FieldData": data}})

@click.command('restore-falsy-deleted-notebooks')
@with_appcontext
def restore_falsy_deleted_notebooks_click_method():
    restore_falsy_deleted_notebooks()

def restore_falsy_deleted_notebooks():
    from tenjin.mongo_engine.Notebook import Notebook
    from tenjin.mongo_engine.Versioning import Versioning
    from tenjin.mongo_engine.FieldData import FieldData
    from tenjin.database.db import get_db
    from tenjin.mongo_engine import Database
    Database.set_no_access_check(True)
    from tenjin.execution.update import Update
    from tenjin.execution.create import Create
    db = get_db().db

    deleted_notebooks = Versioning.objects(Collection="Notebook", Operation="Delete due to LayoutCheck")
    for deleted_nb in deleted_notebooks:
        version_cache_fd = db["VersioningCache"].find_one({"Collection": "FieldData", "Value.Value": deleted_nb.DataID})
        if not version_cache_fd:
            continue
        fd_id = version_cache_fd["DataID"]
        fd = FieldData.objects(id=fd_id).first()
        if not fd:
            continue
        new_nb_id = fd.Value
        if new_nb_id:
            new_nb = Notebook.objects(id=new_nb_id).first()
            if new_nb.Content:
                continue
        version_cache_nb = list(db["VersioningCache"].find({"DataID": deleted_nb.DataID,
                                                           "Operation": "Update",
                                                           "Attribute": "Content"}))
        if not version_cache_nb:
            continue
        content = version_cache_nb[-1]["Value"]
        print(content)
        if not new_nb_id:
            data = {"Content": content}
            nb_id = Create.create("Notebook", data)
            Update.update("FieldData", "Value", nb_id, fd.id)
        else:
            Update.update("Notebook", "Content", content, new_nb_id)
    Database.set_no_access_check(False)


def init_app(app):
    app.cli.add_command(restore_falsy_deleted_notebooks_click_method)


if __name__ == "__main__":
    from tenjin.database.database_client import DatabaseClient

    db = DatabaseClient("localhost:27017", "FURTHRmind_Demo")
    updater = DatabaseVersionUpdate(db, "1.22.0", "1.23.0")
    updater.performDBUpdate()
