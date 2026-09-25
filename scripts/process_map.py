import json, math, glob, os, collections
def dp(pts,tol):
    if len(pts)<3: return pts
    a,b=pts[0],pts[-1]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    if L<1e-12:
        # closed ring: split at farthest point
        mi=max(range(1,len(pts)-1),key=lambda i:math.hypot(pts[i][0]-a[0],pts[i][1]-a[1]))
        return dp(pts[:mi+1],tol)[:-1]+dp(pts[mi:],tol)
    md,mi=0,0
    for i in range(1,len(pts)-1):
        p=pts[i]; dd=abs(dy*p[0]-dx*p[1]+b[0]*a[1]-b[1]*a[0])/L
        if dd>md: md,mi=dd,i
    if md>tol: return dp(pts[:mi+1],tol)[:-1]+dp(pts[mi:],tol)
    return [a,b]
R=lambda v:round(v,5)
# ---- bounds
d=json.load(open('hjd.geojson'))
SGG={'41111','41113','41115','41117','41461','41463','41465','41590','41591','41593','41595','41597','41370','41220','11590'}
def coords(g): return [g['coordinates']] if g['type']=='Polygon' else g['coordinates']
def bbox(polys):
    xs=[x for poly in polys for x,y in poly[0]]; ys=[y for poly in polys for x,y in poly[0]]; return min(xs),min(ys),max(xs),max(ys)
bounds=[]
for x in d['features']:
    p=x['properties']
    if not (p['sgg'] in SGG or p['sggnm'].startswith('화성')): continue
    polys=coords(x['geometry']); bx=bbox(polys)
    inmain = not (bx[2]<126.94 or bx[0]>127.21 or bx[3]<37.14 or bx[1]>37.37)
    special = ('동작구'==p['sggnm'] and '사당' in p['adm_nm']) or ('평택' in p['sggnm'] and bx[1]<37.01 and bx[3]>36.96 and bx[0]<127.14 and bx[2]>127.08)
    if not (inmain or special): continue
    out=[]
    for poly in polys:
        ring=[[R(a),R(b)] for a,b in dp(poly[0],0.00006)]
        if len(ring)>=4: out.append(ring)
    bounds.append({'nm':p['adm_nm'].split()[-1],'sgg':p['sgg'],'sggnm':p['sggnm'].replace('용인시','용인시 ').replace('수원시','수원시 ').replace('화성시','화성시 ').strip(),'sido':p['sidonm'],'cd':p['adm_cd2'],'polys':out})
print('bounds',len(bounds))
# ---- osm
def load(f):
    try: return json.load(open(f))['elements']
    except Exception: return []
roads=[]
for f in sorted(glob.glob('roads[0-9].json')):
    for e in load(f):
        if e['type']!='way' or 'geometry' not in e: continue
        t=e.get('tags',{}); pts=[[R(g['lon']),R(g['lat'])] for g in e['geometry']]
        roads.append({'c':t.get('highway'),'n':t.get('name',''),'p':dp(pts,0.00005)})
rails=[];stations=[]
for e in load('osm_rail.json'):
    t=e.get('tags',{})
    if e['type']=='node':
        if 'name' in t: stations.append({'n':t['name'],'x':R(e['lon']),'y':R(e['lat']),'s':t.get('station','')})
    elif 'geometry' in e:
        pts=[[R(g['lon']),R(g['lat'])] for g in e['geometry']]
        rails.append({'c':t.get('railway'),'n':t.get('name',''),'p':dp(pts,0.00005)})
water=[]
for e in load('osm_water.json'):
    t=e.get('tags',{})
    if e['type']!='way' or 'geometry' not in e: continue
    pts=[[R(g['lon']),R(g['lat'])] for g in e['geometry']]
    if t.get('natural')=='water':
        if len(pts)<8 or pts[0]!=pts[-1]: continue
        xs=[q[0] for q in pts]; ys=[q[1] for q in pts]
        if max(xs)-min(xs)>0.05 or max(ys)-min(ys)>0.05: continue
        water.append({'k':'a','p':dp(pts,0.00006)})
    else: water.append({'k':'l','n':t.get('name',''),'p':dp(pts,0.00006)})
# dedupe stations by name (keep first)
seen=set(); st=[]
for s in stations:
    if s['n'] in seen: continue
    seen.add(s['n']); st.append(s)
M={'bounds':bounds,'roads':roads,'rails':rails,'stations':st,'water':water}
js='const MAPDATA='+json.dumps(M,ensure_ascii=False,separators=(',',':'))+';'
open('mapdata.js','w').write(js)
print('roads',len(roads),'rails',len(rails),'stations',len(st),'water',len(water),'bytes',len(js.encode()))
print(collections.Counter(r['c'] for r in rails), collections.Counter(r['c'] for r in roads))
