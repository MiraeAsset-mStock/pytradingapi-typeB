## TradingAPI SDK - Python Client for accessing TradingAPI and Streaming Market Data

### Description
TradingAPI is a complete SDK that allows you to build a trading and investment platform which includes executing orders in real time, streaming live trade and order data (Using Websockets) and more. 

### Installation
> [!IMPORTANT]
> You can install the python client with below command. For requirements.txt file [refer here](https://github.com/MiraeAsset-mStock/pytradingapi-typeB/blob/main/requirements.txt).
```
pip install -r requirements.txt
 
pip install --upgrade mStock-TradingApi-B
```
 
It is recommended to update 'pip' and `setuptools` to the latest version if you are facing any issues during installation
 
```
pip install -U pip setuptools
```
 
>[!NOTE]
>The package can be used with the name **tradingapi_b**
```

### API Usage

```python
import logging
from tradingapi_b.mconnect import *

logging.basicConfig(level=logging.DEBUG)

#Object for MConnect API
mconnect_obj=MConnectB()

#Login
login_response=mconnect_obj.login("<user_id>","<password>")

#Generate access token by calling generate session
gen_response=mconnect_obj.generate_session("<API_Key>","<request_token_here>","<otp>")

#Place Order
try:
    porder_resp=mconnect_obj.place_order(_variety="NORMAL",_trading_symbol="ACC-EQ",_symboltoken="22",_exchange="NSE",_transactiontype="BUY",_ordertype="MARKET",_quantity="20",_producttype="DELIVERY",_price="0",_triggerprice="0",_squareoff="0",_stoploss="0",_trailingStopLoss="",_disclosedquantity="0",_duration="DAY",_ordertag="")
    
    logging.info("Order placed. ID is: {}".format(porder_resp["data"]["order_id"]))

except Exception as e:
    logging.info("Order placement failed: {}".format(e.message))

#Fetch all orders
mconnect_obj.get_order_book()

#Fetch all holdings
mconnect_obj.get_holdings()

#Get Net position for logged in user
mconnect_obj.get_net_position()

#Cancel All orders
mconnect_obj.cancel_all()

#Get fund Summary
mconnect_obj.get_fund_summary()

```

### Websocket Usage
```python
from tradingapi_b.mticker import *
import logging

logging.basicConfig(level=logging.DEBUG)

#Testing Web Socket or MTicker
m_ticker=MTicker("<API_KEY>","<ACCESS_TOKEN>","<WEB_SOCKET_URL>")


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    logging.info("Ticks: {}".format(ticks))

def on_order_update(ws,data):
    #Callback to receive Order Updates
    logging.info("On Order Updates Packet received : {}".format(data))

def on_trade_update(ws,data):
    #Callback to receive Trade Updates
    logging.info("On Trade Updates Packet received : {}".format(data))

def on_connect(ws, response):
    # Callback on successful connect.
    m_ticker.send_login_after_connect()
    # Subscribe to a list of instrument_tokens 
    ws.subscribe("NSE",[5633])
    print("Connected to socket and logged in successfully")

def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
m_ticker.on_ticks = on_ticks
m_ticker.on_connect = on_connect
m_ticker.on_close = on_close
m_ticker.on_order_update=on_order_update
m_ticker.on_trade_update=on_trade_update

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
m_ticker.connect()


logging.info('Now Closing Web socket connection')

m_ticker.close()

logging.info('Testing complete')


```

### Running Unit Tests

This requires having pytest library pre installed. You can install the same via pip:

``` pip install pytest ```

Navigate to the ```unit``` directory and run the ```connect_test.py``` file using pytest

```
cd unit
pytest connect_test.py
```

### Support
For issues, please open an issue on GitHub.

### Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a new branch (feature-xyz)
3. Commit your changes
4. Push the branch and create a pull request
