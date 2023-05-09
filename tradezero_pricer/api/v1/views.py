# -*- coding: utf-8 -*-

import json
import pandas_datareader.data as datareader
import yfinance as yf
import pandas as pd
import requests_cache

from datetime import date
from flask import render_template, Blueprint, current_app, jsonify,\
     Response
from flasgger import swag_from
from tradezero_pricer.domain.models.stock import Stock, stock_factory
from . import api_bp

def update_stock_data(ticker, days=10) -> Stock:
    '''
    Fetch and transform pandas dataframe of stock ticker and create or
    update the stock opersist in the DB.
    ---
    Returns a Stock object.

    ticker: Stock ticker
    days: The span of days of the chart data
    '''
    current_app.logger.debug(f"Updating stock info for {ticker}.")
    # Magic stock
    if ticker == 'ZERO':
        current_app.logger.debug("Updating magic stock!")
        fetched_name = 'TradeZero Inc.'
        fetched_price = 0.0
        fetched_price_y = 0.0
        fetched_volume = 0.0
        fetched_marketcap = 0
        fetched_chart_final = [{ "open" : 0.0,
                                 "high" : 0.0,
                                 "low" : 0.0,
                                 "close" : 0.0,
                                 "timestamp" : 1682395200 }]
    else:
        # Fetch
        try:
            session = requests_cache.CachedSession('yfinance.cache')
            session.headers['User-agent'] = 'tradezero-pricer/1.0'
            stock_data = yf.Ticker(ticker, session=session)
        except:
            current_app.logger.error(f'ERROR while fetching stock data for {ticker}.')
            return None

        # Transform
        current_app.logger.debug(f"Transforming stock data for {ticker}.")
        fetched_name = stock_data.info['shortName']
        fetched_price = stock_data.info['currentPrice']
        fetched_price_y = stock_data.info['regularMarketPreviousClose']
        fetched_volume = stock_data.info['regularMarketVolume']
        fetched_marketcap = stock_data.info['marketCap']
        fetched_chart_data = stock_data.history(period=str(days)+'d')
        fetched_chart_data['timestamp'] = fetched_chart_data.index
        fetched_chart_data = fetched_chart_data.drop(["Dividends",
                                                     "Stock Splits", "Volume"], axis=1)
        fetched_chart_data.columns = fetched_chart_data.columns.str.strip().str.lower()
        fetched_chart_final = fetched_chart_data.to_dict(orient='records')
        for record in fetched_chart_final:
            record['timestamp'] = record['timestamp'].timestamp()
        current_app.logger.debug(f"Transforming stock data for {ticker} finished.")

    # If the stock document exists update it, otherwise create it
    stock = load_stock(ticker)
    try:
        if stock:
            current_app.logger.debug(f"Calling stock update for {ticker}.")
            stock.update(price_y=fetched_price_y, price=fetched_price,
                         candle_data=fetched_chart_final,
                         last_update=date.today())
        else:
            current_app.logger.debug(f"Calling stock factory for {ticker}.")
            stock = stock_factory(ticker=ticker, name=fetched_name,
                        price=fetched_price, price_y=fetched_price_y,
                        volume=fetched_volume, marketcap=fetched_marketcap,
                        candle_data=fetched_chart_final, last_update=date.today())
            current_app.logger.debug(stock.to_json())

        stock.save()
        current_app.logger.debug(f'{ticker} saved to the DB')
        return stock

    except:
        current_app.logger.error('Failed to update stock price data in the database.'
                                 f' Is the ticker {ticker} valid?')
        return None


def fetch_stock_data(ticker) -> Stock:
    '''
    Fetch stock data from DB, if it is stale update first.
    Returns a Stock object.
    ---
    ticker: Stock ticker
    '''
    current_app.logger.debug("Fetch stock")
    stock = load_stock(ticker)
    if stock:
        if stock.last_update.date() == date.today():
            current_app.logger.debug(f"{ticker} last update was today.")
            return stock
        else:
            current_app.logger.debug(f"{ticker} data is not fresh.")

    try:
        current_app.logger.debug(f"Updating {ticker} data!")
        stock = update_stock_data(ticker)
        return stock

    except:
        current_app.logger.error(f'While updating {ticker} stock data.')
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
    # This is a mock stock for TradeZero
    if ticker == 'ZERO':
        data = {
            "ticker": ticker,
            "name": 'TradeZero Inc.',
            "volume": 0.0,
            "marketcap": 0,
            "price": 0.00,
        }
        return jsonify(data), 200

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
            return jsonify(data), 200
        else:
            return jsonify({"status": 404, "reason": "Stock not found."}), 404
    except:
        return jsonify({"status": 500, "reason": "Internal Server Error"}), 500


@api_bp.route('/candlechart/<ticker>', methods=['GET'])
@swag_from('candlechart.yml')
def candlechart(ticker):
    '''
    Endpoint to return stock candle chart data for the last 7 days.
    '''
    if ticker == 'ZERO':
        data = [{ "open" : 0.0,
                   "high" : 0.0,
                   "low" : 0.0,
                   "close" : 0.0,
                   "timestamp" : 1682395200
               }]
        return jsonify(data), 200

    try:
        stock = fetch_stock_data(ticker)
        if stock.candle_data:
            return jsonify(stock.candle_data), 200
        else:
            return jsonify({"status": 404, "reason": "Stock not found."}), 404
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
        if stock:
            return jsonify(stock.get_intraday()), 200
        else:
            return jsonify({"status": 404, "reason": "Stock not found."}), 404
    except:
        return jsonify({"status": 500, "reason": "Internal Server Error"}), 500


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

