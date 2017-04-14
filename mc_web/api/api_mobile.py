# -*- coding: utf-8 -*-
import notification
from db.db import DbMongo
from flask import jsonify, request
from model.model_db import DeviceModel, AccountModel


# Xử lý về child

def register_urls(app):
    @app.route('/api/v1/get_list_child', methods=['POST'])
    def get_list_child():
        json_data = request.get_json(force=True)
        token = json_data[notification.PARAMS["token"]]
        imei = json_data[notification.PARAMS["imei"]]
        device_name = json_data[notification.PARAMS["device_name"]]

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
        if value is not None:
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

