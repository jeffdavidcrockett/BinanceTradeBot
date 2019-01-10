from TradeBotClass.trade_bot import Bot
from DatabaseClass.database import Database
from MenuClass.mainmenu import Menu


bot = Bot()
db = Database()
menu = Menu(bot, db)
