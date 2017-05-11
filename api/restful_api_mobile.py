# -*- coding: utf-8 -*-
from functools import wraps

__author__ = 'ThangLD'
import abc

import notification
from db.db import DbMongo, Version
from flask import request, send_file
from flask_restful import abort, Resource
from model.model_db import *
from utils import *
from werkzeug.utils import secure_filename
from googlecloudstore import *


def abort_if_json_request_invalid(request_json, param_keys):
    if not request_json.json:
        abort(404)
    for param_key in param_keys:
        if param_key not in request_json.json:
            abort(404)


def abort_if_json_invalid(jsonObject, param_keys):
    for param_key in param_keys:
        if param_key not in jsonObject:
            abort(404)


def require_api_key(api_method):
    @wraps(api_method)
    def check_api_key(*args, **kwargs):
        if request.method == 'GET':
            token = request.values[notification.PARAMS["token"]]
            imei = request.values[notification.PARAMS["imei"]]
            device_name = request.values[notification.PARAMS["device_name"]]
        else:
            json_data = request.get_json(force=True)
            token = json_data[notification.PARAMS["token"]]
            imei = json_data[notification.PARAMS["imei"]]
            device_name = json_data[notification.PARAMS["device_name"]]
        db_mongo = DbMongo()
        db_mongo.connect_db()
        device_model = DeviceModel(db_mongo.db)
        dev_status, dev_value = device_model.is_login_now(token, imei, device_name)
        # Lỗi query db là trả về lỗi luôn
        if not dev_status:
            db_mongo.close_db()
            return notification.notify_error_db()

        # Kiểm tra đăng nhập
        if dev_value is None or len(dev_value) == 0:
            db_mongo.close_db()
            return notification.notify_error_auth()

        kwargs['db_mongo'] = db_mongo
        kwargs['device_model'] = device_model
        kwargs['dev_value'] = dev_value
        kwargs['token'] = token
        kwargs['imei'] = imei
        kwargs['device_name'] = device_name
        if request.method == 'GET':
            return api_method(*args, **kwargs)
        else:
            kwargs['json_data'] = json_data
            return api_method(*args, **kwargs)

    return check_api_key


def auth_child_and_device(api_method):
    @wraps(api_method)
    def function_auth(*args, **kwargs):
        if request.method == 'GET':
            child_id = request.values[notification.PARAMS["child_id"]]
        else:
            json_data = request.get_json(force=True)
            child_id = json_data[notification.PARAMS["child_id"]]
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']

        device_id = json_data[notification.PARAMS["device_id"]]

        # Check childid
        account_id = dev_value[device_model.ACCOUNT_ID]
        account_model = AccountModel(db_mongo.db)
        ac_status, ac_value = account_model.find_one(
            spec={
                account_model._ID: account_id,
                account_model.CHILD + "." + account_model._ID: ObjectId(child_id)
            }
        )
        if not ac_status:
            return notification.notify_error_db()
        if ac_value is None or len(ac_value) <= 0:
            abort(400)
        if child_id is None or len(child_id) == 0:
            abort(400)

            # check device_id
            # Kiểm tra device id có phaỉ là của child id này không,
            # Trạng thái có đăng nhập
        status_check_device_id, value_check_device_id = device_model.find_one(
            spec={
                DeviceModel.ACCOUNT_ID: account_id,
                DeviceModel.DEVICES + "." + DeviceModel._ID: ObjectId(device_id),
                DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.CHILD_ID: child_id,
                DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_CHILD,
                DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.LATEST_LOGIN: DeviceModel.LATEST_LOGIN_TRUE
            }
        )
        if value_check_device_id is None or len(value_check_device_id) == 0:
            abort(400)
        kwargs[notification.PARAMS["device_id"]] = device_id
        kwargs[notification.PARAMS["child_id"]] = child_id
        return api_method(*args, **kwargs)

    return function_auth


class TokenFcmApi(Resource):
    @require_api_key
    def post(self, **kwargs):
        """cap nhat token_fcm"""
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']
        imei = kwargs['imei']
        device_name = kwargs['device_name']
        token = kwargs['token']
        token_fcm = json_data[notification.PARAMS["token_fcm"]]

        device_model.update_one(
            {
                DeviceModel.ACCOUNT_ID: dev_value[DeviceModel.ACCOUNT_ID],
                DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.IMEI: imei,
                DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.DEVICE_NAME: device_name,
                DeviceModel.DEVICES + "." + DeviceModel.TOKEN: token,
            },
            {
                '$set': {
                    DeviceModel.DEVICES + ".$." + DeviceModel.TOKEN_FCM: token_fcm
                }

            }
        )
        db_mongo.close_db();
        return jsonify(status=1)


class AuthenticationApi(Resource):
    def post(self):
        """
        Authenticate login
        :return:
        True,_id neu co tai khoan
        False,Exception neu khong co tai khoang
        """
        # parser = reqparse.RequestParser()
        # parser.add_argument('username')
        # parser.add_argument('password')
        # args = parser.parse_args()
        json_data = request.get_json(force=True)
        email = json_data['email']
        password = json_data['password']
        imei = json_data['imei']
        device_name = json_data['device_name']

        # email = request.values['email']
        # password = request.values['password']
        # imei = request.values['imei']
        # device_name = request.values['device_name']

        db_mongo = DbMongo()
        db_mongo.connect_db()
        print db_mongo.db
        device_model = DeviceModel(db_mongo.db)
        account_model = AccountModel(db_mongo.db)
        # Tìm trong db
        ac_status, ac_value = account_model.auth(email, password)
        if not ac_status:
            print str(ac_value)
            db_mongo.close_db()
            return notification.notify_error_db()

        if ac_value is not None and len(ac_value) > 0:
            # Nếu tài khoản tồn tại
            dev_status, dev_value = device_model.find_one(
                spec={
                    device_model.ACCOUNT_ID: ac_value[account_model._ID],
                    device_model.DEVICES + "." + device_model.INFOR + "." + device_model.IMEI: imei,
                    device_model.DEVICES + "." + device_model.INFOR + "." + device_model.DEVICE_NAME: device_name,
                }
            )
            if not dev_status:
                # query db mà lỗi là trả về lỗi luôn
                db_mongo.close_db()
                return notification.notify_error_db()

            token = device_model.generate_token()
            status_final = None;
            if dev_value is not None and len(dev_value) > 0:
                # Đã đăng nhập từ trước, chỉ cập nhật thôi
                status_final, value_final = device_model.update_one(
                    {
                        device_model.ACCOUNT_ID: ac_value[account_model._ID],
                        device_model.DEVICES + "." + device_model.INFOR + "." + device_model.IMEI: imei,
                        device_model.DEVICES + "." + device_model.INFOR + "." + device_model.DEVICE_NAME: device_name
                    },
                    {
                        '$set': {
                            device_model.DEVICES + ".$." + device_model.PRIVILEGE: {
                                device_model.PRIVILEGE_TYPE: device_model.PRIVILEGE_UNKNOWN
                            },
                            device_model.DEVICES + ".$." + device_model.TOKEN: token,
                            device_model.DEVICES + ".$." + device_model.STATUS: device_model.STATUS_LOGIN
                        }
                    }, True
                )
            else:
                # Nếu thiết bị chưa được đăng nhập lần nào
                # THêm thiết bị vào màng devices trong db
                ex_account_status, ex_account_value = device_model.find_one(
                    spec={
                        device_model.ACCOUNT_ID: ac_value[account_model._ID]
                    }
                )
                if not ex_account_status:
                    return notification.notify_error_db()
                if ex_account_value is None or len(ex_account_value) == 0:
                    status_final, value = device_model.insert_one(
                        {
                            device_model.ACCOUNT_ID: ac_value[account_model._ID],
                            device_model.DEVICES:
                                [
                                    {
                                        device_model._ID: ObjectId(),
                                        device_model.INFOR: {
                                            device_model.IMEI: imei,
                                            device_model.DEVICE_NAME: device_name
                                        },
                                        device_model.PRIVILEGE: {
                                            device_model.PRIVILEGE_TYPE: device_model.PRIVILEGE_UNKNOWN},
                                        device_model.TOKEN: token,
                                        device_model.STATUS: device_model.STATUS_LOGIN
                                    }
                                ]
                        }
                    )
                else:
                    # Nếu chưa có
                    status, value = device_model.find_one(
                        spec={
                            device_model.ACCOUNT_ID: ac_value[account_model._ID],
                            device_model.DEVICES + "." + device_model.INFOR + "." + device_model.IMEI: imei,
                            device_model.DEVICES + "." + device_model.INFOR + "." + device_model.DEVICE_NAME: device_name,
                        }
                    )
                    if not status:
                        return notification.notify_error_db()
                    if value is None or len(value) == 0:
                        status_final, value = device_model.update_one(
                            {
                                device_model.ACCOUNT_ID: ac_value[account_model._ID]
                            },
                            {
                                '$addToSet':
                                    {
                                        device_model.DEVICES: {
                                            device_model._ID: ObjectId(),
                                            device_model.INFOR: {
                                                device_model.IMEI: imei,
                                                device_model.DEVICE_NAME: device_name
                                            },
                                            device_model.PRIVILEGE: {
                                                device_model.PRIVILEGE_TYPE: device_model.PRIVILEGE_UNKNOWN},
                                            device_model.TOKEN: token,
                                            device_model.STATUS: device_model.STATUS_LOGIN
                                        }
                                    }
                            }
                        )
                    else:
                        status_final, value = device_model.update_one(
                            {
                                device_model.ACCOUNT_ID: ac_value[account_model._ID]
                            },
                            {
                                '$set': {
                                    device_model.DEVICES: {
                                        device_model.PRIVILEGE: {
                                            device_model.PRIVILEGE_TYPE: device_model.PRIVILEGE_UNKNOWN},
                                        device_model.TOKEN: token,
                                        device_model.STATUS: device_model.STATUS_LOGIN
                                    }
                                }
                            }
                        )
                db_mongo.close_db()
            if not status_final:
                return notification.notify_error_db()
                # Gửi về status và token.
                # Nếu cập nhật không thành công
            return jsonify(status=1, token=token)
        else:  # Thông báo user hoặc mật khẩu không đúng
            db_mongo.close_db()
            return notify_error_auth()


@require_api_key
def put(self, **kwargs):
    return


