from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID
import datetime
import asyncio


class DataView(BaseClassProjectID):
    meta = {"collection": __qualname__, "indexes": ["ProjectID"]}

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)

        from .DataViewChart import DataViewChart
        from .SpreadSheet import SpreadSheet

        collection_attribute_list = [
            {"class": DataViewChart, "attr": DataViewChart.DataViewID.name},
            {"class": SpreadSheet, "attr": SpreadSheet.DataViewID.name},
        ]
        DataView.post_delete_cascade(collection_attribute_list, document.id)

    @staticmethod
    def update_spreadsheet(dataview_id):
        from tenjin.execution.update import Update
        from .SpreadSheet import SpreadSheet
        from tenjin.database.db import get_db
        from tenjin.logic.spreadsheet_generator import SpreadsheetGenerator
        import flask

        dataview = get_db().db["DataView"].find_one({"_id": dataview_id})
        SpreadsheetGenerator(
            exp_list=[],
            sample_list=[],
            research_item_list=[],
            dataview=dataview,
            user_id=flask.g.user,
            template_id=None,
        )
  
        

    def update_method(self, kwargs):
        from tenjin.execution.update import Update
        from tenjin.tasks.rq_task import create_task

        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == DataView.ItemIDList.name:
            Update.update(
                "DataView",
                "ItemIDListUpdated",
                datetime.datetime.now(tz=datetime.UTC),
                self.id,
                no_versioning=True,
            )
        if attr in [DataView.ItemIDList.name, DataView.DisplayedColumns.name]:
            create_task(DataView.update_spreadsheet, self.id)
            

    Name = StringField(required=True)
    NameLower = StringField(required=True, unique_with=["ProjectID"])
    DisplayedColumns = ListField(StringField(), default=list)
    DisplayedCategories = ListField(StringField(), default=list)
    FilterList = ListField(default=list)
    NameFilter = StringField(null=True)
    IncludeLinked = StringField(default="none")
    Col = IntField(null=True)
    Row = IntField(null=True)
    SizeX = IntField(null=True)
    SizeY = IntField(null=True)
    ItemIDList = ListField(ObjectIdField(), default=list)
    ItemIDListUpdated = DateTimeField(null=True)
