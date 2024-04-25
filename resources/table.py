from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from business import TableBusiness
from utility import make_response, Logger, Status

ALLOWED_STATUES = {'AVAILABLE', 'OCCUPIED',
                   'RESERVED', 'OUT_OF_SERVICE', 'ON_HOLD'}


class TableManagement(Resource):
    def __init__(self):
        self.business = TableBusiness()

    # @jwt_required
    def get(self):
        result = self.business.get_tables()
        if result['status'] == Status.SUCCESS:
            return make_response(200, data=result.get('data'))
        else:
            return make_response(500, message=result.get('message'), errors=result.get('errors'))

    # @jwt_required

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('table_number', type=str, required=True,
                            help="this field cannot be blank.")
        parser.add_argument('capacity', type=int, required=True,
                            help="this field cannot be blank.")
        parser.add_argument('status', choices=ALLOWED_STATUES,
                            help='Bad choice: {error_msg}'
                            )

        data = parser.parse_args()
        result = self.business.add_table(**data)
        if result['status'] == Status.SUCCESS:
            return make_response(200, data=result.get('data'))
        else:
            return make_response(500, message=result.get('message'), errors=result.get('errors'))

    def patch(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('table_number', type=str,
                            help="this field cannot be blank.")
        parser.add_argument('capacity', type=int,
                            help="this field cannot be blank.")
        parser.add_argument('status', choices=ALLOWED_STATUES,
                            help='Bad choice: {error_msg}'
                            )

        data = parser.parse_args()

        data = {field: value for field,
                value in data.items() if value is not None}

        result = self.business.modify_product(id, data)
        if result['status'] == Status.SUCCESS:
            return make_response(200, message=result.get('message'))
        elif result['status'] == Status.NOT_FOUND:
            return make_response(404, message=result.get('message'))
        else:
            return make_response(500, message=result.get('message'))
