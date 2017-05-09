import json
import requests

import config
from bson import ObjectId
from notification import *


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class FCMRequest():
    def send_request_location(self, to, device_id):
        url = 'https://fcm.googleapis.com/fcm/send'
        body = {
            "data": {
                "type_request": FCM_TYPE["request_location"],
                "device_id": device_id
            },
            "to": to
        }

        headers = {"Content-Type": "application/json",
                   "Authorization": "key=" + config.KEY_FCM_SERVER}
        respond = requests.post(url, data=json.dumps(body), headers=headers)
        return respond;

    def send_respond_location(self, to, lat_location, long_location):
        url = 'https://fcm.googleapis.com/fcm/send'
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
        respond = requests.post(url, data=json.dumps(body), headers=headers)
        return respond;