class ParentAccountApi(Resource):
    def post(self):
        """
        Thực hiện đăng ký tài khoản
        :return:
        { "status": True|False, "msg":"error_id"}
        error_1: Tài khoản đã tồn tại
        error_0: Đã có lỗi xảy ra
        """
        json_data = request.get_json(force=True)
        email = json_data['email']
        password = json_data['password']
        full_name = json_data['full_name']

        db_mongo = DbMongo()
        db_mongo.connect_db()
        account_model = AccountModel(db_mongo.db)
        # Tìm trong db
        status, value = account_model.find_one(
            spec={account_model.PARENT + "." + account_model.EMAIL: email,},
            fields={account_model._ID: 1}
        )

        if not status:
            db_mongo.close_db()
            return notification.notify_error_db()

        if value is not None and len(value) > 0:
            # Nếu email đã tồn tại
            db_mongo.close_db()
            return notification.notify_error_exist()
        else:
            # Nếu email chưa tồn tại, thêm vào csdl
            status, value = account_model.insert_one({
                account_model.PARENT: {
                    account_model._ID: ObjectId(),
                    account_model.EMAIL: email,
                    account_model.PASSWORD: password,
                    account_model.FULL_NAME: full_name
                }
            })
            db_mongo.close_db()
            if not status:
                return notification.notify_error_db()
            return notification.notify_status_success();


class ChildAccountApi(Resource):
    @require_api_key
    def post(self, **kwargs):
        """
        Thêm thiết bị trẻ con
        :return:
        {"status":"0|1", "msg":"error_id"}
        error_3: Yêu cầu đăng nhập lại, token,device_name, imei không hợp lệ
        error_1: Child này đã tồn tại.
        """
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']

        account_id = dev_value[device_model.ACCOUNT_ID]
        account_model = AccountModel(db_mongo.db)
        full_name = json_data['full_name']
        birth = json_data['birth']

        ac_status, ac_value = account_model.find_one(
            spec={
                account_model._ID: account_id,
                account_model.CHILD + "." + account_model.FULL_NAME: full_name
            }
        )
        if not ac_status:
            notification.notify_error_db()
        if ac_value is not None and len(ac_value) > 0:
            return notification.notify_error_exist()
        else:
            # Nếu child chưa tồn tại, thêm vào db
            status, value = account_model.update_one(
                {
                    account_model._ID: account_id
                },
                {
                    "$addToSet": {
                        account_model.CHILD: {
                            account_model._ID: ObjectId(),
                            account_model.FULL_NAME: full_name,
                            account_model.BIRTH: birth
                        }
                    }
                }
            )
            if not status:
                return notification.notify_error_db()
            return jsonify(status=1);

    @require_api_key
    def get(self, **kwargs):
        """
        Lấy tất cả danh sách trẻ con
        :return:
        """
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']

        account_model = AccountModel(db_mongo.db)
        status, value = account_model.get_all_child(dev_value[device_model.ACCOUNT_ID]);
        if not status:
            db_mongo.close_db()
            return notification.notify_error_db();
        data = []
        if account_model.CHILD in value.keys():
            for child in value[account_model.CHILD]:
                # Chuyen object id sang string
                child_id = child[account_model._ID]
                child.pop(account_model._ID)
                child["id_server"] = str(child_id)
                data.append(child)
        db_mongo.close_db()
        return jsonify(status=1, data=data)

    @require_api_key
    def put(self, **kwargs):
        # Lấy các thông tin cần cập nhật
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']

        # Lấy data
        if DeviceModel.PRIVILEGE in json_data:
            privilege_rec = json_data[DeviceModel.PRIVILEGE]
            device_model.update_one(
                {
                    device_model.DEVICES + "." + device_model.TOKEN:
                        json_data[notification.PARAMS["token"]],
                    device_model.DEVICES + "." + device_model.DEVICE_NAME:
                        json_data[notification.PARAMS["device_name"]],
                    device_model.DEVICES + "." + device_model.IMEI:
                        json_data[notification.PARAMS["imei"]],
                },
                {
                    '$set': {
                        device_model.PRIVILEGE: {
                            device_model.PRIVILEGE + "." + device_model.PRIVILEGE_TYPE: privilege_rec
                        }
                    }
                }
            )
        if DeviceModel.CHILD_ID in json_data:
            id_child = json_data[notification.PARAMS["child_id"]]
            device_model.update_one(
                {
                    device_model.DEVICES + "." + device_model.TOKEN:
                        json_data[notification.PARAMS["token"]],
                    device_model.DEVICES + "." + device_model.DEVICE_NAME:
                        json_data[notification.PARAMS["device_name"]],
                    device_model.DEVICES + "." + device_model.IMEI:
                        json_data[notification.PARAMS["imei"]],
                },
                {
                    '$set': {
                        device_model.PRIVILEGE: {
                            device_model.PRIVILEGE + "." + DeviceModel.CHILD_ID: id_child
                        }
                    }
                }
            )
        if DeviceModel.STATUS in json_data:
            status_rec = json_data[DeviceModel.STATUS]
            device_model.update_one(
                {
                    device_model.DEVICES + "." + device_model.TOKEN:
                        json_data[notification.PARAMS["token"]],
                    device_model.DEVICES + "." + device_model.DEVICE_NAME:
                        json_data[notification.PARAMS["device_name"]],
                    device_model.DEVICES + "." + device_model.IMEI:
                        json_data[notification.PARAMS["imei"]],
                },
                {
                    '$set': {
                        device_model.PRIVILEGE: {
                            device_model.STATUS: status_rec
                        }
                    }
                }
            )
        return notification.notify_update_successfully()


class JsonResourceApi(Resource):
    # collection_version_key key ở trong collection version : ex sms_collection
    collection_version_key = None;

    @property
    def get_collection_version_key(self):
        return self.collection_version_key

    def get_current_version_server(self, ver_value):
        """
        Trả về version curren
        :param ver_value:
        :return:
        """
        if ver_value is not None and len(ver_value) > 0:
            exist_record = True
            # sms_version_key = "sms_version"

            if self.collection_version_key in ver_value.keys():
                version_current = ver_value[self.collection_version_key]
            else:
                version_current = "0.0.0.0"
        else:
            # Chưa có version_data cho collection
            version_current = "0.0.0.0"
            exist_record = False;
        return exist_record, version_current

    @abc.abstractmethod
    def insert(self, db_mongo, device_id, child_id, version_client, data):
        return

    @abc.abstractmethod
    def update_version(self, db_mongo, device_id, child_id, version_client):
        return

    @abc.abstractmethod
    def retrieve_items(self, db_mongo, ids):
        return

    @require_api_key
    def post(self, **kwargs):
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']

        child_id = json_data[notification.PARAMS["child_id"]]
        version_client = json_data[notification.PARAMS["version"]]
        # Authen child
        account_id = dev_value[device_model.ACCOUNT_ID]
        account_model = AccountModel(db_mongo.db)
        ac_status, ac_value = account_model.find_one(
            spec={
                account_model._ID: account_id,
                account_model.CHILD + "." + account_model._ID: ObjectId(child_id)
            }
        )
        if not ac_status:
            return notification.notify_error_db()
        if ac_value is None or len(ac_value) <= 0:
            abort(400)
        if child_id is None or len(child_id) == 0:
            abort(400)

        # lấy device_id
        device_id = str(dev_value[DeviceModel.DEVICES][0][DeviceModel._ID])
        version_model = VersionModel(db_mongo.db)
        ver_status, ver_value = version_model.find_one(
            spec={
                version_model.DEVICE_ID: device_id,
                version_model.CHILD_ID: child_id
            }
        )

        if not ver_status:
            db_mongo.close_db()
            return notification.notify_error_db();

            # version_current = "0.0.0.0"
            # version_model.insert_one({"_id": ObjectId(device_id), ver_name_type: version_current})

        exist_record_version, version_sever = self.get_current_version_server(ver_value)

        if not exist_record_version or Version(version_client).compare(Version(version_sever)) > 0:
            # Nếu version ở client lớn hơn server hoặc chưa có có version trước đó ở server(chưa đc upload lên )
            # Thì mới thực hiện cập nhật
            # Nhận data
            data = json_data[notification.PARAMS["data"]]
            # Thực hiện insert vào db
            ins_status, ins_value = self.insert(db_mongo, device_id, child_id, version_client, data)
            if not ins_status:
                db_mongo.close_db()
                return notification.notify_error_db()
            # insert thành công rồi thì thực hiện cập nhật
            version_model.update_version(device_id, child_id, self.collection_version_key, version_client)
            db_mongo.close_db()
            if not ins_status:
                return notification.notify_error_db()

            return notification.notify_insert_successfully()
        else:
            # Trả về client đã db đã up to date
            db_mongo.close_db()
            return notification.notify_error_uptodate()

    @require_api_key
    def get(self):
        return

        """Lấy json"""

        # child_id = request.values[notification.PARAMS["version"]]
        # version_client = request.values[notification.PARAMS["version"]]
        # db_mongo = ** kwargs['db_mongo']
        # dev_value = kwargs['dev_value']
        # device_model = kwargs['device_model']
        #
        # # Khi thực hiện đăng nhập thành công
        # # Lấy danh sách id nó có
        # ids = json_data[notification.PARAMS["ids"]]
        # return self.retrieve_items(db_mongo, ids);
        #
        """
        format trả về là 1 mảng json với mỗi jsonobject có định dạng như sau
        {
        "id":String,
        "action":String add|delete|update
        "date_taken":..... (Các thuộc tính của )
        }
        """
        # Thực hiện query trong csdl


class SmsApi(JsonResourceApi):
    def update_version(self, db_mongo, device_id, child_id, version_client):
        pass

    def retrieve_items(self, db_mongo, ids):
        pass

    collection_version_key = "sms_version"

    def insert(self, db_mongo, device_id, child_id, version_client, data):
        super(SmsApi, self).insert(db_mongo, device_id, child_id, version_client, data)
        try:
            sms_model = SmsModel(db_mongo.db)
            item = {
                sms_model.DEVICE_ID: device_id,
                sms_model.CHILD_ID: child_id,
            }
            status, value = sms_model.find_one(
                spec={
                    sms_model.DEVICE_ID: device_id,
                    sms_model.CHILD_ID: child_id,
                }
            )
            if not status:
                return notification.notify_error_db()
            if value is None or len(value) <= 0:
                sms_model.insert_one(item);

            for item in data:
                item[sms_model._ID] = ObjectId();
                # Kiểm tra record này có chưa, nếu có rồi thì không insert
                fi_status, fi_value = sms_model.find_one(
                    spec={
                        sms_model.DEVICE_ID: device_id,
                        sms_model.CHILD_ID: child_id,
                        sms_model.SMS + "." + sms_model.DATE: item[sms_model.DATE],
                        sms_model.SMS + "." + sms_model.BODY: item[sms_model.BODY],
                        sms_model.SMS + "." + sms_model.ADDRESS: item[sms_model.ADDRESS],
                        sms_model.SMS + "." + sms_model.TYPE: item[sms_model.TYPE],
                    }
                )
                if fi_value is None or len(fi_value) <= 0:
                    # item[sms_model._ID] = ObjectId();
                    item[sms_model.VERSION] = version_client;

                    sms_model.update_one(
                        {
                            sms_model.DEVICE_ID: device_id,
                            sms_model.CHILD_ID: child_id
                        },
                        {
                            '$push': {
                                sms_model.COLLECTION_NAME: item
                            }
                        }
                    )
        except Exception as e:
            print "SmsApi-insert" + e.message
            return False, e
        return True, None


