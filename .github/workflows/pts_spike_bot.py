import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML', 'disable_web_page_preview': True}, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_pts():
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst).strftime('%m/%d %H:%M')
    
    # User-Agent追加。SBIはBot弾くから必須
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
    }
    
    # URLを最新版に変更
    url = "https://site0.sbisec.co.jp/marble/market/board/pts/ranking.do"
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        res.raise_for_status() # HTTPエラー検知
        soup = BeautifulSoup(res.text, 'html.parser')
        
        alerts = []
        # class名が変わってる可能性高いので広く取る
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:16]: # ヘッダー飛ばして15件
                cols = row.find_all('td')
                if len(cols) >= 5:
                    try:
                        code = cols[0].text.strip()
                        name = cols[1].text.strip()[:8]
                        price = cols[2].text.strip()
                        change = cols[3].text.strip()
                        
                        if '+' in change and '%' in change:
                            pct = float(change.replace('+','').replace('%','').replace(',',''))
                            if pct >= 4: # +4%以上
                                alerts.append(f"<b>{code}</b> {name} {change} | {price}円")
                    except:
                        continue
            if alerts: break # 1つテーブル取れたら終わり
        
        if alerts:
            msg = f"🌙 <b>PTS急騰 {now}</b>\n監視リスト↓\n\n" + "\n".join(alerts[:15])
            msg += "\n\n※朝8:55気配確認。PTSで買わない"
            send(msg)
        else:
            print("No PTS spikes or parse failed")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        send(f"PTS Bot エラー: SBIに接続できませんでした {now}")
    except Exception as e:
        print(f"Parse error: {e}")

if __name__ == "__main__":
    check_pts()
