from flask import Flask, render_template, jsonify, Markup
import sqlite3
import datetime

app = Flask(__name__)

@app.template_filter('currencyFormat')
def currencyFormat(value):
    value = float(value)
    return "${:,.2f}".format(value)

@app.template_filter('shortLong')
def shortLong(value):
    if value == "SELL":
        return "LONG".format(value)
    else:
        return "SHORT".format(value)

@app.route("/")
def index():
    try:
        print("Checking for Todays Data")

        todayCalc = datetime.date.today()
        today = str(todayCalc)

        now = datetime.datetime.utcnow()
        yday = now - datetime.timedelta(days = 1)
        ts = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        yts = yday.strftime('%Y-%m-%d %H:%M:%S.%f')
        time = now.strftime("%m/%d/%Y, %H:%M:%S")
        ytime = yday.strftime("%m/%d/%Y, %H:%M:%S")

        conn = sqlite3.connect('tracker.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        sizes = c.execute('SELECT coin,sum(size) FROM liquidation WHERE time > ? GROUP BY coin ORDER BY sum(size) DESC LIMIT 10', (yts,)).fetchall()
        amounts = c.execute('SELECT coin,count(coin) FROM liquidation WHERE time > ? GROUP BY coin ORDER BY sum(size) DESC LIMIT 10', (yts,)).fetchall()
        datas = c.execute('SELECT coin,avg(size),avg(qty),price FROM liquidation WHERE time > ? GROUP BY coin', (yts,)).fetchall()
        conn.commit()
        conn.close()

        conn = sqlite3.connect('tracker.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        top10 = c.execute('SELECT * FROM market ORDER BY percent DESC LIMIT 10').fetchall()
        low10 = c.execute('SELECT * FROM market ORDER BY percent ASC LIMIT 10').fetchall()
        markets = c.execute('SELECT * FROM market').fetchall()
        conn.commit()
        conn.close()

        return render_template('index.html',time = time,ytime = ytime,ts = ts,yts = yts,sizes = sizes,amounts = amounts,datas = datas,markets = markets,top10 = top10,low10 = low10)

    except TypeError as missing_data:
        print(missing_data)
        return render_template('index.html')

@app.route("/livetracker")
def livetracker():
    try:
        print("Checking for Todays Data")

        todayCalc = datetime.date.today()
        today = str(todayCalc)

        now = datetime.datetime.utcnow()
        yday = now - datetime.timedelta(days = 1)
        ts = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        yts = yday.strftime('%Y-%m-%d %H:%M:%S.%f')
        time = now.strftime("%m/%d/%Y, %H:%M:%S")
        ytime = yday.strftime("%m/%d/%Y, %H:%M:%S")

        min15 = now - datetime.timedelta(minutes = 15)
        min15 = min15.strftime('%Y-%m-%d %H:%M:%S.%f')
        min30 = now - datetime.timedelta(minutes = 30)
        min30 = min30.strftime('%Y-%m-%d %H:%M:%S.%f')
        hour1 = now - datetime.timedelta(hours = 1)
        hour1 = hour1.strftime('%Y-%m-%d %H:%M:%S.%f')
        hour12 = now - datetime.timedelta(hours = 12)
        hour12 = hour12.strftime('%Y-%m-%d %H:%M:%S.%f')

        conn = sqlite3.connect('tracker.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        datas = c.execute('SELECT * FROM liquidation WHERE time > ? ORDER BY time DESC LIMIT 100', (yts,)).fetchall()
        conn.commit()
        conn.close()

        conn = sqlite3.connect('tracker.db')
        conn.row_factory = lambda cursor, row: row[0]
        c = conn.cursor()
        dmin15 = c.execute('SELECT sum(size) FROM liquidation WHERE time > ?', (min15,)).fetchall()
        dmin30 = c.execute('SELECT sum(size) FROM liquidation WHERE time > ?', (min30,)).fetchall()
        dhour1 = c.execute('SELECT sum(size) FROM liquidation WHERE time > ?', (hour1,)).fetchall()
        dhour12 = c.execute('SELECT sum(size) FROM liquidation WHERE time > ?', (hour12,)).fetchall()
        dday1 = c.execute('SELECT sum(size) FROM liquidation WHERE time > ?', (yts,)).fetchall()
        conn.commit()
        conn.close()

        return render_template('livetracker.html',time = time,ytime = ytime,ts = ts,yts = yts,datas = datas,dmin15 = dmin15,dmin30 = dmin30,dhour1 = dhour1,dhour12 = dhour12,dday1 = dday1)

    except TypeError as missing_data:
        print(missing_data)
        return render_template('livetracker.html')

@app.route("/tracker")
def tracker():
    try:
        return render_template('tracker.html')

    except TypeError as missing_data:
        print(missing_data)
        return render_template('tracker.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80,debug=True)
