#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template
from extensions import login_required

def register_urls(app):
    """
    Xử lý các url chưa được login
    :param app:
    :return:
    """

    @app.route('/sms-list')
    @login_required
    def sms_list():
        """
        Hiển thị danh sách sms
        :return:
        """
        list_sms = [
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "1"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "2"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "3"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "4"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "5"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "6"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "7"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "8"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "9"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "10"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "11"},
            {"contact_name": "Mrs Loan", "short_conversation": "hello ffe feere fdnfjer", "date": "17-03-2017",
             "id": "12"},
        ]
        return render_template("dashboard/sms/sms-list.html", list_sms=list_sms)

    @app.route('/sms-detail/<id>')
    def sms_detail(id):
        """
        Hiển thị danh sách sms
        :return:
        """
        print id
        return render_template("dashboard/sms/sms-detail.html")
