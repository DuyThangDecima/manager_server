#!/usr/bin/env python
# -*- coding: utf-8 -*-
from api import authentication
from flask_restful import Resource,Api

def add_resources(api_flask):
    """
    Đăng ký tất cả api cho mobile
    :param api_flask:
    :return:
    """
    api_flask.add_resource(authentication.AuthenticationApi, '/api/mobile/authentication')
    api_flask.add_resource(authentication.ParentAccountApi, '/api/mobile/parentregister')
    api_flask.add_resource(authentication.ChildAccountApi, '/api/mobile/addchild')
