from flask import abort

from tenjin.database.db import get_db
from tenjin.execution.create import Create
import re
import bcrypt

from tenjin.authentication import Authentication
import flask

bp = flask.Blueprint('webldap', __name__)


def connect_accounts(ldap_name, ldap_pass, furthr_email, furthr_pass):

    if not Authentication.ldap_auth(ldap_name, ldap_pass):
        return False

    regx = re.compile(f"^{furthr_email}", re.IGNORECASE)
    user = get_db().find_one("User", {"Email": regx})

    if user:
        pwServer = user["Password"].encode()
        password = furthr_pass.encode()
        check = bcrypt.checkpw(password, pwServer)
        if check:
            get_db().db["User"].update_one(
                {"_id": user["_id"]}, {"$set": {"UserName": ldap_name}})
        else:
            abort(401)
    else:
        if not get_db().find_one("User", {"UserName": ldap_name}):
            Create.create("User", {
                          "UserName": ldap_name, "Email": furthr_email}, get_db(), None)
        else:
            abort(401)


@bp.route('/ldap-signup', methods=['POST'])
def ldap_signup():
    data = flask.request.get_json()
    if not 'ldapuser' in data or not 'ldappassword' in data or not 'email' in data:
        flask.abort(400)
    if not 'furthrpassword' in data:
        connect_accounts(data['ldapuser'],
                         data['ldappassword'], data["email"], "")
    else:
        connect_accounts(data['ldapuser'], data['ldappassword'],
                         data["email"], data["furthrpassword"])

    return 'success'
