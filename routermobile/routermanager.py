#!/usr/bin/env python
# -*- coding: utf-8 -*-
from api import restful_api_mobile
import config

def add_resources(api_flask):
    """
    Đăng ký tất cả api cho mobile
    :param api_flask:
    :return:
    """
    api_version1 = config.API_VERSION

    api_flask.add_resource(restful_api_mobile.AuthenticationApi, api_version1 + '/authentication')

    # Parent
    api_flask.add_resource(restful_api_mobile.ParentAccountApi, api_version1 + '/parent')
    # Child
    api_flask.add_resource(restful_api_mobile.ChildAccountApi, api_version1 + '/child')
    # Sms
    api_flask.add_resource(restful_api_mobile.SmsApi, api_version1 + '/sms')
    # contact
    api_flask.add_resource(restful_api_mobile.ContactApi, api_version1 + '/contact')
    # Sms
    api_flask.add_resource(restful_api_mobile.VersionApi, api_version1 + '/version')
    # Calllog
    api_flask.add_resource(restful_api_mobile.CallLogApi, api_version1 + '/calllog')
    # Calllog
    api_flask.add_resource(restful_api_mobile.AppApi, api_version1 + '/app')

    # Image
    api_flask.add_resource(restful_api_mobile.ImageApi, api_version1 + '/image/<file_id>')
    api_flask.add_resource(restful_api_mobile.ImageListApi, api_version1 + '/image')

    # Video
    api_flask.add_resource(restful_api_mobile.VideoApi, api_version1 + '/video/<file_id>')
    api_flask.add_resource(restful_api_mobile.VideoListApi, api_version1 + '/video')

    # Image
    api_flask.add_resource(restful_api_mobile.AudioApi, api_version1 + '/audio/<file_id>')
    api_flask.add_resource(restful_api_mobile.AudioListApi, api_version1 + '/audio')


    # Token fcm
    api_flask.add_resource(restful_api_mobile.TokenFcmApi, api_version1 + '/token_fcm')
    api_flask.add_resource(restful_api_mobile.RuleParentApi, api_version1 + '/rule_parent')

    api_flask.add_resource(restful_api_mobile.ImageNeedDownload, api_version1 + '/get_files_need_download/image')
    api_flask.add_resource(restful_api_mobile.AudioNeedDownload, api_version1 + '/get_files_need_download/audio')
    api_flask.add_resource(restful_api_mobile.VideoNeedDownload, api_version1 + '/get_files_need_download/video')

    api_flask.add_resource(restful_api_mobile.SmsDownloader, api_version1 + '/download/sms')
    api_flask.add_resource(restful_api_mobile.CallLogDownloader, api_version1 + '/download/calllog')


    api_flask.add_resource(restful_api_mobile.ImageDownload, api_version1 + '/download/image')
    api_flask.add_resource(restful_api_mobile.VideoDownload, api_version1 + '/download/video')
    api_flask.add_resource(restful_api_mobile.AudioDownload, api_version1 + '/download/audio')