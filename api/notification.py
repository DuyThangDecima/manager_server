# -*- coding: utf-8 -*-

from flask import jsonify

PARAMS = {
    "token": "token",
    "token_fcm": "token_fcm",
    "device_name": "device_name",
    "imei": "imei",
    "email": "email",
    "password": "password",
    "version": "version",
    "data": "data",
    "status_login": "status_login",  # 0 nếu không ở trạng thái đăng nhập, 1 nếu ở trạng thái đăng nhập
    "type_version": "type_version",
    "privilege": "privilege",
    "child_id": "child_id",
    "device_id": "device_id",
    "file_name": "file_name",
    "file_id": "file_id",
    "json_data": "json_data",
    "request_type": "request_type",
    "lat_location": "lat_location",
    "long_location": "long_location",

}

ACTION = {
    "add": "add",
    "delete": "delete",
    "update": "update",
    "action": "action"
}

FCM_TYPE = {
    "request_location": "request_location",
    "respond_location": "respond_location",
    "request_upload": "request_upload",
    "request_update_rule_parent":"request_update_rule_parent"
}

# msg="error_0": Tương tác với db lỗi

# CÁC TÁC VỤ VỚI DB
# example:
#   msg="success_1" : Insert db successful
ACTION_DB = {
    "insert_success": "success_11",
    "get_success": "success_12",
    "delete_success": "success_13",
    "update_success": "success_14",

    "insert_error": "error_11",
    "get_error": "error_12",
    "delete_error": "error_13",
    "update_error": "error_14",
}

STATUS_DB = {
    "uptodate": "status_1",
}

"""
Các nguyên nhân lỗi
1. Lỗi server: do thực hiện db
2. Lỗi server: logic của server
3. Lỗi server: không xác định
4. Lỗi đăng nhập: Đăng nhập thất bại

FORMAT GÓI TIN NOTIFICATION
1. FORMAT SUCCESS
{"status": "1", msg= ""}

2. FORMAT ERROR
    {"status": "0", msg= ""}
    msg: nguyên nhân lỗi
    error_1: thực thi db lỗi
    error_2: Lỗi authen

    error_3: Đã tồn tại (muốn thêm nhưng tồn tại ex: đăng ký tài khoản)
    error_4: Db đã mới nhất (request update db nhưng db đã ở bản mới nhất)

"""

ERROR = {
    "db_action": "error_1",
    "auth": "error_2",
    "exist": "error_3",
    "up_to_date": "error_4",
}
STATUS = {
    "status_success": "1",
    "status_error": "0",
}

PRIVILEGE_TYPE = {
    "parent": 1,
    "child": 0,
    "unknown": -1
}

LOGIN_STATUS = {
    "login": 1,
    "logout": 0,
}

WHO_REQUEST = {
    "parent": "parent",
    "child": "child"
}


def notify_error_db():
    """
    Bất cứ các hành động liên quan đến db mà lỗi,
    Là trả về lỗi và kết thúc tác vụ
    :return:
    """
    return jsonify(status=STATUS["status_error"], msg=ERROR["db_action"])


def notify_error_auth():
    """
    Khi kiểm tra token và hiện tại chưa được đăng nhập
    :return:
    """
    return jsonify(status=STATUS["status_error"], msg=ERROR["auth"])


def notify_error_uptodate():
    """
    :return:
    """
    return jsonify(status=STATUS["status_error"], msg=ERROR["up_to_date"])


def notify_error_exist():
    """
    :return:
    """
    return jsonify(status=STATUS["status_error"], msg=ERROR["exist"])


def notify_insert_successfully():
    """
    :return:
    """
    return jsonify(status=STATUS["status_success"], msg=ACTION_DB["insert_success"])


def notify_update_successfully():
    """
    :return:
    """
    return jsonify(status=STATUS["status_success"], msg=ACTION_DB["update_success"])


def notify_status_success():
    """
    :return:
    """
    return jsonify(status=STATUS["status_success"])
