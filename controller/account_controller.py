#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.db import DbMongo
from flask import session, redirect, render_template
from model.account_model import AccountModel


class AccountController():
    def __init__(self):
        self.db_mongo = DbMongo()
        self.model = AccountModel(self.db_mongo.db)
        pass

    def login(self, username, password):
        """
        Người dùng ấn đăng nhập
        :param username:
        :param password:
        :return:
        """
        self.db_mongo.connect_db();
        status, value = self.model.login(username, password)
        self.db_mongo.close_db()

        if status:
            if value is not None and len(value) > 0:
                # Nếu đăng nhập thành công
                session['logged_in'] = True
                session['user_id'] = str(value[self._ID])
                return redirect('home')
            else:
                # Thông báo user hoặc mật khẩu không đúng
                session['logged_in'] = False
                msg = "Tài khoản hoặc mật khẩu không đúng"
                return render_template("home/login.html", msg=msg)
        else:
            # Đã có lỗi xảy ra
            session['logged_in'] = False
            msg = "Đã có lỗi xảy ra"
            return render_template("home/login.html", msg=msg)
