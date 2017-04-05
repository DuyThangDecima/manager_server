# -*- coding: utf-8 -*-


class ModelDb():
    # Chứa tên các column
    _ID = '_id'
    # Số lần thử
    MAX_RETRY = 2

    def __init__(self, db_mongo, collection_name):
        self.db = db_mongo
        self.collection_name = collection_name
        pass

    def find_one(self, **kwargs):
        """
        Tim trong db, neu co thi tra ve True, doc
        nguoc lai tra ve false, Exception
        :param kwargs:
        :return:
        """
        spec = kwargs.pop('spec', None)
        fields = kwargs.pop('fields', None)

        exception = None
        result = None
        for i in range(0, self.MAX_RETRY):
            exception = None
            try:
                result = self.db[self.collection_name].find_one(filter=spec, projection=fields)
                # result = self.db[self.collection_name].find()
                break
            except Exception as e:
                exception = e

        if exception:
            return False, exception
        return True, result

    def update_one(self, filter, update, upsert=False,
                   bypass_document_validation=False,
                   collation=None):
        """
        THực hiện update_one
        :param filter:
        :param update:
        :param upsert:
        :param bypass_document_validation:
        :param collation:
        :return:
        """
        for i in range(0, self.MAX_RETRY):
            exception = None
            try:
                result = self.db[self.collection_name].update_one(filter, update, upsert,
                                                                  bypass_document_validation, collation)
                # result = self.db[self.collection_name].find()
                break
            except Exception as e:
                exception = e
        if exception:
            return False, exception
        # result[0] = [true,false] ket qua cua update
        return True, result

    def insert_one(self, document, bypass_document_validation=False):
        """
        Thực hiện insert_one
        :param document:
        :param bypass_document_validation:
        :return:
        """
        for i in range(0, self.MAX_RETRY):
            exception = None
            try:
                result = self.db[self.collection_name].insert_one(document, bypass_document_validation)
                break
            except Exception as e:
                exception = e
        if exception:
            return False, exception
        # result[0] = [true,false] ket qua cua update
        return True, result
