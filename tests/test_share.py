# 被 · oración con 被：分享成績鈕＋ ?ref=share 記號測試（假 Firebase 記錄 visits／plays 寫入）
# 用法：python3 tests/test_share.py
import sys, json
from playwright.sync_api import sync_playwright
import common
from common import *

R = Runner()
URL = 'https://wangchiapin.github.io/practica-de-bei-oracion/?ref=share'

def stubs(share='ok', clip='ok'):
    s = "window.__shared=[];window.__copied=[];"
    if share == 'none': s += "try{Object.defineProperty(navigator,'share',{value:undefined,configurable:true});}catch(e){}"
    else:
        body = "window.__shared.push(d);"
        if share == 'abort': body += "const e=new Error('x');e.name='AbortError';throw e;"
        if share == 'hang': body += "await new Promise(r=>setTimeout(r,600));"
        s += "navigator.share=async d=>{%s};" % body
    s += "document.execCommand=()=>%s;" % ('false' if clip == 'fail' else 'true')
    s += "try{Object.defineProperty(navigator,'clipboard',{value:{writeText:async t=>{%s}},configurable:true});}catch(e){}" % ("throw new Error('no')" if clip == 'fail' else "window.__copied.push(t)")
    return s

def page(p, settings=None, query='', share='ok', clip='ok', wait=1500):
    return open_page(p, query=query, settings=settings, wait=wait, extra_init=stubs(share, clip))

def result(pg, score=300, name='Ana', lv=1):
    pg.evaluate("(a)=>{cfg.name=a[1]; ST.lv=a[0]; beginLevel();}", [lv, name]); pg.wait_for_timeout(200)
    pg.evaluate("(sc)=>{ST.qs=ST.qs.slice(0,3); ST.firstOK=3; ST.score=sc; finishLevel();}", score); pg.wait_for_timeout(300)

def ids(pg): return pg.evaluate("[...document.querySelectorAll('#app button')].map(b=>b.id||b.textContent.trim().slice(0,8))")
def txt(pg, sel): return ' '.join(pg.inner_text(sel).split())
def ops(pg): return pg.evaluate("window.__ops||[]")

