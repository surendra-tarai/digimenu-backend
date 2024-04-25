

from datetime import datetime, timezone

from bson import ObjectId
from utility import (MongoDBSerializer,
                     Status,
                     DateStringFormat,
                     DAL,
                     Logger, PaginationSetting)


DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10

LOGGER = Logger('ITEM_BUSINESS')


class ItemBusiness:
    def __init__(self) -> None:
        self.dal = DAL('menu_items')
        self.serializer = MongoDBSerializer()

    def get_items(self, page=PaginationSetting.DEFAULT_PAGE_NUMBER, size=PaginationSetting.DEFAULT_PAGE_SIZE, search_keyword: str = None):
        result = {'status': Status.UNKNOWN, 'data': []}
        try:

            filter_ = {}
            if search_keyword:
                filter_ = {
                    '$or': [
                        {'name': {'$regex': search_keyword, '$options': 'i'}},
                        {'description': {'$regex': search_keyword, '$options': 'i'}}
                    ]
                }

            fields = {'_id', 'name', 'description', 'is_available', 'price', 'sale_price'}
            pagination = {'page': page, 'size': size}
            db_result = self.dal.find_documents(filter_, fields=fields, pagination=pagination)

            items = db_result.get('data')
            items = self.serializer.serialize(items)

            result = {'status': Status.SUCCESS,
                      'data': items,
                      'pagination': db_result.get('pagination')}

        except Exception as ex:
            result['status'] = Status.ERROR.value
            LOGGER.error(ex)
        finally:
            return result

    def add_item(self, name: str, description: str, price: float, sale_price: float, is_available: bool = True):
        result = {'status': Status.UNKNOWN, 'data': None}

        current_time = datetime.now(timezone.utc)

        payload = {
            'name': name,
            'description': description,
            'price': price,
            'sale_price': sale_price,
            'is_available': is_available,
            'added_on': current_time
        }

        db_result = self.dal.insert_document(payload)

        if db_result and db_result.acknowledged:
            payload['_id'] = str(payload.get('_id'))
            result['data']  = self.serializer.serialize(payload)
            result['status'] = Status.SUCCESS

        return result
    
    def modify_item(self, id:str, data: dict):
        result = {'status': Status.UNKNOWN, 'data': None}
        try:
            item_id = ObjectId(id)
            filter_ = {'_id': item_id}
            
            data['modified_on'] = datetime.now(timezone.utc)#.strftime(DateStringFormat.ISO_FORMAT.value)
        
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

    def delete_item(self, id):
        result = {'status': Status.UNKNOWN, 'data': None}

        item_id = ObjectId(id)
        filter_ = {'_id': item_id}
        
        deleted_count = self.dal.delete_document(filter_)
        if deleted_count:
            result['status'] = Status.SUCCESS
            result['message'] = f'{deleted_count} item was removed.'
        else:
            result['status'] = Status.NOT_FOUND
            result['message'] = 'No item was removed.'
        
        return result