# 從 index.html 的 DATA 產生 sentences.json（給老師管理中心「自訂句庫」挑句子用）
# 用法：python3 tools/make_sentences.py          → 重新產生 sentences.json
#       python3 tools/make_sentences.py --check  → 只檢查是否過期（過期就回傳 1）
import os, sys, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HTML = 'file://' + os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'sentences.json')
OUT2 = os.path.join(ROOT, 'sentences-tk.json')   # 含逐詞拼音／注音：每句 {id, tk:['繁|簡|拼音|注音',…]}，簡體與繁體相同就留空（學習單用）

def build():
    with sync_playwright() as p:
        kw = {}
        if os.path.exists('/usr/bin/google-chrome'): kw = {'executable_path': '/usr/bin/google-chrome', 'args': ['--no-sandbox']}
        b = p.chromium.launch(**kw)
        pg = b.new_page()
        pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
        pg.goto(HTML); pg.wait_for_timeout(500)
        rows = pg.evaluate("DATA.map(d=>({id:d.id,lv:d.lv,zh:d.tok.map(t=>t.tc).join(''),sc:d.tok.map(t=>t.sc).join(''),es:d.es,en:d.en}))")
        tk = pg.evaluate("DATA.map(d=>({id:d.id,tk:d.tok.map(t=>[t.tc,t.sc===t.tc?'':t.sc,t.py,t.zy].join('|'))}))")
        b.close()
    return {'v': 1, 'sentences': rows}, {'v': 1, 'sentences': tk}

def dump(d): return json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n'

if __name__ == '__main__':
    d1, d2 = build()
    t1, t2 = dump(d1), dump(d2)
    if '--check' in sys.argv:
        c1 = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
        c2 = open(OUT2, encoding='utf-8').read() if os.path.exists(OUT2) else ''
        if c1 != t1 or c2 != t2:
            print('sentences.json／sentences-tk.json 過期了：遊戲的句子有變，請執行 python3 tools/make_sentences.py'); sys.exit(1)
        print('sentences.json／sentences-tk.json OK（%d 句）' % len(d1['sentences'])); sys.exit(0)
    open(OUT, 'w', encoding='utf-8').write(t1); open(OUT2, 'w', encoding='utf-8').write(t2)
    print('寫入 sentences.json、sentences-tk.json：%d 句' % len(d1['sentences']))
