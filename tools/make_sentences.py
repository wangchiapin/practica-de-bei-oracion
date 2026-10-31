# 從 index.html 的 DATA 產生 sentences.json（給老師管理中心「自訂句庫」挑句子用）
# 用法：python3 tools/make_sentences.py          → 重新產生 sentences.json
#       python3 tools/make_sentences.py --check  → 只檢查是否過期（過期就回傳 1）
import os, sys, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HTML = 'file://' + os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'sentences.json')

def build():
    with sync_playwright() as p:
        kw = {}
        if os.path.exists('/usr/bin/google-chrome'): kw = {'executable_path': '/usr/bin/google-chrome', 'args': ['--no-sandbox']}
        b = p.chromium.launch(**kw)
        pg = b.new_page()
        pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
        pg.goto(HTML); pg.wait_for_timeout(500)
        rows = pg.evaluate("DATA.map(d=>({id:d.id,lv:d.lv,zh:d.tok.map(t=>t.tc).join(''),sc:d.tok.map(t=>t.sc).join(''),es:d.es,en:d.en}))")
        b.close()
    return {'v': 1, 'sentences': rows}

if __name__ == '__main__':
    data = build()
    text = json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'
    if '--check' in sys.argv:
        cur = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
        if cur != text:
            print('sentences.json 過期了：遊戲的句子有變，請執行 python3 tools/make_sentences.py'); sys.exit(1)
        print('sentences.json OK（%d 句）' % len(data['sentences'])); sys.exit(0)
    open(OUT, 'w', encoding='utf-8').write(text)
    print('寫入 sentences.json：%d 句' % len(data['sentences']))
