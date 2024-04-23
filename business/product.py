

from datetime import datetime

from bson import ObjectId
from utility import (MongoDBSerializer,
                     Status,
                     DateStringFormat,
                     DAL,
                     Logger, PaginationSetting)


DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10

LOGGER = Logger('PRODUCT_BUSINESS')


class ProductBusiness:
    def __init__(self, collection: str = 'products') -> None:
        self.dal = DAL(collection)
        self.serializer = MongoDBSerializer()

    def get_products(self, page=PaginationSetting.DEFAULT_PAGE_NUMBER, size=PaginationSetting.DEFAULT_PAGE_SIZE, search_keyword: str = None):
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

            pagination = {'page': page, 'size': size}
            db_result = self.dal.find_documents(filter_, pagination=pagination)

            products = db_result.get('data')
            products = self.serializer.serialize(products)

            result = {'status': Status.SUCCESS,
                      'data': products,
                      'pagination': db_result.get('pagination')}

        except Exception as ex:
            result['status'] = Status.ERROR.value
            LOGGER.error(ex)
        finally:
            return result

    def add_product(self, name: str, description: str, mrp: float, sale_price: float, is_available: bool = True):
        result = {'status': Status.UNKNOWN, 'data': None}

        currentTime = datetime.utcnow().strftime(DateStringFormat.ISO_FORMAT.value)

        payload = {
            'name': name,
            'description': description,
            'mrp': mrp,
            'sale_price': sale_price,
            'is_available': is_available,
            'added_on': currentTime
        }

        db_result = self.dal.insert_document(payload)

        if db_result and db_result.acknowledged:
            payload['_id'] = str(payload.get('_id'))
            result['data'] = payload
            result['status'] = Status.SUCCESS

        return result
    
    def modify_product(self, id:str, data: dict):
        result = {'status': Status.UNKNOWN, 'data': None}
        try:
            product_id = ObjectId(id)
            filter_ = {'_id': product_id}
            
            data['modified_on'] = datetime.utcnow().strftime(DateStringFormat.ISO_FORMAT.value)
        
            is_modified = self.dal.modify_document(filter_, data)

            if is_modified:
                result['status'] = Status.SUCCESS
                result['message'] = 'Modified Successfully'
        except Exception as e:
            LOGGER.error(e)
            result['status'] = Status.ERROR
            
        return result

    def delete_product(self, id):
        result = {'status': Status.UNKNOWN, 'data': None}

        product_id = ObjectId(id)
        filter_ = {'_id': product_id}
        
        deleted_count = self.dal.delete_document(filter_)
        if deleted_count:
            result['status'] = Status.SUCCESS
            result['message'] = f'{deleted_count} product was removed.'
        else:
            result['status'] = Status.NOT_FOUND
            result['message'] = 'No product was removed.'
        
        return result