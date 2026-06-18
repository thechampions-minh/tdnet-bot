import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML'}, timeout=10)

print("=== PTS Bot Start ===")

jst = timezone(timedelta(hours=9))
now = datetime.now(jst).strftime('%m/%d %H:%M')
print(f"Time: {now}")

url = "https://site0.sbisec.co.jp/marble/market/board/pts/ranking.do"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

try:
    print(f"Requesting: {url}")
    res = requests.get(url, headers=headers, timeout=20)
    print(f"Status: {res.status_code}")
    print(f"Content length: {len(res.text)}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")
    
    alerts = []
    for i, table in enumerate(tables):
        rows = table.find_all('tr')
        print(f"Table {i}: {len(rows)} rows")
        
        if len(rows) > 1:
            cols = rows[1].find_all('td')
            print(f"Row 1 cols: {len(cols)}")
            if len(cols) > 0:
                print(f"First cell: {cols[0].text.strip()[:50]}")
            
            # 全部の行チェック
            for row in rows[1:16]:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    try:
                        raw = [c.text.strip() for c in cols]
                        print(f"Row data: {raw}") # ← これ重要
                        
                        code = cols[0].text.strip()
                        change = cols[3].text.strip()
                        
                        if '+' in change:
                            alerts.append(f"{code} {change}")
                    except Exception as e:
                        print(f"Parse row error: {e}")
        break # 最初のテーブルだけ
    
    print(f"Total alerts: {len(alerts)}")
    
    if alerts:
        msg = f"🌙 <b>PTS {now}</b>\n" + "\n".join(alerts[:10])
        send(msg)
    else:
        send(f"PTS Debug: 0件 {now}") # 何もなくても通知飛ばす
        
except Exception as e:
    print(f"FATAL: {e}")
    send(f"PTS Bot FATAL: {e}")

print("=== PTS Bot End ===")
