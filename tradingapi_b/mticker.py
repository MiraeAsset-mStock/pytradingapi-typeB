'''
This is the socket based implementation: nFeed _OpenAPI Type B
'''
import sys
import time
import sys,traceback
import six
import json
import threading
import struct
import logging
from datetime import datetime
from twisted.internet import reactor,ssl
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS
from twisted.python import log as twisted_log

default_log = logging.getLogger("mticker.log")
default_log.addHandler(logging.FileHandler("mticker.log", mode='a'))

class MTickerClientProtocol(WebSocketClientProtocol):
    PING_INTERVAL = 2.5
    KEEPALIVE_INTERVAL = 5

    _next_ping = None
    _next_pong_check = None
    _last_pong_time = None
    _last_ping_time = None
    
    def __init__(self, *args, **kwargs):
        """Initialize protocol with all options passed from factory."""
        super(MTickerClientProtocol, self).__init__(*args, **kwargs)

    def onConnect(self, response):  # noqa
        """Called when WebSocket server connection was established"""
        self.factory.ws = self

        if self.factory.on_connect:
            self.factory.on_connect(self, response)

        # Reset reconnect on successful reconnect
        self.factory.resetDelay()

    def onOpen(self):  # noqa
        """Called when the initial WebSocket opening handshake was completed."""
        # send ping
        self._loop_ping()
        # init last pong check after X seconds
        self._loop_pong_check()

        if self.factory.on_open:
            self.factory.on_open(self)

    def onMessage(self, payload, is_binary):  # noqa
        """Called when text or binary message is received."""
        if self.factory.on_message:
            self.factory.on_message(self, payload, is_binary)

    def onClose(self, was_clean, code, reason):  # noqa
        """Called when connection is closed."""
        if not was_clean:
            if self.factory.on_error:
                self.factory.on_error(self, code, reason)

        if self.factory.on_close:
            self.factory.on_close(self, code, reason)

        # Cancel next ping and timer
        self._last_ping_time = None
        self._last_pong_time = None

        if self._next_ping:
            self._next_ping.cancel()

        if self._next_pong_check:
            self._next_pong_check.cancel()

    def onPong(self, response):  # noqa
        """Called when pong message is received."""
        if self._last_pong_time and self.factory.debug:
            default_log("last pong was {} seconds back.".format(time.time() - self._last_pong_time))

        self._last_pong_time = time.time()

        if self.factory.debug:
            default_log("pong => {}".format(response))

    """
    Custom helper and exposed methods.
    """

    def _loop_ping(self):  # noqa
        """Start a ping loop where it sends ping message every X seconds."""
        if self.factory.debug:
            if self._last_ping_time:
                default_log.debug("last ping was {} seconds back.".format(time.time() - self._last_ping_time))

        # Set current time as last ping time
        self._last_ping_time = time.time()

        # Call self after X seconds
        self._next_ping = self.factory.reactor.callLater(self.PING_INTERVAL, self._loop_ping)

    def _loop_pong_check(self):
        """
        Timer sortof to check if connection is still there.

        Checks last pong message time and disconnects the existing connection to make sure it doesn't become a ghost connection.
        """
        if self._last_pong_time:
            # No pong message since long time, so init reconnect
            last_pong_diff = time.time() - self._last_pong_time
            if last_pong_diff > (2 * self.PING_INTERVAL):
                if self.factory.debug:
                    default_log.debug("Last pong was {} seconds ago. So dropping connection to reconnect.".format(
                        last_pong_diff))
                # drop existing connection to avoid ghost connection
                self.dropConnection(abort=True)

        # Call self after X seconds
        self._next_pong_check = self.factory.reactor.callLater(self.PING_INTERVAL, self._loop_pong_check)


class MTickerClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    """Autobahn WebSocket client factory to implement reconnection and custom callbacks."""
    protocol = MTickerClientProtocol
    maxDelay = 5
    maxRetries = 10

    _last_connection_time = None

    def __init__(self, *args, **kwargs):
        """Initialize with default callback method values."""
        self.debug = False
        self.ws = None
        self.on_open = None
        self.on_error = None
        self.on_close = None
        self.on_message = None
        self.on_connect = None
        self.on_reconnect = None
        self.on_noreconnect = None

        super(MTickerClientFactory, self).__init__(*args, **kwargs)

    def startedConnecting(self, connector):  # noqa
        """On connecting start or reconnection."""
        if not self._last_connection_time and self.debug:
            default_log.debug("Start WebSocket connection.")

        self._last_connection_time = time.time()

    def clientConnectionFailed(self, connector, reason):  # noqa
        """On connection failure (When connect request fails)"""
        if self.retries > 0:
            default_log.error("Retrying connection. Retry attempt count: {}. Next retry in around: {} seconds".format(self.retries, int(round(self.delay))))

            # on reconnect callback
            if self.on_reconnect:
                self.on_reconnect(self.retries)

        # Retry the connection
        self.retry(connector)
        self.send_noreconnect()

    def clientConnectionLost(self, connector, reason):  # noqa
        """On connection lost (When ongoing connection got disconnected)."""
        if self.retries > 0:
            # on reconnect callback
            if self.on_reconnect:
                self.on_reconnect(self.retries)

        # Retry the connection
        self.retry(connector)
        self.send_noreconnect()

    def send_noreconnect(self):
        """Callback `no_reconnect` if max retries are exhausted."""
        if self.maxRetries is not None and (self.retries > self.maxRetries):
            if self.debug:
                default_log.debug("Maximum retries ({}) exhausted.".format(self.maxRetries))
                # Stop the loop for exceeding max retry attempts
                self.stop()

            if self.on_noreconnect:
                self.on_noreconnect()

