import os
import time
from io import BytesIO

import mongoengine.base.datastructures
from PIL import Image
from bson import ObjectId
from mongoengine import *

from .BaseClassProjectIDOptional import BaseClassProjectIDOptional


class File(BaseClassProjectIDOptional):
    meta = {"collection": __qualname__,
            "indexes": [
                "uuid",
                "S3Key"
            ]}

    @staticmethod
    def update_project_external_triggered(file_list, project):
        if not file_list:
            return
        file = file_list[0]
        if isinstance(file, mongoengine.base.datastructures.LazyReference):
            file_id_list = [f.id for f in file_list]
            file_list = File.objects(id__in=file_id_list)
        elif isinstance(file, ObjectId):
            file_id_list = file_list
            file_list = File.objects(id__in=file_id_list)

        # in case of uploads through the webapp, a potential thumbnail cannot be generated during upload. Thus as
        # soon the file is linked to an item, the project is updated. Then, also one can try to genereate a thumbnail
        # if not done yet.

        for file in file_list:
            if file.ProjectID is not None:
                return
            file.ProjectID = project
            file.save(signal_kwargs={
                "Opr": "Update",
                "Attr": File.ProjectID.name,
                "Value": project
            })
            if file.ThumbnailFileID is None:
                File.create_thumbnail(file)
            if file.ThumbnailFileID is not None:
                thumbnalil_file = file.ThumbnailFileID.fetch()
                if thumbnalil_file.ProjectID is not None:
                    thumbnalil_file.ProjectID = project
                    thumbnalil_file.save(signal_kwargs={
                        "Opr": "Update",
                        "Attr": File.ProjectID.name,
                        "Value": project
                    })

    def create_method(self, kwargs):
        self.create_thumbnail(self)
        if self.ChunkIDList:
            from .Chunk import Chunk
            Chunk.update_project_external_triggered(self.ChunkIDList, self.ProjectID)

    def update_method(self, kwargs):
        from tenjin.execution.update import Update
        attr = kwargs.get("Attr")
        if not attr:
            return
        from .Chunk import Chunk
        if attr == File.ChunkIDList.name:
            if self.ProjectID is None:
                return
            Chunk.update_project_external_triggered(self.ChunkIDList, self.ProjectID)
            self.create_thumbnail(self)
        if attr == File.ProjectID.name:
            Chunk.update_project_external_triggered(self.ChunkIDList, self.ProjectID)
            if self.ThumbnailFileID is not None:
                Update.update("File", "ProjectID", self.ProjectID, self.ThumbnailFileID.id)
        if attr == File.S3Key.name:
            self.create_thumbnail(self)
        if attr == File.ThumbnailFileID.name:
            if self.ThumbnailFileID is not None:
                Update.update("File", "ProjectID", self.ProjectID, self.ThumbnailFileID.id)

    def append_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        from .Chunk import Chunk
        if attr == File.ChunkIDList.name:
            if self.ProjectID is None:
                return
            Chunk.update_project_external_triggered(self.ChunkIDList, self.ProjectID)

    @staticmethod
    def create_thumbnail(file):
        if file.IsThumbnail:
            return
        from tenjin.execution.create import Create

        from tenjin.execution.update import Update
        from tenjin.file.file_storage import FileStorage
        fs = FileStorage(get_db())
        size = fs.get_size(file.id)
        if not size:
            return
        if size > 100 * 1e6:
            return
        fileBytes = fs.get_file(file.id)
        fileBytesIO = BytesIO(fileBytes)
        try:
            fileName = file.Name
            fileroot, fileext = os.path.splitext(fileName)

            im = Image.open(fileBytesIO)
            imageSize = im.size
            imageWidth = imageSize[0]
            imageHeight = imageSize[1]
            widthToHeight = imageWidth / imageHeight
            newHeight = 150
            newWidth = newHeight * widthToHeight
            newWidth = round(newWidth)
            size = newWidth, newHeight
            im.thumbnail(size)
            thumbnailByteIO = BytesIO()
            im.save(thumbnailByteIO, "PNG")
            im.close()

            file_dict = {"Name": f"{fileroot}_thumbnail.png", "IsThumbnail": True}
            thumbnail_file_id = Create.create("File", file_dict)

            thumbnailFileID = fs.put(thumbnailByteIO.getbuffer().tobytes(), file_id=thumbnail_file_id,
                                     fileName=f"{fileroot}_thumbnail.png")

            Update.update("File", "ThumbnailFileID", thumbnail_file_id, file.id)
        except:
            return None

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .SpreadSheet import SpreadSheet
        from .Field import Field
        from .User import User
        from .ComboBoxEntry import ComboBoxEntry
        from .Experiment import Experiment
        from .Notebook import Notebook
        from .Project import Project
        from .Sample import Sample
        from .ResearchItem import ResearchItem
        from .Group import Group

        collection_attribute_list = [
            {"class": SpreadSheet,
             "attr": "FileID"},
            {"class": Field,
             "attr": "RawDataCalcScriptFileID"},
            {"class": File,
             "attr": "ThumbnailFileID"},
            {"class": User,
             "attr": "ImageFileID"}
        ]
        File.post_delete_nullify(collection_attribute_list, document.id)

        collection_attribute_list = [
            {"class": ComboBoxEntry,
             "attr": ComboBoxEntry.FileIDList.name},
            {"class": Experiment,
             "attr": Experiment.FileIDList.name},
            {"class": Sample,
             "attr": Sample.FileIDList.name},
            {"class": ResearchItem,
             "attr": ResearchItem.FileIDList.name},
            {"class": Group,
             "attr": Group.FileIDList.name},
            {"class": Notebook,
             "attr": Notebook.FileIDList.name},
            {"class": Notebook,
             "attr": Notebook.ImageFileIDList.name},
            {"class": Project,
             "attr": Project.FileIDList.name}
        ]
        File.post_delete_pull(collection_attribute_list, document.id)

    Name = StringField(required=True)
    ChunkIDList = ListField(LazyReferenceField("Chunk"), default=list)  # , reverse_delete_rule=PULL
    FieldDataIDList = ListField(LazyReferenceField("FieldData"), default=list)  # , reverse_delete_rule=PULL
    EditFlag = BooleanField(default=True)
    S3Key = StringField(null=True)
    uuid = UUIDField(null=True)
    ThumbnailFileID = LazyReferenceField("self", null=True)  # , reverse_delete_rule=NULLIFY)
    IsThumbnail = BooleanField(default=False)
