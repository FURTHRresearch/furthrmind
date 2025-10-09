import flask
import json
from tenjin.tasks.rq_task import create_task
from tenjin.api2.schema.mail import MailSchema
from .helper_methods import response_wrapper

bp = flask.Blueprint("api2/send_email", __name__)

@bp.route("/send-email", methods=["POST"])
@response_wrapper
def send_email():
    from tenjin.web.helper.email_helper import send_email

    data = flask.request.get_json()
    parameter = json.loads(MailSchema().dumps(data))

    mail_to = parameter.get("mail_to")
    mail_subject = parameter.get("mail_subject")
    mail_body = parameter.get("mail_body")

    create_task(send_email, mail_to, mail_subject, mail_body)
    return "email sent"