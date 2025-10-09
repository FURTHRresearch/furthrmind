import bson
import flask


from tenjin.execution.create import Create

from tenjin.database.db import get_db
from ..web.helper.fieldsHelper import createNewFieldOn, getFields
from ..web.helper.furthrHelper import ensureAccess
from .auth import login_required

bp = flask.Blueprint('api1', __name__)


@bp.route('/experiments/<id>/fields', methods=['POST'])
@login_required
def set_experiment_field(id):
    userId = flask.g.user
    db = get_db().db
    data = flask.request.get_json()
    if not data['fieldType'] in ['Numeric', 'SingleLine', 'CheckBox']:
        flask.abort(400)
    fieldName = data['fieldName']
    ensureAccess("Experiment", "Update", id)
    experiment = db.Experiment.find_one(
        {'_id': bson.ObjectId(id)})
    fieldDataId = ''
    fieldDatas = getFields(experiment['FieldDataIDList'])
    fieldData = next((f for f in fieldDatas if f['Name'] == fieldName), None)
    if fieldData is None:
        fieldId = ''
        group = db.Group.find_one(
            {'_id': bson.ObjectId(experiment['GroupIDList'][0])})
        field = db.find_one(
            {"$and": [{"Name": fieldName}, {"ProjectID": group['ProjectID']}]})
        if not field:
            parameter = {
                "Type": data['fieldType'],
                "Name": fieldName,
                "ProjectID": [group['ProjectID']],
            }
            fieldId = Create.create(
                "Field", parameter, get_db(), userId)
        else:
            fieldId = field['_id']
        fieldDataId, _ = createNewFieldOn(
            data['fieldType'], id, 'experiments', fieldId)
    else:
        fieldDataId = bson.ObjectId(fieldData['id'])

    db.FieldData.update_one({'_id': fieldDataId}, {
                            '$set': {'Value': data['value']}})

    # then use fields helper
    return {
        'status': 'all good',
    }