class CallLogApi(JsonResourceApi):
    def update_version(self, db_mongo, device_id, child_id, version_client):
        pass

    def retrieve_items(self, db_mongo, ids):
        pass

    collection_version_key = "calllog_version"

    def insert(self, db_mongo, device_id, child_id, version_client, data):
        super(CallLogApi, self).insert(db_mongo, device_id, child_id, version_client, data)
        try:
            model = CallLogModel(db_mongo.db)
            status, value = model.find_one(
                spec={
                    model.DEVICE_ID: device_id,
                    model.CHILD_ID: child_id,
                }
            )
            if not status:
                return
            if value is None or len(value) <= 0:
                model.insert_one(
                    {
                        model.DEVICE_ID: device_id,
                        model.CHILD_ID: child_id,
                    }
                );

            for item in data:
                item[model._ID] = ObjectId()
                # Kiểm tra record này có chưa, nếu có rồi thì không insert
                fi_status, fi_value = model.find_one(
                    spec={
                        CallLogModel.DEVICE_ID: device_id,
                        CallLogModel.CHILD_ID: child_id,
                        CallLogModel.COLLECTION_NAME + "." + CallLogModel.DATE: item[CallLogModel.DATE],
                        CallLogModel.COLLECTION_NAME + "." + CallLogModel.DURATION: item[CallLogModel.DURATION],
                        CallLogModel.COLLECTION_NAME + "." + CallLogModel.NUMBER: item[CallLogModel.NUMBER],
                        CallLogModel.COLLECTION_NAME + "." + CallLogModel.TYPE: item[CallLogModel.TYPE],
                        CallLogModel.COLLECTION_NAME + "." + CallLogModel.TYPE: item[CallLogModel.TYPE]
                    }
                )
                if fi_value is None or len(fi_value) <= 0:
                    item[model.VERSION] = version_client;
                    model.update_one(
                        {
                            model.DEVICE_ID: device_id,
                            model.CHILD_ID: child_id
                        },
                        {
                            '$push': {
                                model.COLLECTION_NAME: item
                            }
                        }
                    )
        except Exception as e:
            print "SmsApi-insert" + e.message
            return False, e
        return True, None


class LocationApi(JsonResourceApi):
    def update_version(self, db_mongo, device_id, child_id, version_client):
        pass

    def retrieve_items(self, db_mongo, ids):
        pass

    collection_version_key = "location_version"

    def insert(self, db_mongo, device_id, child_id, version_client, data):
        super(LocationApi, self).insert(db_mongo, device_id, child_id, version_client, data)
        try:
            model = LocationModel(db_mongo.db)
            status, value = model.find_one(
                spec={
                    model.DEVICE_ID: device_id,
                    model.CHILD_ID: child_id,
                }
            )
            if not status:
                return
            if value is None or len(value) <= 0:
                model.insert_one(
                    {
                        model.DEVICE_ID: device_id,
                        model.CHILD_ID: child_id,
                    }
                );

            for item in data:
                # Kiểm tra record này có chưa, nếu có rồi thì không insert
                fi_status, fi_value = model.find_one(
                    spec={
                        LocationModel.DEVICE_ID: device_id,
                        LocationModel.CHILD_ID: child_id,
                        LocationModel.COLLECTION_NAME + "." + LocationModel.LATITUDE: item[LocationModel.LATITUDE],
                        LocationModel.COLLECTION_NAME + "." + LocationModel.LONGITUDE: item[LocationModel.LONGITUDE],
                    }
                )
                if fi_value is None or len(fi_value) <= 0:
                    item[model.VERSION] = version_client;
                    model.update_one(
                        {
                            model.DEVICE_ID: device_id,
                            model.CHILD_ID: child_id
                        },
                        {
                            '$push': {
                                model.COLLECTION_NAME: item
                            }
                        }
                    )
        except Exception as e:
            print "SmsApi-insert" + e.message
            return False, e
        return True, None


class AppApi(JsonResourceApi):
    def update_version(self, db_mongo, device_id, child_id, version_client):
        pass

    def retrieve_items(self, db_mongo, ids):
        pass

    collection_version_key = "app_version"

    def insert(self, db_mongo, device_id, child_id, version_client, data):
        super(AppApi, self).insert(db_mongo, device_id, child_id, version_client, data)
        try:
            app_model = AppModel(db_mongo.db)
            item = {
                app_model.DEVICE_ID: device_id,
                app_model.CHILD_ID: child_id,
            }
            status, value = app_model.find_one(
                spec={
                    app_model.DEVICE_ID: device_id,
                    app_model.CHILD_ID: child_id,
                }
            )
            if not status:
                return notification.notify_error_db()
            if value is None or len(value) <= 0:
                app_model.insert_one(item);

            for item in data:
                item[app_model._ID] = ObjectId()
                # Kiểm tra record này có chưa, nếu có rồi thì không insert
                fi_status, fi_value = app_model.find_one(
                    spec={
                        app_model.DEVICE_ID: device_id,
                        app_model.CHILD_ID: child_id,
                        app_model.COLLECTION_NAME + "." + app_model.PACKAGE_NAME: item[app_model.PACKAGE_NAME],
                        app_model.COLLECTION_NAME + "." + app_model.APP_NAME: item[app_model.APP_NAME]
                    }
                )
                if fi_value is None or len(fi_value) <= 0:
                    # item[app_model._ID] = ObjectId();
                    item[app_model.VERSION] = version_client;

                    app_model.update_one(
                        {
                            app_model.DEVICE_ID: device_id,
                            app_model.CHILD_ID: child_id
                        },
                        {
                            '$push': {
                                app_model.COLLECTION_NAME: item
                            }
                        }
                    )
                else:
                    print "update_type"
                    print item[app_model.PACKAGE_NAME]
                    app_model.update_one(
                        {
                            app_model.DEVICE_ID: device_id,
                            app_model.CHILD_ID: child_id,
                            app_model.COLLECTION_NAME + "." + app_model.PACKAGE_NAME: item[app_model.PACKAGE_NAME]
                        },
                        {
                            '$set': {
                                app_model.COLLECTION_NAME + ".$." + app_model.TYPE: item[app_model.TYPE]
                            }
                        }
                    )
        except Exception as e:
            print "appApi-insert" + e.message
            return False, e
        return True, None


class ContactApi(Resource):
    @require_api_key
    def post(self, **kwargs):
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']

        child_id = json_data[notification.PARAMS["child_id"]]
        version_client = json_data[notification.PARAMS["version"]]

        account_id = dev_value[device_model.ACCOUNT_ID]
        account_model = AccountModel(db_mongo.db)
        ac_status, ac_value = account_model.find_one(
            spec={
                account_model._ID: account_id,
                account_model.CHILD + "." + account_model._ID: ObjectId(child_id)
            }
        )
        if not ac_status:
            return notification.notify_error_db()
        if ac_value is None or len(ac_value) <= 0:
            abort(400)
        if child_id is None or len(child_id) == 0:
            abort(400)
        # lấy device_id
        device_id = str(dev_value[DeviceModel.DEVICES][0][DeviceModel._ID])
        data = json_data[notification.PARAMS["data"]];
        contact_model = ContactModel(db_mongo.db)
        ex_status, ex_value = contact_model.find_one(
            spec={
                contact_model.DEVICE_ID: device_id,
                contact_model.CHILD_ID: child_id
            }
        )
        if not ex_status:
            return notification.notify_error_db()
        if ex_value is None or len(ex_value) <= 0:
            # Chưa tồn tại
            up_status, up_value = contact_model.insert_one(
                {
                    contact_model.DEVICE_ID: device_id,
                    contact_model.CHILD_ID: child_id,
                    contact_model.COLLECTION_NAME: data
                }
            )
        else:
            up_status, up_value = contact_model.update_one(
                {
                    contact_model.DEVICE_ID: device_id,
                    contact_model.CHILD_ID: child_id,
                },
                {
                    '$set': {
                        contact_model.COLLECTION_NAME: data
                    }
                }
            )

        if not up_status:
            return notification.notify_error_db()
        version_model = VersionModel(db_mongo.db)
        print "version_client" + version_client
        version_model.update_version(device_id, child_id, VersionModel.CONTACT_VERSION, version_client)
        db_mongo.close_db()
        return notification.notify_update_successfully()

    @require_api_key
    def get(self, **kwargs):
        # Check childid
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        child_id = request.values[notification.PARAMS["child_id"]]
        device_id = request.values[notification.PARAMS["device_id"]]
        account_id = dev_value[device_model.ACCOUNT_ID]
        account_model = AccountModel(db_mongo.db)
        ac_status, ac_value = account_model.find_one(
            spec={
                account_model._ID: account_id,
                account_model.CHILD + "." + account_model._ID: ObjectId(child_id)
            }
        )
        if not ac_status:
            return notification.notify_error_db()
        if ac_value is None or len(ac_value) <= 0:
            abort(400)
        if child_id is None or len(child_id) == 0:
            abort(400)

            # check device_id
            # Kiểm tra device id có hợp lệ không
        status_check_device_id, value_check_device_id = device_model.find_one(
            spec={
                DeviceModel.DEVICES + "." + DeviceModel._ID: ObjectId(device_id),
                DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_CHILD,
                DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.LATEST_LOGIN: DeviceModel.LATEST_LOGIN_TRUE
            }

        )
        if value_check_device_id is None or len(value_check_device_id) == 0:
            abort(400)
        contact_model = ContactModel(db_mongo.db)
        co_status, co_value = contact_model.find_one(
            spec={ContactModel.DEVICE_ID: device_id, ContactModel.CHILD_ID: child_id}
        )

        data = []
        for item in co_value[ContactModel.COLLECTION_NAME]:
            item["_id"] = str(item["_id"])

            if notification.PARAMS["version"] in item.keys():
                item.pop(notification.PARAMS["version"])
            data.append(item)
        return jsonify(status=1, data=data)


