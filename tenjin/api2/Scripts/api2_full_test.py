import os

import requests
import json


if __name__ == "__main__":
    home = os.path.expanduser("~")
    with open(f"{home}/dev_api.txt") as f:
        api_key = f.read()

    # host = 'http://localhost:5000'
    host = 'https://dev.furthrmind.app'
    session = requests.session()
    session.headers.update({"X-API-KEY": api_key})
    def testProjectRoute():
        # get projects
        response = session.get(f"{host}/api2/project")
        print("Get Projects: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # create single project
        response = session.post(f"{host}/api2/project", data=json.dumps({"name": "Tim_Test_100_user"}))
        #projectID = response.json()["results"][0]
        projectID = "6567345b0a39d90db93e4115"
        print("Create Project: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # get specific project
        response = session.get(f"{host}/api2/project/{projectID}")
        print("Get specific Project: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # update project
        #response = session.post(f"{host}/api2/project/{projectID}", data=json.dumps({'name': "Test_Project_rena44med"}))
        #print("Update Project:", response)

        return projectID

    def testGroupRoute(projectID):    # create group
        response = session.post(f"{host}/api2/project/{projectID}/group", data=json.dumps({'name': "Test_Group15"}))
        groupID = response.json()["results"][0]
        print("Create Group: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        #get all groups
        response = session.get(f"{host}/api2/project/{projectID}/group")
        print("Get Groups: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # get specific group
        response = session.get(f"{host}/api2/group/{groupID}")
        print("Get specific group: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # update group
        #response = session.post(f"{host}/api2/project/{projectID}/group", data=json.dumps({'name': "Test_Group"}))
        #print("Update group:", response.json())



        return groupID

    def testSampleRoute(projectID, groupID):
        response = session.post(f"{host}/api2/project/{projectID}/sample", data=json.dumps({'name': "Test_Sample", 'groups': [groupID]}))
        try:
            sampleID = response.json()["results"][0]
            print("Create sample: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

            # get specific sample
            responseSpecific = session.get(f"{host}/api2/sample/{sampleID}")
            print("Get specific sample: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

            # update sample
            # response = session.post(f"{host}/api2/project/{projectID}/group", data=json.dumps({'name': "Test_Group"}))
            # print("Update group:", response.json())


            return sampleID

        except:
            print("Create sample: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        #get all samples
        response = session.get(f"{host}/api2/project/{projectID}/sample")
        print("Get all samples: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

    def testExperimentRoute(projectID, groupID):    # create experiment
        response = session.post(f"{host}/api2/project/{projectID}/experiment", data=json.dumps({'name': "Test_Experiment5", 'groups': [groupID]}))
        try:
            expID = response.json()["results"][0]
            print("Create experiment: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

            # get specific experiment
            responseSpecific = session.get(f"{host}/api2/experiment/{expID}")
            print("Get specific experiment: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

            # update experiment
            # response = session.post(f"{host}/api2/project/{projectID}/group", data=json.dumps({'name': "Test_Group"}))
            # print("Update group:", response.json())


            return expID



        except:
            print("Create experiment:", response)

        #get all experiments
        response = session.get(f"{host}/api2/project/{projectID}/experiment")
        print("Get all experiments: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

    def researchcategoryAndItemRouteTest(projectID, groupID):
        # create category
        response = session.post(f"{host}/api2/project/{projectID}/researchcategory", data=json.dumps({'name': "Category Name", 'description': "Description of categoryname"}))
        categoryID = response.json()["results"][0]
        print("Create Reserchcategory: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # update category
        response = session.post(f"{host}/api2/project/{projectID}/researchcategory", data=json.dumps({'id': categoryID, 'name': "NewCategory Name", 'description': " New Description of categoryname"}))
        print("Update Reserchcategory: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # get all categorys
        response = session.get(f"{host}/api2/project/{projectID}/researchcategory")
        print("Get all Reserchcategorys: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # get specific category
        response = session.get(f"{host}/api2/researchcategory/{categoryID}")
        print("Get specific Reserchcategory: ", response, "Message: ", response.json()["message"],"status: ", response.json()["status"] )

        # create Researchitem in not existing group and researchcategory
        response = session.post(f"{host}/api2/project/{projectID}/researchitem", data=json.dumps({'name': "Item Name 2",'groups': [{'name': "New Group Research Item Test"}] ,'category': {'name': "New Research Item Test Category"}}))
        itemID = response.json()["results"][0]
        print("Create Item in not existing group and category: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # update Item
        response = session.post(f"{host}/api2/project/{projectID}/researchitem", data=json.dumps({'id': itemID, 'name': "new Name2"}))
        print("Update researchitem: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # get specific researchitems
        response = session.get(f"{host}/api2/researchitem/{itemID}")
        print("Get specific researchitem: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # get all researchitems
        response = session.get(f"{host}/api2/project/{projectID}/researchitem")
        print("Get all researchitems: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # delete item
        response = session.delete(f"{host}/api2/researchitem/{itemID}", data=json.dumps({'id': itemID}))
        print("Delete specific researchitem: ", response)
              #"Message: ", response.json()["message"],"status: "+ response.json()["status"] )


        # create Researchitem in existing group and category
        response = session.post(f"{host}/api2/project/{projectID}/researchitem", data=json.dumps({'name': "Item Name",'groups': [{'id': groupID}] ,'category': {'id': categoryID}}))
        itemID = response.json()["results"][0]
        print("Create Item in existing group and category: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # delete researchcategory
        response = session.delete(f"{host}/api2/researchcategory/{categoryID}")
        print("Delete researchcategory: ", response)
              #, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

    def authorApiTest():
        # create author
        response = session.post(f"{host}/api2/author/", data =json.dumps({'name': "Neuer Author", 'institution': "Neues Institut"}))
        print("Create author: ", response,)
        #"Message: ", response.json()["message"],"status: "+ response.json()["status"] )

        # get all authors
        response = session.get(f"{host}/api2/author/")
        print("Get author: ", response,)
        #"Message: ", response.json()["message"],"status: "+ response.json()["status"] )

    def fieldApiTest(projectID, expID, groupID):
        fieldTypeList = ['Numeric', 'Date', 'ComboBox', 'ComboBoxSynonym', 'SingleLine', 'MultiLine', 'CheckBox', 'RawDataCalc', 'Link', 'User', 'File', 'Table', 'ChemicalStructure', 'Calculation']
        for type in fieldTypeList:
            response = session.post(f"{host}/api2/project/{projectID}/field", data=json.dumps({"name": str(type), "type": type}))
            print("Create Field: "+type+" Message: ", response.json()["message"],"status: "+ response.json()["status"] )
            fieldID = response.json()["results"][0]
            #expData = session.post(f"{host}/api2/project/{projectID}/experiment",data=json.dumps({'id': expID, "fielddata": [{'id':fieldID}]}))

            #get specific field
            response = session.get(f"{host}/api2/field/{fieldID}")
            print("Get specific field: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )


        # get all fields
        response = session.get(f"{host}/api2/project/{projectID}/field")
        print("Get all fields: ", response, "Message: ", response.json()["message"],"status: "+ response.json()["status"] )

    def deleteApiTest(projectID, groupID, sampleID, expID):
        # delete sample
        response = session.delete(f"{host}/api2/sample/{sampleID}")
        print("Delete sample:", response)

        # delete experiment
        response = session.delete(f"{host}/api2/experiment/{expID}")
        print("Delete experiment:", response)

        # delete group
        #response = session.delete(f"{host}/api2/group/{groupID}")
        print("Delete group:", response)

        # delete project
        #response = session.delete(f"{host}/api2/project/{projectID}")
        #print("Delete project:", response)


    projectID = testProjectRoute()
    groupID = testGroupRoute(projectID)
    sampleID = testSampleRoute(projectID, groupID)
    expID = testExperimentRoute(projectID, groupID)
    researchcategoryAndItemRouteTest(projectID, groupID)
    authorApiTest()
    fieldApiTest(projectID, expID, groupID)
    #deleteApiTest(projectID, groupID,sampleID, expID)

    print("Done.")
