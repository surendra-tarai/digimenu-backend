import os
from flask import Flask, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
# resources
from resources import (AdminUserLogin,
                       AdminProducts,
                       TokenRefresh, 
                       Ping)

app = Flask(__name__)
app.config['BUNDLE_ERRORS'] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=4)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config['USER_PHOTO_FOLDER'] = 'files/user-photos'
app.secret_key = '<secret_key>'

# CORS(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)
jwt = JWTManager(app)

api.add_resource(Ping, '/ping')
api.add_resource(AdminUserLogin, '/admin/login')
api.add_resource(TokenRefresh, '/user/refresh')
api.add_resource(AdminProducts, '/admin/products', '/admin/products/<id>')

@app.route("/assets/<path:path>")
def static_dir(path):
    return send_from_directory("assets", path)


if __name__ == '__main__':
    app.run(debug=True)
    # port = int(os.environ.get("PORT", 5000))
    # app.run(debug=True, host='0.0.0.0', port=5000)
    # app.run(host='192.168.56.103', port=5000)
    # app.run(debug=True, host='192.168.29.154', port=5000)
    # app.run(debug=True, port=5000, host='0.0.0.0')