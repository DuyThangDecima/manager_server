# -.- coding:utf-8 -.-
import logging

from config import *
from model.model_db import AccountModel
from pymongo import MongoClient

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus


class DbMongo:
    db = None
    client = None

    def __init__(self):
        try:
            # self.client = MongoClient("35.184.69.50", 27017)
            # print "DB_NAME:" + DB_NAME
            # self.db = self.client[DB_NAME]
            # print "self.db: " + str(self.db)
            # test_db = self.client.test
            # data = test_db['account'].find({})

            uri = "mongodb://%s:%s@%s" % (
                quote_plus("thangld_1202_user"), quote_plus("QAZwsx*098#pl,"), "35.184.69.50:27017")

            client = MongoClient(uri)
            db = client.test
            data = db['account'].find({})
            for item in data:
                print item
            for item in data:
                print item

        except Exception as e:
            logging.error("Fail to connect db" + str(e))

    def connect_db(self):
        return
        # try:
            # self.db.authenticate(DB_ACCOUNT["user"], DB_ACCOUNT["password"], mechanism='SCRAM-SHA-1')
        # except Exception as e:
        #     logging.error("auth db fail " + str(e))
        # return

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
        account.create_index(AccountModel.PARENT + "." + AccountModel.EMAIL,
                             unique=True)
        self.close_db()


class Version:
    """
        VersionUtils của tất cả các bảng được lưu theo format
        version_code.version1.version2
        version_code không có ý nghĩa gì.
        <p>
        example:
        1.01.5.100
        <p>
        Nếu version2 > 65000 thì tăng version1 lên 1
        </p>
    """

    def __init__(self, version):
        version_array_str = version.split(".")
        self.version = []
        for versionStr in version_array_str:
            self.version.append(int(versionStr))

    def compare(self, b):
        """
        So sánh 2 version
        :param a:
        :param b:
        :return: int
        0 nếu bằng nhau
        1 nếu a > b
        -1 nếu a < b
        """
        for i in range(4):
            if self.version[i] < b.version[i]:
                return -1
            elif self.version[i] > b.version[i]:
                return 1
            else:
                if i == 3:
                    return 0;
                else:
                    continue

    def increase(self):
        if self.version[3] < 65000:
            self.version[3] += 1
        else:
            self.version[2] += 1
            self.version[3] = 1

    def to_string(self):
        return self.version_code + "." + self.version_one + "." + self.version_two
