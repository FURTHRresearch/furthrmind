import os

from furthrmind import Furthrmind

def calc(config):
    """
    config is d dict and contains: projectId, groupId, sampleId, experimentId, rawdataId, fieldId, callbackUrl, apiKey
    """
    fm = Furthrmind(config['callbackUrl'], config['apiKey'],
                    project_id=config['projectId'],)

    experiments = fm.Experiment.get_all()
    if not experiments:
        return
    exp = experiments[0]
    print(exp)

    # iterating all exp
    if exp.fielddata:
        for fielddata in exp.fielddata:
            print("field_data_id: ", fielddata.id)
            print("field_id: ", fielddata.field_id)  # id of field definition, type name etc
            print("field_name: ", fielddata.field_name)

    # downloading a file
    files = exp.files
    if files:
        file = files[0]
        folder = os.getcwd()
        file.download(folder)
        print("File exists: ", os.path.isfile(f"{folder}/{file['name']}"))


    # getting all groups
    groups = fm.Group.get_all()
    if groups:
        group = groups[0]
        print("number of exp: ", len(group.experiments))
        if group.experiments:
            print("name and id of first exp: ", group.experiments[0]["name"],group.experiments[0]["id"])

    exp = fm.Experiment.get(config["experimentId"])
    result = {"key": "value",
              "key2": "value2"}
    exp.set_calculation_result(result, fielddata_id=config["fieldId"])





