# -*- coding: utf-8 -*-

__author__ = 'ThangLD'
from db.db import DbMongo
from flask import request
from flask_restful import Resource
from model.account_model import AccountModel




class ParentApi(Resource):
    def post(self):
        """
        Thực hiện đăng ký tài khoản
        :return:
        { "status": True|False, "msg":"error_id"}
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

class ChildApi(Resource):
    def post(self):
        """
        Thêm trẻ con
        :return:
        """

        imei = request.values['imei']
        device_name = request.values['device_name']
        token = request.values['token']


        full_name = request.values['full_name']
        age = request.values['age']

        db_mongo = DbMongo()
        db_mongo.connect_db()
        model_account = AccountModel(db_mongo.db)
        # Tìm trong db
        status, value = model_account.find_one(
            spec={
                model_account.DEVICES + "." + model_account.IMEI:imei,
                model_account.DEVICES + "." + model_account.DEVICES:device_name,
                model_account.DEVICES + "." + model_account.TOKEN:token,
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
