# -*- coding: utf-8 -*-

from datetime import date
from flask import current_app, request, url_for
from flask_mongoengine import MongoEngine
from tradezero_pricer import db


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

    def get_intraday(self):
        change = (self.price_y - self.price) / self.price_y if stock_price_y else 0.00,
        return {"ticker": self.ticker,
                "variation": change}

    def is_active(self):
        return True

    def get_ticker(self):
        return str(self.ticker)


def stock_factory(ticker: str, name: str, price: float, price_y: float,
                 volume: float, marketcap: float, candle_data: list,
                 last_update: date) -> Stock:
    '''
    Stock factory method
    '''
    if ticker in current_app.config['TICKER_WATCHLIST']:
        current_app.logger.debug(f'{ticker} is in the watchlist. Instantiating.')
        return Stock(ticker=ticker, name=name, price=price, price_y=price_y,
                 volume=volume, marketcap=marketcap, candle_data=candle_data,
                 last_update=_last_update)
    else:
       current_app.logger.error(f" {ticker} not in the watchlist. Ignoring.")
    return None


