# -*- coding: utf-8 -*-

__author__ = 'ThangLD'
import abc

import notification
from bson import ObjectId
from db.db import DbMongo, Version
from flask import jsonify
from flask_restful import Resource, request
from model.model_db import DeviceModel, AccountModel, VersionModel


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
        device_model = DeviceModel(db_mongo.db)
        account_model = AccountModel(db_mongo.db)
        # Tìm trong db
        ac_status, ac_value = account_model.auth(email, password)
        if not ac_status:
            db_mongo.close_db()
            return notification.notify_db_error()

        if ac_value is not None and len(ac_value) > 0:
            # Nếu tài khoản tồn tại
            # danh sách các thiết bị đăng nhập

            dev_status, dev_value = device_model.find_one(spec={
                device_model.ACCOUNT_ID: ac_value[account_model._ID],
                device_model.DEVICES + "." + device_model.INFOR + "." + device_model.IMEI: imei,
                device_model.DEVICES + "." + device_model.INFOR + "." + device_model.DEVICE_NAME: device_name,
            })
            if not dev_status:
                # query db mà lỗi là trả về lỗi luôn
                db_mongo.close_db()
                return notification.notify_db_error()

            token = device_model.generate_token()
            if dev_value is not None and len(dev_value) > 0:
                # Đã đăng nhập từ trước, chỉ cập nhật thôi
                status, value = device_model.update_one(
                    {
                        device_model.ACCOUNT_ID: ac_value[account_model._ID],
                        device_model.DEVICES + "." + device_model.INFOR + "." + device_model.IMEI: imei,
                        device_model.DEVICES + "." + device_model.INFOR + "." + device_model.DEVICE_NAME: device_name
                    },
                    {
                        '$set': {
                            device_model.DEVICES + ".$." + device_model.PRIVILEGE: device_model.PRIVILEGE_UNKNOWN,
                            device_model.DEVICES + ".$." + device_model.TOKEN: token,
                            device_model.DEVICES + ".$." + device_model.STATUS: device_model.STATUS_LOGIN
                        }
                    }, True
                )
                db_mongo.close_db()
                if not status:
                    return notification.notify_db_error()
            else:
                # Nếu thiết bị chưa được đăng nhập lần nào
                # THêm thiết bị vào màng devices trong db
                status, value = device_model.insert_one(
                    {
                        device_model.ACCOUNT_ID: ac_value[account_model._ID],
                        device_model.DEVICES: [
                            {
                                device_model.INFOR: {
                                    device_model.IMEI: imei,
                                    device_model.DEVICE_NAME: device_name
                                },
                                device_model.PRIVILEGE: {
                                    device_model.PRIVILEGE_TYPE: device_model.PRIVILEGE_UNKNOWN
                                },
                                device_model.TOKEN: token,
                                device_model.STATUS: device_model.STATUS_LOGIN
                            }
                        ]
                    }
                )
                db_mongo.close_db()
                if not status:
                    return notification.notify_db_error()
            # Gửi về status và token.
            # Nếu cập nhật không thành công
            return {"status": '1', "token": token}
        else:  # Thông báo user hoặc mật khẩu không đúng
            db_mongo.close_db()
            return {"status": "0", "msg": "error_1"}


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
            spec={
                account_model.PARENT + "." + account_model.EMAIL: email,
            },
            fields={account_model._ID: 1})

        if not status:
            db_mongo.close_db()
            return notification.notify_db_error()

        if value is not None and len(value) > 0:
            # Nếu email đã tồn tại
            db_mongo.close_db()
            return {"status": "0", "msg": "error_1"}
        else:
            # Nếu email chưa tồn tại, thêm vào csdl
            status, value = account_model.insert_one({
                account_model.PARENT: {
                    account_model.PROFILE_ID: ObjectId(),
                    account_model.EMAIL: email,
                    account_model.PASSWORD: password,
                    account_model.FULL_NAME: full_name
                }
            })
            db_mongo.close_db()
            if not status:
                return notification.notify_db_error()
            return {"status": "1"}


