
def hasChanged(dataIDList, timestamp, db):

	""" Delivers a boolean flag to indicate whether a change has occurred since the
	given timestamp on the given object in the specified collection. This check
	includes referenced objects in a depth of 1 (so for example field data of an
	experiment are checked).

	Please Note: Reference depth could be enhanced or included as a parameter of this
	method if needed, but would make things exponentially slower and more complicated.

	:param dataIDList as bson objectid
	:param timestamp as datetime
	:param db as DatabaseClient instance """


	versionList = db.db["Versioning"].find_one({"DataID":{"$in":dataIDList},"ExecutionTime":{"$gt":timestamp}})
	return bool(versionList)








