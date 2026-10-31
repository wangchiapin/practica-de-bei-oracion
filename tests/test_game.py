# 把／被 練習遊戲測試（兩款是同一套程式，這份檔案兩個 repo 內容相同，會依資料夾名稱判斷是哪一款）
# 涵蓋：維修開關（ba 看 portalStatus/center-ba、bei 看 center-bei）＋ ?preview ＋ ?class 各種狀態、
#       共用設定每個值（字形／語言／拼音注音／語速）、星等門檻邊界、計分、全部關卡都開放、班級成績回傳、題目回報
import os, sys, json, re
from playwright.sync_api import sync_playwright
import common
from common import *

GAME = 'bei' if os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).endswith('bei-oracion') else 'ba'
OTHER = 'ba' if GAME == 'bei' else 'bei'
CID = 'abcdefgh12'
R = Runner()

FAKE_FB = r"""
(function(){
  window.__db = window.__db || {}; window.__ops = window.__ops || [];
  if (window.firebase && window.firebase.__fake) return;
  const DB = window.__db, ops = window.__ops, clone = x => JSON.parse(JSON.stringify(x));
  const depth = p => p.split('/').length;
  function docRef(path){ return {
    path, id: path.split('/').pop(),
    async get(){ if (path.startsWith('portalStatus') && window.__failPortal) throw new Error('portal-fail');
      return { exists: path in DB, id: path.split('/').pop(), data: () => DB[path] && clone(DB[path]) }; },
    async set(d){ if (window.__hangReport && path.startsWith('game_reports')) return new Promise(() => {});
      if (window.__denyScores && path.startsWith('class_scores')) { const e = new Error('denied'); e.code = 'permission-denied'; throw e; }
      ops.push({k:'set', p:path, d:clone(d)}); DB[path] = clone(d); },
    async update(d){ ops.push({k:'update', p:path, d:clone(d)}); DB[path] = Object.assign(DB[path]||{}, clone(d)); } }; }
  function colRef(path){ const q = { doc: id => docRef(path + '/' + (id || ('D' + (window.__ops.length + 1) + Math.random().toString(36).slice(2, 6)))),
    async add(d){ ops.push({k:'add', p:path, d:clone(d)}); const id = 'A' + ops.length; DB[path + '/' + id] = clone(d); return { id }; },
    where(){ return q; }, orderBy(){ return q; }, limit(){ return q; },
    async get(){ const ks = Object.keys(DB).filter(k => k.startsWith(path + '/') && depth(k) === depth(path) + 1);
      return { docs: ks.map(k => ({ id: k.split('/').pop(), data: () => clone(DB[k]) })), size: ks.length }; } };
    return q; }
  const auth = { currentUser: null, async signInAnonymously(){ auth.currentUser = { uid: window.__uid || 'UID1' }; return { user: auth.currentUser }; } };
  const fsInst = { collection: colRef };
  const fire = () => fsInst; fire.FieldValue = { serverTimestamp: () => 'TS' };
  window.firebase = { __fake: true, apps: [], auth: () => auth, firestore: fire,
    initializeApp(c, n){ if (window.__failConn) throw new Error('conn-fail'); const a = { name: n || '[DEFAULT]', auth: () => auth, firestore: () => fsInst }; this.apps.push(a); return a; } };
})();
"""
def route(r):
    u = r.request.url
    if u.startswith('file:'): return r.continue_()
    if 'firebase-app-compat' in u: return r.fulfill(status=200, content_type='application/javascript', body=FAKE_FB)
    if 'gstatic.com/firebasejs' in u: return r.fulfill(status=200, content_type='application/javascript', body='')
    r.abort()
common.route = route

def page(p, query='', settings=None, db=None, flags=None, width=420, height=900):
    init = ''
    if db is not None: init += "window.__db=%s;" % json.dumps(db)
    for k, v in (flags or {}).items(): init += "window.%s=%s;" % (k, json.dumps(v))
    b, pg, errs = open_page(p, query, settings=settings, width=width, height=height, wait=1500, extra_init=init or None)
    return b, pg, errs

