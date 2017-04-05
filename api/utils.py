# -*- coding: utf-8 -*-
import datetime
import hashlib
import random
import string

from model.account_model import AccountModel


def generate_token():
    """
    Tạo session cho
    :return:
    """
    time_now = str(datetime.datetime.now())
    chars = string.ascii_letters + string.digits
    size = 1000
    content_random = time_now.join(random.choice(chars) for _ in range(size))

    m = hashlib.md5()
    m.update(content_random)
    return m.hexdigest()


def auth_device(model_account, token, imei, device_name):
    """
    Kiểm tra thiết bị này đã đăng nhập trước đó hay chưa
    :param model_account: @link model.accountmodel.AccountModel
    :param token:
    :param imei:
    :param device_name:
    :return:
    """
    # Tìm trong db
    status, value = model_account.find_one(
        spec={
            AccountModel.DEVICES + "." + AccountModel.INFOR + "." + AccountModel.IMEI: imei,
            AccountModel.DEVICES + "." + AccountModel.INFOR + "." + AccountModel.DEVICE_NAME: device_name,
            AccountModel.DEVICES + "." + AccountModel.TOKEN: token,
        })
    if status:
        if value is not None and len(value) > 0:
            # Nếu email đã tồn tại
            return True, value
        else:
            return False, None
    else:  # Đã có lỗi xảy ra
        return False, None

