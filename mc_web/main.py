#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api import api_mobile
from db.db import DbMongo
from flask import Flask
from flask_restful import Api
from router import home, dashboard
from routermobile import routermanager

# Khởi tạo db
DbMongo().init_db()

# Khởi tạo app
app = Flask(__name__)
api = Api(app)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

app.debug = True

# Đăng ký các url
home.register_urls(app)
dashboard.register_urls(app)

# Đăng ký api
api_mobile.register_urls(app)
routermanager.add_resources(api)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
