import requests, re, json, time, os, warnings
warnings.filterwarnings("ignore")
D = os.path.dirname(__file__)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
s = requests.Session(); s.headers.update({"User-Agent": UA, "Referer": "https://apt2.me/apt/middleGrade.jsp"})
AREAS = ["41111", "41113", "41115", "41117", "41463", "41465", "41461", "41597", "41595", "41591", "41593", "41370", "41220", "11590"]
COMBOS = [("2025", "2", "1"), ("2024", "3", "2"), ("2024", "2", "2")]
SUBJ = ["국어", "영어", "수학"]
card_re = re.compile(r'<article class="scard[^"]*">(.*?)</article>', re.S)
def parse(html):
    out = []
    for c in card_re.findall(html):
        nm = re.search(r'class="nm">([^<]+)<', c); addr = re.search(r'class="addr">([^<]*)<', c)
        mcode = re.search(r"mcode=([A-Za-z0-9=]+)", c); avg = re.search(r'<div class="v">([\d.]+)<small>', c)
        A = re.search(r'A등급 <b>([\d.]+)%', c); n = re.search(r'응시 <b>([\d,]+)명', c); sd = re.search(r'표준편차 <b>([\d.]+)</b>', c)
        dist = re.search(r'<b>([\d. /]+)</b> %', c); pos = re.search(r'pos_x=([\d.]+)&pos_y=([\d.]+)', c)
        yr = re.search(r'class="yr">([^<]*)<', c)
        if not nm or not mcode: continue
        out.append({"name": nm.group(1).strip(), "addr": addr.group(1).strip() if addr else "", "mcode": mcode.group(1), "avg": float(avg.group(1)) if avg else None,
                    "A": float(A.group(1)) if A else None, "n": int(n.group(1).replace(",", "")) if n else None, "sd": float(sd.group(1)) if sd else None,
                    "dist": [float(x) for x in dist.group(1).split("/")] if dist else None, "lat": float(pos.group(1)) if pos else None, "lng": float(pos.group(2)) if pos else None,
                    "tag": yr.group(1).strip() if yr else ""})
    return out
res = {}
for area in AREAS:
    for (y, g, t) in COMBOS:
        for sub in SUBJ:
            page = 1
            while page <= 6:
                try:
                    r = s.get("https://apt2.me/apt/middleGrade.jsp", params={"pages": page, "area": area, "Cmb_year": y, "Cmb_grade": g, "Cmb_term": t, "Cmb_subject": sub}, timeout=30)
                except Exception as e:
                    print("err", e, flush=True); time.sleep(3); continue
                cards = parse(r.text)
                if not cards: break
                for c in cards:
                    k = c["mcode"]
                    rec = res.setdefault(k, {"name": c["name"], "addr": c["addr"], "mcode": k, "lat": c["lat"], "lng": c["lng"], "area": area, "scores": {}})
                    if rec.get("lat") is None and c["lat"]: rec["lat"], rec["lng"] = c["lat"], c["lng"]
                    rec["scores"][f"{y}-{g}-{t}-{sub}"] = {"avg": c["avg"], "A": c["A"], "n": c["n"], "sd": c["sd"], "dist": c["dist"]}
                if len(cards) < 50: break
                page += 1; time.sleep(0.3)
            time.sleep(0.3)
        print("area", area, y, g, t, "schools so far", len(res), flush=True)
json.dump(res, open(os.path.join(D, "apt2me_middle.json"), "w"), ensure_ascii=False)
# 특목실적
for k, rec in res.items():
    try:
        r = s.get("https://apt2.me/apt/msch.jsp", params={"mcode": k}, timeout=30)
        txt = re.sub(r"<script.*?</script>", "", r.text, flags=re.S)
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", txt, re.S)
        tab = []
        for row in rows:
            cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
            if cells and any(cells): tab.append(cells)
        rec["msch"] = tab[:40]
    except Exception as e:
        rec["msch"] = None
    time.sleep(0.25)
json.dump(res, open(os.path.join(D, "apt2me_middle.json"), "w"), ensure_ascii=False)
print("DONE", len(res), flush=True)
