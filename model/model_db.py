# -*- coding: utf-8 -*-
import datetime
import hashlib
import random
import string


class ModelDb():
    # Chứa tên các column
    _ID = '_id'
    # Số lần thử
    MAX_RETRY = 2

    def __init__(self, db_mongo, collection_name):
        self.db = db_mongo
        self.collection_name = collection_name
        pass

    def find_one(self, **kwargs):
        """
        Tim trong db, neu co thi tra ve True, doc
        nguoc lai tra ve false, Exception
        :param kwargs:
        :return:
        """
        spec = kwargs.pop('spec', None)
        fields = kwargs.pop('fields', None)

        exception = None
        result = None
        for i in range(0, self.MAX_RETRY):
            exception = None
            try:
                result = self.db[self.collection_name].find_one(filter=spec, projection=fields)
                # result = self.db[self.collection_name].find()
                break
            except Exception as e:
                exception = e

        if exception:
            return False, exception
        return True, result

    def find(self, *args, **kwargs):
        for i in range(0, self.MAX_RETRY):
            exception = None
            try:
                result = self.db[self.collection_name].find(*args, **kwargs)
                # result = self.db[self.collection_name].find()
                break
            except Exception as e:
                exception = e
        if exception:
            return False, exception
        # result[0] = [true,false] ket qua cua update
        return True, result

    def update_one(self, filter, update, upsert=False,
                   bypass_document_validation=False,
                   collation=None):
        """
        THực hiện update_one
        :param filter:
        :param update:
        :param upsert:
        :param bypass_document_validation:
        :param collation:
        :return:
        """
        for i in range(0, self.MAX_RETRY):
            exception = None
            try:
                result = self.db[self.collection_name].update_one(filter, update, upsert,
                                                                  bypass_document_validation, collation)
                # result = self.db[self.collection_name].find()
                break
            except Exception as e:
                exception = e
        if exception:
            return False, exception
        # result[0] = [true,false] ket qua cua update
        return True, result

    def insert_one(self, document, bypass_document_validation=False):
        """
        Thực hiện insert_one
        :param document:
        :param bypass_document_validation:
        :return:
        """
        for i in range(0, self.MAX_RETRY):
            exception = None
            try:
                result = self.db[self.collection_name].insert_one(document, bypass_document_validation)
                break
            except Exception as e:
                print e.message
                exception = e
        if exception:
            return False, exception
        # result[0] = [true,false] ket qua cua update
        return True, result

    def insert_many(self, documents, ordered=True,
                    bypass_document_validation=False):
        """
        Thực hiện insert many
        :param documents:
        :param ordered:
        :param bypass_document_validation:
        :return:
        """
        for i in range(0, self.MAX_RETRY):
            exception = None
            try:
                result = self.db[self.collection_name].insert_many(documents, bypass_document_validation)
                break
            except Exception as e:
                print e.message
                exception = e
        if exception:
            return False, exception
        # result[0] = [true,false] ket qua cua update
        return True, result

    def update_many(self, filter, update, upsert=False,
                    bypass_document_validation=False, collation=None):
        for i in range(0, self.MAX_RETRY):
            exception = None
            try:
                result = self.db[self.collection_name].update_many(
                    filter, update, upsert, bypass_document_validation, collation)
                break
            except Exception as e:
                print e.message
                exception = e
        if exception:
            return False, exception
        # result[0] = [true,false] ket qua cua update
        return True, result


class AccountModel(ModelDb):
    """
    Cấu trúc của collections
    {
        "parent": {
            "_ID": int,
            "username": "",
            "password": "",
            "full_name": ""
        },
        "child": [
            {
                "_ID": int,
                "birth": int,
                "full_name": "",
            }
        ]
    }
    """

    COLLECTION_NAME = "account"
    # Lưu danh profile parent và các con
    # parent
    PARENT = 'parent'
    EMAIL = "email"
    PASSWORD = "password"
    FULL_NAME = "full_name"
    # child
    CHILD = 'child'
    BIRTH = 'birth'

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)

    def auth(self, email, password):
        """
        Đăng nhập băng email và password
        :param email:
        :param password:
        :return:
        """
        # Tìm trong db
        status, value = self.find_one(
            spec={
                self.PARENT + "." + self.EMAIL: email,
                self.PARENT + "." + self.PASSWORD: password

            })
        return status, value

    def get_all_child(self, account_id):
        """
        Lấy danh sách con của tài khoản
        :param account_id:
        :return:
        """
        # Tìm trong db
        status, value = self.find_one(
            spec={
                self._ID: account_id
            },
            fields={self.CHILD: 1}
        )
        return status, value


