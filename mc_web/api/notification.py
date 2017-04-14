# -*- coding: utf-8 -*-



PARAMS = {
    "token": "token",
    "device_name": "device_name",
    "imei": "imei",
    "email": "email",
    "password": "password",
    "version": "version",
    "data": "data",
    "status_login": "status_login",  # 0 nếu không ở trạng thái đăng nhập, 1 nếu ở trạng thái đăng nhập

}

# "msg":"error_0": Tương tác với db lỗi

# CÁC TÁC VỤ VỚI DB
# example:
#   "msg":"success_1" : Insert db successful
ACTION_DB = {
    "insert_success": "success_1",
    "get_success-": "success_2",
    "delete_success": "success_3",
    "update": "success_4",

    "action_error": "error_0",  # Khong xac dinh, cu co loi db la tra ve loi nay
    "insert_error": "error_1",
    "get_error": "error_2",
    "delete_error": "error_3",
    "update_error": "error_4",
}

STATUS_DB = {
    "uptodate": "status_1",
}


def notify_db_error():
    """
    Bất cứ các hành động liên quan đến db mà lỗi,
    Là trả về lỗi và kết thúc tác vụ
    :return:
    """
    return {"status": "0", "msg": ACTION_DB["action_error"]}


def notify_insert_successfully():
    """
    Bất cứ các hành động liên quan đến db mà lỗi,
    Là trả về lỗi và kết thúc tác vụ
    :return:
    """
    return {"status": "1", "msg": ACTION_DB["insert_success"]}


def notify_db_uptodate():
    """
    Bất cứ các hành động liên quan đến db mà lỗi,
    Là trả về lỗi và kết thúc tác vụ
    :return:
    """
    return {"status": "0", "msg": STATUS_DB["uptodate"]}


def notify_status_login_false():
    """
    Khi kiểm tra token và hiện tại chưa được đăng nhập
    :return:
    """
    return {"status": "0", PARAMS["status_login"]: "0"}
