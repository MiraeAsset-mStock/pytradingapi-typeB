import os,sys
import csv
import logging
import json
  
parent_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from tradingapi_b.mticker import *
from tradingapi_b.mconnect import *
from tradingapi_b import __config__

# Create and configure logger
logging.basicConfig(filename="miraesdk_typeB_socket.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')

# Creating an object
test_logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
test_logger.setLevel(logging.INFO)

#Object for NConnect API
mconnect_obj=MConnectB()


username="XXXXXXXX" #Replace Your username here
password="XXXXXXXX" #Replace Your password here

#Login Via Tasc API, Receive Token in response
login_response=mconnect_obj.login(username,password)
test_logger.info(f"Request : Login. Response received : {login_response.json()}")

## !!!! NOTE - Use generate_session() only when TOTP is NOT enabled for the user. Else use verify_totp() to generate access_token !!!!

#Generate access token by calling generate session
# OTP=input("Enter OTP received on mobile no or email id : ");
# gen_response=mconnect_obj.generate_session(__config__.API_KEY,login_response.json()["data"]["jwtToken"],OTP)
# test_logger.info(f"Request : Generate Session. Response received : {gen_response.json()}")


## !!!! NOTE - If TOTP is enabled for the user, then only call Verify TOTP. Else skip verify_totp() !!!!

#verify TOTP 
TOTP=input("Enter TOTP from Auhtenticator app : ");
gen_response=mconnect_obj.verify_totp(__config__.API_KEY,login_response.json()["data"]["jwtToken"],TOTP)
test_logger.info(f"Request : Verify TOTP. Response received : {gen_response.json()}")
print(gen_response.json())


#Testing Orders Modification, Placement API etc
#Getting API Key
api_key=__config__.API_KEY

#GEtting Access token
access_token=gen_response.json()["data"]["jwtToken"]

#Testing Web Socket or NTicker

m_ticker=MTicker(api_key,access_token,__config__.mticker_url)


def on_ticks(ws, ticks):
    # Use the built-in format_tick_data method from MTicker
    formatted_ticks = m_ticker.format_tick_data(ticks)
    for formatted_tick in formatted_ticks:
        test_logger.info(json.dumps(formatted_tick, separators=(',', ':')))

def on_order_update(ws,data):
    #Callback to receive Order Updates
    test_logger.info("On Order Updates Packet received : {}".format(data))

def on_trade_update(ws,data):
    #Callback to receive Trade Updates
    test_logger.info("On Trade Updates Packet received : {}".format(data))

def on_connect(ws, response):
    # Callback on successful connect.
    m_ticker.send_login_after_connect()
    # Subscribe to a list of instrument_tokens with different modes
    ws.subscribe("NSE",[22], m_ticker.MODE_SNAP)  # Full market depth
    # ws.subscribe("NSE",[22], m_ticker.MODE_LTP)   # LTP only
    # ws.subscribe("NSE",[22], m_ticker.MODE_QUOTE) # Quote data

    # Try subscribing to an F&O instrument to test open interest
    # ws.subscribe("NFO",[38477], m_ticker.MODE_SNAP)  # Example F&O token
    print("Connected to socket and logged in successfully")

def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    try:
        ws.stop()
    except:
        pass

# Assign the callbacks.
m_ticker.on_ticks = on_ticks
m_ticker.on_connect = on_connect
m_ticker.on_close = on_close
#Assigning Order Update Callback
m_ticker.on_order_update=on_order_update
#Assigning Trade Update Callback
m_ticker.on_trade_update=on_trade_update

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
try:
    m_ticker.connect()
except KeyboardInterrupt:
    test_logger.info('Keyboard interrupt received')
except Exception as e:
    test_logger.info(f'Error occurred: {e}')
finally:
    test_logger.info('Now Closing Web socket connection')
    try:
        m_ticker.close()
    except:
        pass
    test_logger.info('Testing complete')







