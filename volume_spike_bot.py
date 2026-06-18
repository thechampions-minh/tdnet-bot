import yfinance as yf
import os
import requests
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML'}, timeout=10)

jst = timezone(timedelta(hours=9))
now = datetime.now(jst).strftime('%H:%M')

# 監視銘柄。好きなの入れとけ
codes = ['7203.T', '6758.T', '9984.T', '8306.T', '7974.T']  # トヨタ、ソニー、SBG、三菱UFJ、任天堂

alerts = []
for code in codes:
    try:
        tk = yf.Ticker(code)
        hist = tk.history(period='2d', interval='1d')
        if len(hist) < 2: continue
        
        vol_today = hist['Volume'].iloc[-1]
        vol_prev = hist['Volume'].iloc[-2]
        
        if vol_prev > 0 and vol_today / vol_prev >= 3.0: # 3倍以上
            price = hist['Close'].iloc[-1]
            ratio = vol_today / vol_prev
            name = code.replace('.T', '')
            alerts.append(f"<b>{name}</b> {price:.0f}円 出来高{ratio:.1f}倍")
    except:
        continue

if alerts:
    msg = f"📈 <b>出来高急増 {now}</b>\n" + "\n".join(alerts)
    send(msg)
