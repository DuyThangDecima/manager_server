# -.- coding:utf-8 -.-
__author__ = 'ThangLD'

import model_db


class AccountModel(model_db.ModelDb):
    """
    Cấu trúc của collections
    {
        "profiles": {
            "parent": {
                "profile_id": int,
                "username": "",
                "password": "",
                "full_name": ""
            },
            "child": [
                {
                    "profile_id": int,
                    "birth": int,
                    "full_name": ""
                }
            ]
        },
        "devices": [
            {
                "infor": {"imei": "", "device_name": ""},
                "token": "",
                "privilege": "",
                "profile_id":""
            }
        ]
    }
    """

    COLLECTION_NAME = "account"
    # Lưu danh profile parent và các con
    PROFILES = 'profiles'
    PROFILE_ID = 'profile_id'
    # parent
    PARENT = 'parent'
    EMAIL = "email"
    PASSWORD = "password"
    FULL_NAME = "full_name"
    # child
    CHILD = 'child'
    BIRTH = 'birth'

    # Danh sách các thiết bị đăng nhập
    DEVICES = "devices"
    INFOR = "infor"
    IMEI = "imei"
    DEVICE_NAME = "device_name"
    # quyền của thiết bị trên máy
    PRIVILEGE = "privilege"

    TOKEN = 'token'

    PRIVILEGE_UNKNOWN = -1;
    PRIVILEGE_PARENT = 0;
    PRIVILEGE_CHILD = 1;

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        model_db.ModelDb.__init__(self, db, collection)

    def login(self, username, password):
        """
        Authenticate login
        :return:
        True,_id neu co tai khoan
        False,Exception neu khong co tai khoang
        """
        status, value = self.find_one(
            spec={
                self.USERNAME: username, self.PASSWORD: password
            },
            fields={self._ID: 1}
        )

        print value
        if status and value is not None:
            if len(value) > 0:
                return True, str(value[self._ID])
        return False, value
