# -*- coding: utf-8 -*-

import json
import pandas_datareader.data as datareader
import yfinance as yf
import pandas as pd

from datetime import date
from flask import render_template, Blueprint, current_app, jsonify,\
     Response
from flasgger import swag_from
from tradezero_pricer.domain.models.stock import Stock
from . import api_bp

def update_stock_data(ticker, days=7) -> Stock:
    '''
    Fetch and transform pandas dataframe of stock ticker and create or
    update the stock opersist in the DB.
    ---
    Returns a Stock object.

    ticker: Stock ticker
    days: The span of days of the chart data
    '''
    print("Update stock")
    # Fetch
    try:
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
    fetched_chart_final = fetched_chart_data.to_dict(orient='records')
    for record in fetched_chart_final:
        record['timestamp'] = record['timestamp'].timestamp()

    # If the stock document exists update it, otherwise create it
    stock = load_stock(ticker)
    try:
        if stock:
            stock.update(price_y=fetched_price_y, price=fetched_price,
                         candle_data=fetched_chart_final,
                         last_update=date.today())
        else:
            stock = Stock(ticker=ticker, name=fetched_name,
                        price=fetched_price, price_y=fetched_price_y,
                        volume=fetched_volume, marketcap=fetched_marketcap,
                        candle_data=fetched_chart_final)
        stock.save()
        print("saved to the DB")
        return stock

    except:
        print(f'ERROR: Failed to update stock price data in the database. Is the ticker {ticker} valid?')
        return None


def fetch_stock_data(ticker) -> Stock:
    '''
    Fetch stock data from DB, if it is stale update first.
    Returns a Stock object.
    ---
    ticker: Stock ticker
    '''
    print("Fetch stock")
    stock = load_stock(ticker)
    if stock:
        if stock.last_update.date() == date.today():
            print(f"{ticker} last update was today")
            return stock
        else:
            print(f"{ticker} data is not fresh")
    try:
        print(f"Updating {ticker} data!")
        stock = update_stock_data(ticker)
        return stock

    except:
        print(f'ERROR while updating stock {ticker} data')
        return None


def load_stock(ticker) -> Stock:
    '''
    Bring stock object corresponding to ticker if it exist.
    '''
    return Stock.objects(ticker=ticker).first()

@api_bp.route('/price/<ticker>', methods=['GET'])
@swag_from('price.yml')
def price(ticker):
    '''
    Stock price endpoint.
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
        return jsonify({"status": 404, "reason": "Stock not found."}), 404
    except:
        return jsonify({"status": 500, "reason": "Internal Server Error"}), 500


@api_bp.route('/candlechart/<ticker>', methods=['GET'])
@swag_from('candlechart.yml')
def candlechart(ticker):
    '''
    Endpoint to return stock candle chart data for the last 7 days.
    '''
    try:
        stock = fetch_stock_data(ticker)
        if stock.candle_data:
            return Response(json.dumps(stock.candle_data), mimetype='application/json')
        else:
            return Response(json.dumps({"status": 404, "reason": "Stock not found."}, mimetype='application/json'))

    except:
        return jsonify({"status": 500, "reason": "Internal Server Error"}), 500


@api_bp.route('/intraday/<ticker>', methods=['GET'])
@swag_from('intraday.yml')
def intraday():
    '''
    Endpoint to return intraday stock price variation.
    '''
    try:
        stock = fetch_stock_data(ticker)
        if stock.candle_data:
            return Response(json.dumps(stock.candle_data), mimetype='application/json')
        else:
            return Response(json.dumps({"status": 404, "reason": "Stock not found."}, mimetype='application/json'))

    except:
        return jsonify({"status": 500, "reason": "Internal Server Error"}), 500

    stock = load_stock(ticker)
    if stock:
        data = {
           "ticker": stock.ticker,
           "change": stock.price_y - stock.price,
           "pct": (stock.price_y - stock.price) / stock.price_y if stock_price_y else 0.00,
        }
        return Response(json.dumps(data), mimetype='application/json')
        #return jsonify(stock.intraday_json()), 200
    else:
        return jsonify({"status": 404, "reason": "Stock not found."})


@api_bp.route('/listall', methods=['GET'])
@api_bp.route('/catalog', methods=['GET'])
@swag_from('catalog.yml')
def listall():
    '''
    Endpoint to return the catalog of all stocks stored in the DB
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

