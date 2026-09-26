import json, math, os, re
D = os.path.dirname(__file__)
data = json.load(open(os.path.join(D, "data.json")))
M = json.loads(open(os.path.join(D, "map", "mapdata.js")).read()[len("const MAPDATA="):-1])
bounds = M["bounds"]; stations = M["stations"]
def pip(x, y, ring):
    inside = False; n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1
            if x < xin: inside = not inside
    return inside
bb = []
for b in bounds:
    xs = [p[0] for poly in b["polys"] for p in poly]; ys = [p[1] for poly in b["polys"] for p in poly]
    bb.append((min(xs), min(ys), max(xs), max(ys)))
def find_dong(lng, lat):
    for b, (x0, y0, x1, y1) in zip(bounds, bb):
        if not (x0 <= lng <= x1 and y0 <= lat <= y1): continue
        if any(pip(lng, lat, poly) for poly in b["polys"]): return b
    return None
def hav(a, b, c, d):
    R = 6371; dl = math.radians(c - a); dg = math.radians(d - b)
    x = math.sin(dl / 2) ** 2 + math.cos(math.radians(a)) * math.cos(math.radians(c)) * math.sin(dg / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))
SKIP_ST = {"railway": 1}
n_hit = 0
for c in data["complexes"]:
    b = find_dong(c["lng"], c["lat"])
    if b: c["hj"] = b["nm"]; c["hjcd"] = b["cd"]; c["sggnm"] = b["sggnm"]; n_hit += 1
    else: c["hj"] = None; c["hjcd"] = None; c["sggnm"] = c["sgg"]
    best = None
    for s in stations:
        dkm = hav(c["lat"], c["lng"], s["y"], s["x"])
        if best is None or dkm < best[1]: best = (s["n"], dkm)
    if best: c["st"] = [best[0], round(best[1], 2)]
print("hj matched", n_hit, "/", len(data["complexes"]))
# schools
SCH = json.load(open(os.path.join(D, "schools_out.json"))) if os.path.exists(os.path.join(D, "schools_out.json")) else {"ms": [], "assign": {}}
msmap = {s["id"]: s for s in SCH["ms"]}
for c in data["complexes"]:
    a = SCH["assign"].get(c["id"]); c["sch"] = a if a else None
data["schools"] = [{k: s[k] for k in ("id", "name", "lat", "lng", "A", "E", "avg", "n", "A3", "grade", "pct", "special", "gender", "subj", "addr") if k in s} for s in SCH["ms"]]
# trim payload
for c in data["complexes"]:
    for k, z in c["sizes"].items():
        z["trades"] = z["trades"][:12]; z["rents"] = z["rents"][:4]
    for key in ("nname","road"):
        c.pop(key, None)
js = "const DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
WS = "/Users/sam/Library/Application Support/Claude/scratch-workspaces/90c0a10e-dd5a-46a9-b2e4-6d5637301d7d/5aaa6540-cfa6-4307-864a-a35ab6b571f8/scratch-2026-09-25-39bc00"
open(os.path.join(D, "data.js"), "w").write(js)
open(os.path.join(WS, "data.js"), "w").write(js)
md = open(os.path.join(D, "map", "mapdata.js")).read()
open(os.path.join(WS, "mapdata.js"), "w").write(md)
t = open(os.path.join(D, "template_v2.html"), encoding="utf-8").read()
import time
BUILD_TAG = time.strftime("%Y%m%d%H%M")
out = t.replace('src="data.js"', f'src="data.js?v={BUILD_TAG}"').replace('src="mapdata.js"', f'src="mapdata.js?v={BUILD_TAG}"')
dest = os.path.join(WS, "gwanggyo-home-finder.html")
open(dest, "w", encoding="utf-8").write(out)
m = re.search(r"<script>(.*)</script>", out, re.S); open("/tmp/_chk2.js", "w").write(js + "\n" + md + "\n" + m.group(1))
print("page bytes", len(out.encode("utf-8")), "data.js", len(js.encode()), "mapdata.js", len(md.encode()))
