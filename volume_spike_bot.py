import yfinance as yf
import requests
import os
import time
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML', 'disable_web_page_preview': True})

def get_jp_tickers():
    """東証全銘柄取得。失敗したら主要200銘柄"""
    try:
        url = "https://raw.githubusercontent.com/youyo/jp-stock-codes/main/data/jp_stock_codes.json"
        res = requests.get(url, timeout=15).json()
        tickers = [f"{d['code']}.T" for d in res if d['market'] in ['プライム','スタンダード','グロース'] and d['code'][-1]!= '0']
        return tickers
    except:
        return ['7203.T','6758.T','9984.T','8035.T','6861.T','9432.T','8306.T','7974.T','4063.T','6981.T']

def check_spike():
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst).strftime('%H:%M')
    tickers = get_jp_tickers()
    alerts = []
    
    # 100銘柄ずつバッチ処理。無料枠節約
    for i in range(0, len(tickers), 100):
        batch = tickers[i:i+100]
        try:
            # 5分足で寄り15分のデータ取得。yfinanceは15分遅延だから9:15に9:00のデータ取れる
            data = yf.download(batch, period='30d', interval='1d', group_by='ticker', threads=True, progress=False)
            
            for ticker in batch:
                try:
                    df = data[ticker] if len(batch) > 1 else data
                    if len(df) < 21 or df['Volume'].iloc[-1] == 0: continue
                    
                    today_vol = df['Volume'].iloc[-1]
                    avg_vol = df['Volume'].iloc[-21:-1].mean() # 過去20日平均
                    today_close = df['Close'].iloc[-1]
                    prev_close = df['Close'].iloc[-2]
                    price_change = (today_close / prev_close - 1) * 100
                    
                    # 条件：出来高3倍以上 + 3%↑ + 株価200円以上 + 出来高10万株以上
                    if today_vol > avg_vol * 3 and price_change > 3 and today_close > 200 and today_vol > 100000:
                        code = ticker.replace('.T','')
                        alerts.append(f"<b>{code}</b> +{price_change:.1f}% | 出来高{today_vol/avg_vol:.1f}倍")
                        
                except: continue
                
        except: continue
        time.sleep(2)
    
    if alerts:
        msg = f"🚨 <b>9:15 出来高急増 {len(alerts)}件</b>\n\n"
        msg += "\n".join(sorted(alerts, key=lambda x: float(x.split('+')[1].split('%')[0]), reverse=True)[:15])
        msg += f"\n\n{now}時点"
        send(msg)

if __name__ == "__main__":
    check_spike()