class MTicker(object):
    EXCHANGE_MAP = {
        "nse": 1,
        "nfo": 2,
        "cds": 3,
        "bse": 4,
        "bfo": 5,
        "bcd": 6,
        "mcx": 7,
        "mcxsx": 8,
        "indices": 9,
        "bsecds": 6,
    }

    # Default connection timeout
    CONNECT_TIMEOUT = 30
    # Default Reconnect max delay.
    RECONNECT_MAX_DELAY = 60
    # Default reconnect attempts
    RECONNECT_MAX_TRIES = 50
    # Default root API endpoint. It's possible to
    # override this by passing the `root` parameter during initialisation.

    # Available streaming modes.
    MODE_LTP = 1
    MODE_QUOTE = 2
    MODE_SNAP = 3

    # Flag to set if its first connect
    _is_first_connect = True

    # Available actions.
    _message_code = 11
    _message_subscribe = 1
    _message_unsubscribe = 0
    _message_setmode = "mode"

    #Available Exchange Types
    EXCHANGE_TYPE={
        "nsecm":1,
        "nsefo":2,
        "bsecm":3,
        "bsefo":4,
        "nsecd":13
    }

    # Minimum delay which should be set between retries. User can't set less than this
    _minimum_reconnect_max_delay = 5
    # Maximum number or retries user can set
    _maximum_reconnect_max_tries = 300

    def __init__(self,api_key, access_token, root,debug=False, 
                 reconnect=True, reconnect_max_tries=RECONNECT_MAX_TRIES, reconnect_max_delay=RECONNECT_MAX_DELAY,
                 connect_timeout=CONNECT_TIMEOUT): #Added api_key, parameter

        self.root = root #or self.ROOT_URI

        # Set max reconnect tries
        if reconnect_max_tries > self._maximum_reconnect_max_tries:
            default_log.warning("`reconnect_max_tries` can not be more than {val}. Setting to highest possible value - {val}.".format(
                val=self._maximum_reconnect_max_tries))
            self.reconnect_max_tries = self._maximum_reconnect_max_tries
        else:
            self.reconnect_max_tries = reconnect_max_tries

        # Set max reconnect delay
        if reconnect_max_delay < self._minimum_reconnect_max_delay:
            default_log.warning("`reconnect_max_delay` can not be less than {val}. Setting to lowest possible value - {val}.".format(
                val=self._minimum_reconnect_max_delay))
            self.reconnect_max_delay = self._minimum_reconnect_max_delay
        else:
            self.reconnect_max_delay = reconnect_max_delay

        self.connect_timeout = connect_timeout

        #Adding access token variable
        self.access_token=access_token
        
        #Adding API KEy variable
        self.api_key=api_key
        self.socket_url = "{root}?ACCESS_TOKEN={access_token}&API_KEY={api_key}".format(
                root=self.root,
                access_token=access_token,
                api_key=api_key
            )
        # Debug enables logs
        self.debug = debug

        # Initialize default value for websocket object
        self.ws = None

        # Placeholders for callbacks.
        self.on_ticks = None
        self.on_open = None
        self.on_close = None
        self.on_error = None
        self.on_connect = None
        self.on_message = None
        self.on_reconnect = None
        self.on_noreconnect = None

        # Text message updates
        #For Orders
        self.on_order_update = None
        #For Trades
        self.on_trade_update=None

        # List of current subscribed tokens
        self.subscribed_tokens = {}

    def _create_connection(self, url, **kwargs):
        """Create a WebSocket client connection."""
        self.factory = MTickerClientFactory(url, **kwargs)

        # Alias for current websocket connection
        self.ws = self.factory.ws
        self.factory.debug = self.debug

        # Register private callbacks
        self.factory.on_open = self._on_open
        self.factory.on_error = self._on_error
        self.factory.on_close = self._on_close
        self.factory.on_message = self._on_message
        self.factory.on_connect = self._on_connect
        self.factory.on_reconnect = self._on_reconnect
        self.factory.on_noreconnect = self._on_noreconnect

        self.factory.maxDelay = self.reconnect_max_delay
        self.factory.maxRetries = self.reconnect_max_tries

    def connect(self, threaded=False, disable_ssl_verification=False, proxy=None):

        # Init WebSocket client factory
        self._create_connection(self.socket_url,
                                proxy=proxy, ) 

        # Set SSL context
        context_factory = None
        if self.factory.isSecure and not disable_ssl_verification:
            context_factory = ssl.ClientContextFactory()

        # Establish WebSocket connection to a server
        connectWS(self.factory, contextFactory=context_factory, timeout=self.connect_timeout)

        if self.debug:
            twisted_log.startLogging(sys.stdout)

        # Run in seperate thread of blocking
        opts = {}

        # Run when reactor is not running
        if not reactor.running:
            if threaded:
                # Signals are not allowed in non main thread by twisted so suppress it.
                opts["installSignalHandlers"] = False
                self.websocket_thread = threading.Thread(target=reactor.run, kwargs=opts)
                self.websocket_thread.daemon = True
                self.websocket_thread.start()
            else:
                reactor.run(**opts)

    def is_connected(self):
        """Check if WebSocket connection is established."""
        if self.ws and self.ws.state == self.ws.STATE_OPEN:
            return True
        else:
            return False

    def _close(self, code=None, reason=None):
        """Close the WebSocket connection."""
        if self.ws:
            self.ws.sendClose(code, reason)

    def close(self, code=None, reason=None):
        """Close the WebSocket connection."""
        self.stop_retry()
        self._close(code, reason)

    def stop(self):
        """Stop the event loop. Should be used if main thread has to be closed in `on_close` method.
        Reconnection mechanism cannot happen past this method
        """
        reactor.stop()

    def stop_retry(self):
        """Stop auto retry when it is in progress."""
        if self.factory:
            self.factory.stopTrying()

    def send_login_after_connect(self):
        try:
            #Send Login:AccessToken to socket to maintain connection
            self.ws.sendMessage(six.b(f"LOGIN:{self.access_token}"))
            return True
        except Exception as e:
            self._close(reason="Error while subscribe: {}".format(str(e)))
            raise

    def subscribe(self,exchangeType,instrument_tokens):
        """
        Subscribe to a list of instrument_tokens.

        - `instrument_tokens` is list of instrument instrument_tokens to subscribe
        """
        try:
            #Subscription Packet
            _packet={
                "correlationID": "",
                "action": self._message_subscribe,
                "params": {
                    "mode": self.MODE_QUOTE,
                    "tokenList": [
                    {
                        "exchangeType": self.EXCHANGE_TYPE[str(exchangeType).lower()] if str(exchangeType).lower() in self.EXCHANGE_TYPE else 1,
                        "tokens": instrument_tokens
                    }
                    ]
                    }
            }

            self.ws.sendMessage(six.b(json.dumps(_packet)))

            for token in instrument_tokens:
                self.subscribed_tokens[token] = self.MODE_QUOTE

            return True
        except Exception as e:
            self._close(reason="Error while subscribe: {}".format(str(e)))
            raise

    def unsubscribe(self,exchangeType, instrument_tokens):
        """
        Unsubscribe the given list of instrument_tokens.

        - `instrument_tokens` is list of instrument_tokens to unsubscribe.
        """
        try:
            #Unsubscription Packet
            _packet={
                "correlationID": "",
                "action": self._message_unsubscribe,
                "params": {
                    "mode": self.MODE_QUOTE,
                    "tokenList": [
                    {
                        "exchangeType": self.EXCHANGE_TYPE[str(exchangeType).lower()] if str(exchangeType).lower() in self.EXCHANGE_TYPE else 1,
                        "tokens": instrument_tokens
                    }
                    ]
                    }
            }
            self.ws.sendMessage(
                six.b(json.dumps(_packet))
            )

            for token in instrument_tokens:
                try:
                    del (self.subscribed_tokens[token])
                except KeyError:
                    pass

            return True
        except Exception as e:
            self._close(reason="Error while unsubscribe: {}".format(str(e)))
            raise

    def resubscribe(self):
        """Resubscribe to all current subscribed tokens."""
        modes = {}

        for token in self.subscribed_tokens:
            m = self.subscribed_tokens[token]

            if not modes.get(m):
                modes[m] = []

            modes[m].append(token)

        for mode in modes:
            if self.debug:
                default_log.debug("Resubscribe and set mode: {} - {}".format(mode, modes[mode]))

            self.subscribe(modes[mode])

    def _on_connect(self, ws, response):
        self.ws = ws
        if self.on_connect:
            print("WebSocket connected")
            self.on_connect(self, response)

    def _on_close(self, ws, code, reason):
        """Call `on_close` callback when connection is closed."""
        default_log.error("Connection closed: {} - {}".format(code, str(reason)))

        if self.on_close:
            self.on_close(self, code, reason)

    def _on_error(self, ws, code, reason):
        """Call `on_error` callback when connection throws an error."""
        default_log.error("Connection error: {} - {}".format(code, str(reason)))

        if self.on_error:
            self.on_error(self, code, reason)

    def _on_message(self, ws, payload, is_binary):
        """Call `on_message` callback when text message is received."""
        if self.on_message:
            self.on_message(self, payload, is_binary)

        # If the message is binary, parse it and send it to the callback.
        if self.on_ticks and is_binary and len(payload) > 4:
            self.on_ticks(self, self._parse_binary(payload))

        # Parse text messages
        if not is_binary:
            self._parse_text_message(payload)

    def _on_open(self, ws):
        # Resubscribe if its reconnect
        if not self._is_first_connect:
            self.resubscribe()

        # Set first connect to false once its connected first time
        self._is_first_connect = False
        
        if self.on_open:
            return self.on_open(self)

    def _on_reconnect(self, attempts_count):
        if self.on_reconnect:
            return self.on_reconnect(self, attempts_count)

    def _on_noreconnect(self):
        if self.on_noreconnect:
            return self.on_noreconnect(self)

    def _parse_text_message(self, payload):
        """Parse text message."""
        # Decode unicode data
        if not six.PY2 and type(payload) == bytes:
            payload = payload.decode("utf-8")

        try:
            data = json.loads(payload)
        except ValueError:
            return

        # Order update callback
        if self.on_order_update and data.get("order_status") == "order" and data.get("orderData"):
            self.on_order_update(self, data["orderData"])

        #Trade Update Callback
        if self.on_trade_update and data.get("order_status") == "trade" and data.get("orderData"):
            self.on_trade_update(self, data["orderData"])

        # Custom error with websocket error code 0
        if data.get("type") == "error":
            self._on_error(self, 0, data.get("data"))

    def _parse_binary(self, bin):
        """Parse binary data to a (list of) ticks structure."""
        try:
            #Assuming every message has a single packet
            data = []

            #for packet in packets:
            packet=bin
            subscription_mode=int.from_bytes(packet[0:1], sys.byteorder)
            exchange_type=int.from_bytes(packet[1:2], sys.byteorder)
            instrument_token = int.from_bytes( packet[2:27], sys.byteorder)
            sequence_no=int.from_bytes( packet[27:35], sys.byteorder)
            ex_timestamp=datetime.fromtimestamp(int.from_bytes( packet[35:43], sys.byteorder))
            ltp=int.from_bytes( packet[43:51], sys.byteorder)

            #segment = instrument_token & 0xff  # Retrive segment constant from instrument_token

            # Add price divisor based on segment
            #Right now keeping it 100 for all
            divisor = 100.0

            #LTP Mode packets
            if len(packet)==6:
                data.append(
                    {
                        "mode":self.MODE_LTP,
                        "subscription_mode":subscription_mode,
                        "exchange_type":exchange_type,
                        "instrument_token":instrument_token,
                        "sequence_no":sequence_no,
                        "ex_timestamp":ex_timestamp,
                        "ltp":ltp
                    }
                )
            #123 for quote 
            elif len(packet)==123 or len(packet)==379:

                d={
                    "mode":self.MODE_QUOTE if len(packet)==123 else self.MODE_SNAP,
                    "subscription_mode":subscription_mode,
                    "exchange_type":exchange_type,
                    "instrument_token":instrument_token,
                    "sequence_no":sequence_no,
                    "ex_timestamp":ex_timestamp,
                    "ltp":ltp,

                    "last_traded_qty":int.from_bytes( packet[51:59], sys.byteorder),
                    "avg_traded_price":int.from_bytes( packet[59:67], sys.byteorder),
                    "vol_traded_today":int.from_bytes( packet[67:75], sys.byteorder),
                    "tot_buy_qty":int.from_bytes( packet[75:83], sys.byteorder),
                    "tot_sell_qty":int.from_bytes( packet[83:91], sys.byteorder),
                    "ohlc": {
                            "open": int.from_bytes( packet[91:99], sys.byteorder),
                            "high": int.from_bytes( packet[99:107], sys.byteorder),
                            "low": int.from_bytes( packet[107:115], sys.byteorder),
                            "close": int.from_bytes( packet[115:123], sys.byteorder),
                        }
                    }

                if len(packet)==379:
                    try:
                        timestamp = datetime.fromtimestamp(self._unpack_int(packet, 123, 131))
                    except Exception:
                        timestamp = None
                    d["last_traded_timestamp"]=timestamp
                    d["open_interest"]=self._unpack_int(packet, 131, 139)
                    d["open_interest_percent"]=self._unpack_int(packet, 139, 147)

                    #Market Depth 200 bytes 147+200
                    depth = {
                            "bid": [],
                            "ask": []
                            }

                    for i,p in enumerate(range(147, len(packet), 4)):
                        depth["ask" if i >= 5 else "bid"].append({
                                    "buy_or_sell":self._unpack_int(packet, p, p + 2),
                                    "quantity":self._unpack_int(packet, p + 2, p + 10),
                                    "price":self._unpack_int(packet, p + 10, p + 18)/divisor,
                                    "orders":self._unpack_int(packet, p + 18, p + 20, byte_format="H")
                                })

                    d["upper_circuit_lmt"]=self._unpack_int(packet, 347, 355)
                    d["lower_circuit_lmt"]=self._unpack_int(packet, 355, 363)
                    d["52_wk_high"]=self._unpack_int(packet, 363, 371)
                    d["52_wk_low"]=self._unpack_int(packet, 371, 379)

                data.append(d)
            return data
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            default_log.error(stack_trace)
            raise e
        

    def _unpack_int(self, bin, start, end, byte_format="I"):
        """Unpack binary data as unsigned interger."""
        return struct.unpack(">" + byte_format, bin[start:end])[0]
