# -*- coding: utf-8 -*-

__author__ = 'ThangLD'
import utils
from bson import ObjectId
from db.db import DbMongo
from flask_restful import Resource, request
from model.account_model import AccountModel


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
        email = request.values['email']
        password = request.values['password']
        imei = request.values['imei']
        device_name = request.values['device_name']

        db_mongo = DbMongo()
        db_mongo.connect_db()
        model_account = AccountModel(db_mongo.db)
        # Tìm trong db
        status, value = model_account.find_one(
            spec={
                model_account.PROFILES + "." + model_account.PARENT + "." + model_account.EMAIL: email,
                model_account.PROFILES + "." + model_account.PARENT + "." + model_account.PASSWORD: password
            },
            fields={model_account._ID: 1, model_account.DEVICES: 1})
        db_mongo.close_db()
        if status:
            if value is not None and len(value) > 0:
                # Nếu tài khoản tồn tại
                # danh sách các thiết bị đăng nhập
                devices = value[model_account.DEVICES]
                print devices
                is_login_before = False

                while True:
                    # Đảm bảo token tạo ra không trùng với bất kỳ
                    # token nào trước đó trong danh sách thiết bị đã đăng nhập
                    token = utils.generate_token()
                    for device in devices:
                        if model_account.TOKEN in device.keys() and token == device[model_account.TOKEN]:
                            continue;
                    break
                # Kiểm tra thiết bị đã đăng nhập trước đó hay chưa
                for device in devices:
                    if device[model_account.INFOR][model_account.IMEI] == imei \
                            and device[model_account.INFOR][model_account.DEVICE_NAME] == device_name:
                        is_login_before = True
                        break;

                if is_login_before:
                    # Nếu thiết bị này đã được đăng nhập trước đó
                    # Update lại token, đưa role của devices unknow
                    status, value = model_account.update_one(
                        {
                            model_account.PROFILES + "." + model_account.PARENT + "." + model_account.EMAIL: email,
                            model_account.PROFILES + "." + model_account.PARENT + "." + model_account.PASSWORD: password,
                            model_account.DEVICES + "." + model_account.INFOR + "." + model_account.IMEI: imei,
                            model_account.DEVICES + "." + model_account.INFOR + "." + model_account.DEVICE_NAME: device_name
                        },
                        {
                            '$set': {
                                model_account.DEVICES + ".$." + model_account.PRIVILEGE: model_account.PRIVILEGE_UNKNOWN,
                                model_account.DEVICES + ".$." + model_account.TOKEN: token
                            }
                        }
                    )
                    if not status:
                        return {"status": "0", "msg": "error_0"}
                else:
                    # Nếu thiết bị chưa được đăng nhập lần nào
                    # THêm thiết bị vào màng devices trong db
                    status, value = model_account.update_one(
                        {
                            model_account.PROFILES + "." + model_account.PARENT + "." + model_account.EMAIL: email,
                            model_account.PROFILES + "." + model_account.PARENT + "." + model_account.PASSWORD: password
                        },
                        {
                            '$addToSet': {
                                model_account.DEVICES: {
                                    model_account.INFOR: {
                                        model_account.IMEI: imei,
                                        model_account.DEVICE_NAME: device_name
                                    },
                                    model_account.PRIVILEGE: model_account.PRIVILEGE_UNKNOWN,
                                    model_account.PROFILE_ID: -1,
                                    model_account.TOKEN: token
                                }
                            }
                        }
                    )
                    if not status:
                        return {"status": "0", "msg": "error_0"}
                # Gửi về status và token.
                # Nếu cập nhật không thành công
                # if not status:
                return {"status": "1", "token": token}
            else:  # Thông báo user hoặc mật khẩu không đúng
                return {"status": "0", "msg": "error_1"}

        else:  # Đã có lỗi xảy ra
            return {"status": "0", "msg": "error_0"}


            # db_mongo = DbMongo()
            # db_mongo.connect_db()
            # model_account = AccountModel(db_mongo.db)
            #
            # result = model_account.update_one({'password': 4}, {'$set': {'pass': '40'}})
            # print result[0]
            # print result[1]
            #
            # print str(result)


