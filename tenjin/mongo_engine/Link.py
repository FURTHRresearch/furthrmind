from mongoengine import *
from .BaseClass import BaseClass
from bson import ObjectId
from tenjin.cache import Cache

class Link(BaseClass):
    meta = {"collection": __qualname__,
            "indexes": [
                {"fields": ["DataID1"], "unique": False},
                {"fields": ["DataID2"], "unique": False},
                {"fields": ["DataID1", "DataID2"], "unique": True}
            ]}

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        if isinstance(document_list[0], ObjectId):
            doc_id_list = document_list
        else:
            doc_id_list = [doc.id for doc in document_list]

        return document_list, {doc_id: True for doc_id in doc_id_list}

    def clean(self):
        if self.DataID1 == self.DataID2:
            if self.Collection1 == self.Collection2:
                raise ValidationError("DataID1 and DataID2 cannot be the same.")

    @classmethod
    def post_save_method(cls, sender, document, **kwargs):
        super().post_save_method(sender, document, **kwargs)
        cache = Cache.get_cache()
        # cache must be cleaned
        id_1 = str(document.DataID1)
        id_2 = str(document.DataID2)
        cache.delete(f"link_{id_1}")
        cache.delete(f"link_{id_2}")
        
    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        
        # cache must be cleaned
        cache = Cache.get_cache()
        id_1 = str(document.DataID1)
        id_2 = str(document.DataID2)
        cache.delete(f"link_{id_1}")
        cache.delete(f"link_{id_2}")
        
    
    DataID1 = ObjectIdField(required=True)
    Collection1 = StringField(choices=("Experiment", "Sample", "ResearchItem"),)
    DataID2 = ObjectIdField(required=True)
    Collection2 = StringField(choices=("Experiment", "Sample", "ResearchItem"))

