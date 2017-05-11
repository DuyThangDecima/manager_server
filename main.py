#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.restful_api_mobile import *
from flask import Flask
from flask_restful import Api
from router import home, dashboard
from db.db import *

# Khởi tạo db
from routermobile import routermanager
from api.googlecloudstore import *
#DbMongo().init_db()

# Khởi tạo app
app = Flask(__name__)
api = Api(app)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']
# [end config]


# connect to another MongoDB server altogether
# app.config['MC_HOST'] = config.DB_IP["ip"]
# app.config['MC_PORT'] = config.DB_IP["port"]
# app.config['MC_DBNAME'] = config.DB_NAME;
# mongo3 = PyMongo(app, config_prefix='MC_DB')

app.debug = True

# Đăng ký các url
home.register_urls(app)
dashboard.register_urls(app)
register_extra(app)
# Đăng ký api
# api_mobile.register_urls(app)

routermanager.add_resources(api)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
