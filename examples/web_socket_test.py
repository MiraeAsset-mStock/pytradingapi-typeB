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

#Login Via Tasc API, Receive Token in response
login_response=mconnect_obj.login("RAHUL","Macm@123")
test_logger.info(f"Request : Login. Response received : {login_response.json()}")

#Generate access token by calling generate session
gen_response=mconnect_obj.generate_session(__config__.API_KEY,login_response.json()["data"]["jwtToken"],"123")
test_logger.info(f"Request : Generate Session. Response received : {gen_response.json()}")


#Testing Orders Modification, Placement API etc
#Getting API Key
api_key=__config__.API_KEY

#GEtting Access token
access_token=gen_response.json()["data"]["jwtToken"]

#Testing Web Socket or NTicker

m_ticker=MTicker(api_key,access_token,__config__.mticker_url)


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    test_logger.info("Ticks: {}".format(ticks))

def on_order_update(ws,data):
    #Callback to receive Order Updates
    test_logger.info("On Order Updates Packet received : {}".format(data))

def on_trade_update(ws,data):
    #Callback to receive Trade Updates
    test_logger.info("On Trade Updates Packet received : {}".format(data))

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
#Assigning Order Update Callback
m_ticker.on_order_update=on_order_update
#Assigning Trade Update Callback
m_ticker.on_trade_update=on_trade_update

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
m_ticker.connect()


test_logger.info('Now Closing Web socket connection')

m_ticker.close()

test_logger.info('Testing complete')







