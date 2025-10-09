import flask
from tenjin.web.webdatacalc import run_custom_script

bp = flask.Blueprint("api2/custom_script", __name__)

@bp.route("/run-custom-script", methods=["POST"])
def api_run_custom_script():
    """
       Structure of expected data: calculation-type currently not used. If more programming languages
       supported, than it will be necessary

       for files, either the content can be submitted or the fileID. In both cases, the webdatacalc
       server will save the content with the filename as specified under "filename"

       data["script"] = {
           "calculation-type": "custom-script-python",
           "content": "xxx"}
       data["files"] = [
           {"filename": "xxx",  with file extension
            "content": "xxx",
            "format": "text", or "bytes"
            "fileId": "xxx"}
       data["config"] = {} , additional input parameter passed to the script as a dict
       """

    
    return run_custom_script()