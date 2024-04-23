from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse
from business import ProductBusiness
from utility import make_response, Logger, Status
from utility.constant import PaginationSetting


class AdminProducts(Resource):
    def __init__(self):
        self.business = ProductBusiness()

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q', location='args')
        parser.add_argument('page', type=int, location='args',
                            help="It should be a valid positive number.")
        parser.add_argument('pageSize', type=int, location='args',
                            help="It should be a valid positive number.")

        args = parser.parse_args()
        page_number = args.get('page')
        if not isinstance(page_number, int):
            if isinstance(page_number, str) and page_number.isdigit():
                page_number = int(page_number)
            else:
                page_number = PaginationSetting.DEFAULT_PAGE_NUMBER.value
        page_size = args.get('pageSize')
        if not isinstance(page_size, int):
            if isinstance(page_size, str) and page_size.isdigit():
                page_size = int(page_size)
            else:
                page_size = PaginationSetting.DEFAULT_PAGE_SIZE.value
        search_text = args.get('q')

        result = self.business.get_products(page=page_number,
                                            size=page_size,
                                            search_keyword=search_text)

        if result['status'] == Status.SUCCESS:
            return make_response(200, data=result.get('data'), pagination=result.get('pagination'))
        else:
            return make_response(500, message=result.get('message'), errors=result.get('errors'))

        return {"data": products}

    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help="this field cannot be blank.")
        parser.add_argument('description', type=str)
        parser.add_argument('mrp', type=float, required=True)
        parser.add_argument('sale_price', type=float, required=True)

        data = parser.parse_args()

        name = data.get('name')
        description = data.get('description')
        mrp = data.get('mrp')
        sale_price = data.get('sale_price')
        is_available = str(data.get('is_available', 1)) in (
            'true', 'True', 1, 'yes')
        result = self.business.add_product(
            name, description, mrp, sale_price, is_available=is_available)
        if result['status'] == Status.SUCCESS:
            return make_response(201, data=result.get('data'))
        else:
            return make_response(500, message=result.get('message'))

    @jwt_required()
    def patch(self, id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location=['json', 'form'])
        parser.add_argument('description', type=str, location=['json', 'form'])
        parser.add_argument('mrp', type=float, location=['json', 'form'],)
        parser.add_argument('sale_price', type=float,
                            location=['json', 'form'])
        parser.add_argument('is_available', type=bool,
                            location=['json', 'form'])

        data = parser.parse_args()
        
        data = {field: value for field, value in data.items() if value is not None}
        
        if 'is_available' in data:
            data['is_available'] = data['is_available'] in ('true', 'True', 1, 'yes')
            
        result = self.business.modify_product(id, data)
        if result['status'] == Status.SUCCESS:
            return make_response(200, message=result.get('message'))
        else:
            return make_response(500, message=result.get('message'))

    @jwt_required()
    def delete(self, id):
        result = self.business.delete_product(id)
        if result['status'] == Status.SUCCESS:
            return make_response(204, message=result.get('message'))
        elif result['status'] == Status.NOT_FOUND:
            return make_response(404, message=result.get('message'))
        else:
            return make_response(500, message=result.get('message'))
