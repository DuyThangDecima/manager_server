# -*- coding: utf-8 -*-

import json

import logging
from google.appengine.api import urlfetch

# import requests

import config
from bson import ObjectId
from notification import *


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


# START SEND_POST_SSL
def send_post_ssl(url, method, headers, content):
    try:
        result = urlfetch.fetch(
            url=url,
            method=method,
            payload=content,
            headers=headers,
            validate_certificate=True
        )
        return result
    except urlfetch.Error as e:
        logging.exception('Caught exception fetching url')
        return e.message


# END SEND_POST_SSL

class FCMRequest():
    def send_request_location(self, to, device_id):
        url_fcm_send = 'https://fcm.googleapis.com/fcm/send'
        body = {
            "data": {
                "type_request": FCM_TYPE["request_location"],
                "device_id": device_id
            },
            "to": to
        }

        headers = {"Content-Type": "application/json",
                   "Authorization": "key=" + config.KEY_FCM_SERVER}
        # GOOGLE_APP_ENGINE: Dùng send_post_ssl để thay request.post
        respond = send_post_ssl(url_fcm_send, urlfetch.POST, headers, json.dumps(body))
        # respond = requests.post(url, data=json.dumps(body), headers=headers)
        return respond;

    def send_respond_location(self, to, lat_location, long_location):
        url_fcm_send = 'https://fcm.googleapis.com/fcm/send'
        body = {
            "data": {
                "type_request": FCM_TYPE["respond_location"],
                PARAMS["lat_location"]: lat_location,
                PARAMS["long_location"]: long_location,
            },
            "to": to
        }

        headers = {"Content-Type": "application/json",
                   "Authorization": "key=" + config.KEY_FCM_SERVER}

        # GOOGLE_APP_ENGINE: Dùng send_post_ssl để thay request.post
        respond = send_post_ssl(url_fcm_send, urlfetch.POST, headers, json.dumps(body))
        # respond = requests.post(url, data=json.dumps(body), headers=headers)
        return respond;

    def send_request_download_rule_parent(self, to):
        print "send_request_download_rule_parent to " + to
        url_fcm_send = 'https://fcm.googleapis.com/fcm/send'
        body = {
            "data": {
                "type_request": FCM_TYPE["request_update_rule_parent"],
            },
            "to": to
        }

        headers = {"Content-Type": "application/json",
                   "Authorization": "key=" + config.KEY_FCM_SERVER}
        # GOOGLE_APP_ENGINE: Dùng send_post_ssl để thay request.post
        respond = send_post_ssl(url_fcm_send, urlfetch.POST, headers, json.dumps(body))
        # respond = requests.post(url, data=json.dumps(body), headers=headers)
        return respond;