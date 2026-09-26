import json, math, os, re, statistics
D = os.path.dirname(__file__); P = os.path.dirname(D)
M = json.load(open(os.path.join(D, "apt2me_middle.json")))
OSM = json.load(open(os.path.join(D, "schools.json")))
MS = json.load(open(os.path.join(D, "msch.json"))) if os.path.exists(os.path.join(D, "msch.json")) else {}
data = json.load(open(os.path.join(P, "data.json")))
def hav(a, b, c, d):
    R = 6371; dl = math.radians(c - a); dg = math.radians(d - b)
    x = math.sin(dl / 2) ** 2 + math.cos(math.radians(a)) * math.cos(math.radians(c)) * math.sin(dg / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))
PREF = ["2025-2-1", "2024-3-2", "2024-2-2"]
EXCL = re.compile(r"국제중|중앙기독중|예술중|체육중|특수|대안")
ms = []
for k, v in M.items():
    if not v.get("lat") or EXCL.search(v["name"]): continue
    subj = {}
    for sub in ["국어", "영어", "수학"]:
        for pre in PREF:
            sc = v["scores"].get(f"{pre}-{sub}")
            if sc and sc.get("A") is not None: subj[sub] = dict(sc, src=pre); break
    if len(subj) < 2: continue
    A = statistics.mean(x["A"] for x in subj.values()); E = statistics.mean((x["dist"][4] if x.get("dist") and len(x["dist"]) == 5 else 0) for x in subj.values())
    avg = statistics.mean(x["avg"] for x in subj.values() if x.get("avg") is not None)
    n = max((x.get("n") or 0) for x in subj.values())
    # 3학년 2학기(2024) 참고값
    A3 = [v["scores"][f"2024-3-2-{s}"]["A"] for s in ["국어", "영어", "수학"] if v["scores"].get(f"2024-3-2-{s}") and v["scores"][f"2024-3-2-{s}"].get("A") is not None]
    mz = MS.get(k, {}); lt = mz.get("latest") or {}
    special_rate = lt.get("rate"); grads = lt.get("grads")
    ms.append({"id": k, "name": v["name"], "addr": v["addr"], "lat": v["lat"], "lng": v["lng"], "area": v["area"], "A": round(A, 1), "E": round(E, 1), "avg": round(avg, 1), "n": n,
               "A3": round(statistics.mean(A3), 1) if A3 else None, "subj": {s: {"A": x["A"], "avg": x["avg"], "src": x["src"]} for s, x in subj.items()},
               "special": special_rate, "grads": grads, "kinds": mz.get("kinds"), "gender": ("여" if "여자" in v["name"] else ("남" if re.search(r"남중|북중\b", v["name"]) else "")), "private": "사립" in json.dumps(v["scores"], ensure_ascii=False) or False})
# composite & grade (경기 남부 학교만으로 분포 산정: 동작구 제외)
pool = [s for s in ms if s["area"] != "11590"]
for s in ms: s["idx"] = round(s["A"] - 0.5 * s["E"], 1)
vals = sorted(x["idx"] for x in pool)
def pct(v): return sum(1 for x in vals if x <= v) / len(vals)
for s in ms:
    p = pct(s["idx"])
    g = 5 if p >= 0.85 else 4 if p >= 0.60 else 3 if p >= 0.30 else 2 if p >= 0.10 else 1
    if s["special"] is not None and s["special"] >= 5 and g < 5: g += 1
    s["grade"] = g; s["pct"] = round(p * 100)
ms_by_id = {s["id"]: s for s in ms}
es = [s for s in OSM if s["type"] == "초"]
def city(area): return area[:4]
assign = {}
for c in data["complexes"]:
    # 초등: 가장 가까운
    best = None
    for s in es:
        d = hav(c["lat"], c["lng"], s["lat"], s["lng"])
        if best is None or d < best[1]: best = (s["name"], d)
    esr = [best[0], int(best[1] * 1000)] if best and best[1] <= 2.5 else None
    # 중학교 후보: 같은 시 우선, 4km 내 3개
    cands = []
    for s in ms:
        d = hav(c["lat"], c["lng"], s["lat"], s["lng"])
        if d <= 4.0: cands.append((d, s))
    cands.sort(key=lambda x: x[0])
    same = [x for x in cands if c.get("sggnm", "").startswith({"4111": "수원", "4146": "용인", "4159": "화성", "4137": "오산", "4122": "평택", "1159": "동작"}.get(city(x[1]["area"]), "?"))]
    pick = (same or cands)[:3]
    assign[c["id"]] = {"es": esr, "ms": [[s["id"], int(d * 1000)] for d, s in pick]}
json.dump({"ms": ms, "assign": assign}, open(os.path.join(P, "schools_out.json"), "w"), ensure_ascii=False)
import collections
print("middle schools", len(ms), "graded dist", collections.Counter(s["grade"] for s in ms), "with special", sum(1 for s in ms if s["special"] is not None))
print("assigned", sum(1 for a in assign.values() if a["ms"]), "/", len(assign), "es", sum(1 for a in assign.values() if a["es"]))
for nm in ["영덕중학교", "광교중학교", "정평중학교", "매탄중학교", "반송중학교", "병점중학교"]:
    s = next((x for x in ms if x["name"] == nm), None)
    if s: print(nm, "A", s["A"], "E", s["E"], "avg", s["avg"], "idx", s["idx"], "pct", s["pct"], "grade", s["grade"], "special", s["special"])
