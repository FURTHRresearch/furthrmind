from mongoengine import *
from .BaseClass import BaseClass
from flask import request
from bson import ObjectId

class BaseClassProjectID(BaseClass):

    def update_project(self):
        """
        Checks if the projectID is set
        """
        if not hasattr(self, "ProjectID"):
            return
        if self.ProjectID is not None:
            return
        project_id = None
        try:
            project_id = request.view_args.get("projectID")
            if project_id is None:
                project_id = request.view_args.get("project_id")
                if project_id is None:
                    project_id = request.view_args.get("projectid")
                    if project_id is None:
                        project_id = request.view_args.get("projid")
        except:
            pass
        if project_id is not None:
            self.ProjectID = ObjectId(project_id)
            return

    ProjectID = LazyReferenceField("Project", required=True)

    meta = {"abstract": True}
            # "strict": False}