class RuleParentApi(Resource):
    @require_api_key
    def post(self, **kwargs):
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']
        privilege = json_data[notification.PARAMS["privilege"]]
        child_id = json_data[notification.PARAMS["child_id"]]
        # TODO authen child_id

        #
        if privilege == notification.PRIVILEGE_TYPE["parent"]:
            dev_child = device_model.find_one(
                spec={
                    DeviceModel.ACCOUNT_ID: dev_value[DeviceModel.ACCOUNT_ID]
                },
                fields={
                    DeviceModel.DEVICES: {
                        '$elemMatch': {
                            DeviceModel.PRIVILEGE + "." + DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_CHILD,
                            DeviceModel.PRIVILEGE + "." + DeviceModel.CHILD_ID: child_id,

                        }
                    }
                }
            )
            if dev_child is not None and len(dev_child) > 0:
                device_id = dev_child[DeviceModel._ID]
            else:
                return notify_error_db()

        elif privilege == notification.PRIVILEGE_TYPE["child"]:
            device_id = dev_value[DeviceModel._ID]

        rule_model = RuleParentModel(db_mongo.db)
        status, value_ex = rule_model.find_one(spec={
            RuleParentModel.DEVICE_ID: device_id,
            RuleParentModel.CHILD_ID: child_id,
        })
        if value_ex is None or len(value_ex) == 0:
            rule_model.insert_one(
                {
                    RuleParentModel.DEVICE_ID: device_id,
                    RuleParentModel.CHILD_ID: child_id,
                    RuleParentModel.IS_SET_TIME_LIMIT_APP: json_data[RuleParentModel.IS_SET_TIME_LIMIT_APP],
                    RuleParentModel.TIME_LIMIT_APP: json_data[RuleParentModel.TIME_LIMIT_APP]

                }
            )
        else:
            rule_model.update_one(
                {
                    RuleParentModel.DEVICE_ID: device_id,
                    RuleParentModel.CHILD_ID: child_id,
                },
                {
                    '$set': {
                        RuleParentModel.IS_SET_TIME_LIMIT_APP: json_data[RuleParentModel.IS_SET_TIME_LIMIT_APP],
                        RuleParentModel.TIME_LIMIT_APP: json_data[RuleParentModel.TIME_LIMIT_APP]
                    }
                }
            )
        return notify_update_successfully()

    @require_api_key
    @auth_child_and_device
    def get(self, **kwargs):
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']
        privilege = json_data[notification.PARAMS["privilege"]]
        child_id = kwargs[notification.PARAMS["child_id"]]
        # lay childid
        if privilege == notification.PRIVILEGE_TYPE["parent"]:
            dev_child = device_model.find_one(
                spec={
                    DeviceModel.ACCOUNT_ID: dev_value[DeviceModel.ACCOUNT_ID]
                },
                fields={
                    DeviceModel.DEVICES: {
                        '$elemMatch': {
                            DeviceModel.PRIVILEGE + "." + DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_CHILD,
                            DeviceModel.PRIVILEGE + "." + DeviceModel.CHILD_ID: child_id,

                        }
                    }
                }
            )
            if dev_child is not None and len(dev_child) > 0:
                device_id = dev_child[DeviceModel._ID]
            else:
                return notify_error_db()

        elif privilege == notification.PRIVILEGE_TYPE["child"]:
            device_id = dev_value[DeviceModel._ID]
        rule_model = RuleParentModel(db_mongo.db)
        status, value = rule_model.find_one(
            spec={
                RuleParentModel.CHILD_ID: child_id,
                RuleParentModel.DEVICE_ID: device_id
            },
            fields={
                RuleParentModel.IS_SET_TIME_LIMIT_APP: 1,
                RuleParentModel.TIME_LIMIT_APP: 1
            }
        )
        return jsonify(status=1, msg=value)


class VersionApi(Resource):
    @require_api_key
    def get(self, **kwargs):

        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']

        type_version = request.values[notification.PARAMS["type_version"]]
        child_id = request.values[notification.PARAMS["child_id"]]
        privilege = request.values[notification.PARAMS["privilege"]]

        try:
            object_id = ObjectId(child_id)
            privilege = int(privilege)
        except Exception as e:
            print e.message
            return abort(400)

        # Kiểm tra child_id
        account_id = dev_value[device_model.ACCOUNT_ID]
        account_model = AccountModel(db_mongo.db)
        ac_status, ac_value = account_model.find_one(
            spec={
                account_model._ID: account_id,
                account_model.CHILD + "." + account_model._ID: object_id
            }
        )
        if not ac_status:
            return notification.notify_error_db()
        if ac_value is None or len(ac_value) <= 0:
            abort(400)
        if child_id is None or len(child_id) == 0:
            abort(400)

        # Nếu trường hợp là bố mẹ gửi lên, thì token, imei, device_name là
        # của bố mẹ => device_id của trẻ con chưa có.
        # Nếu trường hợp là trẻ con gửi lên, thì token, imei, device_name là
        # của trẻ con => lấy device_id của token luôn
        if DeviceModel.PRIVILEGE_CHILD == privilege:
            device_id = str(dev_value[DeviceModel.DEVICES][0][DeviceModel._ID])
            # Check device_id
        elif DeviceModel.PRIVILEGE_PARENT == privilege:
            device_id = request.values[notification.PARAMS["device_id"]]
            try:
                object_device_id = ObjectId(device_id)
            except:
                abort(400)
            # Kiểm tra device id có hợp lệ không
            status_check, value_check = device_model.find_one(
                spec={
                    DeviceModel.ACCOUNT_ID: dev_value[DeviceModel.ACCOUNT_ID],
                    DeviceModel.DEVICES + "." + DeviceModel._ID: object_device_id,
                    DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_CHILD,
                    DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.LATEST_LOGIN: DeviceModel.LATEST_LOGIN_TRUE
                },
                fields={

                    DeviceModel.DEVICES: {
                        '$elemMatch': {
                            DeviceModel.PRIVILEGE + "." + DeviceModel.CHILD_ID: child_id,
                            DeviceModel.PRIVILEGE + "." + DeviceModel.LATEST_LOGIN: DeviceModel.LATEST_LOGIN_TRUE,
                        }
                    }
                }
            )
            if value_check is None or len(value_check) == 0:
                abort(400)
        else:
            abort(400);

        fields_in_db = type_version + "_version"
        version_model = VersionModel(db_mongo.db)

        ver_status, ver_value = version_model.find_one(
            spec={
                version_model.DEVICE_ID: device_id,
                version_model.CHILD_ID: child_id,
            }
        )

        if not ver_status:
            db_mongo.close_db()
            return notification.notify_error_db()
        if ver_value is not None and len(ver_value) > 0:
            if fields_in_db in ver_value.keys():
                return jsonify(status=1, msg=ver_value[fields_in_db])
            else:
                return jsonify(status=1, msg="0.0.0.0")
        else:
            # Chua co trong db, tra ve version 0.0.0.0
            return jsonify(status=1, msg="0.0.0.0")


class MediaListApi(Resource):
    """
        Không có id
    """
    type_media = None

    @abc.abstractmethod
    def create_record(self, db_mongo, device_id, child_id, info_file, version_client):
        return

    @require_api_key
    def post(self, **kwargs):
        """
        Yeu cau gui file len,
        Tra ve dia chi cua file
        :return:
        """
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']
        info_file = json_data["info_file"]
        child_id = json_data["child_id"]
        version_client = json_data[notification.PARAMS["version"]]
        # authen child
        account_id = dev_value[device_model.ACCOUNT_ID]
        account_model = AccountModel(db_mongo.db)
        ac_status, ac_value = account_model.find_one(
            spec={
                account_model._ID: account_id,
                account_model.CHILD + "." + account_model._ID: ObjectId(child_id)
            }
        )
        if not ac_status:
            return notification.notify_error_db()
        if ac_value is None or len(ac_value) <= 0:
            abort(400)
        if child_id is None or len(child_id) == 0:
            abort(400)

        # Khi thực hiện đăng nhập thành công
        if dev_value is not None and len(dev_value) > 0:
            # Trả về location để save
            # Lưu trong db
            device_id = str(dev_value[DeviceModel.DEVICES][0][DeviceModel._ID])
            return self.create_record(db_mongo, device_id, child_id, info_file, version_client)
        else:
            db_mongo.close_db()
            return notification.notify_error_auth()


class MediaApi(Resource):
    """
    Liên quan đến id,
    """
    type_media = None

    def update_version(self, db_mongo, device_id, child_id, version_client, type):
        version_model = VersionModel(db_mongo.db)
        version_server = version_model.get_version(device_id, child_id, type)
        if Version(version_client).compare(Version(version_server)) > 0:
            version_model.update_version(device_id, child_id, type, version_client)
        return

    @abc.abstractmethod
    def save_file(self, db_mongo, device_id, child_id, file_id):
        return

    def put(self, file_id):
        """
        Thực hiện put 1 file lên,
        :param file_id:
        :return:
        """
        token = request.form[notification.PARAMS["token"]]
        imei = request.form[notification.PARAMS["imei"]]

        device_name = request.form[notification.PARAMS["device_name"]]

        child_id = request.form[notification.PARAMS["child_id"]]
        db_mongo = DbMongo()
        db_mongo.connect_db()
        device_model = DeviceModel(db_mongo.db)
        dev_status, dev_value = device_model.is_login_now(token, imei, device_name)

        # Lỗi query db là trả về lỗi luôn
        if not dev_status:
            db_mongo.close_db()
            return notification.notify_error_db()

        # Kiểm tra đăng nhập
        if dev_value is None or len(dev_value) == 0:
            db_mongo.close_db()
            return notification.notify_error_auth()

        # Khi thực hiện đăng nhập thành công
        if dev_value is None and len(dev_value) <= 0:
            db_mongo.close_db()
            return notification.notify_error_auth()

        # Authen xem child_id
        account_id = dev_value[device_model.ACCOUNT_ID]
        account_model = AccountModel(db_mongo.db)
        ac_status, ac_value = account_model.find_one(
            spec={
                account_model._ID: account_id,
                account_model.CHILD + "." + account_model._ID: ObjectId(child_id)
            }
        )
        if not ac_status:
            return notification.notify_error_db()
        if ac_value is None or len(ac_value) <= 0:
            abort(400)
        if child_id is None or len(child_id) == 0:
            abort(400)
        try:
            file_id_object = ObjectId(file_id)
        except:
            abort(400)

        # Tìm trong image collection đưa ra đường dẫn
        device_id = str(dev_value[DeviceModel.DEVICES][0][DeviceModel._ID])
        return self.save_file(db_mongo, device_id, child_id, file_id)


