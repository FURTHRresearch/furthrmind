from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID
import datetime

class SpreadSheet(BaseClassProjectID):
    meta = {"collection": __qualname__,
            "indexes": [
                "ExperimentIDList",
                "SampleIDList",
                "ResearchItemIDList",
                "DataViewID"
            ]
            }

    def update_project(self):
        super().update_project()
        if self.ProjectID is not None:
            return self.ProjectID
        if self.ExperimentIDList:
            exp = self.ExperimentIDList[0]
            exp = exp.fetch()
            self.ProjectID = exp.ProjectID
        elif self.SampleIDList:
            s = self.SampleIDList[0]
            s = s.fetch()
            self.ProjectID = s.ProjectID
        elif self.ResearchItemIDList:
            r = self.ResearchItemIDList[0]
            r = r.fetch()
            self.ProjectID = r.ProjectID
        elif self.DataViewID:
            d = self.DataViewID.fetch()
            self.ProjectID = d.ProjectID

    def clean(self):
        super().clean()

        if self.TemplateName:
            speadsheets = SpreadSheet.objects(TemplateName=self.TemplateName,
                                              ProjectID=self.ProjectID)
            if len(speadsheets) > 0:
                if len(speadsheets) == 1 and speadsheets[0].id == self.id:
                    return
                return ValidationError("Template name must be unique within a project",
                                       errors={"TemplateName": {
                                           "Value": self.TemplateName,
                                           "List": False,
                                           "Message": "Template name must be unique within a project"
                                       }})


    @classmethod
    def pre_save_method(cls, sender, document, **kwargs):
        super().pre_save_method(sender, document, **kwargs)
        document.LastUpdate = datetime.datetime.now(datetime.UTC)

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == SpreadSheet.FileID.name:
            from .File import File
            File.update_project_external_triggered([self.FileID], self.ProjectID)

    ExperimentIDList = ListField(LazyReferenceField("Experiment"), default=list)
    SampleIDList = ListField(LazyReferenceField("Sample"), default=list)
    ResearchItemIDList = ListField(LazyReferenceField("ResearchItem"), default=list)
    DataViewID = LazyReferenceField("DataView", null=True)
    FileID = LazyReferenceField("File", null=True)
    LastUpdate = DateTimeField(default=datetime.datetime.now(datetime.UTC))
    Template = BooleanField(default=False)
    TemplateName = StringField(null=True)
    MD5 = StringField(null=True)

