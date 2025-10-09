from marshmallow import Schema, fields
from bson import ObjectId

class Response:
    def __init__(self, status=True, results=None, message=None):
        if not isinstance(status, bool):
            raise TypeError("status wrong type")

        if status:
            status = "ok"
        else:
            status = "error"
        self.status = status
        
        if isinstance(results, ObjectId):
            results = str(results)
            
        if isinstance(results, list):
            new_results = []
            for result in results:
                if isinstance(result, ObjectId):
                    new_results.append(str(result))
                else:
                    new_results.append(result)
            results = new_results

        if results is None:
            results = []
        
        if not isinstance(results, list):
            results = [results]
        
        self.results = results
        self.message = message

class ResponseSchema(Schema):
    status = fields.Str()
    results = fields.List(fields.Raw())
    message = fields.Str()

class ResponseSchemaListValueStr(ResponseSchema):
    results = fields.List(fields.Str())