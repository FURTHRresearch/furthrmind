from marshmallow import Schema, fields


class MailSchema(Schema):
    mail_to = fields.Email(data_key="mail_to", required=True, metadata={"description": "The recipient email address"})
    mail_subject = fields.String(data_key="mail_subject", required=True, metadata={"description": "The email subject"})
    mail_body = fields.String(data_key="mail_body", required=True, metadata={"description": "The email body"})