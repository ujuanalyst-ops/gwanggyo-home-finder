import requests, json, os, glob, csv, io, re, time, warnings
warnings.filterwarnings("ignore")
D = os.path.dirname(__file__); OUT = os.path.join(D, "zigbang.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
s = requests.Session(); s.headers.update({"User-Agent": UA})
def norm(n):
    n = re.sub(r"\(.*?\)", lambda m: m.group(0)[1:-1], n)
    n = re.sub(r"[\s\-·ㆍ,.'’\"]", "", n).replace("아파트", "")
    return n.lower()
STOP = ["휴먼시아", "주공", "그린빌", "이편한세상", "e편한세상", "아파트", "블럭", "단지", "차", "마을", "용인", "수원", "화성", "동탄", "평택", "오산"]
def bigrams(x): return {x[i:i+2] for i in range(len(x)-1)} if len(x) > 1 else {x}
def sim(a, b):
    A, B = bigrams(a), bigrams(b)
    return len(A & B) / max(1, len(A | B))
def read_csv(path):
    raw = open(path, "rb").read().decode("cp949", errors="replace"); lines = raw.splitlines()
    idx = next(i for i, l in enumerate(lines) if l.startswith('"NO"'))
    return list(csv.DictReader(io.StringIO("\n".join(lines[idx:]))))
keys = {}
for f in glob.glob(os.path.join(D, "molit", "*.csv")):
    for r in read_csv(f):
        sgg = r["시군구"].strip(); dong = sgg.split()[-1]; name = r["단지명"].strip()
        keys.setdefault(dong + "|" + norm(name), (sgg, dong, name, r.get("번지", ""), r.get("도로명", "")))
res = json.load(open(OUT))
todo = [k for k, v in res.items() if v is None and k in keys]
print("todo", len(todo), flush=True)
def search(q):
    for attempt in range(3):
        try:
            r = s.get("https://apis.zigbang.com/v2/search", params={"leaseYn": "N", "q": q, "serviceType": "아파트"}, timeout=20)
            if r.status_code == 200: return [it for it in r.json().get("items", []) if it.get("type") == "apartment"]
        except Exception: pass
        time.sleep(3)
    return []
def pick(items, dong, sgg, name, bunji):
    nn = norm(name); best = None; bs = 0
    core = nn
    for w in STOP: core = core.replace(w, "")
    for it in items:
        src = it.get("_source", {})
        d_ok = src.get("local3") == dong
        s_ok = src.get("local2") and src["local2"] in sgg
        if not (d_ok or s_ok): continue
        zn = norm(it["name"]); zc = zn
        for w in STOP: zc = zc.replace(w, "")
        sc = max(sim(nn, zn), sim(core, zc) if core and zc else 0)
        if src.get("address2") and bunji and src["address2"] == bunji: sc += 0.5
        if d_ok: sc += 0.1
        if sc > bs: bs, best = sc, it
    return (best, bs)
done = 0
for k in todo:
    sgg, dong, name, bunji, road = keys[k]
    cands = search(f"{dong} {name}")
    best, bs = pick(cands, dong, sgg, name, bunji)
    if bs < 0.45 and road and road != "-":
        cands2 = search(f"{sgg.split()[1] if len(sgg.split())>1 else ''} {road}".strip())
        b2, s2 = pick(cands2, dong, sgg, name, bunji)
        if s2 > bs: best, bs = b2, s2
        time.sleep(0.15)
    if bs < 0.45 and bunji:
        cands3 = search(f"{dong} {bunji}")
        b3, s3 = pick(cands3, dong, sgg, name, bunji)
        if s3 > bs: best, bs = b3, s3
        time.sleep(0.15)
    if best and bs >= 0.45:
        src = best.get("_source", {})
        res[k] = {"zid": best["id"], "zname": best["name"], "lat": best["lat"], "lng": best["lng"], "bcode": src.get("법정동코드"), "approved": src.get("사용승인일"), "units": src.get("household"), "road": src.get("신주소"), "floor": src.get("floor"), "score": round(bs, 2)}
    done += 1
    if done % 50 == 0:
        json.dump(res, open(OUT, "w"), ensure_ascii=False); print("progress", done, "found", sum(1 for v in res.values() if v), flush=True)
    time.sleep(0.15)
json.dump(res, open(OUT, "w"), ensure_ascii=False)
print("DONE2", "found", sum(1 for v in res.values() if v), "of", len(res), flush=True)