class ChildAccountApi(Resource):
    def post(self):
        """
        Thêm thiết bị trẻ con
        :return:
        {"status":"0|1", "msg":"error_id"}
        error_3: Yêu cầu đăng nhập lại, token,device_name, imei không hợp lệ
        error_1: Child này đã tồn tại.
        """

        json_data = request.get_json(force=True)

        token = json_data[notification.PARAMS["token"]]
        imei = json_data[notification.PARAMS["imei"]]
        device_name = json_data[notification.PARAMS['device_name']]
        db_mongo = DbMongo()
        db_mongo.connect_db()
        account_model = AccountModel(db_mongo.db)
        device_model = DeviceModel(db_mongo.db)

        status, value = account_model.auth_token(token, imei, device_name)

        if not status:
            return notification.notify_db_error()

        # TODO Chưa chhuyeenr thành jsom
        if status:
            full_name = json_data['full_name']
            birth = json_data['birth']
            exist = False

            for child in value[account_model.PROFILES][account_model.CHILD]:
                if child[account_model.FULL_NAME] == full_name:
                    exist = True
                    break
            if exist:
                # Nếu tên trẻ con này tồn tại
                return {"status": "0", "msg": "error_1"}
            else:
                # Đảm bảo ObjectId không bị trùng
                while True:
                    profile_tmp = ObjectId()
                    for child in value[account_model.PROFILES][account_model.CHILD]:
                        print child

                        print str(profile_tmp)
                        if child[account_model.PROFILE_ID] == profile_tmp:
                            continue
                    break

                # Nếu child chưa tồn tại, thêm vào db
                status, value = account_model.update_one(
                    {
                        account_model.DEVICES + "." + account_model.INFOR + "." + account_model.IMEI: imei,
                        account_model.DEVICES + "." + account_model.INFOR + "." + account_model.DEVICE_NAME: device_name,
                        account_model.DEVICES + "." + account_model.TOKEN: token,
                    },
                    {
                        "$addToSet": {
                            account_model.CHILD: {
                                account_model.PROFILE_ID: profile_tmp,
                                account_model.FULL_NAME: full_name,
                                account_model.BIRTH: birth
                            }
                        }
                    }
                )
                if not status:
                    return {"status": "0", "msg": "error_0"}
                return {"status": "1"}

    def get(self):
        """
        Lấy tất cả danh sách trẻ con
        :return:
        """
        token = request.values[notification.PARAMS["token"]]
        imei = request.values[notification.PARAMS["imei"]]
        device_name = request.values[notification.PARAMS["device_name"]]

        db_mongo = DbMongo()
        db_mongo.connect_db()
        device_model = DeviceModel(db_mongo.db)

        # Check trạng thái login
        status, value = device_model.is_login_now(token, imei, device_name)
        print value
        if not status:
            db_mongo.close_db()
            return notification.notify_db_error();

        # Trạng thái đăng nhập
        if value is not None and len(value) > 0:
            account_model = AccountModel(db_mongo.db)
            status, value = account_model.get_all_child(value[device_model.ACCOUNT_ID]);
            if not status:
                db_mongo.close_db()
                return notification.notify_db_error();
            data = []
            if account_model.CHILD in value.keys():
                for i in value[account_model.CHILD]:
                    data.append(i)
            db_mongo.close_db()
            return jsonify(status_login=1, data=data)
        else:
            return jsonify(status_login=0)


class AbstractResourceApi(Resource):
    @abc.abstractmethod
    def get_current_version_server(self, ver_value):
        """
        Trả về version curren
        exist_record = False
        if ver_value is not None and len(ver_value) > 0:
            exist_record = True
            if ver_name_type in ver_value.keys():
                version_current = ver_value[ver_name_type]
            else:
                version_current = "0.0.0.0"
        else:
            # Chưa có version_data cho collection
            version_current = "0.0.0.0"
            exist_record = False;
        return exist_record, version_current

        :param ver_value:
        :return:
        """
        return

    @abc.abstractmethod
    def insert(self, db_mongo, version_model, exist_record_version, data):
        return

    def post(self):

        json_data = request.get_json(force=True)
        token = json_data[notification.PARAMS["token"]]
        imei = json_data[notification.PARAMS["imei"]]
        device_name = json_data[notification.PARAMS["device_name"]]
        version_client = json_data[notification.PARAMS["version"]]

        db_mongo = DbMongo()
        db_mongo.connect_db()
        device_model = DeviceModel(db_mongo.db)
        dev_status, dev_value = device_model.auth_token(token, imei, device_name)

        # Lỗi query db là trả về lỗi luôn
        if not dev_status:
            db_mongo.close_db()
            return notification.notify_db_error()
        if dev_value is not None and len(dev_value) > 0:
            # lấy device_id
            device_id = dev_value[device_model._ID]
            # kiểm tra trong collection version
            version_model = VersionModel(db_mongo.db)
            ver_status, ver_value = version_model.find_one(spec={
                version_model.DEVICE_ID: device_id
            })

            if not ver_status:
                db_mongo.close_db()
                return notification.notify_db_error();

                # version_current = "0.0.0.0"
                # version_model.insert_one({"_id": ObjectId(device_id), ver_name_type: version_current})

            exist_record_version, version_sever = self.get_current_version_server(ver_value)

            if not exist_record_version or Version(version_client).compare(Version(version_sever)) > 0:
                # Nếu version ở client lớn hơn server thì mới thực hiện cập nhật
                # Nhận data
                data = json_data[notification.PARAMS["data"]]
                ins_status, ins_value = self.insert(db_mongo, version_model, exist_record_version, data)

                db_mongo.close_db()
                if not ins_status:
                    notification.notify_db_error()
                return notification.notify_insert_successfully()

            else:
                # Trả về client đã db đã up to date
                db_mongo.close_db()
                return notification.notify_db_uptodate()
        else:
            # trạng thái không đăng nhập
            db_mongo.close_db()
            notification.notify_status_login_false()


class SmsApi(AbstractResourceApi):
    def get_current_version_server(self, ver_value):
        """
        Trả về version curren

        :param ver_value:
        :return:
        """
        exist_record = False
        if ver_value is not None and len(ver_value) > 0:
            exist_record = True
            sms_version_key = "sms_version"
            if sms_version_key in ver_value.keys():
                version_current = ver_value[sms_version_key]
            else:
                version_current = "0.0.0.0"
        else:
            # Chưa có version_data cho collection
            version_current = "0.0.0.0"
            exist_record = False;
        return exist_record, version_current

    def insert(self, db_mongo, version_model, exist_record_version, data):
        super(SmsApi, self).insert(db_mongo, version_model, exist_record_version, data)




