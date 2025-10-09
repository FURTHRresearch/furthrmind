import hashlib

from tenjin.mongo_engine import Database
import bcrypt
import requests
from flask import current_app

from bson import ObjectId
from tenjin.cache import Cache
cache = Cache.get_cache()

import datetime
from xmlrpc.client import Boolean

import bson
import flask
from flask import request, session
from tenjin.database.db import get_db
from ldap3 import Connection, Server
import ldap3
import os

class Authentication:

    @staticmethod
    def filter_list_get(collection, documents, user_id, database=None, local=False):

        cls = Database.get_collection_class(collection)
        permission_list, permission_dict = cls.check_permission(documents, "read", user_id)
        return permission_list

    @staticmethod
    def hasAccess(collection, operation, entry_id, user_id, database=None, attribute=None, value=None):
        assert operation in ["read", "write", "delete", "invite"]
        cls = Database.get_collection_class(collection)
        permission_list, permission_dict = cls.check_permission([entry_id], operation, user_id)
        return permission_dict[entry_id]


    @staticmethod
    def enrollUser(email_username, password):

        # First try LDAP
        if flask.current_app.config["LDAP_LOGIN"]:
            check, user_id = Authentication.enroll_user_ldap(email_username, password)
            if check:
                return check, user_id

        # If LDAP is not enabled or if LDAP Login fails, try normal login. For external users, login without LDAP
        # must be possible
        check, user_id = Authentication.enroll_user_no_ldap(email_username, password)
        return check, user_id

    @staticmethod
    def enroll_user_no_ldap(email, password):
        from tenjin.mongo_engine.User import User

        all_user = User.objects()

        for user in all_user:

            if "Email" not in user or not "Password" in user:
                continue

            if user["Email"] and user["Email"].lower() == email.lower():
                if not user["Password"]:
                    return False, None
                pwServer = user["Password"].encode()
                password = password.encode()
                check = bcrypt.checkpw(password, pwServer)

                if not check:
                    return False, None

                return True, user.id

        return False, None

    @staticmethod
    def enroll_user_ldap(username, password):
        from tenjin.mongo_engine.User import User
        from tenjin.execution.create import Create
        from tenjin.execution.update import Update
        from tenjin.mongo_engine import Database

        check, email = Authentication.ldap_auth(username, password)
        if not check:
            return False, None

        user = User.objects(UserName=username).first()
        if not user:
            # look for user by email => save username
            user = User.objects(Email=email.lower()).first()
            if not user:
                user_dict = {
                    "Email": email.lower(),
                    "UserName": username,
                    "Password": os.urandom(16).hex(),
                }
                Database.set_no_access_check(True)
                user_id = Create.create("User", user_dict)
                Database.set_no_access_check(False)
                return True, user_id
            else:
                Database.set_no_access_check(True)
                Update.update("User", "UserName", username, user.id)
                Database.set_no_access_check(False)
                return True, user.id

        else:
            if email.lower() != user.Email:  # Email is always in lower case
                Database.set_no_access_check(True)
                Update.update("User", "Email", email.lower(), user.id)
                Database.set_no_access_check(False)
            return True, user.id

    @staticmethod
    def authenticate_user():
        flask.g.user = None
        user_id = None
        api_key_names = ['X-API-KEY', "X-Api-Key", "uppy-auth-token"]
        api_key_found = False
        for api_key_name in api_key_names:
            if api_key_name in request.headers:
                api_key_found = True
                api_key = request.headers.get(api_key_name)
                authData = get_db().db.ApiKey.find_one(
                    {'KeyString': api_key,
                     "TTL": {"$gt": datetime.datetime.now(datetime.UTC)}})
                if authData and 'UserID' in authData:
                    # session['userID'] = str(authData['UserID'])
                    flask.g.user = bson.ObjectId(authData['UserID'])
                    user_id = authData["UserID"]
                break
        if not api_key_found:
            if 'userID' in session and session['userID']:
                flask.g.user = bson.ObjectId(session['userID'])
                user_id = session["userID"]

        isAuthenticated = Boolean(flask.g.user)
        return isAuthenticated

    @staticmethod
    def ldap_auth(ldap_uid, ldap_pass):
        try:
            host = flask.current_app.config['LDAP_URL']
            port = int(flask.current_app.config['LDAP_PORT'])
            domain_prefix = flask.current_app.config['LDAP_DOMAIN_PREFIX']

            user = ldap_uid
            if domain_prefix:
                user = f"{domain_prefix}\\{ldap_uid}"
            server = Server(host=host, port=port, connect_timeout=2)
            # c = Connection(server, auto_bind=True, version=3, authentication=SASL, receive_timeout=2,
            #                sasl_mechanism=DIGEST_MD5, sasl_credentials=(None, ldap_uid, ldap_pass, None, 'sign'))
            c = Connection(server, user, ldap_pass)
            c.bind()

            base = flask.current_app.config['LDAP_BASE_DN']
            filter = "(&(objectClass=person)(sAMAccountName=" + ldap_uid + "))"
            attrs = ["*"]
            c.search(base, filter, ldap3.SUBTREE, attributes=attrs)

            return c.bound, str(c.entries[0]["mail"]).lower()
        except Exception as e:
            return False, None
