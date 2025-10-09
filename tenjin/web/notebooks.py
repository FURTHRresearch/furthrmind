import flask

from .auth import login_required
from tenjin.database.db import get_db
import bson
from urllib.parse import quote
import re

from tenjin.file.file_storage import FileStorage

from tenjin.execution.update import Update

from .helper.furthrHelper import ensureAccess

bp = flask.Blueprint('notebooks', __name__)


@bp.route('/notebooks/<id>', methods=['GET'])
@login_required
def notebook(id):
    ensureAccess("Notebook", "read", id)
    content = get_db().db.Notebook.find_one(
        {"_id": bson.ObjectId(id)})['Content']
    if not content:
        content = ''
    # Upgrade old links
    content = re.sub(r'(!?\[.*\])\(([a-f\d]{24})\)', r'\1(/files/\2)', content)
    return flask.render_template('notebook.html', content=quote(content))


@bp.route('/notebooks/<id>/content', methods=['GET'])
@login_required
def notebook_content(id):
    ensureAccess("Notebook", "read", id)
    content = get_db().db.Notebook.find_one(
        {"_id": bson.ObjectId(id)})['Content']
    if not content:
        content = ''
    # Upgrade old links
    content = re.sub(r'(!?\[.*\])\(([a-f\d]{24})\)', r'\1(/files/\2)', content)
    return {"content": content}


@bp.route('/notebooks/<id>', methods=['POST'])
@login_required
def notebook_update(id):
    ensureAccess("Notebook", "write", id)
    userID = flask.g.user
    text = flask.request.data.decode('utf8')
    Update.update("Notebook", "Content",
                  text, bson.ObjectId(id), get_db(), userID)
    # get_db().db.Notebook.update_one({"_id": bson.ObjectId(id)}, {"$set":{'Content': text}})

    oldImages = get_db().db.Notebook.find_one(
        {"_id": bson.ObjectId(id)})['ImageFileIDList']
    newImages = re.findall(r'!\[.*\]\(\/nbfiles\/([a-f\d]{24})\)', text)

    Update.update("Notebook", "ImageFileIDList", [
        bson.ObjectId(i) for i in newImages], bson.ObjectId(id), get_db(), userID)
    return "all clear"


@bp.route('/nbfiles/upload', methods=['POST'])
@login_required
def notebook_upload_image():
    file = flask.request.data
    fs = FileStorage(get_db())
    fh = fs.put(file)
    return str(fh)