class ImageListApi(MediaListApi):
    """
    Thực hiện request create
    """
    type_media = "image"

    def create_record(self, db_mongo, device_id, child_id, info_file, version_client):
        super(ImageListApi, self).create_record(db_mongo, device_id, child_id, info_file, version_client)
        abort_if_json_invalid(
            info_file,
            [

                MediaModel.IMAGE_FIELDS["DISPLAY_NAME"],
                MediaModel.IMAGE_FIELDS["DATE_ADDED"],
                MediaModel.IMAGE_FIELDS["SIZE"],
            ]
        )

        info_file[MediaModel.IMAGE_FIELDS["STATUS"]] = 0

        info_file[MediaModel.IMAGE_FIELDS["VERSION"]] = version_client
        info_file[MediaModel.IMAGE_FIELDS["DATA"]] = config.FILE_STORAGE_PATH \
                                                     + "/" + device_id \
                                                     + "/" + child_id \
                                                     + "/" + self.type_media
        object_id = ObjectId()
        info_file[MediaModel._ID] = object_id

        media_model = MediaModel(db_mongo.db)
        status, value = media_model.find_one(
            spec={
                media_model.DEVICE_ID: device_id,
                media_model.CHILD_ID: child_id
            }
        )

        if not status:
            return notification.notify_error_db()

        if value is None or len(value) <= 0:
            in_status, va_status = media_model.insert_one(
                {
                    media_model.DEVICE_ID: device_id,
                    media_model.CHILD_ID: child_id,
                    media_model.IMAGE: [info_file]
                }
            )
            return jsonify(status=1, id=str(object_id))
        else:
            status, value = media_model.find_one(
                spec={
                    media_model.DEVICE_ID: device_id,
                    media_model.CHILD_ID: child_id,
                    media_model.IMAGE + "." + MediaModel.IMAGE_FIELDS["DISPLAY_NAME"]: info_file[
                        MediaModel.IMAGE_FIELDS["DISPLAY_NAME"]],
                    media_model.IMAGE + "." + MediaModel.IMAGE_FIELDS["DATE_ADDED"]: info_file[
                        MediaModel.IMAGE_FIELDS["DATE_ADDED"]],
                    media_model.IMAGE + "." + MediaModel.IMAGE_FIELDS["SIZE"]: info_file[
                        MediaModel.IMAGE_FIELDS["SIZE"]],
                    media_model.IMAGE + "." + MediaModel.IMAGE_FIELDS["STATUS"]: 1,
                }
            )
            if value is None or len(value) <= 0:
                # CHưa có thì add to set
                up_status, up_value = media_model.update_one(
                    {
                        media_model.DEVICE_ID: device_id,
                        media_model.CHILD_ID: child_id,
                    },
                    {
                        '$addToSet': {
                            media_model.IMAGE: info_file
                        }
                    }
                )
                return jsonify(status=1, id=str(object_id))
            else:
                return notification.notify_error_exist();

    def post(self, **kwargs):
        return super(ImageListApi, self).post(**kwargs)


class VideoListApi(MediaListApi):
    """
    Thực hiện request create
    """
    type_media = "video"

    def create_record(self, db_mongo, device_id, child_id, info_file, version_client):
        super(VideoListApi, self).create_record(db_mongo, device_id, child_id, info_file, version_client)
        abort_if_json_invalid(
            info_file,
            [
                MediaModel.VIDEO_FIELDS["DISPLAY_NAME"],
                MediaModel.VIDEO_FIELDS["DATE_ADDED"],
                MediaModel.VIDEO_FIELDS["DURATION"],
                MediaModel.VIDEO_FIELDS["SIZE"],
            ]
        )

        info_file[MediaModel.VIDEO_FIELDS["STATUS"]] = 0

        info_file[MediaModel.VIDEO_FIELDS["VERSION"]] = version_client
        info_file[MediaModel.VIDEO_FIELDS["DATA"]] = config.FILE_STORAGE_PATH \
                                                     + "/" + device_id \
                                                     + "/" + child_id \
                                                     + "/" + self.type_media
        object_id = ObjectId()
        info_file[MediaModel._ID] = object_id

        media_model = MediaModel(db_mongo.db)
        status, value = media_model.find_one(
            spec={
                media_model.DEVICE_ID: device_id,
                media_model.CHILD_ID: child_id
            }
        )

        if not status:
            return notification.notify_error_db()

        if value is None or len(value) <= 0:
            in_status, va_status = media_model.insert_one(
                {
                    media_model.DEVICE_ID: device_id,
                    media_model.CHILD_ID: child_id,
                    media_model.VIDEO: [info_file]
                }
            )
            return jsonify(status=1, id=str(object_id))
        else:
            status, value = media_model.find_one(
                spec={
                    media_model.DEVICE_ID: device_id,
                    media_model.CHILD_ID: child_id,
                    media_model.VIDEO + "." + MediaModel.VIDEO_FIELDS["DISPLAY_NAME"]:
                        info_file[MediaModel.VIDEO_FIELDS["DISPLAY_NAME"]],
                    media_model.VIDEO + "." + MediaModel.VIDEO_FIELDS["DATE_ADDED"]:
                        info_file[MediaModel.VIDEO_FIELDS["DATE_ADDED"]],
                    media_model.VIDEO + "." + MediaModel.VIDEO_FIELDS["DURATION"]:
                        info_file[MediaModel.VIDEO_FIELDS["DURATION"]],
                    media_model.VIDEO + "." + MediaModel.VIDEO_FIELDS["SIZE"]:
                        info_file[MediaModel.VIDEO_FIELDS["SIZE"]],
                    media_model.VIDEO + "." + MediaModel.VIDEO_FIELDS["STATUS"]: 1,
                }
            )
            if value is None or len(value) <= 0:
                # CHưa có thì add to set
                up_status, up_value = media_model.update_one(
                    {
                        media_model.DEVICE_ID: device_id,
                        media_model.CHILD_ID: child_id,
                    },
                    {
                        '$addToSet': {
                            media_model.VIDEO: info_file
                        }
                    }
                )
                return jsonify(status=1, id=str(object_id))
            else:
                return notification.notify_error_exist()

    def post(self, **kwargs):
        return super(VideoListApi, self).post(**kwargs)


class AudioListApi(MediaListApi):
    """
    Thực hiện request create
    """
    type_media = "audio"

    def create_record(self, db_mongo, device_id, child_id, info_file, version_client):
        super(AudioListApi, self).create_record(db_mongo, device_id, child_id, info_file, version_client)
        abort_if_json_invalid(
            info_file,
            [
                MediaModel.AUDIO_FIELDS["DISPLAY_NAME"],
                MediaModel.AUDIO_FIELDS["DATE_ADDED"],
                MediaModel.AUDIO_FIELDS["DURATION"],
                MediaModel.AUDIO_FIELDS["SIZE"],
            ]
        )

        info_file[MediaModel.AUDIO_FIELDS["STATUS"]] = 0
        info_file[MediaModel.AUDIO_FIELDS["VERSION"]] = version_client
        info_file[MediaModel.AUDIO_FIELDS["DATA"]] = config.FILE_STORAGE_PATH \
                                                     + "/" + device_id \
                                                     + "/" + child_id \
                                                     + "/" + self.type_media
        object_id = ObjectId()
        info_file[MediaModel._ID] = object_id

        media_model = MediaModel(db_mongo.db)
        status, value = media_model.find_one(
            spec={
                media_model.DEVICE_ID: device_id,
                media_model.CHILD_ID: child_id
            }
        )

        if not status:
            return notification.notify_error_db()

        if value is None or len(value) <= 0:
            in_status, va_status = media_model.insert_one(
                {
                    media_model.DEVICE_ID: device_id,
                    media_model.CHILD_ID: child_id,
                    media_model.AUDIO: [info_file]
                }
            )
            return jsonify(status=1, id=str(object_id))
        else:
            status, value = media_model.find_one(
                spec={
                    media_model.DEVICE_ID: device_id,
                    media_model.CHILD_ID: child_id,
                    media_model.AUDIO + "." + MediaModel.AUDIO_FIELDS["DISPLAY_NAME"]: info_file[
                        MediaModel.AUDIO_FIELDS["DISPLAY_NAME"]],
                    media_model.AUDIO + "." + MediaModel.AUDIO_FIELDS["DATE_ADDED"]: info_file[
                        MediaModel.AUDIO_FIELDS["DATE_ADDED"]],
                    media_model.AUDIO + "." + MediaModel.AUDIO_FIELDS["SIZE"]: info_file[
                        MediaModel.AUDIO_FIELDS["SIZE"]],
                    media_model.AUDIO + "." + MediaModel.AUDIO_FIELDS["DURATION"]: info_file[
                        MediaModel.AUDIO_FIELDS["DURATION"]],
                    media_model.AUDIO + "." + MediaModel.AUDIO_FIELDS["STATUS"]: 1,
                }
            )
            if value is None or len(value) <= 0:
                # CHưa có thì add to set
                up_status, up_value = media_model.update_one(
                    {
                        media_model.DEVICE_ID: device_id,
                        media_model.CHILD_ID: child_id,
                    },
                    {
                        '$addToSet': {
                            media_model.AUDIO: info_file
                        }
                    }
                )
                return jsonify(status=1, id=str(object_id))
            else:
                return notification.notify_error_db()

    def post(self, **kwargs):
        return super(AudioListApi, self).post(**kwargs)


class ImageApi(MediaApi):
    type_media = "image"

    def save_file(self, db_mongo, device_id, child_id, file_id):
        super(ImageApi, self).save_file(db_mongo, device_id, child_id, file_id)

        media_model = MediaModel(db_mongo.db)

        im_status, im_value = media_model.find(
            {
                media_model.CHILD_ID: child_id,
                media_model.DEVICE_ID: device_id,
            },
            {
                '_id': 0,
                media_model.IMAGE: {'$elemMatch': {media_model._ID: ObjectId(file_id)}}
            }
        )

        data_retrive = None
        for item in im_value:
            data_retrive = item;
            break;
        if data_retrive is None:
            return notification.notify_error_db()
        data = data_retrive[media_model.IMAGE][0][media_model.IMAGE_FIELDS["DATA"]]
        display_name = data_retrive[media_model.IMAGE][0][media_model.IMAGE_FIELDS["DISPLAY_NAME"]]
        id = data_retrive[media_model.IMAGE][0][media_model._ID]

        # check file exist

        display_name = secure_filename(display_name)

        if os.path.exists(os.path.join(data, display_name)):
            if display_name.rfind('.') != -1:
                # co ky tu '.'
                extension_file = display_name[(display_name.rfind('.')) + 1:]
                head_file = display_name[:(display_name.rfind('.'))]
            else:
                head_file = display_name
                extension_file = ""
            i = 1;
            while os.path.exists(os.path.join(data, display_name)):
                display_name = head_file + "-" + str(i) + "." + extension_file
                i += 1

        # Chuyển trạng thái của file trong image
        content = request.files['file'].read()
        CloudStorageManager().create_file(data + "/" + id, content)

        # XXX : Thay the dung google cloud storage
        # if not os.path.exists(data):
        #     os.makedirs(data)
        #
        # content.save(data + "/" + display_name)
        # Cap nhat thong tin
        media_model.update_one(
            {
                media_model.CHILD_ID: child_id,
                media_model.DEVICE_ID: device_id,
                media_model.IMAGE + "." + media_model._ID: ObjectId(file_id)
            },
            {
                '$set': {
                    media_model.IMAGE + ".$." + media_model.IMAGE_FIELDS["DISPLAY_NAME"]: display_name,
                    media_model.IMAGE + ".$." + media_model.IMAGE_FIELDS["STATUS"]: 1,
                }
            }
        )
        self.update_version(db_mongo, device_id, child_id,
                            data_retrive[media_model.IMAGE][0][media_model.IMAGE_FIELDS["VERSION"]],
                            VersionModel.IMAGE_VERSION);
        db_mongo.close_db()
        return jsonify(status=1)

    def put(self, file_id):
        return super(ImageApi, self).put(file_id)


