from flask_restful import Resource

class Ping(Resource):
    def get(self):
        return {'message': 'API is running...'}
