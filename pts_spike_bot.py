import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML', 'disable_web_page_preview': True})

def check_pts():
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst).strftime('%m/%d %H:%M')
    
    # SBI証券 PTS値上がり率ランキング
    url = "https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETmgR001Control&_PageID=WPLETmgR001Mdtl20&_DataStoreID=DSWPLETmgR001Control&_ActionID=DefaultAID&getFlg=on"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        alerts = []
        tables = soup.find_all('table', class_='md-table-01')
        if tables and len(tables) > 0:
            rows = tables[0].find_all('tr')[1:16] # 上位15件
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    code = cols[1].text.strip()
                    name = cols[2].text.strip()[:8] # 名前長いと通知崩れる
                    price = cols[3].text.strip()
                    change = cols[4].text.strip()
                    
                    # +4%以上を通知
                    if '+' in change:
                        try:
                            pct = float(change.replace('+','').replace('%','').replace(',',''))
                            if pct > 4:
                                alerts.append(f"<b>{code}</b> {name} {change} | {price}円")
                        except: continue
        
        if alerts:
            msg = f"🌙 <b>PTS急騰 {now}</b>\n明日監視リスト↓\n\n" + "\n".join(alerts)
            msg += "\n\n※朝8:55気配確認必須。PTSで買わない"
            send(msg)
    except Exception as e:
        print(f"PTS error: {e}")

if __name__ == "__main__":
    check_pts()