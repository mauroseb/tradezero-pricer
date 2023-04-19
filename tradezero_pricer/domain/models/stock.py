# -*- coding: utf-8 -*-

from datetime import date
from flask import current_app, request, url_for
from flask_mongoengine import MongoEngine


class Stock(db.Document):
    #_id = db.IntegerField(required=True, primary_key=True)
    ticker = db.StringField(required=True, max_length=5, unique=True)
    name = db.StringField(required=True, max_length=40)
    price = db.FloatField(required=True, default=0.0)
    price_y = db.FloatField(required=True, default=0.0)
    volume = db.FloatField(required=True, default=0.0)
    marketcap = db.FloatField(required=True, default=0.0)
    candle_data = db.ListField(required=True, default=lambda: {})
    last_update = db.DateTimeField(required=True, default=date.today())

    def to_json(self):
        return {"ticker": self.ticker,
                "name": self.name,
                "volume": self.volume,
                "marketcap": self.marketcap,
                "price": self.price,
                "price_y": self.price_y,
                "last_update": self.last_update}

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

