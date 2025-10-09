


class Delete:

    @staticmethod
    def delete(collection, entry_id, database=None, user_id=None, layout_check=False, include_attributes=None):
        from tenjin.mongo_engine import Database
        cls = Database.get_collection_class(collection)
        try:
            doc = cls.objects(id=entry_id).only("id", "ProjectID")
            for attr in include_attributes:
                doc = doc.only(attr)
        except:
            # docs that do not have ProjectID will crash, thus we need to catch the exception
            doc = cls.objects(id=entry_id)

        doc = doc.first()
        if doc is None:
            return entry_id

        if layout_check:
            doc.delete()
        else:
            doc.delete(signal_kwargs={
                "Opr": "Delete",
                "Attr": None,
                "Value": None,
            })
        return entry_id
