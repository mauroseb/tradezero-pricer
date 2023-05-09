# -*- coding: utf-8 -*-

import unittest
import json
import tradezero_pricer
from flask import Flask


class TestTradeZeroApi(unittest.TestCase):
    """
    Test tradezero_pricer main module
    """
    def setUp(self):
        self.app = tradezero_pricer.create_app("container")
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


    def test_get_version(self):
        '''
        Verify GET /version
        '''
        tzp_version = self.app.config['TZP_VERSION']
        response = self.client.get("/version")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.is_valid_json(response.get_data(as_text=True)))
        self.assertTrue(f'"version": "{tzp_version}"' in response.get_data(as_text=True))

    def test_get_index(self):
        '''
        Verify GET /
        '''
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_get_swagger(self):
        '''
        Verify GET /apidocs/
        '''
        response = self.client.get("/apidocs/")
        self.assertEqual(response.status_code, 200)