class DeviceModel(ModelDb):
    """
    Cấu trúc của collections
    {
        "_id":ObjectId
        "account_id"::ObjectId,
        devices:[
             "infor":{
                "imei":String,
                "device_name":String
             },
             "token":String,
             "token_fcm":String
             "privilege":{
                type:Int # "parent|child|unknown"<=>"1|0|-1"
                "id_child":"" # Chỉ dùng khi type= "child" để định danh trẻ con
                "latest_login":Int "true|false"= "0|1" Chi dung khi type = child
             },
             "status": Int # "login|logout"="0|1"

        ]
    }
    """

    COLLECTION_NAME = "device"
    # Lưu danh profile parent và các con
    ACCOUNT_ID = 'account_id'

    # Danh sách các thiết bị đăng nhập
    INFOR = "infor"
    IMEI = "imei"
    DEVICES = "devices"
    DEVICE_NAME = "device_name"

    # quyền của thiết bị trên máy
    PRIVILEGE_TYPE = "privilege_type"
    PRIVILEGE = "privilege"
    CHILD_ID = "child_id"
    LATEST_LOGIN = "latest_login"
    TOKEN = 'token'
    TOKEN_FCM = "token_fcm"
    STATUS = 'status'

    PRIVILEGE_UNKNOWN = -1
    PRIVILEGE_CHILD = 0
    PRIVILEGE_PARENT = 1

    STATUS_LOGOUT = 0
    STATUS_LOGIN = 1

    LATEST_LOGIN_TRUE = 1
    LATEST_LOGIN_FALSE = 0

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)

    def is_login_now(self, token, imei, device_name):
        """
        Kiểm tra thiết bị này đã đăng nhập trước đó hay chưa
        :param model_account: @link model.accountmodel.AccountModel
        :param token:
        :param imei:
        :param device_name:
        :return:
        """
        # Tìm trong db
        # return self.find_one(
        #     spec={
        #         DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.IMEI: imei,
        #         DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.DEVICE_NAME: device_name,
        #         DeviceModel.DEVICES + "." + DeviceModel.TOKEN: token,
        #         DeviceModel.DEVICES + "." + DeviceModel.STATUS: DeviceModel.STATUS_LOGIN,
        #     }
        # )
        return self.find_one(
            spec={
                DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.IMEI: imei,
                DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.DEVICE_NAME: device_name,
                DeviceModel.DEVICES + "." + DeviceModel.TOKEN: token,
                DeviceModel.DEVICES + "." + DeviceModel.STATUS: DeviceModel.STATUS_LOGIN,
            },
            fields={
                DeviceModel.ACCOUNT_ID: 1,
                DeviceModel.DEVICES: {'$elemMatch': {DeviceModel.TOKEN: token}}
            }
        )

    def is_login_before(self, token, imei, device_name):
        """
        Kiểm tra thiết bị này đã đăng nhập trước đó hay chưa
        :param model_account: @link model.accountmodel.AccountModel
        :param token:
        :param imei:
        :param device_name:
        :return:
        """
        # Tìm trong db
        return self.find_one(
            spec={
                DeviceModel.INFOR + "." + DeviceModel.IMEI: imei,
                DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.DEVICE_NAME: device_name,
                DeviceModel.DEVICES + "." + DeviceModel.TOKEN: token,
            })

    def generate_token(self):
        """
        Tạo token và đảm bảo không trùng với bất kỳ token nào trong db
        :return:
        """
        while True:
            token = self.algorithm_token()
            status, value = self.find_one(spec={self.TOKEN: token})
            if status:
                if value is not None and len(value) > 0:
                    continue
                else:
                    break
        return token

    def algorithm_token(self):
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


class SmsModel(ModelDb):
    """
    Cấu trúc của collections
    {
        "device_id": device_id
        "child_id":
        "sms":[
            "address":String,
            "body":String,
            "date":String,
            "status":Int, # Trạng thái gửi nhận
            "body":String,
            "thread_id":Int
            "type":int # inbox or outbox
            "version":String
         ]

    }
    """

    COLLECTION_NAME = "sms"
    SMS = "sms"
    DEVICE_ID = 'device_id'
    CHILD_ID = 'child_id'
    ADDRESS = "address"
    BODY = "body"
    DATE = "date"
    STATUS = "status"
    TYPE = "type"
    VERSION = "version"

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)


