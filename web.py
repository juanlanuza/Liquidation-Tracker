from flask import Flask, render_template, jsonify, Markup
import sqlite3
import datetime

app = Flask(__name__)

@app.route("/")
def index():
    try:
        print("Checking for Todays Data")
        todayCalc = datetime.date.today()
        today = str(todayCalc)

        now = datetime.datetime.now()
        yday = now - datetime.timedelta(days = 1)
        ts = now.timestamp()
        yts = yday.timestamp()
        time = now.strftime("%m/%d/%Y, %H:%M:%S")

        conn = sqlite3.connect('liquidation.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        sizes = c.execute('SELECT coin,sum(size) FROM liquidation WHERE time > ? GROUP BY coin ORDER BY sum(size) DESC LIMIT 10', (yts,)).fetchall()
        amounts = c.execute('SELECT coin,count(coin) FROM liquidation WHERE time > ? GROUP BY coin ORDER BY sum(size) DESC LIMIT 10', (yts,)).fetchall()
        datas = c.execute('SELECT coin,avg(size),avg(qty),price FROM liquidation WHERE time > ? GROUP BY coin', (yts,)).fetchall()
        conn.commit()
        conn.close()

        conn = sqlite3.connect('market.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        top10 = c.execute('SELECT * FROM market WHERE date = ? ORDER BY percent DESC LIMIT 10', (today,)).fetchall()
        low10 = c.execute('SELECT * FROM market WHERE date = ? ORDER BY percent ASC LIMIT 10', (today,)).fetchall()
        markets = c.execute('SELECT * FROM market WHERE date = ?', (today,)).fetchall()
        conn.commit()
        conn.close()

        return render_template('index.html',time = time,ts = ts,yts = yts,sizes = sizes,amounts = amounts,datas = datas,markets = markets,top10 = top10,low10 = low10)

    except TypeError as missing_data:
        print(missing_data)
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000,debug=True)
