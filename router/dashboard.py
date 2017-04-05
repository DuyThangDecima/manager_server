#!/usr/bin/env python
# -*- coding: utf-8 -*-
import application_dashboard
import contact_dashboard
import location_dashboard
import sms_dashboard
import calllog_dashboard
from flask import render_template


def register_urls(app):
    """
    Xử lý các url của dashboard sau khi đã được login
    :param app:
    :return:
    """
    # Đăng ký cho sms
    sms_dashboard.register_urls(app)
    location_dashboard.register_urls(app)
    contact_dashboard.register_urls(app)
    application_dashboard.register_urls(app)
    calllog_dashboard.register_urls(app)