def start(pg, lv=1, name='Test'):
    pg.evaluate("(a)=>{cfg.name=a[1]; ST.lv=a[0]; beginLevel();}", [lv, name]); pg.wait_for_timeout(200)

def solve_one(pg, ok=True):
    # 用內部資料直接作答一題（排句子／選圖／選句）
    return pg.evaluate("""(ok)=>{
      const q=ST.qs[ST.qi], c=ST.cur;
      if(q.type==='A'){
        const n=q.s.tok.length;
        if(ok){ for(let i=0;i<n;i++) placeTok(i); confirmA(); }
        else { // 故意排錯：反過來排（單詞句不可能，題庫都 ≥3 個詞）
          for(let i=n-1;i>=0;i--) placeTok(i); confirmA(); }
      } else {
        const k=c.opts.findIndex(o=>o.ok===ok); pickOpt(k);
      }
      return ST.cur.done;
    }""", ok)

CLS_OPEN = {'portalStatus/center-' + GAME: {'off': False}, 'classes/' + CID: {'owner': 'T1', 'showBoard': True}}
def fatal(pg):
    return pg.evaluate("(document.getElementById('clsFatal')||{}).textContent||''")

with sync_playwright() as p:
    # ───── 1) 維修開關與班級連結 ─────
    cases = [
        ('沒有 ?class：一般玩，不出現班級列', '', {}, None, lambda pg, f: f == '' and pg.locator('#clsBar').count() == 0),
        ('?class＋沒有開關文件＝維修中', '?class=' + CID, {'classes/' + CID: {'owner': 'T1'}}, None, lambda pg, f: '維修中' in f),
        ('?class＋開關 off:true＝維修中', '?class=' + CID, {'portalStatus/center-' + GAME: {'off': True}, 'classes/' + CID: {'owner': 'T1'}}, None, lambda pg, f: '維修中' in f),
        ('?class＋開關 off:false＝開放（有班級列）', '?class=' + CID, CLS_OPEN, None, lambda pg, f: f == '' and pg.locator('#clsBar').count() == 1),
        ('只開了「另一款」的開關，這款仍是維修中（開關沒用錯）', '?class=' + CID, {'portalStatus/center-' + OTHER: {'off': False}, 'classes/' + CID: {'owner': 'T1'}}, None, lambda pg, f: '維修中' in f),
        ('開放但班級碼不存在＝連結失效', '?class=' + CID, {'portalStatus/center-' + GAME: {'off': False}}, None, lambda pg, f: '失效' in f),
        ('?preview＋?class＋沒有開關文件＝老師預覽，不受維修影響', '?class=' + CID + '&preview=1', {'classes/' + CID: {'owner': 'T1'}}, None, lambda pg, f: f == ''),
        ('讀開關時出錯＝照常放行', '?class=' + CID, CLS_OPEN, {'__failPortal': True}, lambda pg, f: f == ''),
        ('連不上雲端＝「暫時連不上」', '?class=' + CID, CLS_OPEN, {'__failConn': True}, lambda pg, f: '連不上' in f),
        ('班級碼格式不對（太短）＝當作沒有班級', '?class=abc', {}, None, lambda pg, f: f == '' and pg.locator('#clsBar').count() == 0),
    ]
    for name, q, db, flags, check in cases:
        b, pg, errs = page(p, q, db=db, flags=flags)
        f = fatal(pg)
        R.check(check(pg, f), f'{name}（畫面：{f or "正常"}）')
        b.close()

    # ───── 2) 全部關卡都開放（程式沒有解鎖機制；README 第 40 行「要 1 星才解鎖」與此不符，見測試說明）─────
    b, pg, errs = page(p)
    nlv = pg.evaluate("LV.length")
    R.check(nlv == (4 if GAME == 'bei' else 3), f'關卡數 {nlv}（ba 3 關、bei 4 關）')
    R.check(pg.evaluate("[1,2,3,4].slice(0,LV.length).every(n=>isUnlocked(n))"), '所有關卡一開始就能玩')
    R.check(pg.locator('button.ticket').count() == nlv, '開始畫面有 %d 張關卡票' % pg.locator('button.ticket').count())
    # 沒填名字不能開始
    pg.locator('button.ticket').first.click(); pg.wait_for_timeout(300)
    R.check(pg.evaluate("ST.screen") == 'start', '沒填暱稱：留在開始畫面')
    R.check(pg.evaluate("document.getElementById('nerr').textContent.length>0"), '沒填暱稱：出現提示')
    pg.fill('#nm', 'Ana'); pg.locator('button.ticket').nth(nlv - 1).click(); pg.wait_for_timeout(500)
    R.check(pg.evaluate("ST.screen") == 'game' and pg.evaluate("ST.lv") == nlv, f'填暱稱後點最後一關（第 {nlv} 關）：開始遊戲')
    R.check(pg.evaluate("ST.qs.length") == 10, '一關 10 題')
    types = pg.evaluate("ST.qs.map(q=>q.type)")
    R.check('T' not in types, '題型沒有已停用/不存在的 T（把⇒被轉換題）：%s' % ''.join(types) if GAME == 'bei' else '題型：%s' % ''.join(types))
    R.check(not errs, '沒有網頁錯誤 %s' % errs)
    b.close()

    # ───── 3) 完整打一關：全部一次答對 → 3 星＋分數範圍 ─────
    for lv in range(1, nlv + 1):
        b, pg, errs = page(p)
        start(pg, lv)
        for i in range(10):
            solve_one(pg, True); pg.evaluate("nextQ()")
        R.check(pg.evaluate("ST.screen") == 'result', f'第 {lv} 關：10 題後進入結果頁')
        f = pg.evaluate("ST.final")
        R.check(f['stars'] == 3 and f['firstOK'] == 10, f'第 {lv} 關：全部一次答對 → 3 星（{f["firstOK"]}/10）')
        R.check(1420 <= f['score'] <= 1920, f'第 {lv} 關：全對分數合理 {f["score"]}（連對加成 ×1.2／×1.5 ＋ 速度加分，應介於 1420–1920）')
        R.check(pg.evaluate("JSON.parse(localStorage.getItem('%s_prog'))[%d]" % (GAME, lv)) == 3, f'第 {lv} 關：星數存進 {GAME}_prog')
        R.check(not errs, f'第 {lv} 關：沒有網頁錯誤 {errs}')
        b.close()

    # ───── 4) 計分規則：第二次才對 50 分、兩次都錯 0 分、提示 −20、連對加成 ─────
    b, pg, errs = page(p)
    start(pg, 1)
    pg.evaluate("ST.qs.forEach(q=>q.type='P'); newCur();")      # 全部改成選句子題，作答最單純
    solve_one(pg, False); pg.wait_for_timeout(100)
    R.check(pg.evaluate("ST.cur.done") is False and pg.evaluate("ST.cur.tries") == 1, '第一次選錯：還能再選')
    solve_one(pg, True)
    R.check(pg.evaluate("ST.cur.pts") == 50 and pg.evaluate("ST.firstOK") == 0, '第二次才答對：50 分、不算一次答對')
    pg.evaluate("nextQ()")
    pg.evaluate("ST.qs[ST.qi].type='P'; newCur();")
    solve_one(pg, False); pg.evaluate("pickOpt(ST.cur.opts.findIndex((o,i)=>!o.ok&&!ST.cur.locked.includes(i)))")
    R.check(pg.evaluate("ST.cur.done") and pg.evaluate("ST.cur.ok") is False and pg.evaluate("ST.cur.pts") == 0, '兩次都錯：0 分、結束這題')
    pg.evaluate("nextQ()"); pg.evaluate("ST.qs[ST.qi].type='P'; newCur();")
    pg.evaluate("useHint()")
    solve_one(pg, True)
    pts = pg.evaluate("ST.cur.pts")
    R.check(80 <= pts <= 130, f'用提示一次答對：100＋速度加分 −20 ＝ {pts}（應 80–130）')
    b.close()

    # ───── 5) 星等門檻邊界 ─────
    b, pg, errs = page(p)
    start(pg, 1)
    def stars_for(n, tot=10):
        return pg.evaluate("""(a)=>{ ST.qs=ST.qs.slice(0,a[1]); ST.firstOK=a[0]; ST.score=100; finishLevel(); return ST.final.stars; }""", [n, tot])
    if GAME == 'ba':
        want = {0:0, 4:0, 5:1, 6:1, 7:2, 8:2, 9:3, 10:3}
        for n, w in want.items():
            start(pg, 1)
            R.check(stars_for(n) == w, f'ba：一次答對 {n} 題 → {w} 星')
    else:
        for tot in (10, 7):
            for n in range(0, tot + 1):
                w = 3 if n >= tot * 0.9 else 2 if n >= tot * 0.7 else 1 if n >= tot * 0.5 else 0
                start(pg, 1)
                got = stars_for(n, tot)
                R.check(got == w, f'bei：{tot} 題裡一次答對 {n} 題（{n/tot:.0%}）→ {w} 星（90%/70%/50% 門檻）' if got == w else f'bei：{tot} 題答對 {n} → 得 {got} 星，應為 {w}')
    # 星數只升不降
    start(pg, 1); stars_for(10)
    start(pg, 1); stars_for(0)
    R.check(pg.evaluate("prog[1]") == 3, '之前拿 3 星，再玩一次 0 星：存檔仍是 3 星（只升不降）')
    R.check(not errs, '沒有網頁錯誤 %s' % errs)
    b.close()

    # ───── 6) 共用設定每個值：字形×語言×拼音注音×語速 ─────
    PY_RE = re.compile(r'[a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]'); ZY_RE = re.compile(r'[ㄅ-ㄩ]')
    base = {'v': 1, 'script': 'trad', 'lang': 'es', 'phon': 'pinyin', 'rate': 'normal'}
    combos = []
    for k, vals in (('script', ['trad', 'simp']), ('lang', ['es', 'en', 'zh']), ('phon', ['pinyin', 'zhuyin', 'both', 'off']), ('rate', ['slow', 'normal', 'fast'])):
        for v in vals: combos.append(dict(base, **{k: v}))
    combos.append(dict(base, script='simp', lang='zh', phon='both', rate='fast'))
    seen = set()
    for st in combos:
        key = json.dumps(st, sort_keys=True)
        if key in seen: continue
        seen.add(key)
        label = f"字形={st['script']} 語言={st['lang']} 拼音注音={st['phon']} 語速={st['rate']}"
        b, pg, errs = page(p, settings=st)
        start(pg, 1)
        pg.evaluate("ST.qs.forEach(q=>q.type='A'); newCur(); render();"); pg.wait_for_timeout(200)
        info = pg.evaluate("""()=>{
          const tks=[...document.querySelectorAll('.tk')];
          const rts=tks.flatMap(t=>[...t.querySelectorAll('rt')].map(r=>r.textContent));
          const rds=tks.flatMap(t=>[...t.querySelectorAll('.rd')].map(r=>r.textContent));
          const shown=tks.map(t=>{const c=t.cloneNode(true);c.querySelectorAll('rt,.rd').forEach(x=>x.remove());return [t.dataset.t,c.textContent.trim()];});
          const lab=I[cfg.lang==='zh'?(cfg.zh==='sc'?'zhs':'zh'):cfg.lang].qA;
          return {n:tks.length, rts, rds, rb2:document.querySelectorAll('.rb2').length, shown,
                  hasEs:document.body.innerText.includes(I.es.qA.slice(0,12)), hasEn:document.body.innerText.includes(I.en.qA.slice(0,12)),
                  cfg:{lang:cfg.lang,zh:cfg.zh,read:cfg.read,speed:cfg.speed}, tokmap:Object.fromEntries(shown_tc()), saved:localStorage.getItem('hanziGames.settings')};
          function shown_tc(){return tks.map(t=>[t.dataset.t,(TOKMAP[t.dataset.t]||{}).sc||t.dataset.t]);}
        }""")
        R.check(info['n'] > 0, f'{label}：畫面有詞卡 ({info["n"]})')
        txt_rt = ''.join(info['rts']); txt_rd = ''.join(info['rds'])
        if st['phon'] == 'pinyin': ok = bool(info['rts']) and PY_RE.search(txt_rt) and not ZY_RE.search(txt_rt)
        elif st['phon'] == 'zhuyin': ok = bool(info['rts']) and ZY_RE.search(txt_rt) and not re.search(r'[a-zA-Z]', txt_rt)
        elif st['phon'] == 'both': ok = info['rb2'] > 0 and PY_RE.search(txt_rd) and ZY_RE.search(txt_rd)
        else: ok = not info['rts'] and not info['rds']
        R.check(bool(ok), f'{label}：拼音注音顯示正確')
        want_simp = st['script'] == 'simp'
        bad = [(tc, sh) for tc, sh in info['shown'] if sh != (info['tokmap'].get(tc, tc) if want_simp else tc)]
        R.check(not bad, f'{label}：字形正確 {bad[:3] if bad else ""}')
        if st['lang'] == 'zh': R.check(not info['hasEs'] and not info['hasEn'], f'{label}：純中文，沒有西文／英文')
        elif st['lang'] == 'es': R.check(info['hasEs'] and not info['hasEn'], f'{label}：中文＋西文')
        else: R.check(info['hasEn'] and not info['hasEs'], f'{label}：中文＋英文')
        R.check(info['cfg']['lang'] == st['lang'] and info['cfg']['speed'] == st['rate'], f'{label}：遊戲內設定與存檔一致')
        # 語速：聽力題自動唸，速度要對
        pg.evaluate("ST.qs[ST.qi].type='L'; newCur(); render();"); pg.wait_for_timeout(900)
        rates = pg.evaluate("window.__spoken.map(s=>s.rate)")
        wantr = {'slow': 0.45, 'normal': 0.65, 'fast': 0.85}[st['rate']]
        R.check(rates and abs(rates[-1] - wantr) < 1e-6, f'{label}：念出速度 {rates[-1] if rates else None}（應為 {wantr}）')
        R.check(not errs, f'{label}：沒有網頁錯誤 {errs}')
        b.close()

    # 設定面板點選（setCfg 就是面板按鈕的 onclick）→ 存檔 → 重新整理仍在
    b, pg, errs = page(p)
    for k, v, exp in (('zh', 'sc', ('script', 'simp')), ('lang', 'en', ('lang', 'en')), ('read', 'zy', ('phon', 'zhuyin')), ('speed', 'fast', ('rate', 'fast'))):
        pg.evaluate("setCfg(%s,%s)" % (json.dumps(k), json.dumps(v)))
        saved = json.loads(pg.evaluate("localStorage.getItem('hanziGames.settings')"))
        R.check(saved.get(exp[0]) == exp[1], f'面板 {k}={v}：存進共用設定 {exp[0]}={saved.get(exp[0])}')
    pg.reload(); pg.wait_for_timeout(1200)
    R.check(pg.evaluate("[cfg.lang,cfg.zh,cfg.read,cfg.speed]") == ['en', 'sc', 'zy', 'fast'], '重新整理後設定還在：%s' % pg.evaluate("[cfg.lang,cfg.zh,cfg.read,cfg.speed]"))
    # 別的遊戲改了共用設定 → 這裡跟著變
    pg.evaluate("localStorage.setItem('hanziGames.settings', JSON.stringify({v:1,script:'trad',lang:'zh',phon:'off',rate:'slow'})); window.dispatchEvent(new StorageEvent('storage',{key:'hanziGames.settings'}))")
    pg.wait_for_timeout(200)
    R.check(pg.evaluate("[cfg.lang,cfg.zh,cfg.read,cfg.speed]") == ['zh', 'tc', 'none', 'slow'], '其他遊戲改設定：這邊即時跟著變')
    b.close()

    # ───── 7) 排行榜（非班級）：寫 baLeaderboard / beiLeaderboard，本機備份 ─────
    b, pg, errs = page(p)
    start(pg, 1, 'A' * 30)
    for i in range(10):
        solve_one(pg, True); pg.evaluate("nextQ()")
    pg.wait_for_timeout(800)
    ops = pg.evaluate("window.__ops")
    sets = [o for o in ops if o['k'] == 'set' and 'Leaderboard' in o['p']]
    R.check(len(sets) == 1, '結算後寫入排行榜一筆：%s' % [o['p'] for o in sets])
    if sets:
        d = sets[0]['d']
        R.check(len(d['name']) <= 14, f'名字最多 14 字：{len(d["name"])}')
        R.check(d['total'] == d['l1'] + d['l2'] + d['l3'] if 'l3' in d else True, '總分＝各關相加')
        R.check(0 < d['l1'] <= 5000, f'第 1 關分數在 0–5000 內：{d["l1"]}')
    lb = json.loads(pg.evaluate("localStorage.getItem('%s_lb')" % GAME) or '{}')
    R.check(len(lb) == 1, '本機排行榜也存了一份')
    b.close()

    # ───── 8) 班級模式成績回傳 ─────
    def class_run(first=True, deny=False, repeat=None):
        b, pg, errs = page(p, '?class=' + CID, db=json.loads(json.dumps(CLS_OPEN)), flags={'__denyScores': True} if deny else None)
        pg.wait_for_timeout(500)
        out = []
        for n_ok in (repeat or [10]):
            start(pg, 1, 'Zoe')
            for i in range(10):
                solve_one(pg, i < n_ok); 
                if i >= n_ok:
                    pg.evaluate("if(!ST.cur.done){const k=ST.cur.opts?ST.cur.opts.findIndex((o,j)=>!o.ok&&!ST.cur.locked.includes(j)):-1; if(k>=0)pickOpt(k); else {clearTok();confirmA();}}")
                    if not pg.evaluate("ST.cur.done"):
                        pg.evaluate("(()=>{const c=ST.cur;const q=ST.qs[ST.qi];if(q.type==='A'){clearTok();for(let i=q.s.tok.length-1;i>=0;i--)placeTok(i);confirmA();}})()")
                pg.evaluate("nextQ()")
            pg.wait_for_timeout(700)
            out.append((pg.evaluate("ST.final.score"), pg.evaluate("document.body.innerText")))
        ops = pg.evaluate("window.__ops")
        db = pg.evaluate("window.__db")
        e = errs
        b.close()
        return out, ops, db, e
    out, ops, db, e = class_run()
    keys = [k for k in db if k.startswith('class_scores/')]
    R.check(len(keys) == 1 and keys[0].startswith('class_scores/%s_%s_lv1_' % (CID, GAME)), '班級成績寫在 class_scores/<班級碼>_<遊戲>_lv1_<暱稱雜湊>：%s' % keys)
    if keys:
        d = db[keys[0]]
        R.check(d.get('game') == GAME and d.get('k') == 'lv1' and d.get('cid') == CID and d.get('owner') == 'T1' and d.get('nick') == 'Zoe', '成績欄位：game／k／cid／owner／nick 正確')
        R.check(d.get('best') == out[0][0] and d.get('plays') == 1, f'best＝本次分數 {d.get("best")}、plays=1')
        R.check(d['extra'] == {'ok': 10, 'q': 10, 'f': 10}, f'extra（答對／題數／一次答對）：{d["extra"]}')
    R.check('成績已回傳給老師' in out[0][1], '結果頁顯示「成績已回傳給老師」')
    R.check('班級排行榜' in out[0][1], 'showBoard:true：結果頁顯示班級排行榜')
    R.check(not any('Leaderboard' in o['p'] for o in ops), '班級模式不寫公開排行榜')
    R.check(not e, '沒有網頁錯誤 %s' % e)
    # 同一個人再玩：只留最高分、plays 加 1
    out2, ops2, db2, e2 = class_run(repeat=[10, 3])
    k2 = [k for k in db2 if k.startswith('class_scores/')][0]
    R.check(db2[k2]['plays'] == 2, f'玩兩次：plays=2（{db2[k2]["plays"]}）')
    R.check(db2[k2]['best'] == max(out2[0][0], out2[1][0]) and out2[1][0] < out2[0][0], f'玩兩次：保留最高分 best={db2[k2]["best"]}（第一次 {out2[0][0]}、第二次 {out2[1][0]}）')
    # 規則拒絕（訂閱過期）
    out3, ops3, db3, e3 = class_run(deny=True)
    R.check('無法記錄成績' in out3[0][1], '訂閱過期（permission-denied）：顯示「無法記錄成績，請通知老師」')

    # ───── 9) 題目回報 ─────
    b, pg, errs = page(p)
    start(pg, 1)
    pg.evaluate("repOpen()"); pg.wait_for_timeout(100)
    pg.evaluate("repWhy('wrong')")
    pg.evaluate("repSend()"); pg.wait_for_timeout(600)
    rep = [o for o in pg.evaluate("window.__ops") if o['k'] in ('add', 'set') and o['p'].startswith('game_reports')]
    R.check(len(rep) == 1, '回報寫入 game_reports 一筆')
    if rep:
        d = rep[0]['d']
        R.check(d.get('game') == GAME, f'回報帶遊戲代號 game={d.get("game")}')
        R.check(d.get('done') is False, '回報預設未處理')
        R.check(pg.evaluate("ST.rep.st") == 'ok', '回報成功後畫面狀態 ok')
    b.close()

    # 網路卡住：超過 15 秒要顯示失敗、按鈕恢復；再送一次只寫同一筆（不重複）
    b, pg, errs = page(p)
    start(pg, 1)
    pg.evaluate("window.__hangReport = true")
    pg.evaluate("repOpen()"); pg.wait_for_timeout(100)
    pg.evaluate("repWhy('wrong')")
    pg.evaluate("setTimeout(repSend, 0)"); pg.wait_for_timeout(1000)
    R.check(pg.evaluate("ST.rep.st") == 'sending', '網路卡住：先顯示送出中')
    pg.wait_for_timeout(15500)
    R.check(pg.evaluate("ST.rep.st") == 'err', '網路卡住：超過 15 秒顯示失敗')
    R.check('disabled' not in pg.evaluate("repHtml()"), '失敗後送出按鈕恢復可按')
    pg.evaluate("window.__hangReport = false")
    pg.evaluate("repSend()"); pg.wait_for_timeout(600)
    R.check(pg.evaluate("ST.rep.st") == 'ok', '再送一次成功')
    docs = [k for k in pg.evaluate("Object.keys(window.__db)") if k.startswith('game_reports/')]
    R.check(len(docs) == 1, f'重送只寫同一筆（{len(docs)} 筆）')
    b.close()

    # 手機版版面：遊戲畫面整頁不捲動，題目卡片在裡面捲、底部按鈕一直看得到
    for (w, h) in [(390, 760), (360, 520)]:
        b, pg, errs = page(p, width=w, height=h)
        start(pg, 1)
        m = pg.evaluate("""(() => { const d = document.documentElement, q = document.querySelector('.qcard'), st = document.querySelector('.stick');
          const r = st ? st.getBoundingClientRect() : null;
          return {page: d.scrollHeight - innerHeight, win: innerHeight, qs: q ? q.scrollHeight - q.clientHeight : -1,
                  top: document.querySelector('.gbar').getBoundingClientRect().top, stickBottom: r ? r.bottom : -1, stickTop: r ? r.top : -1}; })()""")
        R.check(m['page'] <= 1, f'{w}x{h}：整頁不會捲動（多出 {m["page"]}px）')
        R.check(m['top'] >= 0, f'{w}x{h}：最上面的列看得到（top={m["top"]}）')
        R.check(0 <= m['stickTop'] and m['stickBottom'] <= m['win'] + 1, f'{w}x{h}：底部按鈕在畫面內（{m["stickTop"]:.0f}~{m["stickBottom"]:.0f} / {m["win"]}）')
        pg.evaluate("document.querySelector('.qcard').scrollTop = 99999"); pg.wait_for_timeout(100)
        pg.evaluate("window.scrollTo(0, 99999)"); pg.wait_for_timeout(100)
        R.check(pg.evaluate("window.scrollY") == 0, f'{w}x{h}：想捲整頁也捲不動')
        pg.evaluate("document.querySelector('.qcard').scrollTop = 0")
        R.check(pg.evaluate("document.querySelector('.gbar').getBoundingClientRect().top") >= 0, f'{w}x{h}：怎麼捲上面都不會被切掉')
        b.close()

print('FAILS', R.fails); sys.exit(1 if R.fails else 0)
