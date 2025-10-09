from pymongo import MongoClient

import os
class DatabaseClient:


    def __init__(self, dburi, dbname, client = None):
        if client is None:
            self.uri = dburi
            self.name = dbname
            MONGODB_CERT = os.environ.get('MONGODB_CERT')

            if MONGODB_CERT is None:
                self.mongoClient=MongoClient(dburi)
            else:
                if not os.path.isfile("mongodb.ca.crt"):
                    with open("mongodb.ca.crt", "w+") as f:
                        f.write(MONGODB_CERT)
                self.mongoClient = MongoClient(dburi,
                                               ssl=True,
                                               tlsCAFile="mongodb.ca.crt")
            self.db = self.mongoClient[dbname]
        else:
            self.db = client


    def find(self,collection,searchDict,options=None,convertToEnum=True, sortKey=None, sortDirection=1):

        if options is None:
            if sortKey:
                result = list(self.db[collection].find(searchDict).sort(sortKey, sortDirection))
            else:
                result = list(self.db[collection].find(searchDict))
        else:
            if sortKey:
                result = list(self.db[collection].find(searchDict, options).sort(sortKey, sortDirection))
            else:
                result = list(self.db[collection].find(searchDict, options))

        return result



    def find_one(self,collection,searchDict,options=None,convertToEnum=True):

        if options is None:
            result = self.db[collection].find_one(searchDict)
        else:
            result = self.db[collection].find_one(searchDict, options)

        return result



    def insert_one(self,collection, createDict):

        result = self.db[collection].insert_one(createDict)
        return result



    def update(self, collection, searchDict, updateDict):
        return self.db[collection].update_many(searchDict, updateDict)


    def update_one(self,collection, searchDict , updateDict):
        return self.db[collection].update_one(searchDict, updateDict)



    def remove_one(self, collection, searchDict):
        return self.db[collection].delete_one(searchDict)









