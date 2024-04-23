'''
    User role module is used for all user and role related jobs
    like fetching user details, role details, checking permissions, etc.
'''
from flask import request
from utility import DAL, Logger
from bson.objectid import ObjectId
# from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import Schema, fields, validate, ValidationError
from bson.json_util import dumps
from utility import MongoDBSerializer
from utility.constant import Status
LOGGER = Logger('USER_ROLE')


class UserSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1), required=True, error_messages={
                      'validate': 'v error', 'required': 'name is required'})
    mobile = fields.Str(validate=validate.Length(min=10, max=10), error_messages={
        'validate': 'invalid mobile number', })
    email = fields.Float(required=True, error_messages={
        'validate': 'v error', 'required': 'email is required'})
    password = fields.Float(required=True, error_messages={
        'validate': 'v error', 'required': 'password is required'})

    class Meta:
        pass
        # unknown = EXCLUDE


class UserBusiness:
    def __init__(self, collection: str = None) -> None:
        self.dal = DAL(collection)
        self.serializer = MongoDBSerializer()

    def get_admin_user_details_by_login_id(self, login_id):
        '''
            Get user details of given login id

            Parameters:
            login_id (str): login id
            Returns:
            dict: user details
        '''
        try:
            _filter = {'loginid': login_id}
            user_details = self.dal.find_one_document(_filter, collection='admin_users')
            return user_details
        except Exception as ex:
            LOGGER.critical('user details could not fetched by loginId', ex)
            
    def get_customer_user_by_mobile(self, mobile:str):
        '''
            Get user details of given login id

            Parameters:
            mobile (str): 10 digit mobile number
            Returns:
            dict: user details
        '''
        try:
            _filter = {'mobile': mobile}
            user_details = self.dal.find_one_document(_filter, collection='customers')
            return user_details
        except Exception as ex:
            LOGGER.critical('user details could not fetched by loginId', ex)

    @staticmethod
    def get_user_claims(user_details: dict):
        claims = {}
        try:
            if user_details:
                claims['_id'] = user_details.get('_id')
                claims['name'] = user_details.get('name')
                if loginid:=user_details.get('loginid'):
                    claims['loginid'] = loginid
                if mobile:=user_details.get('mobile'):
                    claims['mobile'] = mobile
                    
        except Exception as ex:
            LOGGER.exception(ex)
        finally:
            return claims

    def register_customer_user(self, data: dict):
        try:
            result = {'status': Status.UNKNOWN}
            db_result = self.dal.insert_document(data)
            if db_result and db_result.acknowledged:
                data = self.serializer.serialize(data)
                result = {'status': Status.SUCCESS, 'data': data}
            else:
                result['status'] = Status.ERROR
        except Exception as ex:
            LOGGER.exception(ex)
            result['status'] = Status.ERROR
        finally:
            return result

    def update_photo_path(self, user_id: str, photo_path: str):
        result = {'status': Status.UNKNOWN}
        try:
            filter_ = {'_id': ObjectId(user_id)}
            new_value = {"$set": {'photoUrl': photo_path}}
            db_result = self.dal.update_document(filter_, new_value)
            if db_result:
                result['status'] = Status.SUCCESS
        except Exception as e:
            result['status'] = Status.ERROR
            result['message'] = str(e)

        return result

    def get_users(self):
        result = self.dal.find_documents()
        if users := result.get('data'):
            users = self.serializer.serialize(users)
            return self.__post_processing(users)

    def __post_processing(self, users: list):
        for i, user in enumerate(users):
            if photoUrl := user.get('photoUrl'):
                user['photoUrl'] = f'{request.root_url}{photoUrl}'
                users[i] = user

        return users

    def get_user(self, id):
        result = {'status': Status.UNKNOWN}
        user = self.dal.find_doc_by_id(id)
        if user:
            result['status'] = Status.SUCCESS
            result['data'] = self.serializer.serialize(user)
        else:
            result['status'] = Status.NOT_FOUND
            result['message'] = 'User not found of given user id'

        return result