class AudioApi(MediaApi):
    type_media = "audio"

    def save_file(self, db_mongo, device_id, child_id, file_id):
        super(AudioApi, self).save_file(db_mongo, device_id, child_id, file_id)

        media_model = MediaModel(db_mongo.db)

        im_status, im_value = media_model.find(
            {
                media_model.CHILD_ID: child_id,
                media_model.DEVICE_ID: device_id,
            },
            {
                '_id': 0,
                media_model.AUDIO: {'$elemMatch': {media_model._ID: ObjectId(file_id)}}
            }
        )
        data_retrive = []
        for item in im_value:
            data_retrive = item;
            break;
        if len(data_retrive) <= 0:
            return notification.notify_error_db()
        data = data_retrive[media_model.AUDIO][0][media_model.AUDIO_FIELDS["DATA"]]
        display_name = data_retrive[media_model.AUDIO][0][media_model.AUDIO_FIELDS["DISPLAY_NAME"]]
        id = data_retrive[media_model.AUDIO][0][media_model._ID]

        # check file exist
        i = 1;
        display_name = secure_filename(display_name)
        while os.path.exists(os.path.join(data, display_name)):

            if display_name.rfind('.') != -1:
                # co ky tu '.'
                extension_file = display_name[(display_name.rfind('.')) + 1:]

                head_file = display_name[:(display_name.rfind('.'))]
                head_file += "-" + str(i)
                display_name = head_file + "." + extension_file
            else:
                display_name += "-" + str(i)
            i += 1

        # Chuyển trạng thái của file trong image

        # content = request.files['file']
        # if not os.path.exists(data):
        #     os.makedirs(data)
        #
        # content.save(data + "/" + display_name)

        content = request.files['file'].read()
        CloudStorageManager().create_file(data + "/" + id, content)

        # Cap nhat thong tin
        media_model.update_one(
            {
                media_model.CHILD_ID: child_id,
                media_model.DEVICE_ID: device_id,
                media_model.AUDIO + "." + media_model._ID: ObjectId(file_id)
            },
            {
                '$set': {
                    media_model.AUDIO + ".$." + media_model.AUDIO_FIELDS["DISPLAY_NAME"]: display_name,
                    media_model.AUDIO + ".$." + media_model.AUDIO_FIELDS["STATUS"]: 1,
                }
            }
        )
        self.update_version(db_mongo, device_id, child_id,
                            data_retrive[media_model.AUDIO][0][media_model.AUDIO_FIELDS["VERSION"]],
                            VersionModel.AUDIO_VERSION);

        db_mongo.close_db()
        return jsonify(status=1)

    def put(self, file_id):
        return super(AudioApi, self).put(file_id)


class VideoApi(MediaApi):
    type_media = ""

    def save_file(self, db_mongo, device_id, child_id, file_id):
        super(VideoApi, self).save_file(db_mongo, device_id, child_id, file_id)

        media_model = MediaModel(db_mongo.db)

        im_status, im_value = media_model.find(
            {
                media_model.CHILD_ID: child_id,
                media_model.DEVICE_ID: device_id,
            },
            {
                '_id': 0,
                media_model.VIDEO: {'$elemMatch': {media_model._ID: ObjectId(file_id)}}
            }
        )
        data_retrive = []
        for item in im_value:
            data_retrive = item;
            break;
        if len(data_retrive) <= 0:
            return notification.notify_error_db()
        data = data_retrive[media_model.VIDEO][0][media_model.VIDEO_FIELDS["DATA"]]
        display_name = data_retrive[media_model.VIDEO][0][media_model.VIDEO_FIELDS["DISPLAY_NAME"]]
        display_name = data_retrive[media_model.VIDEO][0][media_model._ID]

        # check file exist
        i = 1;
        display_name = secure_filename(display_name)
        while os.path.exists(os.path.join(data, display_name)):

            if display_name.rfind('.') != -1:
                # co ky tu '.'
                extension_file = display_name[display_name.rfind('.') + 1:]

                head_file = display_name[:(display_name.rfind('.'))]
                head_file += "-" + str(i)
                display_name = head_file + "." + extension_file
            else:
                display_name += "-" + str(i)
            i += 1

        # Chuyển trạng thái của file trong video

        # content = request.files['file']
        # if not os.path.exists(data):
        #     os.makedirs(data)
        #
        # content.save(data + "/" + display_name)

        content = request.files['file'].read()
        CloudStorageManager().create_file(data + "/" + id, content)

        # Cap nhat thong tin
        media_model.update_one(
            {
                media_model.CHILD_ID: child_id,
                media_model.DEVICE_ID: device_id,
                media_model.VIDEO + "." + media_model._ID: ObjectId(file_id)
            },
            {
                '$set': {
                    media_model.VIDEO + ".$." + media_model.VIDEO_FIELDS["DISPLAY_NAME"]: display_name,
                    media_model.VIDEO + ".$." + media_model.VIDEO_FIELDS["STATUS"]: 1,
                }
            }
        )
        self.update_version(db_mongo, device_id, child_id,
                            data_retrive[media_model.VIDEO][0][media_model.VIDEO_FIELDS["VERSION"]],
                            VersionModel.VIDEO_VERSION);

        db_mongo.close_db()
        return jsonify(status=1)

    def put(self, file_id):
        return super(VideoApi, self).put(file_id)


# -----------------------------------------------------
# ----------------                      ---------------
# ----------------  DOWNLOAD JSON       ---------------
# ----------------                      ---------------
# -----------------------------------------------------

class DownloadJsonApi(Resource):
    version_client = None
    ACTION_ADD = "add"
    ACTION_DELETE = "delete"
    ACTION_UPDATE = "update"
    ACTION_KEY = "action"

    @require_api_key
    @auth_child_and_device
    def post(self, **kwargs):
        """Lấy json"""
        db_mongo = kwargs['db_mongo']
        # dev_value = kwargs['dev_value']
        # device_model = kwargs['device_model']
        child_id = kwargs[notification.PARAMS["child_id"]]
        device_id = kwargs[notification.PARAMS["device_id"]]
        json_data = kwargs['json_data']
        # child_id = json_data[notification.PARAMS["child_id"]]
        version_client = json_data[notification.PARAMS["version"]]
        # device_id = json_data[notification.PARAMS["device_id"]]
        #
        # # Check childid
        # account_id = dev_value[device_model.ACCOUNT_ID]
        # account_model = AccountModel(db_mongo.db)
        # ac_status, ac_value = account_model.find_one(
        #     spec={
        #         account_model._ID: account_id,
        #         account_model.CHILD + "." + account_model._ID: ObjectId(child_id)
        #     }
        # )
        # if not ac_status:
        #     return notification.notify_error_db()
        # if ac_value is None or len(ac_value) <= 0:
        #     abort(400)
        # if child_id is None or len(child_id) == 0:
        #     abort(400)
        #
        #     # check device_id
        #     # Kiểm tra device id có phaỉ là của child id này không,
        #     # Trạng thái có đăng nhập
        # status_check_device_id, value_check_device_id = device_model.find_one(
        #     spec={
        #         DeviceModel.ACCOUNT_ID: account_id,
        #         DeviceModel.DEVICES + "." + DeviceModel._ID: ObjectId(device_id),
        #         DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.CHILD_ID: child_id,
        #         DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_CHILD,
        #         DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.LATEST_LOGIN: DeviceModel.LATEST_LOGIN_TRUE
        #     }
        # )
        # if value_check_device_id is None or len(value_check_device_id) == 0:
        #     abort(400)

        ids = json_data[notification.PARAMS["data"]]
        return self.retrieve_item(db_mongo, device_id, child_id, ids, version_client);

    @abc.abstractmethod
    def retrieve_item(self, db_mongo, device_id, child_id, ids, version_client):
        return


class SmsDownloader(DownloadJsonApi):
    def post(self, **kwargs):
        return super(SmsDownloader, self).post(**kwargs)

    def retrieve_item(self, db_mongo, device_id, child_id, ids, version_client):
        super(SmsDownloader, self).retrieve_item(db_mongo, device_id, child_id, ids, version_client)
        sms_model = SmsModel(db_mongo.db);

        ids.sort(key=lambda k: str(k[sms_model._ID]), reverse=False)
        print "retrieve_item" + device_id;
        status, value = sms_model.find_one(
            spec={
                sms_model.DEVICE_ID: device_id,
                sms_model.CHILD_ID: child_id
            }
        )
        if not status:
            return notification.notify_error_db()
        if value is None:
            return jsonify(status=1, data=[])
        sms_array = value[sms_model.SMS]
        sms_array.sort(key=lambda k: str(k[sms_model._ID]), reverse=False)

        index_client = 0
        size_client = len(ids)
        index_server = 0
        size_server = len(sms_array);
        result_action = []
        while index_client < size_client and index_server < size_server:
            item = sms_array[index_server];
            id_server = str(item["_id"])
            # Chuyển object id thành string
            item[sms_model._ID] = id_server
            id_client = ids[index_client]["_id"];
            if id_client == id_server:
                index_client += 1
                index_server += 1
            elif id_client < id_server:
                index_client += 1
                result_action.append({ACTION["action"]: ACTION["delete"], SmsModel._ID: id_client})
            elif id_client > id_server:
                item[ACTION["action"]] = ACTION["add"]
                index_server += 1
                result_action.append(item)

        while index_client < size_client:
            result_action.append({SmsModel._ID: ids[index_client]["_id"], ACTION["action"]: ACTION["delete"]})
            index_client += 1

        while index_server < size_server:
            item = sms_array[index_server];

            item[ACTION["action"]] = ACTION["add"]
            item["id_server"] = str(item["_id"])
            item.pop("_id")
            item.pop(notification.PARAMS["version"])

            result_action.append(item)
            index_server += 1
        for item in result_action:
            print item;
        return jsonify(status=1, data=result_action)


