import requests
from bs4 import BeautifulSoup
import os
import traceback
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg[:4000], 'parse_mode': 'HTML', 'disable_web_page_preview': True}, timeout=10)

jst = timezone(timedelta(hours=9))
now = datetime.now(jst).strftime('%m/%d %H:%M')

try:
    # 2024年以降の正しいYahoo PTS URL
    url = "https://finance.yahoo.co.jp/stocks/pts/ranking?market=pts&term=day&type=price_up"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finance.yahoo.co.jp/'
    }
    
    res = requests.get(url, headers=headers, timeout=20)
    
    if res.status_code!= 200:
        send(f"PTS Error: Yahoo HTTP {res.status_code} {now}")
        raise SystemExit
    
    soup = BeautifulSoup(res.text, 'html.parser')
    alerts = []
    
    # Yahooの新しい構造：data-testid属性で取る
    rows = soup.select('table tbody tr')
    
    for row in rows[:20]:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 4:
            try:
                # 0:コード・銘柄名 1:PTS株価 2:出来高 3:前日比
                code_name = cols[0].get_text(strip=True)
                price = cols[1].get_text(strip=True)
                change = cols[3].get_text(strip=True)
                
                # "1301極洋" みたいにくっついてるので分離
                import re
                match = re.match(r'(\d{4})(.+)', code_name)
                if match:
                    code = match.group(1)
                    name = match.group(2)[:8]
                else:
                    continue
                
                if '+' in change and '%' in change:
                    pct = float(change.replace('+','').replace('%','').replace(',',''))
                    if pct >= 4.0: # +4%以上
                        alerts.append(f"<b>{code}</b> {name} {change} | {price}")
            except:
                continue
    
    if alerts:
        msg = f"🌙 <b>PTS急騰 {now}</b>\n監視リスト↓\n\n" + "\n".join(alerts)
        msg += "\n\n※8:55気配確認。PTSで買わない"
        send(msg)
    else:
        send(f"PTS: +4%超なし {now}")
        
except Exception as e:
    error = traceback.format_exc()
    send(f"PTS FATAL {now}:\n<pre>{error[:3000]}</pre>")
