from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from business import MenuBusiness
from utility import make_response, Logger, Status



class MenuManagement(Resource):
    def __init__(self):
        self.business = MenuBusiness()
        
    def get(self, id=None):
        if id is None:
            return [] # list of menus
        
        result = self.business.get_menu_details(id)

        if result['status'] == Status.SUCCESS:
            return make_response(200, data=result.get('data'))
        else:
            return make_response(500, message=result.get('message'), errors=result.get('errors'))