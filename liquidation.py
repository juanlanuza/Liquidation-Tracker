import sqlite3
import ccxt
import datetime
from sqlite3 import OperationalError
from time import sleep

def create():
    print("DB does not Exist Yet, Creating Now")
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    c.execute('CREATE TABLE liquidation (coin text, price integer, qty integer, size integer, side text, time integer UNIQUE)')
    conn.commit()
    c.execute('CREATE TABLE market (coin text UNIQUE, price integer, percent integer, volume integer)')
    conn.commit()
    conn.close()

def read_db():
    print("Trying to Read DB")
    try:
        conn = sqlite3.connect('tracker.db')
        c = conn.cursor()
        c.execute('SELECT * FROM  liquidation')
        data = c.fetchall()
        print(data)
    except sqlite3.OperationalError:
        create()
        conn.commit()
        conn.close()

def liquidation():
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
    #get liquidation data
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
        time = int(lick['time'])

        #read Current Data in DB
        conn = sqlite3.connect('tracker.db')
        c = conn.cursor()

        print("Inserting New Liquidation Data")
        #Delete Existting Data when updating
        try:
            c.execute('INSERT OR REPLACE INTO liquidation VALUES (?, ?, ?, ?, ?, ?)',
                      (coin, price, qty, size, side, time))
            conn.commit()
            conn.close()
        except OperationalError:
            print("Error In line 2")
            create()
            return
        except IndexError:
            c.execute('INSERT OR REPLACE INTO liquidation VALUES (?, ?, ?, ?, ?, ?)',
                      (coin, price, qty, size, side, time))
            conn.commit()
            conn.close()

        print("Liquidation Data Added")

def market():
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
    #get market data
    market = exchange.fapiPublicGetTicker24hr()

    todayCalc = datetime.date.today()
    today = str(todayCalc)

    #read Current Data in DB
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()

    for data in market:
        coin = data['symbol']
        coin = coin.replace("USDT","")
        price = float(data['lastPrice'])
        percent = round(float(data['priceChangePercent']),2)
        volume = round(float(data['quoteVolume']),0)

        #read Current Data in DB
        conn = sqlite3.connect('tracker.db')
        c = conn.cursor()

        print("Inserting Market Data")
        #Delete Existting Data when updating
        try:
            c.execute('INSERT OR REPLACE INTO market VALUES (?, ?, ?, ?)',
                      (coin, price, percent, volume))
            conn.commit()
            conn.close()
        except OperationalError:
            print("Error In line 2")
            create()
            return
        except IndexError:
            c.execute('INSERT OR REPLACE INTO market VALUES (?, ?, ?, ?)',
                      (coin, price, percent, volume))
            conn.commit()
            conn.close()

        print("Market Data Added")

def run():
    market()
    liquidation()

while True:
    run()
    print("Closing Connection...")
    sleep(60)