class ParentAccountApi(Resource):
    def post(self):
        """
        Thực hiện đăng ký tài khoản
        :return:
        { "status": True|False, "msg":"error_id"}
        error_1: Tài khoản đã tồn tại
        error_0: Đã có lỗi xảy ra
        """
        email = request.values['email']
        password = request.values['password']
        full_name = request.values['full_name']

        db_mongo = DbMongo()
        db_mongo.connect_db()
        model_account = AccountModel(db_mongo.db)
        # Tìm trong db
        status, value = model_account.find_one(
            spec={
                model_account.PROFILES + "." + model_account.PARENT + "." + model_account.EMAIL: email,
            },
            fields={model_account._ID: 1})

        if status:
            if value is not None and len(value) > 0:
                # Nếu email đã tồn tại
                db_mongo.close_db()
                return {"status": "0", "msg": "error_1"}
            else:
                # Nếu email chưa tồn tại, thêm vào csdl
                status, value = model_account.insert_one({
                    model_account.PROFILES: {
                        model_account.PARENT: {
                            model_account.PROFILE_ID: ObjectId(),
                            model_account.EMAIL: email,
                            model_account.PASSWORD: password,
                            model_account.FULL_NAME: full_name
                        }
                    }
                })

                db_mongo.close_db()
                if not status:
                    return {"status": "0", "msg": "error_0"}

                return {"status": "1"}

        else:  # Đã có lỗi xảy ra
            db_mongo.close_db()
            return {"status": "0", "msg": "error_0"}


class ChildAccountApi(Resource):
    def post(self):
        """
        Thêm thiết bị trẻ con
        :return:
        {"status":"0|1", "msg":"error_id"}
        error_3: Yêu cầu đăng nhập lại, token,device_name, imei không hợp lệ
        error_1: Child này đã tồn tại.
        """
        token = request.values['token']
        imei = request.values['imei']
        device_name = request.values['device_name']
        db_mongo = DbMongo()
        db_mongo.connect_db()
        model_account = AccountModel(db_mongo.db)
        status, value = utils.auth_device(model_account, token, imei, device_name)
        if status:
            full_name = request.values['full_name']
            birth = request.values['birth']
            exist = False

            for child in value[model_account.PROFILES][model_account.CHILD]:
                if child[model_account.FULL_NAME] == full_name:
                    exist = True
                    break
            if exist:
                # Nếu tên trẻ con này tồn tại
                return {"status": "0", "msg": "error_1"}
            else:
                # Đảm bảo ObjectId không bị trùng
                while True:
                    profile_tmp = ObjectId()
                    for child in value[model_account.PROFILES][model_account.CHILD]:
                        print child

                        print str(profile_tmp)
                        if child[model_account.PROFILE_ID] == profile_tmp:
                            continue
                    break

                # Nếu child chưa tồn tại, thêm vào db
                status, value = model_account.update_one(
                    {
                        model_account.DEVICES + "." + model_account.INFOR + "." + model_account.IMEI: imei,
                        model_account.DEVICES + "." + model_account.INFOR + "." + model_account.DEVICE_NAME: device_name,
                        model_account.DEVICES + "." + model_account.TOKEN: token,
                    },
                    {
                        "$addToSet": {
                            model_account.PROFILES + "." + model_account.CHILD: {
                                model_account.PROFILE_ID: profile_tmp,
                                model_account.FULL_NAME: full_name,
                                model_account.BIRTH: birth
                            }
                        }
                    }
                )
                if not status:
                    return {"status": "0", "msg": "error_0"}
                return {"status": "1"}
        else:
            return {"status": "0", "msg": "error_0"}
