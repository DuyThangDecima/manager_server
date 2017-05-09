#!/usr/bin/env python
# -*- coding: utf-8 -*-
from controller.account_controller import AccountController
from flask import render_template, request, session, redirect, url_for


def register_urls(app):
    """
    Xử lý các url chưa được login
    :param app:
    :return:
    """

    @app.route('/')
    def home():
        """
        Trang chủ
        :return:
        """
        if session.has_key('logged_in'):
            msg = session.get('msg')
            if session.get('logged_in'):
                # Nếu đăng nhập thành công
                return render_template("dashboard/main.html", msg=msg)
        return render_template("home/index.html")


    @app.route('/login_form', methods=['POST','GET'])
    def login_form():
        """
        Người dùng ấn đăng nhập
        :return:
        """
        print "thangld_xxxx"
        return render_template("home/login.html")

    @app.route('/login', methods=['POST'])
    def login():
        """
        Người dùng ấn đăng nhập
        :return:
        """
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            return AccountController().login(username, password)
        else:
            return redirect(url_for('home'))

    @app.route('/logout')
    def logout():
        session.pop('logged_in', None)
        return redirect(url_for('home'))
