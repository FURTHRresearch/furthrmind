import flask
import bson
from tenjin.web.webdatacalc import set_calculationresults
from tenjin.mongo_engine.FieldData import FieldData

bp = flask.Blueprint("api2/calculation_result", __name__)

@bp.route("/set-result/<field_data_id>", methods=["POST"])
def set_calculation_result(field_data_id):
    # json payload will be requested in the "set_calculationresults" function
    try:
        field_data_id = bson.ObjectId(field_data_id)
    except:
        raise ValueError("Invalid field data ID.")
    # access level is read, because the user might not have write access to the field data, but should be able to trigger a recalculation
    access_list, access_dict = FieldData.check_permission([field_data_id], "read")
    if not access_list:
        raise PermissionError("You do not have permission to read this field data.")
    return set_calculationresults(field_data_id)