import json,re,sys
D=json.load(open('partnerships-data.json'))
T={}
def tag(v,idx):
    for i in idx: T[i]=v
tag('Payments|checkout',[3,129,33,125])
tag('Payments|agentic',[1,114])
tag('Payments|bnpl',[7,10])
tag('Payments|embedded',[4,74,119])
tag('Real estate|distribution',[66])
tag('Payments|rails',[73,23,45,47,63,70,91,97,117,118,120,34,13])
tag('Payments|bankAI',[52,113,19,53,109])
tag('Energy|storage',[2,68])
tag('Energy|datacentre power',[25,30])
tag('Energy|generation',[64,79,89,51])
tag('Energy|AI',[11,36,77,86])
tag('Automotive|autonomy',[21,26,48,92])
tag('Automotive|software and chips',[14,16,98])
tag('Automotive|manufacturing',[29,57,83])
tag('Defence/Space|space',[24,38,40,111])
tag('Defence/Space|defence industry',[31,42,56,59,61,100,101,88])
tag('Healthcare|digital',[5,17,49])
tag('Healthcare|pharma',[94,103])
tag('Healthcare|realestate',[22])
tag('Retail/Ecommerce|tech and AI',[35,12,106,44,115])
tag('Retail/Ecommerce|expansion',[28,96,82,124])
tag('Media',[8])
tag('Logistics|fulfilment',[102,112])
tag('Logistics|property',[104])
tag('Semiconductors|manufacturing',[50,84,27,54])
tag('Semiconductors|chips and design',[9,32,108])
tag('Cloud/AI infra|datacentres',[0,6,46,65,69,110,90,123])
tag('Cloud/AI infra|compute deals',[105,122,71,127,62,93,20])
tag('Cloud/AI infra|sovereign cloud',[18,41,55,126])
tag('Cloud/AI infra|network',[67,43])
tag('Enterprise AI|consulting',[78,80,85,95,107,128,81,99])
tag('Enterprise AI|platforms',[37,75,76,121,130,87,39])
tag('Enterprise AI|models',[15,58,72,116])
tag('Enterprise AI|robotics',[60])
assert len(T)==len(D)
LBL={'Payments|agentic':'agentic payments','Payments|checkout':'checkout and wallets','Payments|bnpl':'BNPL and consumer credit','Payments|embedded':'embedded finance','Payments|rails':'payment rails and cross-border','Payments|bankAI':'AI in banking','Energy|storage':'energy storage','Energy|datacentre power':'power for data centres','Energy|generation':'power generation and hydrogen','Energy|AI':'AI in energy','Automotive|autonomy':'autonomous driving and mobility','Automotive|software and chips':'vehicle software and chips','Automotive|manufacturing':'vehicle manufacturing partnerships','Defence/Space|space':'space and satellites','Defence/Space|defence industry':'defence industry','Healthcare|digital':'digital and consumer health','Healthcare|pharma':'pharma and AI','Healthcare|realestate':'healthcare real estate','Retail/Ecommerce|tech and AI':'retail technology and AI','Retail/Ecommerce|expansion':'retail expansion and deals','Media':'media and AI','Real estate|distribution':'real estate distribution','Logistics|fulfilment':'fulfilment and market entry','Logistics|property':'logistics property','Semiconductors|manufacturing':'chip manufacturing','Semiconductors|chips and design':'AI chips and design','Cloud/AI infra|datacentres':'AI data centres','Cloud/AI infra|compute deals':'AI compute deals','Cloud/AI infra|sovereign cloud':'sovereign cloud','Cloud/AI infra|network':'network and telco cloud','Enterprise AI|consulting':'AI consulting alliances','Enterprise AI|platforms':'enterprise AI platforms','Enterprise AI|models':'AI models for enterprise and government','Enterprise AI|robotics':'industrial robotics'}
V=lambda t:t.split('|')[0]
slug2i={x['slug']:i for i,x in enumerate(D)}
def score(i,j):
    s=0
    if T[i]==T[j]: s+=4
    if V(T[i])==V(T[j]): s+=2
    else: return -1
    s+= (D[j]['announcedDate'][:7]>='2026-09')*0.5
    return s
def label(i,j):
    return ('Same segment · ' if T[i]==T[j] else 'Same industry · ')+LBL[T[i]]
def short(x):
    a=re.split(r' [—–-] ',x['title'],maxsplit=1); return a[0],(a[1] if len(a)>1 else '')
def line(j,why):
    s,desc=short(D[j]); return f"{s} | {desc} | https://www.gctechallies.com/deal/{D[j]['slug']} | {D[j]['slug']} | {why}"
PIN={3:[129,125]}  # user-approved pins
EXCL={(1,3),(3,1)}  # user: Uber x Revolut does not belong with OpenAI wallet
OVER={ 2:'KEEP', 8:'KEEP'}
res={}
for i,x in enumerate(D):
    lines=[l.strip() for l in x['similarDeals'].split('\n') if l.strip()]
    out=[];rem=[];add=[]
    for l in lines:
        p=[s.strip() for s in l.split('|')]
        p=(p+['','','',''])[:5]
        own=p[3] in slug2i
        if own:
            j=slug2i[p[3]]
            ok = (i,j) not in EXCL and (T[i]==T[j] or (V(T[i])==V(T[j]) and sum(1 for k in T if T[k]==T[i])<3))
            if i in PIN or not ok:
                if not (i in PIN and j in PIN[i]): rem.append(p[0]); continue
            out.append((j,p))
        else:
            out.append((None,p))
    res[i]=(out,rem)
# top up
final={}
for i,(out,rem) in res.items():
    have={D[j]['slug'] for j,p in out if j is not None}
    items=[]
    for j,p in out:
        why=label(i,j) if j is not None else (p[4] if (p[4].startswith('Same approach') or i==5) else 'Same segment · '+LBL[T[i]])
        if j is not None: items.append(line(j,why)) if False else items.append(' | '.join(p[:4]+[why]))
        else: items.append(' | '.join(p[:3]+['']+[why]))
    pinned=[j for j in PIN.get(i,[]) if D[j]['slug'] not in have]
    need=max(0,(2 if (rem or pinned) else 0)-len(items)) if i not in PIN else max(0,3-len(items))
    cands=sorted([j for j in range(len(D)) if j!=i and D[j]['slug'] not in have and score(i,j)>=0 and (i,j) not in EXCL and (T[i]==T[j] or sum(1 for k in T if T[k]==T[i])<3)],key=lambda j:-score(i,j))
    adds=pinned+[j for j in cands if j not in pinned][:max(0,need-len(pinned))] if need or pinned else []
    for j in adds: items.append(line(j,label(i,j)))
    final[i]=(items,rem,[D[j]['title'][:40] for j in adds])
if __name__=='__main__':
    for i,(it,rem,add) in final.items():
        if rem or add: print(i,D[i]['title'][:45],'\n  REM',rem,'\n  ADD',add)
    json.dump({D[i]['title']:'\n'.join(it) for i,(it,r,a) in final.items()},open('similar-deals-proposal.json','w'),ensure_ascii=False)
    print(sum(1 for i in final if final[i][0]),'with lists')
