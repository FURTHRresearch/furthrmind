from mongoengine import *

class SoftwareVersion(Document):

	@classmethod
	def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
		return document_list, {doc.id: True for doc in document_list}

	meta = {"collection": __qualname__}

	Version = StringField(required=True)
	Date = DateTimeField(required=True)
