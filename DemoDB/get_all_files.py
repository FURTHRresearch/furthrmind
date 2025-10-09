import os
from tenjin.MongoEngine.ImportCollections import *
from tenjin.file.file_storage import FileStorage
from tenjin import create_app
from tenjin.database.db import get_db


def get_all_files():
    project_id = None
    projects = Project.objects()
    for project in projects:
        if project["Name"].startswith("Masken"):
            project_id = project["id"]

    file_id_list = []
    exps = Experiment.objects(ProjectID=project_id)
    samples = Sample.objects(ProjectID=project_id)
    items = ResearchItem.objects(ProjectID=project_id)

    for exp in exps:
        file_id_list.extend([f.id for f in exp["FileIDList"]])

    for sample in samples:
        file_id_list.extend([f.id for f in sample["FileIDList"]])

    for item in items:
        file_id_list.extend([f.id for f in item["FileIDList"]])

    files = File.objects(id__in=file_id_list)
    for file in files:
        if file.ThumbnailFileID:
            file_id_list.append(file.ThumbnailFileID.id)

    files = File.objects(id__in=file_id_list)
    fs = FileStorage(get_db())
    folder_path = "files"
    for file in files:
        blob = fs.get_file(file.id)
        new_folder = f"{folder_path}/{file.id}"
        os.mkdir(new_folder)
        file_path = f"{folder_path}/{file.id}/{file.Name}"
        with open(file_path, "wb+") as f:
            f.write(blob)


if __name__ == "__main__":
    app = create_app(minimal=True)
    with app.app_context():
        get_all_files()