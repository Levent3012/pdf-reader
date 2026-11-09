import os
import json, sys, time
from playwright.sync_api import sync_playwright
PAGE = sys.argv[1]
INIT = r"""
(()=>{
 const _st = window.setTimeout; window.setTimeout = (f,d,...a)=>_st(f, Math.min(d||0, 2), ...a);
 window.__said = [];
 window.SpeechSynthesisUtterance = function(t){ this.text=t; this.rate=1; };
 const ss = { speaking:false, pending:false, onvoiceschanged:null,
   getVoices(){ return [{name:'Fake', lang:'de-DE'}]; },
   cancel(){}, speak(u){ window.__said.push(u.text); _st(()=>{ u.onstart&&u.onstart(); u.onend&&u.onend(); },0); } };
 Object.defineProperty(window,'speechSynthesis',{value:ss, configurable:true});
})();
"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME','/usr/bin/google-chrome'), args=['--no-sandbox'])
    pg = b.new_page()
    pg.add_init_script(INIT)
    pg.goto('file://'+PAGE)
    faecher = pg.evaluate("Object.keys(window.KMX)")
    total = pg.evaluate("Object.values(window.KMX).reduce((a,f)=>a+f.reduce((b,k)=>b+k.qs.length,0),0)")
    allsaid = set()
    for f in faecher:
        st = {"fach": f, "k": "alle", "pos": {}, "ttsWhat": "full", "res": {}}
        pg.evaluate("s=>{localStorage.setItem('kmx-v1', s)}", json.dumps(st))
        pg.reload()
        n = pg.evaluate("KMX=>0", None) if False else pg.evaluate(f"window.KMX[{json.dumps(f)}].reduce((b,k)=>b+k.qs.length,0)")
        pg.evaluate("window.__said=[]")
        pg.click('#ttsTog')
        last, same = -1, 0
        while True:
            time.sleep(1.0)
            cnt = pg.evaluate("window.__said.length")
            tag = pg.evaluate("(document.querySelector('.card .tag')||{}).textContent||''")
            if not tag.startswith(f) and cnt>5: break
            if cnt == last:
                same += 1
                if same >= 4: break
            else: same = 0
            last = cnt
        said = pg.evaluate("window.__said")
        allsaid.update(said)
        print(f, n, len(said), len(set(said)), 'now at:', tag[:40], flush=True)
    b.close()
import os; os.makedirs('audio',exist_ok=True); json.dump(sorted(allsaid), open('audio/texts.json','w'), ensure_ascii=False)
print('unique', len(allsaid), 'chars', sum(map(len, allsaid)))
