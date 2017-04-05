# -.- coding:utf-8 -.-
import logging

from config import *
from model.account_model import AccountModel
from pymongo import MongoClient


class DbMongo():
    def __init__(self):
        try:
            self.client = MongoClient(DB_IP["ip"], DB_IP["port"])
            self.db = self.client[DB_NAME]
        except Exception as e:
            logging.error("Fail to connect db" + str(e))

    def connect_db(self):
        # try:
        #     self.db.auth(DB_ACCOUNT["user"], DB_ACCOUNT["password"], mechanism='SCRAM-SHA-1')
        # except Exception as e:
        #     logging.error("auth db fail" + str(e))
        return

    def close_db(self):
        """
        Dong db moi khi su dung xong
        :return:
        """
        if self.client is not None:
            self.client.close()

    def init_db(self):
        """
        Đánh index cho collection
        :return:
        """
        self.connect_db()
        account = self.db[AccountModel.COLLECTION_NAME]
        account.create_index(AccountModel.PROFILES + "." + AccountModel.PARENT + "." + AccountModel.EMAIL,
                             unique=True)
        self.close_db()
