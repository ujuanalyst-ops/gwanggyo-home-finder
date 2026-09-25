import requests, json, os, glob, csv, io, re, time, difflib, warnings
warnings.filterwarnings("ignore")
D = os.path.dirname(__file__)
OUT = os.path.join(D, "zigbang.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
s = requests.Session(); s.headers.update({"User-Agent": UA})
def norm(n):
    n = re.sub(r"\(.*?\)", lambda m: m.group(0)[1:-1], n)
    n = re.sub(r"[\s\-·ㆍ,.'’\"]", "", n).replace("아파트", "")
    return n.lower()
def read_csv(path):
    raw = open(path, "rb").read().decode("cp949", errors="replace"); lines = raw.splitlines()
    idx = next(i for i, l in enumerate(lines) if l.startswith('"NO"'))
    return list(csv.DictReader(io.StringIO("\n".join(lines[idx:]))))
keys = {}
for f in glob.glob(os.path.join(D, "molit", "*.csv")):
    for r in read_csv(f):
        sgg = r["시군구"].strip(); dong = sgg.split()[-1]; name = r["단지명"].strip()
        keys.setdefault((dong, norm(name)), (sgg, dong, name, r.get("번지", ""), r.get("도로명", "")))
print("targets", len(keys), flush=True)
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
i = 0
for k, (sgg, dong, name, bunji, road) in keys.items():
    kk = dong + "|" + k[1]
    if kk in res: continue
    q = f"{dong} {name}"
    best = None
    for attempt in range(3):
        try:
            r = s.get("https://apis.zigbang.com/v2/search", params={"leaseYn": "N", "q": q, "serviceType": "아파트"}, timeout=20)
            if r.status_code != 200: time.sleep(3); continue
            items = [it for it in r.json().get("items", []) if it.get("type") == "apartment"]
            nn = norm(name); bs = 0
            for it in items:
                src = it.get("_source", {})
                if src.get("local3") != dong and dong not in (it.get("description") or ""): continue
                sc = difflib.SequenceMatcher(None, nn, norm(it["name"])).ratio()
                if src.get("address2") and bunji and src.get("address2") == bunji: sc += 0.3
                if sc > bs: bs, best = sc, it
            if best and bs < 0.55: best = None
            break
        except Exception as e:
            time.sleep(3)
    if best:
        src = best.get("_source", {})
        res[kk] = {"zid": best["id"], "zname": best["name"], "lat": best["lat"], "lng": best["lng"], "bcode": src.get("법정동코드"), "approved": src.get("사용승인일"), "units": src.get("household"), "road": src.get("신주소"), "floor": src.get("floor")}
    else:
        res[kk] = None
    i += 1
    if i % 50 == 0:
        json.dump(res, open(OUT, "w"), ensure_ascii=False); print("progress", i, "found", sum(1 for v in res.values() if v), flush=True)
    time.sleep(0.15)
json.dump(res, open(OUT, "w"), ensure_ascii=False)
print("DONE", len(res), "found", sum(1 for v in res.values() if v), flush=True)