class CallLogDownloader(DownloadJsonApi):
    def post(self, **kwargs):
        return super(CallLogDownloader, self).post(**kwargs)

    def retrieve_item(self, db_mongo, device_id, child_id, ids, version_client):
        super(CallLogDownloader, self).retrieve_item(db_mongo, device_id, child_id, ids, version_client)
        call_log_model = CallLogModel(db_mongo.db);

        ids.sort(key=lambda k: str(k[call_log_model._ID]), reverse=False)
        print "retrieve_item" + device_id;
        status, value = call_log_model.find_one(
            spec={
                call_log_model.DEVICE_ID: device_id,
                call_log_model.CHILD_ID: child_id
            }
        )
        if not status:
            return notification.notify_error_db()
        if value is None:
            return jsonify(status=1, data=[])
        call_log_array = value[call_log_model.COLLECTION_NAME]
        call_log_array.sort(key=lambda k: str(k[call_log_model._ID]), reverse=False)

        index_client = 0
        size_client = len(ids)
        index_server = 0
        size_server = len(call_log_array);
        result_action = []
        while index_client < size_client and index_server < size_server:
            item = call_log_array[index_server];
            id_server = str(item["_id"])
            # Chuyển object id thành string
            item[call_log_model._ID] = id_server
            id_client = ids[index_client]["_id"];
            if id_client == id_server:
                # if self.version_client != item[call_log_model.VERSION]:
                #     item[ACTION["action"]] = ACTION["update"]
                #     result_action.append(item)
                # else:
                #     """Trong truong hop giong nhau thi ko can action gi ca"""
                index_client += 1
                index_server += 1
            elif id_client < id_server:
                index_client += 1
                result_action.append({ACTION["action"]: ACTION["delete"], CallLogModel._ID: id_client})
            elif id_client > id_server:
                item[ACTION["action"]] = ACTION["add"]
                item["id_server"] = str(item["_id"])
                item.pop("_id")
                index_server += 1
                result_action.append(item)

        while index_client < size_client:
            result_action.append({CallLogModel._ID: ids[index_client], ACTION["action"]: ACTION["delete"]})
            index_client += 1

        while index_server < size_server:
            item = call_log_array[index_server];

            item[ACTION["action"]] = ACTION["add"]
            item["id_server"] = str(item["_id"])
            item.pop("_id")
            item.pop(notification.PARAMS["version"])

            result_action.append(item)
            index_server += 1
        for item in result_action:
            print item;
        return jsonify(status=1, data=result_action)


# --------------------------------------------------
# ---------------                         ----------
# -------------- GET FILE NEED DOWNLOAD   ----------
# ---------------                          ---------
# --------------------------------------------------

class FileNeedDownload(Resource):
    def get_ids_server(self, db_mongo, device_id, child_id, ids):
        """
        Trả vê danh sách id đã được sắp xếp lớn dần
        :return: staus,value
        if status = true, value is array is sorted
        otherwise status = fale, value is id error
        """
        return

    @require_api_key
    @auth_child_and_device
    def post(self, *args, **kwargs):
        db_mongo = kwargs['db_mongo']
        device_id = kwargs[notification.PARAMS["device_id"]]
        child_id = kwargs[notification.PARAMS["child_id"]]
        json_data = kwargs[notification.PARAMS["json_data"]]

        ids = json_data[notification.PARAMS["data"]]
        ids.sort(key=lambda k: str(k["_id"]), reverse=False)

        # lâý ids từ server
        status, value = self.get_ids_server(db_mongo, device_id, child_id, ids)
        if not status:
            return value

        id_array = value
        id_array.sort(key=lambda k: str(k[SmsModel._ID]), reverse=False)

        index_client = 0
        size_client = len(ids)
        index_server = 0
        size_server = len(id_array);
        result_action = []
        while index_client < size_client and index_server < size_server:
            item = id_array[index_server]
            id_server = str(item["_id"])
            # Chuyển object id thành string, chuyen key _id thanh id_server
            item[SmsModel._ID] = id_server
            id_client = ids[index_client]["_id"]
            if id_client == id_server:
                # if self.version_client != item[sms_model.VERSION]:
                #     item[ACTION["action"]] = ACTION["update"]
                #     result_action.append(item)
                # else:
                #     """Trong truong hop giong nhau thi ko can action gi ca"""
                index_client += 1
                index_server += 1
            elif id_client < id_server:
                index_client += 1
                result_action.append({ACTION["action"]: ACTION["delete"], SmsModel._ID: id_client})
            elif id_client > id_server:
                item[ACTION["action"]] = ACTION["add"]
                index_server += 1
                result_action.append(item)

        while index_client < size_client:
            result_action.append({SmsModel._ID: ids[index_client]["_id"], ACTION["action"]: ACTION["delete"]})
            index_client += 1

        while index_server < size_server:
            item = id_array[index_server];
            item[ACTION["action"]] = ACTION["add"]
            item["_id"] = str(item["_id"])
            item.pop(notification.PARAMS["version"])

            result_action.append(item)
            index_server += 1
        for item in result_action:
            print item;
        return jsonify(status=1, data=result_action)

    def merger(self, db_mongo, device_id, child_id, ids):
        return


class ImageNeedDownload(FileNeedDownload):
    def merger(self, db_mongo, device_id, child_id, ids):
        super(ImageNeedDownload, self).merger(db_mongo, device_id, child_id, ids)

    def get_ids_server(self, db_mongo, device_id, child_id, ids):
        super(ImageNeedDownload, self).get_ids_server(db_mongo, device_id, child_id, ids)
        media_model = MediaModel(db_mongo.db)
        status, value = media_model.find_one(
            spec={
                media_model.DEVICE_ID: device_id,
                media_model.CHILD_ID: child_id
            }
        )
        if not status:
            return False, notification.notify_error_db()
        if value is None:
            return False, jsonify(status=1, data=[])
        id_array = value[media_model.IMAGE]
        for item in id_array:
            # Những trường này không gửi về cl
            item.pop(media_model.IMAGE_FIELDS["DATA"])
            item.pop(media_model.IMAGE_FIELDS["STATUS"])

        id_array.sort(key=lambda k: str(k[media_model._ID]), reverse=False)
        return True, id_array


class AudioNeedDownload(FileNeedDownload):
    def post(self, *args, **kwargs):
        return super(AudioNeedDownload, self).post(*args, **kwargs)

    def get_ids_server(self, db_mongo, device_id, child_id, ids):
        super(AudioNeedDownload, self).get_ids_server(db_mongo, device_id, child_id, ids)
        media_model = MediaModel(db_mongo.db)
        status, value = media_model.find_one(
            spec={
                media_model.DEVICE_ID: device_id,
                media_model.CHILD_ID: child_id
            }
        )
        if not status:
            return False, notification.notify_error_db()
        if value is None:
            return False, jsonify(status=1, data=[])
        id_array = value[media_model.AUDIO]
        for item in id_array:
            # Những trường này không gửi về cl
            item.pop(media_model.AUDIO_FIELDS["DATA"])
            item.pop(media_model.AUDIO_FIELDS["STATUS"])
        id_array.sort(key=lambda k: str(k[media_model._ID]), reverse=False)
        return True, id_array


class VideoNeedDownload(FileNeedDownload):
    def post(self, *args, **kwargs):
        return super(VideoNeedDownload, self).post(*args, **kwargs)

    def get_ids_server(self, db_mongo, device_id, child_id, ids):
        super(VideoNeedDownload, self).get_ids_server(db_mongo, device_id, child_id, ids)
        media_model = MediaModel(db_mongo.db)
        status, value = media_model.find_one(
            spec={
                media_model.DEVICE_ID: device_id,
                media_model.CHILD_ID: child_id
            }
        )
        if not status:
            return False, notification.notify_error_db()
        if value is None:
            return False, jsonify(status=1, data=[])
        id_array = value[media_model.VIDEO]
        for item in id_array:
            # Những trường này không gửi về cl
            item.pop(media_model.VIDEO_FIELDS["DATA"])
            item.pop(media_model.VIDEO_FIELDS["STATUS"])

        id_array.sort(key=lambda k: str(k[media_model._ID]), reverse=False)
        return True, id_array


# -----------------------------------------------------------
# ---------------------                  --------------------
# ---------------------  DOWNLOAD  FILE  --------------------
# ---------------------                  --------------------
# -----------------------------------------------------------

class FileDownload(Resource):
    @abc.abstractmethod
    def check_file_id(self, db_mongo, device_id, child_id, file_id):
        return

    @require_api_key
    @auth_child_and_device
    def post(self, *args, **kwargs):
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']
        device_id = kwargs[notification.PARAMS["device_id"]]
        child_id = kwargs[notification.PARAMS["child_id"]]
        # Kiểm tra file_id
        file_id = json_data[notification.PARAMS["file_id"]]
        status, record = self.check_file_id(db_mongo, device_id, child_id, file_id)
        if status:
            data = record[MediaModel.IMAGE_FIELDS["DATA"]];
            display_name = record[MediaModel.IMAGE_FIELDS["DISPLAY_NAME"]];
            id_record = record[MediaModel._ID];
            file_path = data + "/" + id_record
            return send_file(file_path)
        else:
            abort(400)


class ImageDownload(FileDownload):
    def post(self, *args, **kwargs):
        return super(ImageDownload, self).post(*args, **kwargs)

    def check_file_id(self, db_mongo, device_id, child_id, file_id):
        super(ImageDownload, self).check_file_id(db_mongo, device_id, child_id, file_id)

        media_model = MediaModel(db_mongo.db);
        status_check, value_check = media_model.find_one(
            spec={
                MediaModel.DEVICE_ID: device_id,
                MediaModel.CHILD_ID: child_id,
                MediaModel.IMAGE + "." + MediaModel._ID: ObjectId(file_id)
            },
            fields={
                MediaModel.IMAGE: {'$elemMatch': {MediaModel._ID: ObjectId(file_id)}}
            }
        )
        if status_check:
            if value_check is not None and len(value_check) > 0:
                return True, value_check[MediaModel.IMAGE][0]
            else:
                return False, None
        else:
            return False, None


class VideoDownload(FileDownload):
    def post(self, *args, **kwargs):
        return super(VideoDownload, self).post(*args, **kwargs)

    def check_file_id(self, db_mongo, device_id, child_id, file_id):
        super(VideoDownload, self).check_file_id(db_mongo, device_id, child_id, file_id)

        media_model = MediaModel(db_mongo.db);
        status_check, value_check = media_model.find_one(
            spec={
                MediaModel.DEVICE_ID: device_id,
                MediaModel.CHILD_ID: child_id,
                MediaModel.VIDEO + "." + MediaModel._ID: ObjectId(file_id)
            },
            fields={
                MediaModel.VIDEO: {'$elemMatch': {MediaModel._ID: ObjectId(file_id)}}
            }
        )
        if status_check:
            if value_check is not None and len(value_check) > 0:
                return True, value_check[MediaModel.VIDEO][0]
            else:
                return False, None
        else:
            return False, None


