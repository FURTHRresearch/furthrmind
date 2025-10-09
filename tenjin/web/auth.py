import os
from functools import wraps
import datetime
import bson
import flask
from flask import redirect, render_template, request, session, url_for, current_app

from tenjin.authentication import Authentication
from tenjin.database.db import get_db
from .helper.email_helper import send_email
from tenjin.execution.update import Update

import random
import string
from .admin import create_user
from tenjin.tasks.rq_task import create_task



bp = flask.Blueprint('webauth', __name__)


@bp.route('/login',  methods=['GET'])
def login():
    if 'userID' in session and session['userID']:
        return redirect('/projects')
    return flask.send_from_directory('tenjin/web/static', 'react/index.html')


@bp.route('/isloggedin',  methods=['GET'])
def isloggedin():
    if 'userID' in session and session['userID']:
        return {'isLoggedIn': True}
    return {'isLoggedIn': False}


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('web.auth_root.login'))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kws):
        if not Authentication.authenticate_user():
            return redirect(url_for('web.auth_root.login'))
        return current_app.ensure_sync(f)(*args, **kws)
        # return f(*args, **kws)
    return decorated


@bp.route('/password-reset', methods=['POST'])
def password_reset():
    db = get_db().db
    data = request.get_json()
    email = data.get('email', '')
    email = email.lower()
    user = db.User.find_one({'Email': email})
    if user:
        token = str(os.urandom(16).hex())
        db.PasswordReset.insert_one(
            {'email': email, 'token': token})

        link = flask.current_app.config['ROOT_URL'] + \
            '/set-password?token=' + token

        body = render_template('emails/new_password.html', email=email, link=link)
        create_task(send_email, email, 'FURTHRmind Password Reset', body)
        # message = Mail(
        #     from_email='noreply@furthr-research.com',
        #     to_emails=email,
        #     subject='FURTHRmind Password Reset',
        #     html_content=render_template('emails/password-reset.html', link=link))
        # SendGridAPIClient(
        #     flask.current_app.config['SENDGRID_API_KEY']).send(message)
    return 'all clear'


@bp.route('/password-reset', methods=['GET'])
def password_reset_get():
    return flask.send_from_directory('tenjin/web/static', 'react/index.html')


@bp.route('/set-password', methods=['POST'])
def set_password():
    db = get_db().db
    data = flask.request.get_json()
    token = data.get('token', '')
    if not db.PasswordReset.find_one({'token': token}):
        flask.abort(403)
    password = data.get('password', '')
    if password != data.get('password2', ''):
        flask.abort(400)
    if password:
        # hashed = bcrypt.hashpw(
        #     password.encode(), bcrypt.gensalt()).decode()
        password_reset = db.PasswordReset.find_one(
                {'token': token})
        user = db.User.find_one({'Email': password_reset['email'].lower()})
        if not user:
            flask.abort(500)
        flask.g.user = user["_id"]
        Update.update("User", "Password", password, user["_id"])
        db.PasswordReset.delete_one({'token': token})
        return 'all good'
    else:
        flask.abort(400)


@bp.route('/set-password', methods=['GET'])
def set_password_get():
    return flask.send_from_directory('tenjin/web/static', 'react/index.html')


@bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('email')
    password = request.form.get('password')

    if not username:
        data = request.get_json()
        username = data["email"]
        password = data["password"]

    check, userID = Authentication.enrollUser(
        username, password)
    if not check:
        flask.abort(401)
    else:
        session['userID'] = str(userID)
        return "Authentication successful. Check your cookies."

@bp.route("/login_demo", methods=["GET"])
def login_demo():
    from tenjin.mongo_engine.User import User

    if flask.session.get("userID"):
        return flask.redirect("/projects")

    true_list = [True, "true", "True", "TRUE", 1, "1"]
    if flask.current_app.config.get("DEMO_SESSION") in true_list:
        user = User.objects(Admin=True).first()
        flask.g.user = user.id
        rnd = "".join(random.choice(string.ascii_lowercase + string.digits) for i in range(6))
        email = f"{rnd}@furthr-research.com"
        user_id = create_user(email)
        flask.g.user = bson.ObjectId(user_id)
        session["userID"] = str(user_id)
        return flask.redirect("/projects")
    else:
        flask.abort(404)
        
def _getFreeApiKeyString(mongoClient):
	keyString = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
	existCheck = mongoClient["ApiKey"].find_one({"KeyString": keyString})
	return _getFreeApiKeyString(mongoClient) if existCheck else keyString

def _getNewApiKeyDict(mongoClient,timeToLive,name,userID):
	lastValidTime = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=timeToLive)
	creationTime = datetime.datetime.now(datetime.UTC)
	keyString = _getFreeApiKeyString(mongoClient)
	return {"KeyString":keyString,"TTL":lastValidTime,
			"UserID":userID,"Name":name, "Date":creationTime}

def deleteOldApiKeys(mongoClient):
	mongoClient["ApiKey"].delete_many({"TTL": {"$lt": datetime.datetime.now(datetime.UTC)}})

def createNewApiKey(userID, timeToLive, name, mongoClient):
	deleteOldApiKeys(mongoClient)
	apiKeyDict = _getNewApiKeyDict(mongoClient,timeToLive,name,userID)
	mongoClient["ApiKey"].insert_one(apiKeyDict)
	return apiKeyDict["KeyString"]