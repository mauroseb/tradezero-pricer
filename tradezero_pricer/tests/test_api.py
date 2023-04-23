# -*- coding: utf-8 -*-

import unittest
import logging
import json
from tradezero_pricer import tradezero_pricer
#from tradezero.models import User
from flask import Flask


class TestTradeZeroApi(unittest.TestCase):
    """
    Test tradezero_pricer API
    """
    def setUp(self):
        self.app = tradezero_pricer.app
        self.app.config.update({
        "TESTING": True,
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        #db.session_remove()
        #db.drop_all()
        self.app_context.pop()

    def is_valid_json(self, json_string):
        '''
        Verify the string is a valid JSON
        '''
        try:
            json.loads(json_string)
            return True
        except ValueError:
            return False


    def test_get_price_ticker(self):
        '''
        Verify GET /api/v1/price/<ticker> endpoint
        '''
        response = self.client.get("/api/v1/price/IBM")
        self.assertEqual(response.status_code, 200)
        self.assertTrue('{"ticker": "IBM"' in response.get_data(as_text=True))

    def test_get_candlechart_ticker(self):
        '''
        Verify GET /api/v1/candlechart/<ticker> endpoint
        '''
        response = self.client.get("/api/v1/candlechart/IBM")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.is_valid_json(response.get_data(as_text=True)))

