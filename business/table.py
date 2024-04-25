
from datetime import datetime, timezone

from bson import ObjectId
from utility import (MongoDBSerializer,
                     Status,
                     DateStringFormat,
                     DAL,
                     Logger, PaginationSetting)

LOGGER = Logger('PRODUCT_BUSINESS')

class TableBusiness:
    def __init__(self) -> None:
        self.dal = DAL('tables')
        self.serializer = MongoDBSerializer()

    def get_tables(self):
        result = {'status': Status.UNKNOWN, 'data': None}
        try:
            db_result = self.dal.find_documents()
            tables = db_result.get('data')
            result['data'] = self.serializer.serialize(tables)
        except Exception as e:
            result['status'] = Status.ERROR
            LOGGER.error(e)
        else:
            result['status'] = Status.SUCCESS
            
        return result
    
    def add_table(self, table_number: str, capacity: int, status: str = 'available'):
        result = {'status': Status.UNKNOWN, 'data': None}
        try:
            payload = {
                'table_number': table_number,
                'capacity': capacity,
                'status': status
            }
            db_result = self.dal.insert_document(payload)
            if db_result and db_result.acknowledged:
                payload['_id'] = str(payload.get('_id'))
                result['data'] = payload
                result['status'] = Status.SUCCESS
        except Exception as e:
            result['status'] = Status.SUCCESS
            LOGGER.error(e)
            
        return result

    def modify_product(self, id:str, data: dict):
        result = {'status': Status.UNKNOWN, 'data': None}
        try:
            filter_ = {'_id': ObjectId(id)}
            modified_count = self.dal.modify_document(filter_, data)

            if modified_count:
                result['status'] = Status.SUCCESS
                result['message'] = 'Modified Successfully'
            else:
                result['status'] = Status.NOT_FOUND
                result['message'] = 'Could not change anything since the given id was not found.'
                
        except Exception as e:
            LOGGER.error(e)
            result['status'] = Status.ERROR
            
        return result