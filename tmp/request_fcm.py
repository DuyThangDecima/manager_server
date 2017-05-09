import json
import requests

url = 'https://fcm.googleapis.com/fcm/send'
body = {
    "data": {
        "title": "mytitle",
        "body": "mybody",
        "url": "myurl"
    },
    "notification": {
        "title": "My web app name",
        "body": "message",
        "content_available": "true"
    },
    "to": "dMk0xvnh4Sk:APA91bGTy0K5iLQHIYlx7ZPLFkm_V666zZgxgZ4F5BLTYaHJRwP2ylYpyvDMvib5wur5_wgf6c-MB0JrLOBdAV8TJI4juLxBTDKbegFS_c30gF42Dvo5GH2FGjmjk9qtITlhnKh0bMld"
}

headers = {"Content-Type": "application/json",
           "Authorization": "key=AAAASFQ5kDw:APA91bFGQfPNqLwawR5AvI1_90QOEX1tFNntbI7AU8TkXL8cG5ybAWnLO-xXV03nzcC6hAhAPjKkp_05Pmc8cDB_m6Uy1Wy5_-jqKQbQODDQxhse02QBysAxPzGRFCIzE88ldnNLuK9K"}
respond = requests.post(url, data=json.dumps(body), headers=headers)
print respond