class AudioDownload(FileDownload):
    def post(self, *args, **kwargs):
        return super(AudioDownload, self).post(*args, **kwargs)

    def check_file_id(self, db_mongo, device_id, child_id, file_id):
        super(AudioDownload, self).check_file_id(db_mongo, device_id, child_id, file_id)

        media_model = MediaModel(db_mongo.db);
        status_check, value_check = media_model.find_one(
            spec={
                MediaModel.DEVICE_ID: device_id,
                MediaModel.CHILD_ID: child_id,
                MediaModel.AUDIO + "." + MediaModel._ID: ObjectId(file_id)
            },
            fields={
                MediaModel.AUDIO: {'$elemMatch': {MediaModel._ID: ObjectId(file_id)}}
            }
        )
        if status_check:
            if value_check is not None and len(value_check) > 0:
                return True, value_check[MediaModel.AUDIO][0]
            else:
                return False, None
        else:
            return False, None


def register_extra(app):
    api_version1 = config.API_VERSION

    @app.route(api_version1 + "/check_token", methods=["POST"])
    def check_token():
        if request.method == 'GET':
            token = request.values[notification.PARAMS["token"]]
            imei = request.values[notification.PARAMS["imei"]]
            device_name = request.values[notification.PARAMS["device_name"]]
        else:
            json_data = request.get_json(force=True)
            token = json_data[notification.PARAMS["token"]]
            imei = json_data[notification.PARAMS["imei"]]
            device_name = json_data[notification.PARAMS["device_name"]]
        db_mongo = DbMongo()
        db_mongo.connect_db()
        device_model = DeviceModel(db_mongo.db)
        dev_status, dev_value = device_model.is_login_now(token, imei, device_name)

        # Lỗi query db là trả về lỗi luôn
        if not dev_status:
            db_mongo.close_db()
            return notification.notify_error_db()

        # Kiểm tra đăng nhập
        if dev_value is None or len(dev_value) == 0:
            db_mongo.close_db()
            return notification.notify_error_auth()
        else:
            db_mongo.close_db()
            return jsonify(status=1)

    @app.route(api_version1 + "/sync_account", methods=["POST"])
    @require_api_key
    def sync_account_child(**kwargs):
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']
        token = json_data[notification.PARAMS["token"]]
        imei = json_data[notification.PARAMS["imei"]]
        device_name = json_data[notification.PARAMS["device_name"]]

        # Khi dang nhap thanh cong roi
        privilege = json_data[notification.PARAMS["privilege"]]
        if privilege == notification.PRIVILEGE_TYPE["parent"]:
            # Neu tai khoan vua chon la parent
            # TODO Them thiet bi can gui notification
            device_model.update_one(
                {
                    DeviceModel.ACCOUNT_ID: dev_value[DeviceModel.ACCOUNT_ID],
                    DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.IMEI: imei,
                    DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.DEVICE_NAME: device_name,
                    DeviceModel.DEVICES + "." + DeviceModel.TOKEN: token,
                },
                {
                    '$set': {
                        DeviceModel.DEVICES + ".$." + DeviceModel.PRIVILEGE: {
                            DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_PARENT,
                        }
                    }
                }
            )
            return jsonify(status=1)
        elif privilege == notification.PRIVILEGE_TYPE["child"]:
            # Neu do la tai khoan tre con, logout cac tai khoan khac
            child_id = json_data[notification.PARAMS["child_id"]]
            device_model.update_many(
                {
                    DeviceModel.ACCOUNT_ID: dev_value[DeviceModel.ACCOUNT_ID],
                    DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_CHILD,
                    DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.CHILD_ID: child_id,
                },
                {
                    '$set': {
                        DeviceModel.DEVICES + ".$." + DeviceModel.STATUS: DeviceModel.STATUS_LOGOUT,
                        DeviceModel.DEVICES + ".$." + DeviceModel.PRIVILEGE + "." + DeviceModel.LATEST_LOGIN: DeviceModel.LATEST_LOGIN_FALSE

                    }
                }
            )
            device_model.update_one(
                {
                    DeviceModel.ACCOUNT_ID: dev_value[DeviceModel.ACCOUNT_ID],
                    DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.IMEI: imei,
                    DeviceModel.DEVICES + "." + DeviceModel.INFOR + "." + DeviceModel.DEVICE_NAME: device_name,
                    DeviceModel.DEVICES + "." + DeviceModel.TOKEN: token,
                },
                {
                    '$set': {
                        DeviceModel.DEVICES + ".$." + DeviceModel.STATUS: DeviceModel.STATUS_LOGIN,
                        DeviceModel.DEVICES + ".$." + DeviceModel.PRIVILEGE: {
                            DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_CHILD,
                            DeviceModel.CHILD_ID: child_id,
                            DeviceModel.LATEST_LOGIN: DeviceModel.LATEST_LOGIN_TRUE
                        }
                    }
                }
            )
            return jsonify(status=1)
        return jsonify(status=0)
        # Logout cac thiet bi khac,

    @app.route(api_version1 + "/get_latest_device_child", methods=["POST"])
    @require_api_key
    def get_latest_device(**kwargs):
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        json_data = kwargs['json_data']

        child_id = json_data[notification.PARAMS["child_id"]]
        # Authen child
        account_id = dev_value[device_model.ACCOUNT_ID]
        account_model = AccountModel(db_mongo.db)
        ac_status, ac_value = account_model.find_one(
            spec={
                account_model._ID: account_id,
                account_model.CHILD + "." + account_model._ID: ObjectId(child_id),

            }
        )
        if not ac_status:
            return notification.notify_error_db()
        if ac_value is None or len(ac_value) <= 0:
            abort(400)
        if child_id is None or len(child_id) == 0:
            abort(400)

        latest_device_status, latest_device_value = device_model.find_one(
            spec={
                DeviceModel.ACCOUNT_ID: account_id,
                DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.PRIVILEGE_TYPE: DeviceModel.PRIVILEGE_CHILD,
                DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.CHILD_ID: child_id,
                DeviceModel.DEVICES + "." + DeviceModel.PRIVILEGE + "." + DeviceModel.LATEST_LOGIN: DeviceModel.LATEST_LOGIN_TRUE
            },
            fields={
                DeviceModel.ACCOUNT_ID: 1,
                DeviceModel.DEVICES: {
                    '$elemMatch': {
                        DeviceModel.PRIVILEGE + "." + DeviceModel.LATEST_LOGIN: DeviceModel.LATEST_LOGIN_TRUE
                    }
                }
            }
        )
        if latest_device_value is not None and len(latest_device_value[DeviceModel.DEVICES]) > 0:
            latest_device_id = str(latest_device_value[DeviceModel.DEVICES][0][DeviceModel._ID])
            return jsonify(status=1, is_have=1, device_id=latest_device_id)
        else:
            return jsonify(status=1, is_have=0, device_id="no_login_before")

    @app.route(api_version1 + '/return-files/')
    def return_files():
        try:
            return send_file('/var/www/PythonProgramming/PythonProgramming/static/images/python.jpg',
                             attachment_filename='python.jpg')
        except Exception as e:
            return str(e)

    @app.route(api_version1 + '/request_location', methods=['POST'])
    @require_api_key
    def request_location(*args, **kwargs):
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        token = kwargs['token']
        device_name = kwargs['device_name']
        imei = kwargs['imei']
        json_data = kwargs['json_data']
        child_id = json_data[notification.PARAMS["child_id"]]
        # Lay fcm_token
        status, value = device_model.find_one(
            spec={
                DeviceModel.ACCOUNT_ID: dev_value[DeviceModel.ACCOUNT_ID],
                DeviceModel.DEVICES + "." + DeviceModel.STATUS: DeviceModel.STATUS_LOGIN,
            },
            fields={
                DeviceModel.DEVICES: {
                    '$elemMatch': {
                        DeviceModel.STATUS: DeviceModel.STATUS_LOGIN,
                        DeviceModel.PRIVILEGE + "." + DeviceModel.CHILD_ID: child_id,
                    }
                }
            }
        )
        db_mongo.close_db()
        if value is not None and len(value) > 0:
            print "ok, send token"
            token_fcm = value[DeviceModel.DEVICES][0][DeviceModel.TOKEN_FCM];
            device_id = str(dev_value[DeviceModel.DEVICES][0][DeviceModel._ID])
            FCMRequest().send_request_location(token_fcm, device_id);
            return jsonify(status=1)
        else:
            return jsonify(status=0, msg="device not found");

    @app.route(api_version1 + '/location', methods=["POST"])
    @require_api_key
    def child_location(**kwargs):
        """ Child gui vi tri hien tai """
        db_mongo = kwargs['db_mongo']
        dev_value = kwargs['dev_value']
        device_model = kwargs['device_model']
        token = kwargs['token']
        device_name = kwargs['device_name']
        imei = kwargs['imei']
        json_data = kwargs['json_data']
        lat_location = json_data[notification.PARAMS["lat_location"]]
        long_location = json_data[notification.PARAMS["long_location"]]
        device_id = json_data[notification.PARAMS["device_id"]]
        print "device_id receive" + device_id;
        status, value = device_model.find_one(
            spec={
                DeviceModel.ACCOUNT_ID: dev_value[DeviceModel.ACCOUNT_ID]
            },
            fields={
                DeviceModel.DEVICES: {'$elemMatch': {DeviceModel._ID: ObjectId(device_id)}}
            }
        )
        token_fcm = value[DeviceModel.DEVICES][0][DeviceModel.TOKEN_FCM]
        print "token_fcm to respond" + token_fcm

        respond = FCMRequest().send_respond_location(token_fcm, lat_location, long_location)
        print respond

        print str(lat_location) + "," + str(long_location)
        db_mongo.close_db()
        return jsonify(status=1)

    # ---------------------------------------------------
    # --------------                      ---------------
    # ------------   GOOGLE CLOUD STORE TEST  ---------------
    # -------------                       ---------------
    # ---------------------------------------------------


    @app.route(api_version1 + '/save_file', methods=["POST", "PUT"])
    def save_file():
        data = request.form['data']
        print data

        content = request.files['file'].read()
        print content
        print "receive_finish"
        CloudStorageManager().create_file_content("/app_default_bucket/th", content)
        return jsonify(status=1)

    @app.route(api_version1 + '/send_file', methods=["POST", "PUT"])
    def send_file():
        content = CloudStorageManager().read_file("/app_default_bucket/th")
        print content
        return content;
