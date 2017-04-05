#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template


def register_urls(app):
    """
    Xử lý các url chưa được login
    :param app:
    :return:
    """

    @app.route('/location')
    def location():
        list_location = [
            {"location_name": "105 Ho Tung Mau, Cau Giay, Ha Noi", "location_geo": "21.054102,105.817715",
             "date": "10:20-20/10/2017","id":1},
            {"location_name": "105 Ho Tung Mau, Cau Giay, Ha Noi", "location_geo": "21.054102,105.817715",
             "date": "10:20-20/10/2017","id":2},
            {"location_name": "105 Ho Tung Mau, Cau Giay, Ha Noi", "location_geo": "21.054102,105.817715",
             "date": "10:20-20/10/2017","id":3},
            {"location_name": "105 Ho Tung Mau, Cau Giay, Ha Noi", "location_geo": "20.866778, 106.056696",
             "date": "10:20-20/10/2017","id":4},
            {"location_name": "105 Ho Tung Mau, Cau Giay, Ha Noi", "location_geo": "21.054102,105.817715",
             "date": "10:20-20/10/2017","id":5},
            {"location_name": "105 Ho Tung Mau, Cau Giay, Ha Noi", "location_geo": "21.054102,105.817715",
             "date": "10:20-20/10/2017","id":6},
            {"location_name": "105 Ho Tung Mau, Cau Giay, Ha Noi", "location_geo": "21.054102,105.817715",
             "date": "10:20-20/10/2017","id":7},
            {"location_name": "105 Ho Tung Mau, Cau Giay, Ha Noi", "location_geo": "21.054102,105.817715",
             "date": "10:20-20/10/2017","id":8},
            {"location_name": "105 Ho Tung Mau, Cau Giay, Ha Noi", "location_geo": "20.891713, 106.059240",
             "date": "10:20-20/10/2017","id":9}
        ]
        return render_template('dashboard/location/location-map.html', list_location=list_location)