class CallLogModel(ModelDb):
    """
    Cấu trúc của collections
    {
        "device_id":String
        'child_id':String
         "call_log":[
            "number":String,
            "date":String,
            "duration":String,
            "type":int
            "version":String
         ]
    }
    """

    VERSION = "version"
    COLLECTION_NAME = "call_log"
    DEVICE_ID = 'device_id'
    CHILD_ID = 'child_id'
    DATA = "data"
    NUMBER = "number"
    DATE = "date"
    DURATION = "duration"
    # Loai cuoc goi: Goi den,Goi di,Goi nho...
    TYPE = "type"

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)


class ContactModel(ModelDb):
    """
    Cấu trúc của collections
    Note: 1 contact có nhiều email và nhiều số điện thoại
    {
        ""device_id":String
        "child_id":String
        "contacts":
        [
            {
                "display_name":String,
                "email":[
                     String,
                     ...
                 ],
                 "phone":[
                    String,
                    ...
                 ]
                 "version"
            }
        ]
    }
    """

    COLLECTION_NAME = "contact"
    DISPLAY_NAME = "display_name"
    EMAIL = "email"
    PHONE = "phone"
    DEVICE_ID = 'device_id'
    CHILD_ID = 'child_id'
    VERSION = "version"

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)


class MediaModel(ModelDb):
    """
    Cấu trúc của collections
    {

         "device_id":String
         "child_id":String
         "image":[
             {
                "_id":ObjectID
                 "data":String,
                 "display_name":String,
                 "size":Int,
                 "date_taken":String,
                 "status":1/0
                 "sha1":String
                 "version":
             }
             ...
         ],
         "audio":[
             {
                "_id":ObjectID
                 "data":String,
                 "display_name":String,
                 "size":Int,
                 "date_add":String,
                 "duration":Int,
                 "status":1/0
                 "sha1":String
                 "version":String
             }
            ...
         ],
        "video":[
             {
                 "_id":ObjectID
                 "data":String,
                 "display_name":String,
                 "size":Int,
                 "date_taken":String,
                 "duration":Int,
                 "status":1/0
                 "sha1":String
                 "version"
             }
            ...
         ]
    }
    """

    COLLECTION_NAME = "media"
    IMAGE = "image"
    IMAGE_FIELDS = {
        "DATA": "data",
        "DISPLAY_NAME": "display_name",
        "SIZE": "size",
        "DATE_ADDED": "date_added",
        "SHA1": "sha1",
        "STATUS": "status",
        "VERSION": "version"

    }
    AUDIO = "audio"
    CHILD_ID = 'child_id'

    AUDIO_FIELDS = {
        "DATA": "data",
        "DISPLAY_NAME": "display_name",
        "SIZE": "size",
        "DATE_ADDED": "date_added",
        "DURATION": "duration",
        "STATUS": "status",
        "VERSION": "version"
    }

    VIDEO = "video"
    VIDEO_FIELDS = {
        "DATA": "data",
        "DISPLAY_NAME": "display_name",
        "SIZE": "size",
        "DATE_ADDED": "date_added",
        "DURATION": "duration",
        "STATUS": "status",
        "VERSION": "version"
    }

    DEVICE_ID = 'device_id'

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)

    def get_id_put(self, type):
        """
        Lấy id để put file
        :return:
        """
        self.find_one()


class AppModel(ModelDb):
    """
    Cấu trúc của collections
    {
        "devide_id":String,
        "child_id":String
        "app":
            [
             {
             "package_name":String,
             "app_name":String
             "category":String,
             "type":int

             }
             ...
         ]
    }
    """

    COLLECTION_NAME = "app"
    PACKAGE_NAME = "package_name"
    APP_NAME = "app_name"
    CATEGORY = "category"
    TYPE = "type"
    TYPE_LIMIT_TIME_APP = "limit_time_app"
    TYPE_BAN_APP = "ban_app"
    TYPE_NORMAL_APP = "normal_app"

    DEVICE_ID = 'device_id'
    CHILD_ID = 'child_id'
    VERSION = 'version'

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)


