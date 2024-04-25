import os
from dotenv import load_dotenv
load_dotenv(override=True)
from flask import Flask, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
# resources
from resources import (AdminUserLogin,
                       ItemManagement,
                       TokenRefresh,
                       TableManagement, 
                       MenuManagement,
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
api.add_resource(ItemManagement, '/admin/items', '/admin/items/<id>')

# table management
api.add_resource(TableManagement, '/admin/tables', '/admin/tables/<id>')

# menu management
api.add_resource(MenuManagement, '/admin/menus', '/admin/menus/<id>')

@app.route("/assets/<path:path>")
def static_dir(path):
    return send_from_directory("assets", path)

if __name__ == '__main__':
    app.run(debug=True)