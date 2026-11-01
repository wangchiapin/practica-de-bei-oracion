# 產生 blocks.json（老師中心「積木組句」用）：「物品 被 (誰) 動作 了」。
# 句子、讀音、西英文全部取自遊戲現有的肯定句（讀音照 GoodTeacher），圖由遊戲用 sceneM／sceneD 現場畫。
# 並實際把「每個事件 × 每個人物（含不指定）」都畫一次，畫不出來就失敗。
# 用法：python3 tools/make_blocks.py          → 重新產生 blocks.json
#       python3 tools/make_blocks.py --check  → 只檢查是否過期（過期或有組合畫不出來就回傳 1）
#       python3 tools/make_blocks.py --sheet 輸出.png  → 另外畫一張抽樣預覽圖
import os, sys, json, re, collections
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HTML = 'file://' + os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'blocks.json')

# 遊戲裡沒有「X 被 Y 動詞」寫法的幾句（原本是「X 髒了」「X 不見了」這種沒有人動手的說法），這裡補成被動說法
PATCH = {
    'dirty_plate':  ('El plato fue ensuciado', 'The plate was made dirty'),
    'dirty_cup':    ('La taza fue ensuciada', 'The cup was made dirty'),
    'dirty_car':    ('El carro fue ensuciado', 'The car was made dirty'),
    'dirty_wallet': ('La cartera fue ensuciada', 'The wallet was made dirty'),
    'lost_wallet':  ('La cartera fue perdida', 'The wallet was lost'),
}
# 老師有男有女，積木裡只留一個（都是「老師」）
SKIP_WHO = {'tchf'}

def evkey(sp):
    return 'd_%s_%s' % (sp[1], sp[2]) if sp[0] == 'D' else sp[1].replace(':', '_')

def load(pg):
    return pg.evaluate("""DATA.map(d=>({id:d.id,tk:d.tok.map(t=>[t.tc,t.sc===t.tc?'':t.sc,t.py,t.zy].join('|')),
      sp:SPEC[SRC[d.id]||d.id]||null,z:ZSET.has(d.id)?1:0,es:d.es,en:d.en}))""")

def build(pg):
    rows = load(pg)
    aff = [r for r in rows if r['sp'] and r['sp'][0] in ('M', 'D') and not r['z']
           and r['tk'][1].split('|')[0] == '被' and r['tk'][-1].split('|')[0] == '了' and len(r['tk']) in (4, 5)]
    bei, le = aff[0]['tk'][1], aff[0]['tk'][-1]
    evs = collections.OrderedDict()
    whotk = collections.defaultdict(collections.Counter); whotx = collections.defaultdict(collections.Counter)
    for r in aff:
        sp = r['sp']; k = evkey(sp)
        who = sp[2] if sp[0] == 'M' else sp[3]
        e = evs.setdefault(k, {'k': k, 'sp': sp[:3], 'dw': who, 'obs': collections.Counter(), 'vbs': collections.Counter(), 'texts': []})
        e['obs'][r['tk'][0]] += 1; e['vbs'][r['tk'][-2]] += 1
        m = re.match(r'^(.+?) (fue|fueron) (.+?)( por (.+))?\.$', r['es']); n = re.match(r'^(.+?) (was|were) (.+?)( by (.+))?\.$', r['en'])
        if len(r['tk']) == 5:
            whotk[who][r['tk'][2]] += 1
            if m and n and m.group(5) and n.group(5): whotx[who][(m.group(5), n.group(5))] += 1
        if m and n: e['texts'].append((len(r['tk']), ' '.join(m.group(1, 2, 3)), ' '.join(n.group(1, 2, 3))))
    out_ev = []
    for k, e in evs.items():
        if len(e['obs']) != 1 or len(e['vbs']) != 1: raise SystemExit('事件 %s 的物品或動詞不一致：%s %s' % (k, dict(e['obs']), dict(e['vbs'])))
        if e['texts']: es, en = max(e['texts'])[1:]
        elif k in PATCH: es, en = PATCH[k]
        else: raise SystemExit('事件 %s 沒有西英文，請補在 PATCH' % k)
        out_ev.append({'k': k, 'tk': next(iter(e['obs'])), 'vb': next(iter(e['vbs'])), 'es': es, 'en': en, 'dw': e['dw'], 'sp': e['sp']})
    for k, (es, en) in PATCH.items():   # 補寫的句子一律採用（遊戲裡那句不是被動說法）
        for e in out_ev:
            if e['k'] == k: e['es'], e['en'] = es, en
    who = []
    for w in whotk:
        if w in SKIP_WHO: continue
        tk = whotk[w].most_common(1)[0][0]; tx = whotx[w].most_common(1)[0][0] if whotx[w] else None
        if not tx: raise SystemExit('人物 %s 沒有「por／by」寫法' % w)
        who.append({'k': w, 'tk': tk, 'es': tx[0], 'en': tx[1]})
    order = {'me': 0, 'he': 1, 'she': 2}
    who.sort(key=lambda x: (order.get(x['k'], 9), x['k']))
    groups = []
    for e in out_ev:
        if e['vb'] not in groups: groups.append(e['vb'])
    out_ev.sort(key=lambda e: groups.index(e['vb']))
    data = {'v': 1, 'g': 'bei', 'bei': bei, 'le': le, 'who': who, 'ev': [{k: e[k] for k in ('k', 'tk', 'vb', 'es', 'en', 'dw')} for e in out_ev]}
    ev_sp = {e['k']: e['sp'] for e in out_ev}
    return data, ev_sp

