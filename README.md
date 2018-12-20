# Binance Trade Bot
Cryptocurrency trading bot used on the Binance trading platform.

## NOTE
This bot is in testing. The current trading strategy implemented is NOT a
recommended strategy!

Bot will scan the specified trading asset for particular fluctuations in price
action. It calculates the lower bollinger band, as well as the current price.
If current price action is 4% or more below the lower band, a market buy will 
occur. Bot then looks for price to rebound 4.5% or more above entry point. If 
price drops 2% below entry point, a market sell occurs acting as a stoploss in 
order to protect funds.

## Bugs
Bot is still experiencing WSACONNECT faults.