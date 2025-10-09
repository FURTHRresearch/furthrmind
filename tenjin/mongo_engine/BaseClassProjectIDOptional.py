from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID
from tenjin.cache import Cache
cache = Cache.get_cache()

class BaseClassProjectIDOptional(BaseClassProjectID):

    ProjectID = LazyReferenceField("Project", null=True)

    @classmethod
    @cache.memoize()
    def check_permission_to_project(cls, project_id, user_id, flag):
        if project_id is None:
            return True
        else:
            return super().check_permission_to_project(project_id, user_id, flag)


    meta = {"abstract": True}
            # "strict": False}




