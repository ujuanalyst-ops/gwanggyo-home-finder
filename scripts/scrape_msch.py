import requests, re, json, time, os, warnings
warnings.filterwarnings("ignore")
D=os.path.dirname(__file__)
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
s=requests.Session(); s.headers.update({"User-Agent":UA,"Referer":"https://apt2.me/apt/middleGrade.jsp"})
M=json.load(open(os.path.join(D,'apt2me_middle.json')))
out={}
for i,(k,v) in enumerate(M.items()):
    try:
        r=s.get("https://apt2.me/apt/msch.jsp",params={"mcode":k},timeout=30)
        t=re.sub(r"<script.*?</script>","",r.text,flags=re.S); t=re.sub(r"<style.*?</style>","",t,flags=re.S)
        txt=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",t))
        m=re.search(r"(\d{4})년 졸업 총 ([\d,]+)명[^%]{0,60}?([\d.]+)\s*% 특목\+자사",txt)
        years=re.findall(r"(\d{4})년 졸업 총 ([\d,]+)명[^%]{0,60}?([\d.]+)\s*% 특목\+자사",txt)
        kinds={}
        for kw in ["과학고","영재","국제고","외국어고","자사고","자율형사립고"]:
            mm=re.search(kw+r"[^\d]{0,15}(\d{1,3})\s*명",txt)
            if mm: kinds[kw]=int(mm.group(1))
        out[k]={"latest":{"year":int(m.group(1)),"grads":int(m.group(2).replace(",","")),"rate":float(m.group(3))} if m else None,"years":[[int(a),int(b.replace(",","")),float(c)] for a,b,c in years][:10],"kinds":kinds}
    except Exception as e:
        out[k]={"err":str(e)[:80]}
    if i%40==0: print(i,flush=True)
    time.sleep(0.2)
json.dump(out,open(os.path.join(D,'msch.json'),'w'),ensure_ascii=False)
print("DONE",sum(1 for v in out.values() if v.get('latest')),"/",len(out),flush=True)
