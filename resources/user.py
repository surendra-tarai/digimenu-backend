'''
    User resource is used to manage all user related jobs
    such as User Login, refresh token, reset password, etc.
'''

from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required
)
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token)

from utility import make_response, Logger
from business import UserBusiness
from utility import UserStatus
from utility.constant import Status
from flask import request
from werkzeug.utils import secure_filename
import os

LOGGER = Logger('RESOURCE_USER')


class AdminUserLogin(Resource):
    def __init__(self) -> None:
        self.business = UserBusiness()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('loginid', type=str, required=True,
                            help="this field cannot be blank.")
        parser.add_argument('password', type=str, required=True,
                            help="this field cannot be blank.")

        data = parser.parse_args()
        login_id = data.get('loginid')
        user_details = self.business.get_admin_user_details_by_login_id(login_id)

        if user_details:
            if user_details.get('password') == data.get('password'):
                identity = str(user_details.get('id'))
                user_claims = self.business.get_user_claims(user_details)
                access_token = create_access_token(identity=identity,
                                                   fresh=True,
                                                   additional_claims=user_claims)

                refresh_token = create_refresh_token(identity)

                return make_response(200, 'Login successful', data={
                    "access_token": access_token,
                    "refresh_token": refresh_token
                })
            return make_response(400, 'Invalid credential')
        else:
            return make_response(400, 'Invalid user or user doesnt exit, contact admin.')
        
class CustomerUserLogin(Resource):
    def __init__(self) -> None:
        self.business = UserBusiness()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('mobile', type=str, required=True,
                            help="this field cannot be blank.")
        parser.add_argument('otp', type=str, required=True,
                            help="this field cannot be blank.")
        parser.add_argument('name', type=str)

        data = parser.parse_args()
        mobile = data.get('mobile')
        user_details = self.business.get_user_details_by_login_id(mobile)

        if user_details and user_details.get('status') == UserStatus.ACTIVE.value:
            if user_details.get('password') == data.get('password'):
                identity = str(user_details.get('id'))
                user_claims = self.business.get_user_claims(user_details)
                access_token = create_access_token(identity=identity,
                                                   fresh=True,
                                                   additional_claims=user_claims)

                refresh_token = create_refresh_token(identity)

                return make_response(200, 'Login successful', data={
                    "access-token": access_token,
                    "refresh-token": refresh_token
                })
            return make_response(400, 'Invalid credential')
        else:
            return make_response(400, 'Invalid user or user doesnt exit, contact admin.')


class TokenRefresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        user_details = self.business.get_user_details_by_id(identity)
        user_claims = self.business.get_user_claims(user_details)
        new_token = create_access_token(identity=identity,
                                        fresh=False,
                                        additional_claims=user_claims)

        return {'token': new_token}, 200

