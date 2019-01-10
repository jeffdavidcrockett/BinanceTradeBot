import sqlite3


class Database:
    def __init__(self):
        """
        Connects to trade_bot.db database. Initializes cursor. If user_data and
        trade_data tables do not exist, they are created.
        """
        self.conn = sqlite3.connect('trade_bot.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS user_data (username TEXT, password TEXT,
                                                                api_key TEXT, secret_key TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS trade_data (datetime DATE, asset TEXT, 
                                                                 trade_size TEXT, trade_entry TEXT, 
                                                                 trade_exit TEXT, gain_percent TEXT)''')

    def create_user(self, username, password_hash, api_key, secret_key):
        """
        Stores user data into user_data table.

        :param username:
        :param password_hash:
        :param api_key:
        :param secret_key:
        :return:
        """
        self.c.execute('''INSERT INTO user_data VALUES(:username, :password, :api_key, :secret_key)''',
                       {'username': username, 'password': password_hash,
                        'api_key': api_key, 'secret_key': secret_key})
        self.conn.commit()

    def get_user_data(self, username):
        """
        Retrieves all data from specific username. Returns the first
        match found, since duplicate usernames cannot exist.

        :param username:
        :return:
        """
        self.c.execute('SELECT * FROM user_data WHERE username=?', (username,))
        return self.c.fetchone()

    def log_trade(self, datetime, asset, trade_size, entry_price, exit_price, gain):
        """
        Logs trade date into trade_data table.

        :param datetime:
        :param asset:
        :param trade_size:
        :param entry_price:
        :param exit_price:
        :param gain:
        :return:
        """
        self.c.execute('''INSERT INTO trade_data VALUES(:datetime, :asset, :trade_size, :trade_entry,
                        :trade_exit, :gain_percent)''', {'datetime': datetime, 'asset': asset,
                                                         'trade_size': trade_size, 'trade_entry': entry_price,
                                                         'trade_exit': exit_price, 'gain_percent': gain})
        self.conn.commit()