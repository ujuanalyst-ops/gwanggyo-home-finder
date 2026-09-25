import csv, glob, io, json, os, re, statistics, difflib
from collections import defaultdict
D = os.path.dirname(__file__)
MAIN = (37.15, 37.36, 126.95, 127.20)
BOXES = [MAIN, (36.96, 37.01, 127.08, 127.14), (37.470, 37.492, 126.960, 126.985)]
def inbox(lat, lng):
    return any(b[0] <= lat <= b[1] and b[2] <= lng <= b[3] for b in BOXES)
def norm(n):
    n = re.sub(r"\(.*?\)", lambda m: m.group(0)[1:-1], n)
    n = re.sub(r"[\s\-·ㆍ,.'’\"]", "", n)
    n = n.replace("아파트", "").replace("APT", "")
    n = re.sub(r"(\d+)차", r"\1차", n)
    return n.lower()
def won(s):  # "12<em class='txt_unit'>억</em> 8,000" -> 만원
    if not s or s == "0": return None
    t = re.sub(r"<[^>]+>", "", s).replace(",", "")
    m = re.match(r"(?:(\d+)억)?\s*(\d+)?", t.strip())
    if not m: return None
    return (int(m.group(1) or 0)) * 10000 + int(m.group(2) or 0)
def read_csv(path):
    raw = open(path, "rb").read().decode("cp949", errors="replace")
    lines = raw.splitlines()
    # header line begins with "NO"
    idx = next(i for i, l in enumerate(lines) if l.startswith('"NO"'))
    return list(csv.DictReader(io.StringIO("\n".join(lines[idx:]))))
def bucket(area):
    a = float(area)
    return str(int(a))
def pyeong(area):
    return round(float(area) / 0.76 / 3.3058)
# ---------- MOLIT ----------
M = {}  # key (dong, norm) -> record
def key_of(row):
    sgg = row["시군구"].strip()
    dong = sgg.split()[-1]
    return sgg, dong, row["단지명"].strip()
for f in sorted(glob.glob(os.path.join(D, "molit", "sale_*.csv"))):
    for r in read_csv(f):
        if r.get("해제사유발생일", "-") not in ("-", "", None): continue
        sgg, dong, name = key_of(r)
        k = (dong, norm(name))
        rec = M.setdefault(k, {"name": name, "sgg": sgg, "dong": dong, "built": r["건축년도"], "road": r["도로명"], "jibun": r["번지"], "sizes": {}})
        b = bucket(r["전용면적(㎡)"])
        sz = rec["sizes"].setdefault(b, {"area": float(r["전용면적(㎡)"]), "trades": [], "rents": []})
        sz["trades"].append([r["계약년월"], int(r["계약일"]), int(r["층"]), int(r["거래금액(만원)"].replace(",", ""))])
# 연립다세대(평택 소사벌 해링턴코트: 현 거주 주택)
for f in sorted(glob.glob(os.path.join(D, "molit_rh", "sale_*.csv"))):
    for r in read_csv(f):
        nm = r.get("단지명") or r.get("건물명") or ""
        if "해링턴코트" not in nm or "죽백동" not in r["시군구"]: continue
        r["단지명"] = nm
        if r.get("해제사유발생일", "-") not in ("-", "", None): continue
        sgg, dong, name = key_of(r)
        k = (dong, norm(name))
        rec = M.setdefault(k, {"name": name + "(연립·현 거주)", "sgg": sgg, "dong": dong, "built": r["건축년도"], "road": r["도로명"], "jibun": r["번지"], "sizes": {}, "rh": True})
        b = bucket(r["전용면적(㎡)"])
        sz = rec["sizes"].setdefault(b, {"area": float(r["전용면적(㎡)"]), "trades": [], "rents": []})
        sz["trades"].append([r["계약년월"], int(r["계약일"]), int(r["층"]), int(r["거래금액(만원)"].replace(",", ""))])
for f in sorted(glob.glob(os.path.join(D, "molit", "rent_*.csv"))):
    for r in read_csv(f):
        if r.get("전월세구분") != "전세": continue
        sgg, dong, name = key_of(r)
        k = (dong, norm(name))
        if k not in M:
            M[k] = {"name": name, "sgg": sgg, "dong": dong, "built": r["건축년도"], "road": r["도로명"], "jibun": r["번지"], "sizes": {}}
        b = bucket(r["전용면적(㎡)"])
        sz = M[k]["sizes"].setdefault(b, {"area": float(r["전용면적(㎡)"]), "trades": [], "rents": []})
        sz["rents"].append([r["계약년월"], int(r["계약일"]), int(r["층"]), int(r["보증금(만원)"].replace(",", ""))])
print("molit complexes", len(M))
# ---------- NAVER ----------
N = json.load(open(os.path.join(D, "naver", "complexes_raw.json"))) if os.path.exists(os.path.join(D, "naver", "complexes_raw.json")) else {}
Z = json.load(open(os.path.join(D, "zigbang.json"))) if os.path.exists(os.path.join(D, "zigbang.json")) else {}
LOC = json.load(open(os.path.join(D, "naver", "loc.json"))) if os.path.exists(os.path.join(D, "naver", "loc.json")) else {}
REG = json.load(open(os.path.join(D, "naver", "regions.json")))
dongc = {r["name"]: (r["lat"], r["lng"], r["gu"]) for r in REG}
GUNM = {"41117": "수원시 영통구", "41111": "수원시 장안구", "41113": "수원시 권선구", "41115": "수원시 팔달구", "41465": "용인시 수지구", "41463": "용인시 기흥구", "41590": "화성시", "41370": "오산시", "41220": "평택시", "11590": "서울 동작구"}
by_dong = defaultdict(list)
for h, c in N.items():
    by_dong[c.get("dong", "")].append(c)
