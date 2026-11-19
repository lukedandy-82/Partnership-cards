import json,sys,html,base64,os
from playwright.sync_api import sync_playwright
FL=os.environ.get('FLAGS_DIR','node_modules/flag-icons/flags/4x3/')
def flag(iso):
    return 'data:image/svg+xml;base64,'+base64.b64encode(open(FL+iso+'.svg','rb').read()).decode()
def logo():
    return 'data:image/png;base64,'+base64.b64encode(open(os.path.dirname(os.path.abspath(__file__))+'/logo.png','rb').read()).decode()
def mix(h,w,a):
    h=h.lstrip('#');r=[int(h[i:i+2],16) for i in (0,2,4)];w=[int(w[i:i+2],16) for i in (1,3,5)]
    return '#%02x%02x%02x'%tuple(int(r[i]*a+w[i]*(1-a)) for i in range(3))
E=html.escape
def build(c):
    cs=c['companies']
    chips=''.join(f'<div class="chip" style="background:{x["color"]}"><img class="fl" src="{flag(x["iso"])}">{E(x["badge"])}</div>' + ('<div class="x">×</div>' if i<len(cs)-1 else '') for i,x in enumerate(cs))
    metrics=''.join(f'<div class="m"><div class="mv">{E(a)}</div><div class="ml">{E(b)}</div></div>' for a,b in c['metrics'])
    def col(x,items): return f'<div class="col"><div class="ch" style="background:{x["color"]}">{E(x["name"])}</div>'+''.join(f'<div class="b"><span class="n">{i+1}</span><span>{E(t)}</span></div>' for i,t in enumerate(items))+'</div>'
    gets=col(cs[0],c['gets'][0])+'<div class="dv"></div>'+col(cs[1],c['gets'][1])
    impl=''.join(f'<div class="b2"><span class="n">{i+1}</span><span>{E(t)}</span></div>' for i,t in enumerate(c['implications']))
    ppl=''.join(f'<div class="p"><div class="av" style="background:{x["color"]}">{E("".join(w[0] for w in p[0].replace("Dr. ","").split()[:2]))}</div><div><div class="pn" style="background:{x["color"]}">{E(p[0])}</div><div class="pr">{E(p[1])}</div></div></div>' for x,p in zip(cs,c['people']))
    mk=c.get('markets')
    mkt=''
    if mk:
        its=''.join((f'<span class="mk">'+(f'<img class="fl" src="{flag(x["iso"])}">' if x.get('iso') else '')+f'{E(x["name"])}</span>') for x in mk)
        mkt=f'<div class="mkrow"><span class="mkl">MARKETS SERVED</span>{its}</div>'
    tint=mix(cs[0]['color'],'#0c1b4a',0.22)
    return f'''<html><head><meta charset=utf-8><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1200px;font-family:Inter,sans-serif;color:#eaf4ff;background:#0a1a4a}}
.top{{height:72px;background:#050d2a;border-bottom:3px solid #27a9bb;display:flex;justify-content:space-between;align-items:center;padding:0 28px}}
.pills{{display:flex;gap:12px}}.pill{{border:2px solid #27456e;color:#8fb0d6;border-radius:20px;padding:5px 18px;font-size:20px;font-weight:600}}
.pill.cat{{background:#10526a;border-color:#27a9bb;color:#6fe0ee}}
.dt{{text-align:right;color:#8aa6c8;font-size:15px}}.dt b{{display:block;color:#3fd0de;font-size:21px;font-weight:600;margin-top:2px}}
.hero{{background:linear-gradient(135deg,{tint},#0c1b4a 60%);padding:32px 28px 30px;text-align:center;position:relative}}
.stage{{position:absolute;right:28px;top:16px;border:2px solid #27a9bb;border-radius:20px;padding:3px 14px;font-size:13px;font-weight:700;color:#5bd5e5;letter-spacing:.06em}}
.chips{{display:flex;justify-content:center;align-items:center;gap:20px;margin-bottom:18px;flex-wrap:wrap}}
.chip{{display:flex;align-items:center;gap:10px;color:#fff;font-weight:700;font-size:20px;border:2px solid #fff;border-radius:10px;padding:9px 22px;text-transform:uppercase}}
.fl{{width:30px;height:22px;border-radius:3px;object-fit:cover;box-shadow:0 0 0 1px rgba(255,255,255,.55)}}
.x{{font-size:30px;font-weight:800}}
h1{{font-size:38px;font-weight:700;margin-bottom:10px}}.sub{{font-size:23px;color:#b8cfe8;line-height:1.35;max-width:1050px;margin:0 auto}}
.mkrow{{display:flex;justify-content:center;align-items:center;gap:12px;flex-wrap:wrap;margin-top:18px}}.mkl{{color:#27a9bb;font-size:14px;font-weight:700;letter-spacing:.08em}}.mk{{display:inline-flex;align-items:center;gap:8px;background:#0b2a5c;border:2px solid #27a9bb;border-radius:20px;padding:5px 16px;font-size:18px;font-weight:600;color:#eaf4ff}}.mk .fl{{width:26px;height:18px}}
.band{{height:40px;background:#16277a;display:flex;align-items:center;padding:0 28px;font-size:19px;font-weight:700;letter-spacing:.03em;gap:14px;border-left:0}}
.band:before{{content:"";width:7px;height:24px;background:#27a9bb;margin-left:-28px;margin-right:6px;border-radius:0 3px 3px 0}}
.ico{{width:26px;height:26px;border:2px solid #5bd5e5;border-radius:50%;color:#5bd5e5;font-size:14px;display:flex;align-items:center;justify-content:center}}
.sec{{background:linear-gradient(#0e2250,#0b2a60)}}
.ms{{display:flex;gap:12px;padding:18px 28px 22px}}
.m{{flex:1;background:#060f33;border-radius:14px;border-top:5px solid #27a9bb;text-align:center;padding:12px 10px 12px;min-height:92px}}
.mv{{font-size:42px;font-weight:700;line-height:1.1}}.ml{{font-size:16px;color:#c1d6ee;margin-top:3px;line-height:1.2}}
.gets{{display:flex;padding:20px 28px 22px;gap:0}}.col{{flex:1}}.dv{{width:1px;background:#1f3a7a;margin:4px 20px}}
.ch{{border-radius:8px;text-align:center;font-weight:700;font-size:20px;padding:8px 0;margin-bottom:16px;color:#fff}}
.b,.b2{{display:flex;gap:12px;margin-bottom:14px;font-size:20px;line-height:1.3;color:#cfe0f3}}
.b2{{font-size:23px;line-height:1.4;gap:14px}}
.n{{flex:none;width:24px;height:24px;border-radius:50%;background:#17a8bb;color:#04243c;font-size:14px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:3px}}
.impl{{padding:22px 28px 14px}}
.ppl{{background:#070c26;border-top:3px solid #27a9bb;padding:14px 28px 22px}}
.pl{{color:#27a9bb;font-size:15px;font-weight:700;letter-spacing:.04em;margin-bottom:10px}}
.pr2{{display:flex;gap:20px}}.p{{flex:1;display:flex;align-items:center;gap:16px;background:#0e1a52;border:2px solid #1c3070;border-radius:14px;padding:16px 16px}}
.av{{width:60px;height:60px;border-radius:50%;color:#fff;font-weight:700;font-size:24px;display:flex;align-items:center;justify-content:center;flex:none;border:2px solid #fff}}
.pn{{display:inline-block;color:#fff;font-weight:700;font-size:19px;border:2px solid #fff;border-radius:8px;padding:2px 12px}}.pr{{color:#8aa6c8;font-size:17px;margin-top:6px}}
.ft{{background:#050d2a;border-top:2px solid #1c3070;height:90px;display:flex;align-items:center;justify-content:space-between;padding:0 28px}}
.ft img{{height:56px}}.ft .t{{margin-left:20px;flex:1}}.ft b{{display:block;font-size:26px}}.ft span{{color:#27a9bb;font-size:19px}}.ft i{{font-style:normal;color:#6f8fb4;font-size:19px}}
</style></head><body>
<div class="top"><div class="pills"><div class="pill cat">{E(c['category'])}</div><div class="pill">{E(c['region'])}</div></div><div class="dt">Announced<b>{E(c['date'])}</b></div></div>
<div class="hero"><div class="stage">{E(c['stage'].upper())}</div><div class="chips">{chips}</div><h1>{E(c['title'])}</h1><div class="sub">{E(c['sub'])}</div>{mkt}</div>
<div class="sec"><div class="band"><span class="ico">#</span>KEY METRICS</div><div class="ms">{metrics}</div>
<div class="band"><span class="ico">⇄</span>WHAT EACH GETS</div><div class="gets">{gets}</div>
<div class="band"><span class="ico">→</span>STRATEGIC IMPLICATIONS</div><div class="impl">{impl}</div></div>
<div class="ppl"><div class="pl">KEY PEOPLE</div><div class="pr2">{ppl}</div></div>
<div class="ft"><img src="{logo()}"><div class="t"><b>GcTechAllies</b><span>Weekly Partnership Digest</span></div><i>gctechallies.com/partnerships</i></div>
</body></html>'''
if __name__=='__main__':
    out=sys.argv[2]
    with sync_playwright() as p:
        b=p.chromium.launch();pg=b.new_page(viewport={'width':1200,'height':800})
        pg.set_content(build(json.load(open(sys.argv[1]))));pg.wait_for_timeout(300)
        pg.screenshot(path=out,full_page=True);b.close()
