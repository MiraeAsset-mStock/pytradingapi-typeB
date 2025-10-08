import os,sys
import csv
import logging

parent_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
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

username="XXXXXXXX" #Replace with username
password="XXXXXXXX" #Replace wiht password

#Login Via Tasc API, Receive Token in response
login_response=nconnect_obj.login(username,password)
try:
    test_logger.info(f"Request : Login. Response received : {login_response.json()}")
except:
    test_logger.info(f"Request : Login. Response received : {login_response.content} Status: {login_response.status_code}")

## !!!! NOTE - Use generate_session() only when TOTP is NOT enabled for the user. Else use verify_totp() to generate access_token !!!!

#Generate access token by calling generate session
OTP=input("Enter OTP received on mobile no or email id : ")
gen_response=nconnect_obj.generate_session(__config__.API_KEY,login_response.json()["data"]["jwtToken"],OTP)
try:
    test_logger.info(f"Request : Generate Session. Response received : {gen_response.json()}")
except:
    test_logger.info(f"Request : Generate Session. Response received : {gen_response.content} Status: {gen_response.status_code}")

## !!!! NOTE - If TOTP is enabled for the user, then only call Verify TOTP. Else skip verify_totp() !!!!

#verify TOTP 
# TOTP=input("Enter TOTP from Auhtenticator app : ")
# totp_response=nconnect_obj.verify_totp(__config__.API_KEY,login_response.json()["data"]["jwtToken"],TOTP)
# try:
#     test_logger.info(f"Request : Verify TOTP. Response received : {totp_response.json()}")
#     print(totp_response.json())
# except:
#     test_logger.info(f"Request : Verify TOTP. Response received : {totp_response.content} Status: {totp_response.status_code}")

#Test Place Order
porder_resp=nconnect_obj.place_order("NORMAL","ACC-EQ","22","NSE","BUY","MARKET","20","DELIVERY","0","0","0","0","","0","DAY","") 
try:
    test_logger.info(f"Request : Place Order. Response received : {porder_resp.json()}")
except:
    test_logger.info(f"Request : Place Order. Response received : {porder_resp.content} Status: {porder_resp.status_code}")

#Get Order Book
get_ord_bk=nconnect_obj.get_order_book()
try:
    test_logger.info(f"Request : Get Order Book. Response received : {get_ord_bk.json()}")
except:
    test_logger.info(f"Request : Get Order Book. Response received : {get_ord_bk.content} Status: {get_ord_bk.status_code}")

#Get Net Positions
get_net_pos=nconnect_obj.get_net_position()
try:
    test_logger.info(f"Request : Get Net Positions. Response received : {get_net_pos.json()}")
except:
    test_logger.info(f"Request : Get Net Positions. Response received : {get_net_pos.content} Status: {get_net_pos.status_code}")

#Calculate Order Margin
calc_ord_margin=nconnect_obj.calculate_order_margin("DELIVERY","BUY","5","2250","NSE","ACC","22","0")
try:
    test_logger.info(f"Request : Calculate Order Margin. Response received : {calc_ord_margin.json()}")
except:
    test_logger.info(f"Request : Calculate Order Margin. Response received : {calc_ord_margin.content} Status: {calc_ord_margin.status_code}")

#Modify ORder
morder_resp=nconnect_obj.modify_order("NORMAL","1151250130105","MARKET","DELIVERY","DAY","0","10","SBIN-EQ","3045","NSE","780")
try:
    test_logger.info(f"Request : Modify Order. Response received : {morder_resp.json()}")
except:
    test_logger.info(f"Request : Modify Order. Response received : {morder_resp.content} Status: {morder_resp.status_code}")

#Cancel Order
corder_resp=nconnect_obj.cancel_order("NORMAL","1181250130106")
try:
    test_logger.info(f"Request : Cancel Order. Response received : {corder_resp.json()}")
except:
    test_logger.info(f"Request : Cancel Order. Response received : {corder_resp.content} Status: {corder_resp.status_code}")

#Cancel All Orders
c_all_resp=nconnect_obj.cancel_all()
try:
    test_logger.info(f"Request : Cancel All Orders. Responce received : {c_all_resp.json()}")
except:
    test_logger.info(f"Request : Cancel All Orders. Responce received : {c_all_resp.content} Status: {c_all_resp.status_code}")

#Order Details
ord_details=nconnect_obj.get_order_details("1151250207119")
try:
    test_logger.info(f"Request : Get Order details. Responce received : {ord_details.json()}")
except:
    test_logger.info(f"Request : Get Order details. Responce received : {ord_details.content} Status: {ord_details.status_code}")

#Holdings
holdings_resp=nconnect_obj.get_holdings()
try:
    test_logger.info(f"Request : Get Holdings. Response received : {holdings_resp.json()}")
except:
    test_logger.info(f"Request : Get Holdings. Response received : {holdings_resp.content} Status: {holdings_resp.status_code}")

#Historical Chart
hist_chart=nconnect_obj.get_historical_chart("NSE","11536","ONE_HOUR","01-02-2025","07-02-2025")
try:
    test_logger.info(f"Request : Get Historical Chart. Response received : {hist_chart.json()}")
except:
    test_logger.info(f"Request : Get Historical Chart. Response received : {hist_chart.content} Status: {hist_chart.status_code}")

