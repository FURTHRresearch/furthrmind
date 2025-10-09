from mongoengine import *
from .BaseClassProjectIDOptional import BaseClassProjectIDOptional
from bson import ObjectId
from mongoengine.base.datastructures import LazyReference

class Chunk(BaseClassProjectIDOptional):
    meta = {"collection": __qualname__}

    @staticmethod
    def update_project_external_triggered(chunk_list, project):
        if not chunk_list:
            return
        chunk = chunk_list[0]
        if isinstance(chunk, LazyReference):
            chunk_id_list = [c.id for c in chunk_list]
            chunk_list = Chunk.objects(id__in=chunk_id_list).exclude("Data")
        elif isinstance(chunk, ObjectId):
            chunk_id_list = chunk_list
            chunk_list = Chunk.objects(id__in=chunk_id_list).exclude("Data")

        for chunk in chunk_list:
            if chunk.ProjectID is not None:
                return
            chunk.ProjectID = project
            chunk.save(signal_kwargs={
                "Opr": "Update",
                "Attr": Chunk.ProjectID,
                "Value": project
            })

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        from .File import File
        super().post_delete_method(sender, document, **kwargs)

        collection_attribute_list = [
            {"class": File,
             "attr": File.ChunkIDList.name},
        ]
        Chunk.post_delete_pull(collection_attribute_list, document.id)

    Data = BinaryField(null=True)
    MD5 = StringField(null=True)
