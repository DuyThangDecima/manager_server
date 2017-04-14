#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template


def register_urls(app):
    """
    Xử lý các url chưa được login
    :param app:
    :return:
    """

    @app.route('/contact-list')
    def contact_list():
        """
        Hiển thị danh sách sms
        :return:
        """
        list_contact = [
            {"contact_name": "Mrs Loan", "phone_number": "016742555050", "email": "duythangsvbk@gmail.com",
             "id": "1"},
            {"contact_name": "Mrs Loan", "phone_number": "016742555050", "email": "duythangsvbk@gmail.com",
             "id": "2"},
            {"contact_name": "Mrs Loan", "phone_number": "016742555050", "email": "duythangsvbk@gmail.com",
             "id": "3"},
            {"contact_name": "Mrs Loan", "phone_number": "016742555050", "email": "duythangsvbk@gmail.com",
             "id": "4"},
            {"contact_name": "Mrs Loan", "phone_number": "016742555050", "email": "duythangsvbk@gmail.com",
             "id": "5"},
            {"contact_name": "Mrs Loan", "phone_number": "016742555050", "email": "duythangsvbk@gmail.com",
             "id": "6"},
            {"contact_name": "Mrs Loan", "phone_number": "016742555050", "email": "duythangsvbk@gmail.com",
             "id": "7"},
        ]
        return render_template("dashboard/contact/contact.html", list_contact=list_contact)
