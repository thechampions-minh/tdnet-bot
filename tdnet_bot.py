import requests
import json
import os
from bs4 import BeautifulSoup

# ===== GitHub Secretsから読み込み =====
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
# ======================================

SENT_FILE = 'sent_ids.json'

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_sent(sent_ids):
    with open(SENT_FILE, 'w') as f:
        json.dump(list(sent_ids), f)

def send_msg(text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    requests.post(url, data={'chat_id': CHAT_ID, 'text': text})
    print('送信:', text)

sent = load_sent()

try:
    html = requests.get('https://www.release.tdnet.info/inbs/I_list.html', timeout=10).text
    soup = BeautifulSoup(html, 'html.parser')
    
    for row in soup.select('tr')[1:]:
        c = row.select('td')
        if len(c) < 4: continue
        jikoku, code, name, title = [x.text.strip() for x in c[:4]]
        
        if any(k in title for k in ['上方修正','黒字転換','大型受注','株式分割','自社株買い']) and jikoku[:2] in ['09','10','11','12','13','14','15']:
            uid = code + jikoku + title
            if uid not in sent:
                msg = f'🚨 {jikoku}\n{code} {name}\n{title}\nhttps://www.release.tdnet.info/inbs/I_list_001_{code}.html'
                send_msg(msg)
                sent.add(uid)

    save_sent(sent)
    
except Exception as e:
    print('エラー:', e)

print('チェック完了')
