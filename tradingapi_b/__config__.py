API_KEY="<API_KEY>"
default_root_uri= "https://api.mstock.trade/",
routes= {
        "login":"openapi/typeb/connect/login",
        "generate_session":"openapi/typeb/session/token",
        "place_order":"openapi/typeb/orders/regular",
        "modify_order":"openapi/typeb/orders/regular/{order_id}",
        "cancel_order":"openapi/typeb/orders/regular/{order_id}",
        "cancel_all":"openapi/typeb/orders/cancelall",
        "order_book":"openapi/typeb/orders",
        "order_details":"openapi/typeb/order/details",
        "net_position":"openapi/typeb/portfolio/positions",
        "calculate_order_margin":"openapi/typeb/margins/orders",
        "holdings":"openapi/typeb/portfolio/holdings",
        "health_statistics":"openapi/typeb/Health/GetHealthStatistics",
        "historical_chart":"openapi/typeb/instruments/historical",
        "market_quote":"openapi/typeb/instruments/quote",
        "instrument_scrip":"openapi/typeb/instruments/OpenAPIScripMaster",
        "fund_summary":"openapi/typeb/user/fundsummary",
        "trade_history":"openapi/typeb/trades",
        "position_conversion":"openapi/typeb/portfolio/convertposition"
    }
mticker_url="wss://ws.mstock.trade"
