import datetime
import time

from tenjin.database.db import get_db

from tenjin.mongo_engine import *

def update_exp():
    from tenjin.mongo_engine import Database
    Database.set_no_access_check(True)
    e = Experiment.objects.first()
    from tenjin.execution.update import Update
    print(e.id, e.Protected)
    Update.update("Experiment", "Protected", True, e.id)
    Database.set_no_access_check(False)
    

def delete_stuff():
    db = get_db().db
    collections = db.list_collection_names()
    for c in collections:
        db[c].drop_indexes()
    print(collections)

def get_all():
    print("Author", len(Author.objects))
    print("Chunk", len(Chunk.objects))
    print("ComboBoxEntry", len(ComboBoxEntry.objects))
    print("Column", len(Column.objects))
    print("Experiment", len(Experiment.objects))
    print("Field", len(Field.objects))
    print("FieldData", len(FieldData.objects))
    print("File", len(File.objects))
    print("Group", len(Group.objects))
    print("Permission", len(Permission.objects))
    print("ResearchCategory", len(ResearchCategory.objects))
    print("ResearchItem", len(ResearchItem.objects))
    print("Sample", len(Sample.objects))
    print("Unit", len(Unit.objects))
    print("UnitCategory", len(UnitCategory.objects))
    print("User", len(User.objects))

def get_exp():
    e = Experiment.objects[0]
    for field in Experiment._fields.values():
        print(field.name)

    fd_id_list = [fd.id for fd in e.FieldDataIDList]
    start = time.time()
    fd_list = FieldData.objects(id__in=fd_id_list)
    print("mongoengine query __in", time.time() - start)
    # print(fd_list)

    start = time.time()
    fd_list_1 = []
    for fd in e.FieldDataIDList:
        fd = fd.fetch() # To get a Field Object
        # fd.fetch()
        fd_list_1.append(fd)
        # print(fd)
    print("mongoengine iterate and fetch",time.time()-start)


    start = time.time()
    fd_list_2 = list(get_db().db["FieldData"].find({"_id": {"$in": fd_id_list}}))
    print("pymongo", time.time()-start)

    start = time.time()
    fd_list_2 = list(get_db().db["FieldData"].find({"_id": {"$in": fd_id_list}}))
    print("pymongo", time.time() - start)

    print([fd for fd in fd_list_1])
    print([fd for fd in fd_list])
    print([fd for fd in fd_list_2])
    print(id(Experiment.FileIDList))

    start = time.time()
    e_list = Experiment.objects[0:10]
    import copy
    date = copy.copy(e_list[0].Date)
    for e in e_list:
        e.Date = date
        e.save(signal_kwargs={"Attr":1})
    print("save", time.time()-start)

    start = time.time()
    e_list = Experiment.objects[0:10]
    date = datetime.datetime.now()
    for e in e_list:
        e.Date = date
        e.save()
    print("save value change", time.time() - start)
    e = e_list[0]
    group = e.GroupIDList[0]
    group = group.fetch()
    data = {Experiment.GroupIDList.name: [group.id],
            Experiment.Name.name: "My exp",
            Experiment.ProjectID.name: group.ProjectID}

    new_exp = Experiment(**data)
    new_exp.save()
    print(new_exp)

    e_id = e.id
    e_object = e
    e_ = Experiment.objects(id=e_id)
    e__ = Experiment.objects(id=e_object.id)
    e___ = Experiment.objects(id=e.GroupIDList[0].id)
    if not e___:
        print(1)
    print(e_,e__, e___)
def create_project():
    project = Project(Name="Test")
    project.save()

def create_combo():
    start = time.time()
    c = ComboBoxEntry(FieldID="Test")
    c.FieldID = "Test2"
    c["FieldID"] = "Test3"
    print("combo", time.time()-start)

def create_field_data():

    field = Field.objects(ProjectID__ne=None)[0]

    field_data = FieldData(FieldID=field, Value=5)
    field_data.save()


def create_exp():
    e = Experiment.objects[0]
    group = e.GroupIDList[0]
    group = group.fetch()
    data = {Experiment.GroupIDList.name: [group.id],
            Experiment.Name.name: "My exp2",
            Experiment.ProjectID.name: group.ProjectID}
    new_exp = Experiment(**data)
    new_exp.save()
    print(1)

def create_user():
    user = User(Email="Daniel.Menne@furthr-research.com")
    user.save()
    print(1)

def in_operator_test():
    e = Experiment.objects().only("FieldDataIDList", "GroupIDList")[0]
    field_data_list = e.FieldDataIDList
    f1_lazy = field_data_list[0]
    f1_id = field_data_list[0].id
    f1 = field_data_list[0].fetch
    print("Lazy", f1_lazy in field_data_list)
    print("id", f1_id in field_data_list)
    print("dco", f1 in field_data_list)

