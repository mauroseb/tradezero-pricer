![GitHub](https://img.shields.io/github/license/mauroseb/tradezero-pricer)

# TradeZero Pricer Backend Microservice

This service is part of the TradeZero application.
It presents financial data like stock prices through a REST API.

## Test Run
```
$ FLASK_APP=$PWD/tradezero_pricer.py flask run
 * Serving Flask app 'tradezero_pricer.py'
 * Debug mode: on
WARNING: This is a development server...
 * Running on http://127.0.0.1:8080
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 860-991-813
```

## API Documentation

 - Browse http://localhost:8080/apidocs


## Unit Testing

 - Use pytest or tox
~~~
$ pytest
 pytest                               
============================================== test session starts =========================================
platform linux -- Python 3.10.9, pytest-7.3.1, pluggy-1.0.0
rootdir: /home/maur0x/stuff/fin/tradezero_pricer
collected 2 items                                                                                     

tradezero_pricer/tests/test_api.py ..                                                                 [100%]
...
========================================== 2 passed, 8 warnings in 0.90s ===================================
~~~
