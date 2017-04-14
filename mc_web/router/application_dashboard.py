#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template


def register_urls(app):
    """
    Xử lý các url chưa được login
    :param app:
    :return:
    """

    @app.route('/app-list')
    def app_list():
        """
        Hiển thị danh sách sms
        :return:
        """
        list_app = [
            {"app_name": "Vietel Mobile Security", "version": "1.3.25", "package_name": "com.visc.mobilesecurity",
             "id": "1"},
            {"app_name": "Vietel Mobile Security", "version": "1.3.25", "package_name": "com.visc.mobilesecurity",
             "id": "2"},
            {"app_name": "Vietel Mobile Security", "version": "1.3.25", "package_name": "com.visc.mobilesecurity",
             "id": "3"},
            {"app_name": "Vietel Mobile Security", "version": "1.3.25", "package_name": "com.visc.mobilesecurity",
             "id": "4"},
            {"app_name": "Vietel Mobile Security", "version": "1.3.25", "package_name": "com.visc.mobilesecurity",
             "id": "5"},
            {"app_name": "Vietel Mobile Security", "version": "1.3.25", "package_name": "com.visc.mobilesecurity",
             "id": "6"},
            {"app_name": "Vietel Mobile Security", "version": "1.3.25", "package_name": "com.visc.mobilesecurity",
             "id": "7"},
            {"app_name": "Vietel Mobile Security", "version": "1.3.25", "package_name": "com.visc.mobilesecurity",
             "id": "8"},
        ]
        return render_template("dashboard/application/application.html", list_app=list_app)
