import json,re,sys
D=json.load(open('partnerships-data.json'))
T={}
def tag(v,idx):
    for i in idx: T[i]=v
tag('Payments|checkout',[1,3,10,129,33,7,125,114])
tag('Payments|embedded',[4,74,119,73,66])
tag('Payments|rails',[23,45,47,63,70,91,97,117,118,120,34,13])
tag('Payments|bankAI',[52,113,19,53,109])
tag('Energy',[2,25,30,36,51,64,68,77,79,89,11,86])
tag('Automotive',[14,16,21,26,29,48,57,83,98,92])
tag('Defence/Space',[24,31,38,40,42,56,59,61,88,100,101,111])
tag('Healthcare|digital',[5,17,49])
tag('Healthcare|pharma',[94,103])
tag('Healthcare|realestate',[22])
tag('Retail/Ecommerce',[28,35,44,82,96,106,115,12,124])
tag('Media',[8])
tag('Logistics',[102,104,112])
tag('Semiconductors',[9,27,32,50,84,54,108])
tag('Cloud/AI infra',[0,6,18,20,41,43,46,62,65,69,71,90,93,105,110,122,123,126,127,67,55])
tag('Enterprise AI',[15,37,39,58,72,75,76,78,80,81,85,87,95,99,107,116,121,128,130,60])
assert len(T)==len(D)
LBL={'Payments|checkout':'checkout and wallets','Payments|embedded':'finance inside business software','Payments|rails':'payment rails and cross-border','Payments|bankAI':'AI in banking','Energy':'energy','Automotive':'automotive and mobility','Defence/Space':'defence and space','Healthcare|digital':'digital and consumer health','Healthcare|pharma':'pharma and AI','Healthcare|realestate':'healthcare real estate','Retail/Ecommerce':'retail and ecommerce','Media':'media and AI','Logistics':'logistics','Semiconductors':'semiconductors','Cloud/AI infra':'AI infrastructure and cloud','Enterprise AI':'enterprise AI and software'}
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
            ok = V(T[i])==V(T[j]) and (V(T[i])!='Payments' or T[i]==T[j] or T[i]=='Payments|bankAI' and False or T[i]==T[j])
            if V(T[i])!='Payments': ok = V(T[i])==V(T[j])
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
        why=label(i,j) if j is not None else (p[4] if p[4] else 'Same industry · '+LBL[T[i]])
        if j is not None: items.append(line(j,why)) if False else items.append(' | '.join(p[:4]+[why]))
        else: items.append(' | '.join(p[:3]+['']+[why]))
    pinned=[j for j in PIN.get(i,[]) if D[j]['slug'] not in have]
    need=max(0,(2 if (rem or pinned) else 0)-len(items)) if i not in PIN else max(0,3-len(items))
    cands=sorted([j for j in range(len(D)) if j!=i and D[j]['slug'] not in have and score(i,j)>=0 and (V(T[i]) not in ('Payments','Healthcare') or T[i]==T[j])],key=lambda j:-score(i,j))
    adds=pinned+[j for j in cands if j not in pinned][:max(0,need-len(pinned))] if need or pinned else []
    for j in adds: items.append(line(j,label(i,j)))
    final[i]=(items,rem,[D[j]['title'][:40] for j in adds])
if __name__=='__main__':
    for i,(it,rem,add) in final.items():
        if rem or add: print(i,D[i]['title'][:45],'\n  REM',rem,'\n  ADD',add)
    json.dump({D[i]['title']:'\n'.join(it) for i,(it,r,a) in final.items()},open('similar-deals-proposal.json','w'),ensure_ascii=False)
    print(sum(1 for i in final if final[i][0]),'with lists')