base = {'v': 1, 'script': 'trad', 'lang': 'es', 'phon': 'pinyin', 'rate': 'normal'}
with sync_playwright() as p:
    print('結算畫面的分享鈕')
    b, pg, errs = page(p, settings=base)
    result(pg, 300)
    pos = pg.evaluate("""(()=>{const bs=[...document.querySelectorAll('#app button')];const ix=f=>bs.findIndex(b=>(b.getAttribute('onclick')||'').includes(f));return [ix('beginLevel'),ix('doShare'),ix("go('levels')")]})()""")
    R.check(pos[0] >= 0 and pos[0] < pos[1] < pos[2], '分享鈕在「再玩一次」之後、「選單」之前 %s' % pos)
    t = txt(pg, '#shareBtn')
    R.check('分享成績' in t and 'Compartir resultado' in t, '文字：分享成績＋Compartir resultado：%s' % t)
    st = pg.evaluate("(()=>{const e=document.getElementById('shareBtn'),c=getComputedStyle(e);return [c.backgroundColor,parseFloat(c.borderTopWidth),e.className]})()")
    R.check(st[0] == 'rgb(255, 255, 255)' and st[1] >= 1, '空心外框樣式（白底有框）%s' % st)
    R.check('btn-restart' not in st[2], '沒有用 .btn-restart')
    pg.click('#shareBtn'); pg.wait_for_timeout(200)
    sh = pg.evaluate("window.__shared")
    R.check(len(sh) == 1, '呼叫系統分享選單一次')
    R.check(sh and sh[0]['url'] == URL, '連結＝公開頁＋?ref=share：%s' % (sh and sh[0]['url']))
    R.check(sh and 'Ana' in sh[0]['text'] and '300' in sh[0]['text'] and 'oración con 被' in sh[0]['text'], '西文句子含暱稱、分數、遊戲名：%s' % (sh and sh[0]['text']))
    R.check(not errs, '沒有網頁錯誤 %s' % errs)
    b.close()

    print('語言／字體跟著設定')
    b, pg, errs = page(p, settings=dict(base, script='simp', lang='zh'))
    result(pg, 200, name='')
    R.check(txt(pg, '#shareBtn') == '分享成绩', '简体＋純中文：只有「分享成绩」：%s' % txt(pg, '#shareBtn'))
    pg.click('#shareBtn'); pg.wait_for_timeout(200)
    sh = pg.evaluate("window.__shared")
    R.check(sh and sh[0]['text'].startswith('我在「被字句练习」拿了') and '超越我吗' in sh[0]['text'], '简体句子，沒暱稱用「我」：%s' % (sh and sh[0]['text']))
    b.close()
    b, pg, errs = page(p, settings=dict(base, lang='en'))
    result(pg, 200, name='Bo')
    R.check('Share result' in txt(pg, '#shareBtn'), '英文介面：Share result')
    pg.click('#shareBtn'); pg.wait_for_timeout(200)
    sh = pg.evaluate("window.__shared")
    R.check(sh and sh[0]['text'].startswith('Bo scored ') and 'Can you beat me' in sh[0]['text'], '英文句子帶暱稱：%s' % (sh and sh[0]['text']))
    b.close()

    print('分享選單的各種結果')
    b, pg, errs = page(p, settings=base, share='abort')
    result(pg); before = pg.inner_text('#shareBtn')
    pg.click('#shareBtn'); pg.wait_for_timeout(200)
    R.check(pg.inner_text('#shareBtn') == before and pg.evaluate("window.__copied") == [], '玩家關掉選單：文字不變、不複製')
    b.close()
    b, pg, errs = page(p, settings=base, share='none')
    result(pg); pg.click('#shareBtn'); pg.wait_for_timeout(250)
    cp = pg.evaluate("window.__copied")
    R.check(len(cp) == 1 and cp[0].endswith('\n' + URL), '不支援分享選單：複製「句子＋連結」')
    R.check('已複製' in pg.inner_text('#shareBtn') and 'Copiado' in pg.inner_text('#shareBtn'), '按鈕顯示已複製')
    pg.wait_for_timeout(2500)
    R.check('分享成績' in pg.inner_text('#shareBtn'), '約 2 秒後文字恢復')
    b.close()
    b, pg, errs = page(p, settings=base, share='none', clip='fail')
    result(pg); pg.click('#shareBtn'); pg.wait_for_timeout(250)
    R.check('複製失敗' in pg.inner_text('#shareBtn') and 'No se pudo' in pg.inner_text('#shareBtn'), '連複製也失敗：顯示複製失敗')
    b.close()
    b, pg, errs = page(p, settings=base, share='hang')
    result(pg)
    pg.evaluate("document.getElementById('shareBtn').click();document.getElementById('shareBtn').click()"); pg.wait_for_timeout(900)
    R.check(pg.evaluate("window.__shared.length") == 1, '連點兩下只分享一次')
    b.close()

    print('0 分不顯示')
    b, pg, errs = page(p, settings=base)
    result(pg, 0)
    R.check('shareBtn' not in ids(pg), '0 分沒有分享鈕')
    b.close()

    print('?ref=share 記號')
    def refcase(query, label, expect):
        b, pg, errs = page(p, settings=base, query=query, wait=3200)
        pg.evaluate("(a)=>{cfg.name=a; ST.lv=1; beginLevel();}", 'Ana'); pg.wait_for_timeout(500)
        o = [x for x in ops(pg) if x['p'].startswith('visits/') or (x['k'] == 'add' and x['p'] == 'plays')]
        R.check(len(o) >= 2 and all((x['d'].get('ref') == expect) if expect else ('ref' not in x['d']) for x in o), '%s %s' % (label, o))
        if expect: R.check(pg.evaluate("sessionStorage.getItem('hg.ref')") == expect, '記號暫存在 sessionStorage')
        b.close()
    refcase('?ref=share', '訪客與開始紀錄都帶 ref=share', 'share')
    refcase('', '沒有 ref：紀錄不帶 ref 欄位', None)
    refcase('?ref=BAD%20x!', '不合法的 ref 被忽略', None)
    refcase('?ref=Share', '大寫 ref 轉成小寫', 'share')

print('FAILS', R.fails); sys.exit(1 if R.fails else 0)