def find_naver(dong, name):
    cands = by_dong.get(dong, [])
    nn = norm(name)
    for c in cands:
        if norm(c["hscpNm"]) == nn: return c
    for c in cands:
        cn = norm(c["hscpNm"])
        if (nn in cn or cn in nn) and min(len(nn), len(cn)) >= 3: return c
    best, bs = None, 0
    for c in cands:
        r = difflib.SequenceMatcher(None, nn, norm(c["hscpNm"])).ratio()
        if r > bs: best, bs = c, r
    return best if bs >= 0.72 else None
def askOf(nv):
    g = nv.get
    return {"dealMin": won(g("dealPrcMin")), "dealMax": won(g("dealPrcMax")), "leaseMin": won(g("leasePrcMin")), "leaseMax": won(g("leasePrcMax")), "dealCnt": g("dealCnt", 0), "leaseCnt": g("leaseCnt", 0), "minSpc": g("minSpc"), "maxSpc": g("maxSpc")}
out = []
used = set()
CUT12 = "202510"; CUT3 = "202607"
def summarize(sz):
    tr = sorted(sz["trades"], key=lambda t: (t[0], t[1]), reverse=True)
    rn = sorted(sz["rents"], key=lambda t: (t[0], t[1]), reverse=True)
    p12 = [t[3] for t in tr if t[0] >= CUT12]; p3 = [t[3] for t in tr if t[0] >= CUT3]
    j12 = [t[3] for t in rn if t[0] >= CUT12]
    # monthly medians for chart
    mon = defaultdict(list)
    for t in tr: mon[t[0]].append(t[3])
    series = sorted([[m, int(statistics.median(v)), len(v)] for m, v in mon.items()])
    return {"area": round(sz["area"], 2), "py": pyeong(sz["area"]), "trades": tr[:30], "rents": rn[:10],
            "n12": len(p12), "med12": int(statistics.median(p12)) if p12 else None, "med3": int(statistics.median(p3)) if p3 else None,
            "max24": max([t[3] for t in tr]) if tr else None, "last": tr[0] if tr else None,
            "jn12": len(j12), "jmed12": int(statistics.median(j12)) if j12 else None, "series": series}
for (dong, nn), rec in M.items():
    nv = find_naver(dong, rec["name"])
    lat = lng = None; approx = True; hs = None
    if nv:
        used.add(nv["hscpNo"]); hs = nv["hscpNo"]
        if hs in LOC: lat, lng, _ = LOC[hs]; approx = False
    z = Z.get(dong + "|" + nn)
    zid = None; zunits = None; zyear = None
    if z:
        zid = z["zid"]; zunits = z.get("units"); zyear = (z.get("approved") or "")[:4]
        if lat is None: lat, lng = z["lat"], z["lng"]; approx = False
    if lat is None and dong in dongc:
        lat, lng = dongc[dong][0], dongc[dong][1]
    if lat is None: continue
    if not inbox(lat, lng) and not (rec["name"] in ("반석블레스",) or rec.get("rh")): continue
    sizes = {b: summarize(s) for b, s in rec["sizes"].items()}
    ntr = sum(len(s["trades"]) for s in rec["sizes"].values())
    units = (nv.get("totHsehCnt") if nv else None) or zunits
    if (units or 0) < 100 and ntr < 3 and not rec.get("rh"): continue
    sggname = rec["sgg"].replace("경기도 ", "").replace("서울특별시 ", "서울 ")
    sggname = " ".join(sggname.split()[:-1])
    built = int(rec["built"]) if rec["built"].isdigit() else (int(zyear) if zyear and zyear.isdigit() else None)
    out.append({"id": (hs or ("z" + str(zid) if zid else "m" + str(len(out)))), "hs": hs, "zid": zid, "name": rec["name"], "nname": nv["hscpNm"] if nv else None, "dong": dong, "sgg": sggname,
                "lat": round(lat, 5), "lng": round(lng, 5), "approx": approx, "built": built, "rh": bool(rec.get("rh")),
                "road": rec["road"], "units": units, "dongs": nv.get("totDongCnt") if nv else None,
                "ask": askOf(nv) if nv else None,
                "sizes": sizes})
# Naver-only complexes (no trades in 24m) within box
for h, c in N.items():
    if h in used: continue
    if h not in LOC: continue
    lat, lng, _ = LOC[h]
    if not inbox(lat, lng): continue
    if (c.get("totHsehCnt") or 0) < 150: continue
    y = c.get("useAprvYmd", "")[:4]
    out.append({"id": h, "hs": h, "name": c["hscpNm"], "nname": c["hscpNm"], "dong": c.get("dong", ""), "sgg": GUNM.get(c.get("gu", "")[:5], ""), "lat": round(lat, 5), "lng": round(lng, 5), "approx": False,
                "built": int(y) if y.isdigit() else None, "road": "", "units": c.get("totHsehCnt"), "dongs": c.get("totDongCnt"),
                "ask": askOf(c),
                "sizes": {}})
matched = sum(1 for o in out if o["hs"])
print("out", len(out), "matched naver", matched, "approx coords", sum(1 for o in out if o["approx"]))
meta = {"generated": "2026-09-25", "sale_range": "2024-10-01~2026-09-25", "rent_range": "2025-10-01~2026-09-25", "n": len(out)}
json.dump({"meta": meta, "complexes": out}, open(os.path.join(D, "data.json"), "w"), ensure_ascii=False)
js = "const DATA=" + json.dumps({"meta": meta, "complexes": out}, ensure_ascii=False, separators=(",", ":")) + ";"
open(os.path.join(D, "data.js"), "w").write(js)
print("data.js bytes", len(js.encode("utf-8")))
