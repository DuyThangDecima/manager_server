#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

import config
from bson import ObjectId
from model.model_db import AccountModel
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo import ReadPreference

# 35.184.69.50:27017
# uri = "mongodb://%s:%s@%s" % (
#     quote_plus("thangld_1202_user"), quote_plus("QAZwsx*098#pl,"), '127.0.0.1:27017')
# try:
#     client = MongoClient("127.0.0.1",27017)
# except Exception as e:
#     print "client connect " + e.message

# try:
#     # The ismaster command is cheap and does not require auth.
#     client.admin.command('ismaster')
# except ConnectionFailure:
#     print("Server not available")

client = MongoClient("127.0.0.1",27017)
db = client.test
data = db.account.find({})
for item in data:
    print item

try:
    # The ismaster command is cheap and does not require auth.
    db = client.get_database('test')
    # client.admin.command('ismaster')
except ConnectionFailure:
    print("Server not available")

# print "start"
# try:
#     # client = MongoClient('104.155.136.47', 27017)
#     # replicaSet = "rs0"
#     # 35.184.122.206, 35.184.69.50
#     client = MongoClient('35.184.69.50', 27017)
# except Exception as e:
#     print "client connect " + e.message


    # db = client[config.DB_NAME]
    # db.authenticate("thangld_1202_user","QAZwsx*098#pl,")
data = db.test.account.find({})

for item in data:
    print item


def refresh_db():
    try:
        db = client[config.DB_NAME];
        # status = db.authenticate('qpwoei', 'qwesx$1202RFVGYHN', mechanism='SCRAM-SHA-1')
        # print status
        return db
        # client.drop_database(config.DB_NAME)
    except Exception as e:
        print "delete fail" + e.message


def create_db():
    return client[config.DB_NAME]


def insert_account(db):
    account = [
        {

            AccountModel.PARENT: {
                AccountModel._ID: ObjectId(),
                AccountModel.EMAIL: "duythang@gmail.com",
                AccountModel.PASSWORD: generate_md5("password1"),
                AccountModel.FULL_NAME: "parent_1",
            },
            AccountModel.CHILD: [
                {
                    AccountModel._ID: ObjectId(),
                    AccountModel.FULL_NAME: "child_name1",
                    AccountModel.BIRTH: "2011",
                },
                {
                    AccountModel._ID: ObjectId(),
                    AccountModel.FULL_NAME: "child_name2",
                    AccountModel.BIRTH: "2011",
                }
            ]
        },
        {

            AccountModel.PARENT: {
                AccountModel._ID: ObjectId(),
                AccountModel.EMAIL: "duythang1@gmail.com",
                AccountModel.PASSWORD: generate_md5("password1"),
                AccountModel.FULL_NAME: "parent_1",
            },
            AccountModel.CHILD: [
                {
                    AccountModel._ID: ObjectId(),
                    AccountModel.FULL_NAME: "child_name11",
                    AccountModel.BIRTH: "2011",
                }
            ]

        },

    ]

    version = {

        "device_id": "",
        "sms_version": "1.01.18.1",
        "contact_version": "1.01.1.91",
        "callog_version": "1.01.1.10009",
        "location_version": "1.01.5.1",
        "app_version": "1.01.1.1",
        "video_version": "1.01.2.32",
        "audio_version": "1.01.1.1000",

    }

    db['account'].insert(account)
    db['version'].insert(version)


def generate_md5(content):
    m = hashlib.md5()
    m.update(content)
    return m.hexdigest()


def main():
    db = refresh_db()
    insert_account(db)


    # main()

    # version_client = "1.0.10.0"
    # sorted(ids)
    #


    # value = db['device'].find(
    #     {
    #         'account_id': ObjectId("58ff7d964bf65a18193a12b8"),
    #         "devices.token": "b00049a39507f32ce28abfc10da0eae6"
    #     },
    #     {
    #         'devices': {'$elemMatch': {'token': "b00049a39507f32ce28abfc10da0eae6"}}
    #     }
    #
    # )
    # # call_log_array = value['devices']
    #
    # for item in value:
    #     data=  item
    #
    # print value
    #
    # # call_log_array.sort(key=lambda k: str(k["_id"]), reverse=False)
    # #
    # #
    # # index_client = 0
    # # size_client = len(ids)
    # # index_server = 0
    # # size_server = len(call_log_array);
    # # result_action = []
    # # while index_client < size_client and index_server < size_server:
    # #     item = call_log_array[index_server];
    # #     id_server = str(item["_id"])
    # #     id_client = ids[index_client];
    # #     if id_client == id_server:
    # #         if version_client != item["version"]:
    # #             item["action"] = "update"
    # #             result_action.append(item)
    # #         else:
    # #             """Trong truong hop giong nhau thi ko can action gi ca"""
    # #         index_client += 1
    # #         index_server += 1
    # #     elif id_client < id_server:
    # #         item["action"] = "delete"
    # #         index_client += 1
    # #         result_action.append({"action": "delete", "_id": id_client})
    # #     elif id_client > id_server:
    # #         item["action"] = "add"
    # #         index_server += 1
    # #         result_action.append(item)
    # #
    # # while index_client < size_client:
    # #     result_action.append({"_id": ids[index_client], "action": "delete"})
    # #     index_client += 1
    # #
    # # while index_server < size_server:
    # #     item = call_log_array[index_server];
    # #     item["action"] = "add"
    # #     result_action.append(item)
    # #     index_server += 1
    # #
    # # for item in result_action:
    # #     print str(item["_id"]) + "---" + item["action"]
    #
    #
    # print client.database_names
