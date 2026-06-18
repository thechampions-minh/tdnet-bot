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
    # Yahooファイナンス PTS値上がり率
    url = "https://finance.yahoo.co.jp/pts/ranking/price_up"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finance.yahoo.co.jp/',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
    }
    
    res = requests.get(url, headers=headers, timeout=20)
    
    if res.status_code!= 200:
        send(f"PTS Error: Yahoo HTTP {res.status_code} {now}")
        raise SystemExit
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Yahooのテーブル構造
    alerts = []
    rows = soup.select('table tbody tr')
    
    for row in rows[:15]:
        cols = row.find_all('td')
        if len(cols) >= 5:
            try:
                code_name = cols[0].text.strip() # "1301 極洋" の形式
                code = code_name.split()[0]
                name = code_name.split()[1][:8] if len(code_name.split()) > 1 else code_name[:8]
                price = cols[1].text.strip()
                change = cols[3].text.strip() # 前日比%
                
                if '+' in change and '%' in change:
                    pct = float(change.replace('+','').replace('%','').replace(',',''))
                    if pct >= 4.0: # +4%以上だけ
                        alerts.append(f"<b>{code}</b> {name} {change} | {price}円")
            except Exception as e:
                continue
    
    if alerts:
        msg = f"🌙 <b>PTS急騰 {now}</b>\n明日監視↓\n\n" + "\n".join(alerts)
        msg += "\n\n※朝8:55気配確認必須。PTSで買わない"
        send(msg)
    else:
        send(f"PTS: +4%超なし {now}") # 動いてる確認用。安定したら消してOK
        
except Exception as e:
    error = traceback.format_exc()
    send(f"PTS FATAL {now}:\n<pre>{error[:3000]}</pre>")