def create_permission():
    from .Project import Project
    import flask
    user = User.objects(Email="daniel.menne@furthr-research.com")[0]
    project = Project.objects()[0]
    project_id = project.id

    permission = Permission(
        ProjectID=project_id, Read=True, Write=True
    )
    flask.g.user = project.OwnerID.id
    permission.save()

    user.PermissionIDList.append(permission.id)
    user.save()

def test_auth():
    user = User.objects(Email="db@furthr-research.com")[0]

    exp_list = Experiment.objects()[0]
    start = time.time()
    return_value = Experiment.check_permission([exp_list], "read", user=user.id)
    print(time.time() - start, "1 Object Owner")

    exp_list = Experiment.objects()[0:100]
    start = time.time()
    return_value = Experiment.check_permission(exp_list, "read", user=user.id)
    print(time.time() - start, "100 Objects Owner")

    user = User.objects(Email="daniel.menne@furthr-research.com")[0]

    exp_list = Experiment.objects()[0]
    start = time.time()
    return_value = Experiment.check_permission([exp_list], "read", user=user.id)
    print(time.time() - start, "1 Object Direct Permission")

    exp_list = Experiment.objects()[0:100]
    start = time.time()
    return_value = Experiment.check_permission(exp_list, "read", user=user.id)
    print(time.time() - start, "100 Objects Direct Permission")

    user = User.objects(Email="demo2@furthr-research.com")[0]
    exp_list = Experiment.objects()[0]
    start = time.time()
    return_value = Experiment.check_permission([exp_list], "read", user=user.id)
    print(time.time()-start, "1 Object 2 Stage Supervision Permission")

    exp_list = Experiment.objects()[0:100]
    start = time.time()
    return_value = Experiment.check_permission(exp_list, "read", user=user.id)
    print(time.time() - start, "100 Object 2 Stage Supervision Permission")

def create_supervisor():
    data = {User.Email.name: "demo2@furthr-research.com"}
    user = User(**data)
    user.save()
    user_id = user.id

    user2 = User.objects(Email="daniel.menne@furthr-research.com")[0]
    user2_id = user2.id
    data = {
        Supervisor.TopUserID.name: user_id,
        Supervisor.SubUserID.name: user2_id
    }
    sv = Supervisor(**data)
    sv.save()

def create_research_item():
    import datetime
    ri = ResearchItem.objects().first()
    data = {
        ResearchItem.Name.name: ri["Name"] + str(datetime.datetime.now()),
        ResearchItem.GroupIDList.name: ri[ResearchItem.GroupIDList.name],
        ResearchItem.ResearchCategoryID.name: ri[ResearchItem.GroupIDList.name][0].id
    }
    doc = ResearchItem(**data)
    doc.validate()
    print()

def check_default():
    speadsheet = SpreadSheet.objects().first()
    data = {
        "Template": False,
        "ProjectID": speadsheet.ProjectID
    }
    doc = SpreadSheet(**data)
    doc.save()

def check_request_list_with_lazy_ref():
    rd = RawData.objects().first()
    columns = Column.objects(id__in=rd.ColumnIDList)
    print(len(rd.ColumnIDList), columns.count())

def query_operator_test():
    from tenjin import create_app
    from mongoengine.queryset import Q
    from tenjin.mongo_engine.FieldData import FieldData
    from tenjin.mongo_engine.Experiment import Experiment
    from bson import ObjectId
    app = create_app(minimal=True)
    with app.app_context():
        # maskenhalter: Silikon_gruen_orange
        field_data = FieldData.objects(Q(Value__in=[ObjectId("6319f76901c844a436e0b9e6")])).only("id")
        combo_query = Q()
        # combo_query = Q(FieldDataIDList__in=[fd.id for fd in field_data])

        # field "Druck Kammer"
        field_data = FieldData.objects(Q(FieldID=ObjectId("6319f76401c844a436e0b270"),
                                       Value__gte=5,
                                       Value__lte=8)).only("id")
        numeric_query = Q(FieldDataIDList__in=[fd.id for fd in field_data])

        exp = Experiment.objects(Q() & Q() & numeric_query)
        print(exp.count())

def test_subgroup_search():
    from tenjin import create_app
    from bson import ObjectId
    app = create_app(minimal=True)
    with app.app_context():
        groups = Group.objects(ProjectID=ObjectId("66166c6b583bbe1799372bde"), GroupID=None)

    pipeline = [
        {"$match": {"GroupID": {"$in": [g.id for g in groups]}}},
        {"$graphLookup": {
            "from": "Group",
            "startWith": "$_id",
            "connectFromField": "_id",
            "connectToField": "GroupID",
            "as": "groups"}},
    ]
    sub_group_id_set = set()
    groups = list(Group.objects.aggregate(pipeline))
    print(groups)