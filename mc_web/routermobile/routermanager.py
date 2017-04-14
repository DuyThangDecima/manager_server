#!/usr/bin/env python
# -*- coding: utf-8 -*-
from api import restful_api_mobile


def add_resources(api_flask):
    """
    Đăng ký tất cả api cho mobile
    :param api_flask:
    :return:
    """
    api_version1 = "/api/v1"

    api_flask.add_resource(restful_api_mobile.AuthenticationApi, api_version1 + '/authentication')

    # Parent
    api_flask.add_resource(restful_api_mobile.ParentAccountApi, api_version1 + '/parent')
    # Child
    api_flask.add_resource(restful_api_mobile.ChildAccountApi, api_version1 + '/child')
    # Sms
    api_flask.add_resource(restful_api_mobile.SmsApi, api_version1 + '/sms')