class LocationModel(ModelDb):
    """
    Cấu trúc của collections
    {
        "_id":ObjectId ("location")
        "location":
            [
             {
             "package_name":String,
             "app_name":String
             }
             ...
         ]
    }
    """

    COLLECTION_NAME = "location"
    LATITUDE = "latitude";
    LONGITUDE = "longitude";
    DATE = "date"
    NAME = "name"
    DEVICE_ID = "device_id"

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)


class VersionModel(ModelDb):
    """
    Cấu trúc của collections
    {
        "_id":ObjectId

        "device_id":String,
        "child_id":String,

        "sms_version":String,
        "contact_version":String,
        "callog_version":String,
        "location_version":String,
        "app_version":String
        "video_version":String
        "audio_version":String
             ...
    }
    """

    COLLECTION_NAME = "version"
    DEVICE_ID = "device_id"
    CHILD_ID = 'child_id'
    SMS_VERSION = "sms_version"
    IMAGE_VERSION = "image_version"

    CONTACT_VERSION = "contact_version"
    CALLLOG_VERSION = "callog_version"
    LOCATION_VERSION = "location_version"
    APP_VERSION = "app_version"
    VIDEO_VERSION = "video_version"
    AUDIO_VERSION = "audio_version"

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)

    def update_version(self, device_id, child_id, type, version):
        ver_status, ver_value = self.find_one(
            spec={
                self.DEVICE_ID: device_id,
                self.CHILD_ID: child_id
            }
        )
        if ver_value is None or len(ver_value) <= 0:
            # Neu chua co thi insert
            self.insert_one(
                {
                    self.DEVICE_ID: device_id,
                    self.CHILD_ID: child_id,
                    type: version
                }
            )
        else:
            # Co roi thi update len vesion moi
            self.update_one(
                {
                    self.DEVICE_ID: device_id,
                    self.CHILD_ID: child_id,
                },
                {
                    "$set": {
                        type: version
                    }
                }
            )

    def get_version(self, device_id, child_id, type):
        """
        Trả về version curren
        :param ver_value:
        :return:
        """

        ver_status, ver_value = self.find_one(
            spec={
                self.DEVICE_ID: device_id,
                self.CHILD_ID: child_id
            }
        )
        if ver_value is not None and len(ver_value) > 0:
            # sms_version_key = "sms_version"
            if type in ver_value.keys():
                version_current = ver_value[type]
            else:
                version_current = "0.0.0.0"
        else:
            # Chưa có version_data cho collection
            version_current = "0.0.0.0"
        return version_current


class RuleParentModel(ModelDb):
    """
    Cấu trúc của collections
    {
        "_id":ObjectId

        "device_id":String,
        "child_id":String,

        "sms_version":String,
        "contact_version":String,
        "callog_version":String,
        "location_version":String,
        "app_version":String
        "video_version":String
        "audio_version":String
             ...
    }
    """

    COLLECTION_NAME = "rule_parent"
    DEVICE_ID = "device_id"
    CHILD_ID = 'child_id'

    TIME_LIMIT_APP = "time_limit_app";
    IS_SET_TIME_LIMIT_APP = "is_set_time_limit"
    # IS_SET_18_CONTENT = "is_set_18_content";

    def __init__(self, db):
        collection = self.COLLECTION_NAME
        ModelDb.__init__(self, db, collection)

    def update_version(self, device_id, child_id, type, version):
        ver_status, ver_value = self.find_one(
            spec={
                self.DEVICE_ID: device_id,
                self.CHILD_ID: child_id
            }
        )
        if ver_value is None or len(ver_value) <= 0:
            # Neu chua co thi insert
            self.insert_one(
                {
                    self.DEVICE_ID: device_id,
                    self.CHILD_ID: child_id,
                    type: version
                }
            )
        else:
            # Co roi thi update len vesion moi
            self.update_one(
                {
                    self.DEVICE_ID: device_id,
                    self.CHILD_ID: child_id,
                },
                {
                    "$set": {
                        type: version
                    }
                }
            )

    def get_version(self, device_id, child_id, type):
        """
        Trả về version curren
        :param ver_value:
        :return:
        """

        ver_status, ver_value = self.find_one(
            spec={
                self.DEVICE_ID: device_id,
                self.CHILD_ID: child_id
            }
        )
        if ver_value is not None and len(ver_value) > 0:
            # sms_version_key = "sms_version"
            if type in ver_value.keys():
                version_current = ver_value[type]
            else:
                version_current = "0.0.0.0"
        else:
            # Chưa có version_data cho collection
            version_current = "0.0.0.0"
        return version_current
