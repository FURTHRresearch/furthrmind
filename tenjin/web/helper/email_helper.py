import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import flask
from flask import current_app, g
import click

def send_email(mail_to, mail_subject, mail_body,mail_from=None, host=None, port=None, username=None, password=None):

    if not host:
        host = current_app.config["SMTP_HOST"]
        print(host)

    if not port:
        port = current_app.config["SMTP_PORT"]

    if not username:
        username = current_app.config["SMTP_USERNAME"]

    if not password:
        password = current_app.config["SMTP_PASSWORD"]

    if not mail_from:
        mail_from = current_app.config["SMTP_EMAIL"]

    mimemsg = MIMEMultipart()
    mimemsg['From']=mail_from
    mimemsg['To']=mail_to
    mimemsg['Subject']=mail_subject
    mimemsg.attach(MIMEText(mail_body, 'html'))
    true_list = [True, "True", "true", "TRUE", 1, "1"]
    if current_app.config["SMTP_USE_SSL"] in true_list:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host=host, port=port, context=context) as server:
            server.login(username, password)
            server.send_message(mimemsg)
    elif current_app.config["SMTP_USE_STARTTLS"] in true_list:
        with smtplib.SMTP(host=host, port=port) as server:
            server.local_hostname = host.lower()
            server.starttls()
            server.login(username, password)
            server.send_message(mimemsg)

@click.command('send-test-mail')
@click.option('--host')
@click.option('--port')
@click.option('--username')
@click.option('--password')
@click.option('--starttls')
@click.option('--ssl')
@click.option('--mail')
@click.option('--mail_to')
@flask.cli.with_appcontext
def test_email(host, port, username, password, starttls, ssl, mail, mail_to):
    app = flask.current_app
    app.config["SMTP_HOST"] = host
    app.config["SMTP_PORT"] = port
    app.config["SMTP_USERNAME"] = username
    app.config["SMTP_PASSWORD"] = password
    app.config["SMTP_USE_STARTTLS"] = starttls
    app.config["SMTP_USE_SSL"] = ssl
    app.config["SMTP_EMAIL"] = mail
    send_email(mail_to=mail_to, mail_subject="test", mail_body="test")

def init_app(app):
    app.cli.add_command(test_email)


if __name__ == "__main__":
    from tenjin import create_app
    app = create_app(minimal=True)
    with app.app_context():
        send_email(mail_to="daniel.menne@furthr-research.com", mail_subject="test", mail_body="test")
