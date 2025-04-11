import os,sys
parent_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from tradingapi_b.mconnect import *
from tradingapi_b import __config__

# Create and configure logger
logging.basicConfig(filename="miraesdk_typeB.log",
                    format='%(asctime)s %(message)s',
                    filemode='a',)

# Creating an object
test_logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
test_logger.setLevel(logging.INFO)

#Object for NConnect API
nconnect_obj=MConnectB()

#Login Via Tasc API, Receive Token in response
login_response=nconnect_obj.login("RAHUL","Macm@123")
test_logger.info(f"Request : Login. Response received : {login_response.json()}")

#Generate access token by calling generate session
gen_response=nconnect_obj.generate_session(__config__.API_KEY,login_response.json()["data"]["jwtToken"],"123")
test_logger.info(f"Request : Generate Session. Response received : {gen_response.json()}")

#Test Place Order
porder_resp=nconnect_obj.place_order("NORMAL","ACC-EQ","22","NSE","BUY","MARKET","20","DELIVERY","0","0","0","0","","0","DAY","") 
test_logger.info(f"Request : Place Order. Response received : {porder_resp.json()}")

#Get Order Book
get_ord_bk=nconnect_obj.get_order_book()
test_logger.info(f"Request : Get Order Book. Response received : {get_ord_bk.json()}")

#Get Net Positions
get_net_pos=nconnect_obj.get_net_position()
test_logger.info(f"Request : Get Net Positions. Response received : {get_net_pos.json()}")

#Calculate Order Margin
calc_ord_margin=nconnect_obj.calculate_order_margin("DELIVERY","BUY","5","2250","NSE","ACC","22","0")
test_logger.info(f"Request : Calculate Order Margin. Response received : {calc_ord_margin.json()}")

#Modify ORder
morder_resp=nconnect_obj.modify_order("NORMAL","1151250130105","MARKET","DELIVERY","DAY","0","10","SBIN-EQ","3045","NSE")
test_logger.info(f"Request : Modify Order. Response received : {morder_resp.json()}")

#Cancel Order
corder_resp=nconnect_obj.cancel_order("NORMAL","1181250130106")
test_logger.info(f"Request : Cancel Order. Response received : {corder_resp.json()}")

#Cancel All Orders
c_all_resp=nconnect_obj.cancel_all()
test_logger.info(f"Request : Cancel All Orders. Responce received : {c_all_resp.json()}")

#Order Details
ord_details=nconnect_obj.get_order_details("1151250207119","E")
test_logger.info(f"Request : Get Order details. Responce received : {ord_details.json()}")

#Holdings
holdings_resp=nconnect_obj.get_holdings()
test_logger.info(f"Request : Get Holdings. Response received : {holdings_resp.json()}")

#Historical Chart
hist_chart=nconnect_obj.get_historical_chart("NSE","11536","ONE_HOUR","01-02-2025","07-02-2025")
test_logger.info(f"Request : Get Historical Chart. Response received : {hist_chart.json()}")

#Market Quote
mark_quote=nconnect_obj.get_market_quote("OHLC",{"NSE": ["3045"],"BSE": ["500410"]})
test_logger.info(f"Request : Get Market Quote. Response received : {mark_quote}")

#Get Instrument Master
instru_master=nconnect_obj.get_instruments()
test_logger.info(f"Request : Get Instrument Master. Response received : {instru_master.json()}")

#Get fund summary
fund_sum=nconnect_obj.get_fund_summary()
test_logger.info(f"Request : Get Fund Summary. Response received : {fund_sum.json()}")

#Get Trade History
trade_hist=nconnect_obj.get_trade_history("2025-01-15","02-02-2025")
test_logger.info(f"Request : Get Trade History. Response received : {trade_hist.json()}")

#Convert Position
conv_position=nconnect_obj.convert_position("NSE","3787","DELIVERY","INTRADAY","WIPRO-EQ","WIPRO","","","","","","", "","","","","","","BUY", 1,"DAY")
test_logger.info(f"Request : Position Conversion. Response received : {conv_position.json()}")
