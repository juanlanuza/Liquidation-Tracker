import sqlite3
import ccxt
import datetime
from sqlite3 import OperationalError
from time import sleep

def create():
    print("DB does not Exist Yet, Creating Now")
    conn = sqlite3.connect('liquidation.db')
    c = conn.cursor()
    c.execute('CREATE TABLE liquidation (date text, coin text, price integer, qty integer, size integer, side text, time integer UNIQUE)')
    conn.commit()
    conn.close()

def read_db():
    print("Trying to Read DB")
    try:
        conn = sqlite3.connect('liquidation.db')
        c = conn.cursor()
        c.execute('SELECT * FROM  liquidation')
        data = c.fetchall()
        print(data)
    except sqlite3.OperationalError:
        create(exchange)
        conn.commit()
        conn.close()

def binance():
    exchange_id = 'binance'
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({
        'timeout': 30000,
        'enableRateLimit': True,
        'option': {'defaultMarket': 'futures'},
        'urls': {
            'api': {
                'public': 'https://fapi.binance.com/fapi/v1',
                'private': 'https://fapi.binance.com/fapi/v1',
            }, }
    })
    #get Account Balance
    liquidation = exchange.fapiPublicGetAllForceOrders()

    todayCalc = datetime.date.today()
    today = str(todayCalc)

    for lick in liquidation:
        coin = lick['symbol']
        coin = coin.replace("USDT","")
        price = float(lick['price'])
        qty = round(float(lick['executedQty']),4)
        size = round(qty * price,0)
        side = lick['side']
        time = lick['time']

        #read Current Data in DB
        conn = sqlite3.connect('liquidation.db')
        c = conn.cursor()

        print("Inserting New Values")
        #Delete Existting Data when updating
        try:
            c.execute('INSERT OR REPLACE INTO liquidation VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (today, coin, price, qty, size, side, time))
            conn.commit()
            conn.close()
        except OperationalError:
            print("Error In line 2")
            create()
            return
        except IndexError:
            c.execute('INSERT OR REPLACE INTO liquidation VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (today, coin, price, qty, size, side, time))
            conn.commit()
            conn.close()

        print("Data Added")

def run():
    binance()

while True:
    run()
    print("Closing Connection...")
    sleep(60)
