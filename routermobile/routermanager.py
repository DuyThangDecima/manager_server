#!/usr/bin/env python
# -*- coding: utf-8 -*-
from api.restful_api_mobile import AuthenticationApi
from api.restful_api_mobile import ParentAccountApi
from api.restful_api_mobile import ChildAccountApi
from api.restful_api_mobile import SmsApi
from api.restful_api_mobile import ContactApi
from api.restful_api_mobile import AudioDownload
from api.restful_api_mobile import VideoDownload
from api.restful_api_mobile import ImageDownload
from api.restful_api_mobile import CallLogDownloader
from api.restful_api_mobile import SmsDownloader
from api.restful_api_mobile import AudioNeedDownload
from api.restful_api_mobile import VideoListApi
from api.restful_api_mobile import AppApi
from api.restful_api_mobile import ImageApi
from api.restful_api_mobile import ImageListApi
from api.restful_api_mobile import TokenFcmApi
from api.restful_api_mobile import RuleParentApi
from api.restful_api_mobile import ImageNeedDownload
from api.restful_api_mobile import AudioListApi
from api.restful_api_mobile import VideoApi
from api.restful_api_mobile import AudioApi
from api.restful_api_mobile import VersionApi
from api.restful_api_mobile import VideoNeedDownload
from api.restful_api_mobile import CallLogApi
import config


def add_resources(api_flask):
    """
    Đăng ký tất cả api cho mobile
    :param api_flask:
    :return:
    """
    api_version1 = config.API_VERSION

    api_flask.add_resource(AuthenticationApi, api_version1 + '/authentication')

    # Parent
    api_flask.add_resource(ParentAccountApi, api_version1 + '/parent')
    # Child
    api_flask.add_resource(ChildAccountApi, api_version1 + '/child')
    # Sms
    api_flask.add_resource(SmsApi, api_version1 + '/sms')
    # contact
    api_flask.add_resource(ContactApi, api_version1 + '/contact')
    # Sms
    api_flask.add_resource(VersionApi, api_version1 + '/version')
    # Calllog
    api_flask.add_resource(CallLogApi, api_version1 + '/calllog')
    # Calllog
    api_flask.add_resource(AppApi, api_version1 + '/app')

    # Image
    api_flask.add_resource(ImageApi, api_version1 + '/image/<file_id>')
    api_flask.add_resource(ImageListApi, api_version1 + '/image')

    # Video
    api_flask.add_resource(VideoApi, api_version1 + '/video/<file_id>')
    api_flask.add_resource(VideoListApi, api_version1 + '/video')

    # Image
    api_flask.add_resource(AudioApi, api_version1 + '/audio/<file_id>')
    api_flask.add_resource(AudioListApi, api_version1 + '/audio')

    # Token fcm
    api_flask.add_resource(TokenFcmApi, api_version1 + '/token_fcm')
    api_flask.add_resource(RuleParentApi, api_version1 + '/rule_parent')

    api_flask.add_resource(ImageNeedDownload, api_version1 + '/get_files_need_download/image')
    api_flask.add_resource(AudioNeedDownload, api_version1 + '/get_files_need_download/audio')
    api_flask.add_resource(VideoNeedDownload, api_version1 + '/get_files_need_download/video')

    api_flask.add_resource(SmsDownloader, api_version1 + '/download/sms')
    api_flask.add_resource(CallLogDownloader, api_version1 + '/download/calllog')

    api_flask.add_resource(ImageDownload, api_version1 + '/download/image')
    api_flask.add_resource(VideoDownload, api_version1 + '/download/video')
    api_flask.add_resource(AudioDownload, api_version1 + '/download/audio')
