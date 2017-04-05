#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

import config
from bson import ObjectId
from model.account_model import AccountModel
from pymongo import MongoClient

try:
    # client = MongoClient('104.155.136.47', 27017)
    client = MongoClient('127.0.0.1', 27017)
except Exception as e:
    print "client connect " + e.message


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
            AccountModel.PROFILES: {
                AccountModel.PARENT: {
                    AccountModel.PROFILE_ID: ObjectId(),
                    AccountModel.EMAIL: "duythang@gmail.com",
                    AccountModel.PASSWORD: generate_md5("password1"),
                    AccountModel.FULL_NAME: "parent_1",
                },
                AccountModel.CHILD: [
                    {
                        AccountModel.PROFILE_ID: ObjectId(),
                        AccountModel.FULL_NAME: "child_name11",
                        AccountModel.BIRTH: "2011",
                    }
                ],
            },
            AccountModel.DEVICES: [
                {
                    AccountModel.INFOR: {"imei": "imei1", "device_name": "device_name1"},
                    AccountModel.PRIVILEGE: -1,  # 0: parent, 1:child, -1 "unknown"
                    AccountModel.TOKEN: "1",
                    AccountModel.PROFILE_ID: "-1",
                },
                {
                    AccountModel.INFOR: {"imei": "imei2", "device_name": "device_name2"},
                    AccountModel.PRIVILEGE: -1,  # 0: parent, 1:child, -1 "unknown"
                    AccountModel.TOKEN: "1",
                    AccountModel.PROFILE_ID: "-1",

                },
            ]
        },
        {
            AccountModel.PROFILES: {
                AccountModel.PARENT: {
                    AccountModel.PROFILE_ID: ObjectId(),
                    AccountModel.EMAIL: "duythang2@gmail.com",
                    AccountModel.PASSWORD: generate_md5("password2"),
                    AccountModel.FULL_NAME: "parent_2",

                },

                AccountModel.CHILD: [
                    {
                        AccountModel.PROFILE_ID: ObjectId(),
                        AccountModel.FULL_NAME: "child_name21",
                        AccountModel.BIRTH: "2000"
                    }
                ],

            },
            AccountModel.DEVICES: [
                {
                    AccountModel.INFOR: {"imei": "imei3", "device_name": "device_name3"},
                    AccountModel.PRIVILEGE: -1,  # 0: parent, 1:child, -1 "unknown"
                    AccountModel.TOKEN: "2",
                    AccountModel.PROFILE_ID: "-1",
                },
                {
                    AccountModel.INFOR: {"imei": "imei4", "device_name": "device_name5"},
                    AccountModel.PRIVILEGE: -1,  # 0: parent, 1:child, -1 "unknown"
                    AccountModel.TOKEN: "1",
                    AccountModel.PROFILE_ID: "-1",
                },
            ]
        }
    ]
    db['account'].insert(account)


def generate_md5(content):
    m = hashlib.md5()
    m.update(content)
    return m.hexdigest()


def main():
    db = refresh_db()
    insert_account(db)


main()
