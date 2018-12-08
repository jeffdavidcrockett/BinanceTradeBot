from my_classes import db, bot
import sys
import time
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


def startup():
    print('\n1. Login\n'
          '2. Create Account\n'
          '3. Exit\n')
    while True:
        choice = input('> ')
        if choice == '1':
            login()
        elif choice == '2':
            create_account()
        elif choice == '3':
            sys.exit()
        else:
            print('\n*** Not a valid selection, try again ***\n')


def login():
    print("\nEnter your username, or 'X' to return to previous menu")
    username = input('> ')
    if username == 'X':
        startup()
    result = db.get_user_data(username)
    if result:
        password_hash = result[1]
        while True:
            print("\nEnter your password, or 'X' to return to previous menu")
            password = input('> ')
            if password == 'X':
                startup()
            elif check_password_hash(password_hash, password):
                api_key = result[2]
                secret_key = result[3]
                bot.connect(api_key, secret_key)
                print('\nAccess granted\n')
                main_menu()
            else:
                print('\n*** The password you entered was incorrect ***\n')
    else:
        print('\n*** Username does not exist ***\n')
        time.sleep(2)
        login()


def create_account():
    print('\nEnter a username')
    username = input('> ')
    print('\nEnter a password')
    password = input('> ')
    print('\nEnter password again')
    password2 = input('> ')
    if password == password2:
        password_hash = generate_password_hash(password)
        print('\nEnter your Binance account\'s API key (copy/paste recommended)')
        api_key = input('> ')
        print('\nEnter your secret key')
        secret_key = input('> ')
        db.create_user(username, password_hash, api_key, secret_key)
        print('\nAccount Created\n')
        time.sleep(2)
        startup()
    else:
        print('\n*** Passwords did not match! Please start over ***\n')
        time.sleep(3)
        create_account()


def main_menu():
    btc_balance = bot.get_btc_balance()
    print('\n--------------------------------\n')
    print('           MAIN MENU\n')
    print('       Avail BTC:', btc_balance)
    print('--------------------------------\n')
    print('1) Setup\n'
          '2) Run bot\n'
          '3) View current setup\n'
          '4) Quit')
    while True:
        choice = input('> ')

        if choice == '1':
            setup(btc_balance)
        elif choice == '2':
            run()
        elif choice == '3':
            pass
        elif choice == '4':
            sys.exit()
        else:
            print('\n*** Not a valid selection ***\n')


def setup(btc_balance):
    while True:
        print("\nEnter asset pair symbol to trade (all caps),\n"
              "or 'X' to return to main menu.\n"
              "EXAMPLE: BNBBTC")
        selected_asset = input('> ')
        if selected_asset != 'X':
            ticker_found = bot.find_ticker(selected_asset)
            if ticker_found:
                max_trade_size = btc_balance - (btc_balance * .08)
                print('\nAsset located\n')
                print('Enter amount of btc to trade with.')
                print('Maximum trade amount allowed: ', max_trade_size)
                trade_amount = float(input('> '))
                if trade_amount <= max_trade_size:
                    interval_list = ['15m', '30m', '1H', '2H', '4H', '6H', '12H', '1D']
                    print('\nEnter the time frame you would like to trade on')
                    print('Select from the following options:')
                    for item in interval_list:
                        print(item)
                    interval = input('> ')
                    if interval in interval_list:
                        bot.setup_params(selected_asset, trade_amount, interval)
                        print('\nSetup complete')
                        time.sleep(2)
                        main_menu()
                    else:
                        print('\n*** Invalid interval selection ***\n')
                elif trade_amount > max_trade_size:
                    print('\n*** Not enough funds to make desired trade size ***\n'
                          '*** Please deposit bitcoin to trade ***\n'
                          'Your max trade amount is', max_trade_size, '\n')
            else:
                print('\n*** No asset match found ***\n')
                main_menu()
        else:
            main_menu()


def run():
    count = 1
    if bot.check_params():
        while True:
            vals = look_for_trade()

            if len(vals) > 1:
                lower, current_price, percentage_diff, btc_balance = vals
                print('\nLOOKING FOR TRADE')
                print('BTC Balance:', btc_balance)
                print('Lower band:', lower)
                print('Current price:', current_price)
                print('Percentage difference:', str(percentage_diff) + '%')

                if percentage_diff <= -4:
                    print('\nTRADE FOUND\n')
                    in_trade(current_price)
            else:
                error = vals
                print(error)

            time.sleep(count)
            count *= 2
            if count > 32:
                count = 1
        # try:
        #     lower = bot.get_bbands()
        #     current_price = bot.get_current_asset_price()
        #     percentage_diff = round((current_price - lower) / lower * 100, 2)
        #     btc_balance = bot.get_btc_balance()
        # except BinanceAPIException as e:
        #     print(e)
        # else:
        #     print('\nLOOKING FOR TRADE')
        #     print('BTC Balance:', btc_balance)
        #     print('Lower band:', lower)
        #     print('Current price:', current_price)
        #     print('Percentage difference:', str(percentage_diff) + '%')
        #
        #     if percentage_diff <= -4:
        #         print('\nTRADE FOUND, ENTERING TRADE\n')
        #         in_trade(current_price)
        #
        #     time.sleep(15)
        # finally:
        #     run()
    else:
        print('\n*** Please run setup first ***\n')
        time.sleep(2)
        main_menu()


def in_trade(enter_price):
    bot.place_market_buy(enter_price)
    print('Market order was placed')
    while True:
        current_price = bot.get_current_asset_price()
        percentage_gain = round((current_price - enter_price) / enter_price * 100, 2)
        utc_time = datetime.utcnow()
        formatted_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
        print('LOOKING FOR TRADE EXIT')
        print('CURRENT TRADE GAIN:', str(percentage_gain) + '%')
        if percentage_gain >= 4.5:
            bot.place_market_sell()
            print('TRADE EXITED WITH A', str(percentage_gain) + '% GAIN')
            db.log_trade(formatted_time, bot.asset, bot.trade_amount,
                         enter_price, current_price, str(percentage_gain) + '%')
            main_menu()
        elif percentage_gain < -2.1:
            bot.place_market_sell()
            print('TRADE EXITED WITH A', str(percentage_gain) + '% LOSS')
            db.log_trade(formatted_time, bot.asset, bot.trade_amount,
                         enter_price, current_price, str(percentage_gain) + '%')
            main_menu()

        time.sleep(10)


def look_for_trade():
        try:
            lower = bot.get_bbands()
            current_price = bot.get_current_asset_price()
            percentage_diff = round((current_price - lower) / lower * 100, 2)
            btc_balance = bot.get_btc_balance()

            return lower, current_price, percentage_diff, btc_balance
        except BinanceAPIException as error:
            return error



startup()
