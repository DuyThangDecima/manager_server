#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

from model.model_db import AccountModel

import config
from bson import ObjectId
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

            AccountModel.PARENT: {
                AccountModel.PROFILE_ID: ObjectId(),
                AccountModel.EMAIL: "duythang@gmail.com",
                AccountModel.PASSWORD: generate_md5("password1"),
                AccountModel.FULL_NAME: "parent_1",
            },
            AccountModel.CHILD: [
                {
                    AccountModel.PROFILE_ID: ObjectId(),
                    AccountModel.FULL_NAME: "child_name1",
                    AccountModel.BIRTH: "2011",
                },
                {
                    AccountModel.PROFILE_ID: ObjectId(),
                    AccountModel.FULL_NAME: "child_name2",
                    AccountModel.BIRTH: "2011",
                }
            ]
        },
        {

            AccountModel.PARENT: {
                AccountModel.PROFILE_ID: ObjectId(),
                AccountModel.EMAIL: "duythang1@gmail.com",
                AccountModel.PASSWORD: generate_md5("password1"),
                AccountModel.FULL_NAME: "parent_1",
            },
            AccountModel.CHILD: [
                {
                    AccountModel.PROFILE_ID: ObjectId(),
                    AccountModel.FULL_NAME: "child_name11",
                    AccountModel.BIRTH: "2011",
                }
            ]

        },

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