# 畫畫檢查：每個事件 × 每個人物（含不指定）
def check_draw(pg, data, ev_sp):
    whos = [w['k'] for w in data['who']]
    dw = {e['k']: e['dw'] for e in data['ev']}
    return pg.evaluate("""([evs,whos,dw])=>{const bad=[];let n=0;
      for(const k in evs){const sp=evs[k];
        for(const w of [null].concat(whos)){
          try{const ww=w||dw[k];
            const s=sp[0]==='D'?sceneD(sp[1],sp[2],ww):sceneM(sp[1],ww);
            if(!Array.isArray(s)||s.length<2||typeof s[1]!=='string'||s[1].length<50)bad.push(k+'.'+w+' 空圖');n++;
          }catch(e){bad.push(k+'.'+w+' '+e.message);}
        }}
      return {bad,n};}""", [ev_sp, whos, dw])

def main():
    args = sys.argv[1:]
    with sync_playwright() as p:
        kw = {}
        if os.path.exists('/usr/bin/google-chrome'): kw = {'executable_path': '/usr/bin/google-chrome', 'args': ['--no-sandbox']}
        b = p.chromium.launch(**kw); pg = b.new_page()
        pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
        pg.goto(HTML); pg.wait_for_timeout(500)
        data, ev_sp = build(pg)
        res = check_draw(pg, data, ev_sp)
        if res['bad']:
            print('畫不出來：', *res['bad'][:20], sep='\n  '); sys.exit(1)
        txt = json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'
        if '--check' in args:
            cur = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
            if cur != txt: print('blocks.json 過期了，請執行 python3 tools/make_blocks.py'); sys.exit(1)
            print('OK：%d 個事件、%d 位人物，共 %d 張圖都畫得出來' % (len(data['ev']), len(data['who']), res['n'])); return
        open(OUT, 'w', encoding='utf-8').write(txt)
        print('寫入 blocks.json：%d 個事件、%d 位人物，共 %d 張圖都畫得出來' % (len(data['ev']), len(data['who']), res['n']))
        if '--sheet' in args:
            path = args[args.index('--sheet') + 1]
            import random; random.seed(3)
            pick = random.sample(data['ev'], 24)
            pg.set_content('<body style="margin:0;background:#fff;display:grid;grid-template-columns:repeat(6,1fr);gap:6px;padding:6px;font:12px sans-serif"></body>')
            pg.goto(HTML); pg.wait_for_timeout(300)
            items = [[e['k'], e['tk'] + ' ' + e['vb'], ev_sp[e['k']], e['dw']] for e in pick]
            pg.evaluate("""(items)=>{document.body.innerHTML='<div id=sh style="display:grid;grid-template-columns:repeat(6,1fr);gap:6px;padding:6px;background:#fff;font:12px sans-serif"></div>';
              const h=document.getElementById('sh');
              for(const [k,t,sp,w] of items){const s=sp[0]==='D'?sceneD(sp[1],sp[2],w):sceneM(sp[1],w);
                h.insertAdjacentHTML('beforeend','<div style="border:1px solid #ccc"><div style="height:110px">'+s[1]+'</div><div style="text-align:center">'+t+'</div></div>');}}""", items)
            pg.set_viewport_size({'width': 1200, 'height': 700}); pg.screenshot(path=path, full_page=True)
        b.close()

if __name__ == '__main__':
    main()
