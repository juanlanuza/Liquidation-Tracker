import sqlite3
import ccxt
import datetime
from sqlite3 import OperationalError
from time import sleep

def create():
    print("DB does not Exist Yet, Creating Now")
    conn = sqlite3.connect('market.db')
    c = conn.cursor()
    c.execute('CREATE TABLE market (date text, coin text, price integer, percent integer, volume integer)')
    conn.commit()
    c.execute('INSERT INTO market VALUES (?, ?, ?, ?, ?)',
              ('start', 0, 0, 0, 0))
    conn.commit()
    conn.close()

def read_db():
    print("Trying to Read DB")
    try:
        conn = sqlite3.connect('market.db')
        c = conn.cursor()
        c.execute('SELECT * FROM  market')
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
    liquidation = exchange.fapiPublicGetTicker24hr()

    todayCalc = datetime.date.today()
    today = str(todayCalc)

    #read Current Data in DB
    conn = sqlite3.connect('market.db')
    c = conn.cursor()

    try:
        c.execute('SELECT * FROM market')
        c.execute('DELETE FROM market WHERE rowid > 1')
        conn.commit()
        conn.close()
    except OperationalError:
        print("Error In line 2")
        create()
        return
    except IndexError:
        c.execute('SELECT * FROM market')
        c.execute('DELETE FROM market WHERE date > ?', (today,))
        conn.commit()
        conn.close()

    for lick in liquidation:
        coin = lick['symbol']
        coin = coin.replace("USDT","")
        price = float(lick['lastPrice'])
        percent = round(float(lick['priceChangePercent']),2)
        volume = round(float(lick['quoteVolume']),0)

        #read Current Data in DB
        conn = sqlite3.connect('market.db')
        c = conn.cursor()

        print("Inserting New Values")
        #Delete Existting Data when updating
        try:
            c.execute('INSERT INTO market VALUES (?, ?, ?, ?, ?)',
                      (today, coin, price, percent, volume))
            conn.commit()
            conn.close()
        except OperationalError:
            print("Error In line 2")
            create()
            return
        except IndexError:
            c.execute('INSERT INTO market VALUES (?, ?, ?, ?, ?)',
                      (today, coin, price, percent, volume))
            conn.commit()
            conn.close()

        print("Data Added")

def run():
    binance()

while True:
    run()
    print("Closing Connection...")
    sleep(60)
