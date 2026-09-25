import requests, time, os, json, warnings
warnings.filterwarnings("ignore")
OUT = os.path.join(os.path.dirname(__file__), "naver"); P = os.path.join(OUT, "complexes_raw.json")
MUA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
s = requests.Session(); s.headers.update({"User-Agent": MUA, "Referer": "https://m.land.naver.com/", "Accept": "application/json, text/javascript, */*; q=0.01"})
s.get("https://m.land.naver.com/", timeout=30)
regions = json.load(open(os.path.join(OUT, "regions.json")))
# priority: near-Gwanggyo districts first
PRI = {"4111700000": 0, "4146500000": 1, "4111500000": 2, "4111100000": 3, "4146300000": 4, "4111300000": 5, "4159000000": 6, "4137000000": 7, "1159000000": 8, "4122000000": 9}
regions.sort(key=lambda r: PRI.get(r["gu"], 9))
done = json.load(open(P)) if os.path.exists(P) else {}
done_dongs = set(c.get("dongCode") for c in done.values())
blocked = 0
def get(params):
    global blocked
    for i in range(3):
        try:
            r = s.get("https://m.land.naver.com/cluster/ajax/complexList", params=params, timeout=30, allow_redirects=False)
            if r.status_code == 200: blocked = 0; return r.json()
            if r.status_code in (302, 307): blocked += 1; print("blocked", blocked, flush=True); time.sleep(90 if blocked < 4 else 300); continue
        except Exception as e: print("err", e, flush=True); time.sleep(5)
    return None
for r in regions:
    if r["code"] in done_dongs: continue
    if r["gu"] in ("4122000000",) and r["name"] != "죽백동": continue
    if r["gu"] == "1159000000" and r["name"] != "사당동": continue
    R = 0.09; page = 1; got = []
    while True:
        d = get({"cortarNo": r["code"], "rletTpCd": "APT", "tradTpCd": "A1", "z": 16, "lat": r["lat"], "lon": r["lng"], "btm": r["lat"]-R, "lft": r["lng"]-R, "top": r["lat"]+R, "rgt": r["lng"]+R, "page": page})
        if not d or not d.get("result"): break
        got += d["result"]
        if not d.get("more") or page >= 15: break
        page += 1; time.sleep(1.3)
    for c in got:
        c["dongCode"] = r["code"]; c["dong"] = r["name"]; c["gu"] = r["gu"]; c["dlat"] = r["lat"]; c["dlng"] = r["lng"]
        done[c["hscpNo"]] = c
    json.dump(done, open(P, "w"), ensure_ascii=False)
    print("dong", r["name"], len(got), "total", len(done), flush=True)
    time.sleep(1.5)
print("DONE", len(done), flush=True)
