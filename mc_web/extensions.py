# -*- coding: utf-8 -*-
from functools import wraps

from flask import redirect, session


def login_required(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        # Kiểm tra xem user đang đăng nhập hệ thống hay chưa
        # Nếu chưa thì trả về trang đăng nhập
        # Sử dụng cho tất cả các trang yêu cầu đăng nhập khi truy cập
        # Implement lại hàm kiểm tra thay cho đoạn If bên dưới

        # return function(*args, **kwargs)
        if session.has_key('logged_in') and session['logged_in']:
            return function(*args, **kwargs)
        else:
            return redirect('/login')

    return wrap


    # def api_login_required(f):
    #     @wraps(f)
    #     def decorated(*args, **kwargs):
    #         # Kiểm tra xem user đang đăng nhập hoặc đủ diều kiện để sử dụng API hay chưa
    #         # Nếu chưa thì trả về mã lỗi
    #         # Sử dụng cho các API để lấy dữ liệu
    #         # Implement lại hàm kiểm tra thay cho False (bên dưới)
    #
    #         password = get_param_post(request, "password")
    #         if password != current_app.config['STATIC_API_PASSWORD']:
    #             return make_response(jsonify({'code': 502, 'message': "access deny"}), 200)
    #
    #         return f(*args, **kwargs)
    #
    #     return decorated
