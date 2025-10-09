import flask
from bson import ObjectId
from mongoengine import *
from mongoengine.base.datastructures import LazyReference
from mongoengine.queryset.visitor import Q

from .BaseClass import BaseClass
from tenjin.tasks.rq_task import create_task

class Supervisor(BaseClass):
    meta = {"collection": __qualname__,
            "indexes": [
                "SubUserID",
                "TopUserID"
            ]
            }

    SubUserID = LazyReferenceField("User", null=True)  # , reverse_delete_rule=CASCADE)
    TopUserID = LazyReferenceField("User", null=True)  # , reverse_delete_rule=CASCADE)

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        from tenjin.mongo_engine import Database

        if isinstance(document_list[0], ObjectId):
            doc_id_list = document_list
        else:
            doc_id_list = [doc.id for doc in document_list]

        if flag == "read":
            return document_list, {doc_id: True for doc_id in doc_id_list}

        if Database.check_for_no_access_check():
            # if get_from_redis("LayoutCheck") == "1":
            return document_list, {doc.id: True for doc in document_list}

        from .User import User

        # get user
        if user is None:
            user = flask.g.user
        if isinstance(user, LazyReference):
            user = user.fetch()
        elif isinstance(user, ObjectId):
            user = User.objects(id=user)[0]

        if user["Admin"] is True:
            return document_list, {doc_id: True for doc_id in doc_id_list}
        else:
            return [], {doc_id: False for doc_id in doc_id_list}

    def clean(self):
        super().clean()
        # avoid circular refs

        # get all tops of the new top
        top_user_id_list = [self.TopUserID.id]
        top_user_list = [self.TopUserID]
        while top_user_list:
            user_id_list = [u.id for u in top_user_list]
            # get tops of user by looking where those users are subs
            top_user_list = Supervisor.objects(SubUserID__in=user_id_list)
            for u in top_user_list:
                top_user_id_list.append(u.TopUserID)

        # check if sub is somewhere top of all found tops:
        s = Supervisor.objects(Q(TopUserID=self.SubUserID.id) & Q(SubUserID__in=top_user_id_list))
        if s:
            raise ValidationError("SubUser is a TopUser of any TopUser in the complete chain",
                                  errors={"TopUserID": {"Value": self.TopUserID, "List": False,
                                                        "Message": "SubUser is a TopUser of any TopUser in the complete chain"}})

    def create_method(self, kwargs):
        from tenjin.web.helper.email_helper import send_email

        top = self.TopUserID.fetch()
        sub = self.SubUserID.fetch()

        body = flask.render_template('emails/supervisor_mail_to_supervisor.html', email=sub.Email)
        create_task(send_email, top.Email, 'FURTHRmind: supervisor', body)

        body = flask.render_template('emails/supervisor_mail_to_user.html', supervisor=top.Email)
        create_task(send_email, sub.Email, 'FURTHRmind: you got a new supervisor', body)
