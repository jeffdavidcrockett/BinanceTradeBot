from binance.client import Client
import sqlite3
import math


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('trade_bot.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS user_data (username TEXT, password TEXT,
                                                                api_key TEXT, secret_key TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS trade_data (datetime DATE, asset TEXT, 
                                                                 trade_size TEXT, trade_entry TEXT, 
                                                                 trade_exit TEXT, gain_percent TEXT)''')

    def create_user(self, username, password_hash, api_key, secret_key):
        self.c.execute('''INSERT INTO user_data VALUES(:username, :password, :api_key, :secret_key)''',
                       {'username': username, 'password': password_hash,
                        'api_key': api_key, 'secret_key': secret_key})
        self.conn.commit()

    def get_user_data(self, username):
        self.c.execute('SELECT * FROM user_data WHERE username=?', (username,))
        return self.c.fetchone()

    def log_trade(self, datetime, asset, trade_size, entry_price, exit_price, gain):
        self.c.execute('''INSERT INTO trade_data VALUES(:datetime, :asset, :trade_size, :trade_entry,
                        :trade_exit, :gain_percent)''', {'datetime': datetime, 'asset': asset,
                                                         'trade_size': trade_size, 'trade_entry': entry_price,
                                                         'trade_exit': exit_price, 'gain_percent': gain})
        self.conn.commit()


class Bot:
    def __init__(self):
        self.asset = None
        self.trade_amount = None

    def connect(self, api_key, secret_key):
        self.client = Client(api_key, secret_key)

    def setup_params(self, asset, trade_amount, interval):
        self.asset = asset
        self.trade_amount = trade_amount
        self.time_interval = interval

    def check_params(self):
        if self.asset and self.trade_amount:
            return True

    def get_btc_balance(self):
        btc_balance = self.client.get_asset_balance(asset='BTC')
        return float(btc_balance['free'])

    def find_ticker(self, selected_ticker):
        all_tickers = self.client.get_all_tickers()
        ticker_found = False

        for ticker in all_tickers:
            if selected_ticker == ticker['symbol']:
                ticker_found = True

        return ticker_found

    def get_klines(self, limit_):
        kline_intervals = {'15m': Client.KLINE_INTERVAL_15MINUTE, '30m': Client.KLINE_INTERVAL_30MINUTE,
                           '1H': Client.KLINE_INTERVAL_1HOUR, '2H': Client.KLINE_INTERVAL_2HOUR,
                           '4H': Client.KLINE_INTERVAL_4HOUR, '6H': Client.KLINE_INTERVAL_6HOUR,
                           '12H': Client.KLINE_INTERVAL_12HOUR, '1D': Client.KLINE_INTERVAL_1DAY}

        klines = self.client.get_klines(symbol=self.asset,
                                        interval=kline_intervals[self.time_interval],
                                        limit=limit_)
        klines.reverse()
        return klines

    def get_bbands(self):
        klines = self.get_klines(25)

        last_20_closes = [float(klines[i][4]) for i in range(20)]
        simple_ma = sum(last_20_closes) / 20
        squared_list = [(close - simple_ma)**2 for close in last_20_closes]

        standard_deviation = math.sqrt(sum(squared_list) / 20)
        lower_band = round(simple_ma - (standard_deviation * 2), 8)

        # calculate upper band (not used currently)
        # upper_band = simple_ma + (standard_deviation * 2)

        return lower_band

    def place_market_buy(self, current_price):
        self.amount = int((self.trade_amount / current_price))
        self.client.order_market_buy(symbol=self.asset,
                                     quantity=self.amount)

    def place_market_sell(self):
        self.client.order_market_sell(symbol=self.asset,
                                      quantity=self.amount)

    def get_current_asset_price(self):
        klines = self.get_klines(1)
        current_price = float(klines[0][4])
        return current_price
