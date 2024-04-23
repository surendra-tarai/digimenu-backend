'''
    Data access layer:
    Common place holder for all database operation with mongodb
'''
from xmlrpc.client import boolean
from bson import ObjectId
import pymongo
from pymongo.errors import OperationFailure
from utility import Logger
from utility.constant import Status

LOGGER = Logger('DAL')


class DAL:
    '''DAL(Data Access Layer) has commmon CRUD operational functions with mongodb
       such as find, add, update, delete, etc.
    '''
    # MongoDB Atlas
    data_source = 'mongodb+srv://starai:n4euaQdbw8HArLnX@mongodb-hbeu6.mongodb.net'  # cloud
    # data_source = 'mongodb://localhost:27017/'  # local
    client = pymongo.MongoClient(data_source)
    database = 'digi-menu'  # read from one config file or environemnt variable
    db = client[database]

    def __init__(self, collection=None):
        self.collection = collection

    def insert_document(self, document, collection=None):
        '''Insert single document at specified collection

        Parameters:
        document (dict): document details
        collection (str): Target collection name to store given document data.

        Return:
        -> (InsertOneResult)  Object of InsertOneResult
        '''

        try:
            collection = collection or self.collection
            if not collection:
                raise Exception('collection is not defined')
            if not isinstance(collection, str):
                raise TypeError('collection must be a str type of value')
            if not isinstance(document, dict):
                raise TypeError('document must be a dict type of value')

            result = self.db[collection].insert_one(document)
            if result.acknowledged and '_id' in document:
                document['_id'] = str(document.get('_id'))

            return result
        except OperationFailure as e:
            LOGGER.exception(e)
        except Exception as e:
            LOGGER.exception(e)

    def modify_document(self, filter_: dict, new_value: dict) -> boolean:
        update_query = {
            '$set': new_value
        }
        db_result = self.db[self.collection].update_one(filter_, update_query)
        return db_result.acknowledged

    def insert_documents(self, documents, collection=None):
        '''Insert multiple documents/records at speicified collection

        Parametes:
        documents (list of dict): List of document objects
        collection (str): target collection name. default value: object.collection

        Return:
        -> InsertManyResult : which has properties called acknowledged (bool), inserted_ids(list of object ids)
            acknowledged: If insertion succeded return True, else False
            inserted_ids: List inserted Ids(ObjectId)
        '''

        collection = collection or self.collection
        if not collection:
            raise Exception('collection is not defined')
        if not isinstance(collection, str):
            raise TypeError('collection must be a str type of value')
        try:
            return self.db[collection].insert_many(documents)
        except OperationFailure as ex:
            # pass
            pass

    def delete_document(self, filter_: dict):
        result = self.db[self.collection].delete_one(filter_)
        return result.deleted_count

    def find_one_document(self, filter_, fields=None, collection=None):
        '''Find one document of specified collection with specified fields
           based on given filter if any.

           Parametes:
           filter_ (dict): mongodb filter
           fields (set/dict): field(s) u want to return in document, default all
           collection (str): target collect to get data
        '''

        try:
            collection = collection or self.collection
            if not collection:
                raise Exception('collection is not defined')
            if not isinstance(collection, str):
                raise TypeError('collection must be a str type of value')
            if not isinstance(filter_, dict):
                raise TypeError('filter_ must be a dict type of value')
            if fields and not (isinstance(fields, set) or isinstance(fields, dict)):
                raise TypeError('fields must be a set or dict type of value')

            record = self.db[collection].find_one(filter_, fields)

            if record:
                record = dict(record)
                record['_id'] = str(record.get('_id'))
            return record
        except OperationFailure as ex:
            raise OperationFailure(ex)
        except Exception as e:
            print(e)

        return {}

    def find_doc_by_id(self, id, fields=None, collection=None):
        try:
            filter_ = {"_id": ObjectId(id)}
            return self.find_one_document(filter_, fields, collection)
        except Exception as e:
            print(e)

    def find_documents(self, filter_: dict = {}, fields: set = None, collection: str = None, pagination: dict = None):
        '''Retrieve documents/records of speicified collection
           based on given filter_

           Parametes:
           filter_ (dict): MongoDB collection filter criteria
           collection (str): collection name from which data will fetch
           fields (set): list of fields u want to return

           Return:
           -> Return collection of documents
        '''

        try:
            collection = collection or self.collection
            if not collection:
                raise Exception('collection is not defined')
            if not isinstance(collection, str):
                raise TypeError('collection must be a str type of value')
            if filter_ and not isinstance(filter_, dict):
                raise TypeError('filter_ must be a dict type of value')
            if fields and not isinstance(fields, (set, dict)):
                raise TypeError('fields must be a set or dict type of value')
            totalRecords = 0
            if pagination and isinstance(pagination, dict):
                page = pagination['page']
                size = pagination['size']
                skip = size*(page-1)
                limit = size
                records = self.db[collection].find(
                    filter_, fields).skip(skip).limit(limit)
            else:
                records = self.db[collection].find(filter_, fields).limit(500)

            totalRecords = self.db[collection].count_documents(filter_)
            final_records = []
            for record in records:
                record = dict(record)
                record['_id'] = str(record.get('_id'))
                record.update(record)
                final_records.append(record)

            if pagination:
                pagination_content = {'page': page,
                                      'size': size,
                                      'totalRecords': totalRecords}
                return {'data': final_records, 'pagination': pagination_content}

            return {'data': final_records}

        except Exception as ex:
            pass
            return []

    def aggregate(self, foreign_collection: str, local_field: str, foreign_field: str, records_as: str, **kwargs):
        filter_ = kwargs.get('filter_', {})
        search = kwargs.get('search')
        projection = kwargs.get('projection') or kwargs.get('fields')
        collection = kwargs.get('collection', self.collection)
        pagination = kwargs.get('pagination', {})

        collection = collection or self.collection
        agg_clause = [{'$lookup': {
            'from': foreign_collection,
            'localField': local_field,
            'foreignField': foreign_field,
            'as': records_as
        }}]
        if filter_:
            agg_clause.append({"$match": filter_})
        # if search:
        #     agg_clause.append({"$search": search})
        if projection:
            agg_clause.append(projection)
        if pagination:
            page, size = pagination['page'], pagination['size']
            skip = size*(page-1)
            limit = size
            agg_clause.append({'$skip': skip})
            agg_clause.append({'$limit': limit})

        records = self.db[collection].aggregate(agg_clause)
        output = {'data': records}

        if pagination:
            total_records = self.db[collection].count_documents(filter_)
            pagination_content = {'page': page,
                                  'size': size,
                                  'totalRecords': total_records}
            output['pagination'] = pagination_content
        output['status'] = Status.SUCCESS.value
        return output
