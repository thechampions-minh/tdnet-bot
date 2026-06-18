import requests
from bs4 import BeautifulSoup
import os
import traceback
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg[:4000], 'parse_mode': 'HTML'}, timeout=10)
    except:
        pass

jst = timezone(timedelta(hours=9))
now = datetime.now(jst).strftime('%m/%d %H:%M')

try:
    send(f"PTS Debug開始 {now}")
    
    # みんかぶPTS。SBIはBot対策キツすぎ
    url = "https://minkabu.jp/market/pts/ranking/price_up"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    res = requests.get(url, headers=headers, timeout=20)
    send(f"HTTP Status: {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.find_all('li', class_='md_ranking_list_item')
    send(f"取得アイテム数: {len(items)}")
    
    alerts = []
    for i, item in enumerate(items[:10]):
        try:
            code = item.find('div', class_='stock_code').text.strip()
            name = item.find('div', class_='stock_name').text.strip()[:8]
            change = item.find('div', class_='change_rate').text.strip()
            
            send(f"Row{i}: {code} {name} {change}") # 1件ずつ送信して確認
            
            if '+' in change:
                alerts.append(f"<b>{code}</b> {name} {change}")
        except Exception as e:
            send(f"Row{i} Parse Error: {str(e)[:100]}")
    
    if alerts:
        msg = f"🌙 <b>PTS {now}</b>\n" + "\n".join(alerts)
        send(msg)
    else:
        send(f"PTS結果: 急騰0件 {now}")
        
except Exception as e:
    error = traceback.format_exc()
    send(f"PTS FATAL:\n<pre>{error[:3500]}</pre>")

send(f"PTS Debug終了 {now}")
