#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template


def register_urls(app):
    """
    Xử lý các url chưa được login
    :param app:
    :return:
    """

    @app.route('/calllog-list')
    def calllog_list():
        """
        Hiển thị danh sách sms
        :return:
        """
        list_calllog = [
            {"contact_name": "Mrs Loan", "call_time": "00:12:30", "date": "17-03-2017", "time_call": "00:00:12",
             "type": 1, "id": "1"},
            {"contact_name": "Mrs Loan", "call_time": "00:12:30", "date": "17-03-2017", "time_call": "00:00:12",
             "id": "2"},
            {"contact_name": "Mrs Loan", "call_time": "00:12:30", "date": "17-03-2017", "time_call": "00:00:12",
             "type": 2, "id": "3"},
            {"contact_name": "Mrs Loan", "call_time": "00:12:30", "date": "17-03-2017", "time_call": "00:00:12",
             "type": 1, "id": "4"},
            {"contact_name": "Mrs Loan", "call_time": "00:12:30", "date": "17-03-2017", "time_call": "00:00:12",
             "type": 1, "id": "5"},
            {"contact_name": "Mrs Loan", "call_time": "00:12:30", "date": "17-03-2017", "time_call": "00:00:12",
             "type": 1, "id": "6"},
            {"contact_name": "Mrs Loan", "call_time": "00:12:30", "date": "17-03-2017", "time_call": "00:00:12",
             "type": 1, "id": "7"},
            {"contact_name": "Mrs Loan", "call_time": "00:12:30", "date": "17-03-2017", "time_call": "00:00:12",
             "type": 0, "id": "8"},
        ]
        return render_template("dashboard/calllog/calllog.html", list_calllog=list_calllog)