#Market Quote
mark_quote=nconnect_obj.get_market_quote("OHLC",{"NSE": ["3045"],"BSE": ["500410"]})
test_logger.info(f"Request : Get Market Quote. Response received : {mark_quote}")

#Get Instrument Master
instru_master=nconnect_obj.get_instruments()
try:
    test_logger.info(f"Request : Get Instrument Master. Response received : {instru_master.json()}")
except:
    test_logger.info(f"Request : Get Instrument Master. Response received : {instru_master.content} Status: {instru_master.status_code}")

get_instruments=nconnect_obj.get_instruments()
split_data=get_instruments.text.split("\n")
data=[row.strip().split(",") for row in split_data]
with open('instrument_scrip_master.csv', mode='w') as file:
    writer = csv.writer(file,delimiter=",")
    for row in data:
        writer.writerow(row)

#Get fund summary
fund_sum=nconnect_obj.get_fund_summary()
try:
    test_logger.info(f"Request : Get Fund Summary. Response received : {fund_sum.json()}")
except:
    test_logger.info(f"Request : Get Fund Summary. Response received : {fund_sum.content} Status: {fund_sum.status_code}")

#Get Trade History
trade_hist=nconnect_obj.get_trade_history("2025-01-15","02-02-2025")
try:
    test_logger.info(f"Request : Get Trade History. Response received : {trade_hist.json()}")
except:
    test_logger.info(f"Request : Get Trade History. Response received : {trade_hist.content} Status: {trade_hist.status_code}")

#Convert Position
conv_position=nconnect_obj.convert_position("NSE","3787","DELIVERY","INTRADAY","WIPRO-EQ","WIPRO","","","","","","", "","","","","","","BUY", 1,"DAY")
try:
    test_logger.info(f"Request : Position Conversion. Response received : {conv_position.json()}")
except:
    test_logger.info(f"Request : Position Conversion. Response received : {conv_position.content} Status: {conv_position.status_code}")


#Loser Gainer
los_gain=nconnect_obj.loser_gainer("1","13","1","G")
try:
    test_logger.info(f"Request : Loser Gainer. Response received : {los_gain.json()}")
except:
    test_logger.info(f"Request : Loser Gainer. Response received : {los_gain.content} Status: {los_gain.status_code}")

#Create Basket
cre_basket=nconnect_obj.create_basket("Test Baskett","Tets Bakset Description")
try:
    test_logger.info(f"Request : Create Basket. Response received : {cre_basket.json()}")
except:
    test_logger.info(f"Request : Create Basket. Response received : {cre_basket.content} Status: {cre_basket.status_code}")

#Fetch Basket
fetch_bask=nconnect_obj.fetch_basket()
try:
    test_logger.info(f"Request : Fetch Basket. Response received : {fetch_bask.json()}")
except:
    test_logger.info(f"Request : Fetch Basket. Response received : {fetch_bask.content} Status: {fetch_bask.status_code}")

#Rename Basket
rename_bask=nconnect_obj.rename_basket("Tets Basket123","251")
try:
    test_logger.info(f"Request : Rename Basket. Response received : {rename_bask.json()}")
except:
    test_logger.info(f"Request : Rename Basket. Response received : {rename_bask.content} Status: {rename_bask.status_code}")

#Delete Basket
del_basket=nconnect_obj.delete_basket("251")
try:
    test_logger.info(f"Request : Delete Basket. Response received : {del_basket.json()}")
except:
    test_logger.info(f"Request : Delete Basket. Response received : {del_basket.content} Status: {del_basket.status_code}")

#Calculate Basket
calc_basket=nconnect_obj.calculate_basket("0","C","0","E","0","11915","LMT","Test Basket Updated Renamed","I","DAY","1","A","B","1","19.02","269","NSE")
try:
    test_logger.info(f"Request : Calculate Basket. Response received : {calc_basket.json()}")
except:
    test_logger.info(f"Request : Calculate Basket. Response received : {calc_basket.content} Status: {calc_basket.status_code}")

#Get Trade Book
trade_book=nconnect_obj.get_trade_book()
try:
    test_logger.info(f"Request : Get Trade Book. Response received : {trade_book.json()}")
except:
    test_logger.info(f"Request : Get Trade Book. Response received : {trade_book.content} Status: {trade_book.status_code}")

#Get Intraday chart
intr_chart=nconnect_obj.get_intraday_chart("1","AUBANK","ONE_MINUTE")
try:
    test_logger.info(f"Request : Get Intraday chart data. Response received : {intr_chart.json()}")
except:
    test_logger.info(f"Request : Get Intraday chart data. Response received : {intr_chart.content} Status: {intr_chart.status_code}")

#Get Option Chain Master
opt_chain_master=nconnect_obj.get_option_chain_master("5")
try:
    test_logger.info(f"Request : Get Option Chain Master. Response received : {opt_chain_master.json()}")
except:
    test_logger.info(f"Request : Get Option Chain Master. Response received : {opt_chain_master.content} Status: {opt_chain_master.status_code}")

# #Get Option Chain data
# opt_chain_data=nconnect_obj.get_option_chain_data("2","1432996200","22")
# test_logger.info(f"Request : Get Option Chain Data. Response received : {opt_chain_data.json()}")

# #Logout
# logout=nconnect_obj.logout()
# test_logger.info(f"Request : Logout : {logout.json()}")
