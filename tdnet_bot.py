import requests
import json
import os
from bs4 import BeautifulSoup

# ===== ここ2行だけ書き換える =====
TOKEN = '8950681253:AAFMduvBf_-ePdaF6Jpxa_QPg0GaiMJsGgA'
CHAT_ID = '8738195981'
# =================================

# 送信済みIDを保存するファイル
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

# 送信済み読み込み
sent = load_sent()

try:
    html = requests.get('https://www.release.tdnet.info/inbs/I_list.html', timeout=10).text
    soup = BeautifulSoup(html, 'html.parser')
    
    for row in soup.select('tr')[1:]:
        c = row.select('td')
        if len(c) < 4: continue
        jikoku, code, name, title = [x.text.strip() for x in c[:4]]
        
        # 重要ワード判定 + 市場時間のみ
        if any(k in title for k in ['上方修正','黒字転換','大型受注','株式分割','自社株買い']) and jikoku[:2] in ['09','10','11','12','13','14','15']:
            uid = code + jikoku + title
            if uid not in sent:
                msg = f'🚨 {jikoku}\n{code} {name}\n{title}\nhttps://www.release.tdnet.info/inbs/I_list_001_{code}.html'
                send_msg(msg)
                sent.add(uid)

    # 送信済みを保存
    save_sent(sent)
    
except Exception as e:
    print('エラー:', e)

print('チェック完了')