# -*- coding: utf-8 -*-


from webob import Request

from . import common


def setup_module(module):
    common.get_or_load_app()


def test_reforms_without_parameters():
    req = Request.blank('/api/1/reforms', method = 'GET')
    res = req.get_response(common.app)
    assert res.status_code == 200
