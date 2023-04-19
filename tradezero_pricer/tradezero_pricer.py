# -*- coding: utf-8 -*-

import os
import sys
import socket
import time
import json
import pandas_datareader.data as datareader
import yfinance as yf
import pandas as pd

from flask import Flask, request, jsonify, Response, abort
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from flasgger import Swagger
from datetime import date
from tradezero_pricer.config import config as tzp_config
#from tradezero_pricer.domain.models.stock import Stock

app = Flask(__name__)
app.config.from_object(tzp_config.config['container'])
tzp_config.config['container'].init_app(app)
cors = CORS(app)
swagger = Swagger(app)
db = MongoEngine()
db.init_app(app)

tzp_major = 0
tzp_minor = 1
tzp_release = 2
tzp_version = f'{tzp_major}.{tzp_minor}.{tzp_release}'
tzp_commit = '8389e6144fb74ef0a3652c35a31860fe'

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

def check_backend() -> bool:
    # check mongo and yf
    return True


def update_stock_data(ticker,days=7) -> Stock:
        '''
        Fetch and transform pandas dataframe of stock ticker and create or
        update the stock opersist in the DB.
        '''
        try:
            # Fetch
            stock_data = yf.Ticker(ticker)
        except:
            f'ERROR while fetching stock data for {ticker}.'
            return None

        # Transform
        fetched_name = stock_data.info['displayName']
        fetched_price = stock_data.info['regularMarketPrice']
        fetched_price_y = stock_data.info['regularMarketPreviousClose']
        fetched_volume = stock_data.info['regularMarketVolume']
        fetched_marketcap = stock_data.info['marketCap']
        fetched_chart_data = stock_data.history(period='7d')
        fetched_chart_data['timestamp'] = fetched_chart_data.index
        fetched_chart_data = fetched_chart_data.drop(["Dividends", "Stock Splits", "Volume"], axis=1)
        fetched_chart_data.columns = fetched_chart_data.columns.str.strip().str.lower()
        chart_final = fetched_chart_data.to_dict(orient='records')
        for record in chart_final:
            record['timestamp'] = record['timestamp'].timestamp()

        stock = load_stock(ticker)
        # If the stock document exists update it, otherwise create it
        try:
            if stock:
                stock.update(price_y=fetched_price_y, price=fetched_price,
                            chart_data=fetched_chart_data_json,
                            last_update=date.today())
            else:
                stock = Stock(ticker=ticker, name=fetched_name,
                            price=fetched_price, price_y=fetched_price_y,
                            volume=fetched_volume, marketcap=fetched_marketcap,
                            candle_data=chart_final)
            stock.save()
            return stock

        except:
            f"ERROR: Failed to update stock price data in the database. Is the ticker valid?"
            return None


def fetch_stock_data(ticker) -> Stock:
    '''
    Fetch stock data from DB, if it is stale update first.
    '''
    stock = load_stock(ticker)
    print(stock)
    if stock:
        print(stock.last_update.date())
        print(date.today())
        if stock.last_update.date() == date.today():
            print("last_update today!")
            return stock
        else:
            print("last_update NOT today!")
    try:
        print("updating stock data!")
        stock = update_stock_data(ticker)
        return stock

    except:
        f'ERROR while updating stock'
        return None


def load_stock(ticker) -> Stock:
    '''
    Bring stock object corresponding to ticker if it exist.
    '''
    return Stock.objects(ticker=ticker).first()
    #return Stock.objects.first()


@app.route("/index", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def main():
    return f"<h1>TradeZero Price Serivce {tzp_version}</h1>"
    #return render_template(index)


@app.route("/version")
def version():
    """Return version"""
    data = {
        'result': 200,
        'version': tzp_version,
        'major': tzp_major,
        'minor': tzp_minor,
        'release': tzp_release,
        'commit': tzp_commit,
        'api': 'v1',
    }
    #return Response(json.dumps(data), mimetype='application/json')
    return Response(json.dumps(data))

@app.route('/api/v1/price/<ticker>', methods=['GET'])
def price(ticker):
    '''
    Return current stock price.
    '''
    try:
        stock = fetch_stock_data(ticker)
        if stock:
            data = {
                "ticker": stock.ticker,
                "name": stock.name,
                "volume": stock.volume,
                "marketcap": stock.marketcap,
                "price": stock.price,
            }
            return Response(json.dumps(data), mimetype='application/json')
            return Response(json.dumps(data))
        return jsonify({"status": 404, "reason": "Stock not found."})
    except:
        #return jsonify({"status": 404, "reason": "Stock not found."})
        abort(404)


@app.route('/api/v1/candlechart/<ticker>', methods=['GET'])
def candlechart(ticker):
    '''
    Return stock candle chart data for the last 7 days.
    '''
    try:
        stock = fetch_stock_data(ticker)
        if stock.candle_data:
            return Response(json.dumps(stock.candle_data), mimetype='application/json')
        else:
            return Response(json.dumps({"status": 404, "reason": "Stock not found."}, mimetype='application/json'))

    except:
        #return jsonify({"status": 404, "reason": "Stock not found."})
        abort(404)


@app.route('/api/v1/intraday/<ticker>', methods=['GET'])
def intraday():
    '''
    Return intraday stock price variation.
    '''
    stock = load_stock(ticker)
    if stock:
        data = {
           "ticker": stock.ticker,
           "change": stock.price_y - stock.price,
           #"pct": (stock.price_y - stock.price) / stock.price_y if stock_price_y else 0,
        }
        return Response(json.dumps(data), mimetype='application/json')
        return jsonify(stock.intraday_json())
    else:
        return jsonify({"status": 404, "reason": "Stock not found."})


@app.route('/api/v1/listall', methods=['GET'])
@app.route('/api/v1/catalog', methods=['GET'])
def listall():
    '''
    Return list with all stocks stored in the DB
    '''
    resp=[]
    for stock in Stock.objects:
        row = {
            "ticker": stock.ticker,
            "name": stock.name,
            "volume": stock.volume,
            "marketcap": stock.marketcap,
            "price": stock.price,
            "price_y": stock.price_y,
            "last_update": stock.last_update,
        }
        resp.append(row)

    return resp


@app.route('/health')
def healthcheck():
    '''
    Service healthcheck endpoint
    '''
    status = check_backend()
    status_code = 200 if status else 500

    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'

    data = {
        'hostname': socket.gethostname(),
        'status': status,
        'timestamp': time.time(),
        'results': results,
    }

    return Response(json.dumps(data), status=status_code, mimetype='application/json')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

