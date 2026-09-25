import re, os
D = os.path.dirname(__file__)
p = os.path.join(D, "template_v2.html")
s = open(p, encoding="utf-8").read()

# ---------- CSS ----------
css = """
.mapbox svg{max-height:82vh}
.tip{position:absolute;z-index:5;pointer-events:none;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:12px;line-height:1.45;box-shadow:var(--shadow);max-width:280px}
.tip b{font-size:13px}
.tip .tr{color:var(--muted);margin-top:3px}
.tip .tr span{display:inline-block;margin-right:6px}
.dong{fill-opacity:.32;stroke:var(--ink);stroke-opacity:.28;stroke-width:.7;vector-effect:non-scaling-stroke;cursor:pointer;transition:fill-opacity .12s}
.dong:hover{fill-opacity:.55}
.dong.on{fill-opacity:.62;stroke-opacity:.9;stroke-width:1.4}
.dong.off{fill-opacity:.10}
.gulbl{font-weight:700;fill:var(--ink);opacity:.75;paint-order:stroke;stroke:var(--map-land);stroke-width:4px;stroke-linejoin:round;pointer-events:none}
.dlbl{font-weight:600;fill:var(--ink);opacity:.8;paint-order:stroke;stroke:var(--map-land);stroke-width:3px;stroke-linejoin:round;pointer-events:none}
.stn{pointer-events:none}
.stn text{fill:var(--ink);opacity:.85;paint-order:stroke;stroke:var(--map-land);stroke-width:3px}
.rd{fill:none;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke}
.tree{margin-bottom:12px}
.tree .gu{display:flex;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--line2);cursor:pointer;font-weight:600}
.tree .gu .cnt{margin-left:auto;font-size:11px;color:var(--muted);font-weight:400;white-space:nowrap}
.tree .gu .tg{width:18px;text-align:center;color:var(--muted)}
.tree .dongs{display:flex;flex-wrap:wrap;gap:4px;padding:6px 0 8px 18px}
.tree .dongs button,.tree .gu button.pick{font-size:11px;padding:2px 8px;border-radius:999px;border:1px solid var(--line);background:var(--card)}
.tree .dongs button[aria-pressed="true"],.tree .gu button.pick[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.tree .dongs button i{display:inline-block;width:7px;height:7px;border-radius:50%;margin-left:4px;vertical-align:1px}
.maplegend{display:flex;gap:10px;flex-wrap:wrap;font-size:11px;color:var(--muted);margin-top:6px}
.maplegend i{display:inline-block;width:14px;height:3px;vertical-align:2px;margin-right:4px;border-radius:2px}
/* report */"""
s = s.replace("/* report */", css, 1)

# ---------- HTML: tooltip + region tree + legend ----------
s = s.replace("""        <svg id="map" viewBox="0 0 1000 1000" role="img" aria-label="광교역 주변 아파트 단지 지도"></svg>
      </div>""", """        <svg id="map" viewBox="0 0 1000 1070" role="img" aria-label="광교역 주변 아파트 단지 지도"></svg>
        <div id="tip" class="tip" hidden></div>
      </div>
      <div class="maplegend"><span><i style="background:#D4003B"></i>신분당선</span><span><i style="background:#FABE00"></i>수인분당선</span><span><i style="background:#0052A4"></i>1호선·경부선</span><span><i style="background:#9A6292"></i>GTX·SRT</span><span><i style="background:var(--map-hwy);height:4px"></i>고속도로</span><span><i style="background:var(--map-road)"></i>주요도로</span><span><i style="background:var(--map-water);height:6px"></i>하천·호수</span><span>구·동 경계: 행정안전부 행정동(2026-07) · 도로·철도·수계: OpenStreetMap</span></div>""")
s = s.replace("""    <aside>
      <div class="card cond">""", """    <aside>
      <div class="card tree" id="tree"></div>
      <div class="card cond">""")
s = s.replace("""<p class="small" style="margin-top:6px">약도형 지도(도로·철도 근사). 휠로 확대, 드래그로 이동. 좌표는 직방 단지정보 기준(동 중심 표기 단지는 '위치 근사'). 기준가 = 해당 면적의 최근 3개월 실거래 중위값 → 없으면 12개월 중위값 → 마지막 거래 → 네이버 호가 순. 광교역 = 신분당선 광교(경기대)역.</p>""",
"""<p class="small" style="margin-top:6px">휠로 확대, 드래그로 이동, 동 영역을 클릭하면 그 동만 판정 대상으로 좁혀지고 다시 클릭하면 해제됩니다. 마우스를 점에 올리면 단지 특징이 뜹니다. 좌표는 직방 단지정보 기준(동 중심 표기 단지는 점선 테두리 '위치 근사'). 기준가 = 해당 면적의 최근 3개월 실거래 중위값 → 없으면 12개월 중위값 → 마지막 거래 → 네이버 호가 순.</p>""")

# ---------- JS: state ----------
s = s.replace("const S = {budget:7.0,budgetManual:false,", "const S = {hj:new Set(),budget:7.0,budgetManual:false,")
# evaluate: region filter by 행정동 selection
s = s.replace("""  if(S.include.length && !matchRegion(c,S.include)) push(2,'포함 지역 조건 밖');""",
"""  if(S.hj.size && !S.hj.has(c.hjcd)) push(2,'지도에서 선택한 지역 밖');
  if(S.include.length && !matchRegion(c,S.include)) push(2,'포함 지역 조건 밖');""")
s = s.replace("""function matchRegion(c,list){ return list.some(x=>x&&(c.dong.includes(x)||c.sgg.includes(x)||c.m.area.includes(x)||c.name.includes(x))); }""",
"""function matchRegion(c,list){ return list.some(x=>x&&(c.dong.includes(x)||c.sgg.includes(x)||c.m.area.includes(x)||c.name.includes(x)||(c.hj&&c.hj.includes(x))||(c.sggnm&&c.sggnm.replace(/\\s/g,'').includes(x.replace(/\\s/g,''))))); }""")

# ---------- JS: replace MAP block ----------
start = s.index("/* ---------------- MAP (pan/zoom) ---------------- */")
end = s.index("/* ---------------- LIST / DETAIL ---------------- */")
newmap = r"""/* ---------------- MAP (vector base map + pan/zoom) ---------------- */
const EXT={lat0:37.14,lat1:37.37,lng0:126.94,lng1:127.21}; const MW=1000, MH=1070;
function px(lng){return (lng-EXT.lng0)/(EXT.lng1-EXT.lng0)*MW;}
function py(lat){return (EXT.lat1-lat)/(EXT.lat1-EXT.lat0)*MH;}
function pathXY(pts){return pts.map((p,i)=>(i?'L':'M')+px(p[0]).toFixed(1)+' '+py(p[1]).toFixed(1)).join(' ');}
const GUCOL={'수원시 영통구':'#7FB3D5','수원시 장안구':'#A3C9A8','수원시 권선구':'#D9B98A','수원시 팔달구':'#C9A7D6','용인시 수지구':'#F2A38B','용인시 기흥구':'#F5D57A','용인시 처인구':'#C8C8C8','화성시 동탄구':'#8FD3C9','화성시 병점구':'#B8D98A','화성시 효행구':'#D7D7B0','화성시 만세구':'#D7D7B0','오산시':'#E6B8C6','평택시':'#B5C8E8','동작구':'#BBBBBB'};
const RAILCOL=(n)=>/신분당/.test(n)?'#D4003B':/분당|수인/.test(n)?'#FABE00':/1호선|경부선|경부 본선/.test(n)?'#0052A4':/GTX|SRT|수서|고속/.test(n)?'#9A6292':/경전철|에버라인/.test(n)?'#6FB245':'#8A8F96';
const VB={x:0,y:0,w:MW,h:MH};
const DONGS=MAPDATA.bounds; const DONGBB={}; const GUBB={};
DONGS.forEach(b=>{ const xs=[],ys=[]; b.polys.forEach(pl=>pl.forEach(p=>{xs.push(p[0]);ys.push(p[1]);})); const bb=[Math.min(...xs),Math.min(...ys),Math.max(...xs),Math.max(...ys)]; DONGBB[b.cd]=bb; const g=GUBB[b.sggnm]||(GUBB[b.sggnm]=[1e9,1e9,-1e9,-1e9]); g[0]=Math.min(g[0],bb[0]);g[1]=Math.min(g[1],bb[1]);g[2]=Math.max(g[2],bb[2]);g[3]=Math.max(g[3],bb[3]); });
function setVB(){ const svg=document.getElementById('map'); svg.setAttribute('viewBox',`${VB.x} ${VB.y} ${VB.w} ${VB.h}`); drawDynamic(); }
function zoomTo(lat,lng,w){ VB.w=w; VB.h=w*MH/MW; VB.x=px(lng)-w/2; VB.y=py(lat)-VB.h/2; setVB(); }
function zoomBB(bb,pad=1.25){ const x0=px(bb[0]),x1=px(bb[2]),y0=py(bb[3]),y1=py(bb[1]); const w=Math.max((x1-x0)*pad,(y1-y0)*pad*MW/MH,50); zoomTo((bb[1]+bb[3])/2,(bb[0]+bb[2])/2,w); }
function drawMap(){
  const svg=document.getElementById('map'); let s='';
  s+=`<rect x="-3000" y="-3000" width="7000" height="7000" fill="var(--map-land)"/>`;
  // 행정동 polygons
  s+='<g id="dongs">'+DONGS.map(b=>`<path class="dong" data-cd="${b.cd}" fill="${GUCOL[b.sggnm]||'#CCCCCC'}" d="${b.polys.map(pl=>pathXY(pl)+'Z').join(' ')}"><title>${b.sggnm} ${b.nm}</title></path>`).join('')+'</g>';
  // water
  s+='<g>'+MAPDATA.water.map(w=>w.k==='a'?`<path d="${pathXY(w.p)}Z" fill="var(--map-water)" stroke="none"/>`:`<path class="rd" d="${pathXY(w.p)}" stroke="var(--map-water)" stroke-width="2.2"/>`).join('')+'</g>';
  // roads
  const rw={motorway:3.4,trunk:2.2,primary:1.3};
  s+='<g>'+MAPDATA.roads.map(r=>`<path class="rd" d="${pathXY(r.p)}" stroke="${r.c==='motorway'?'var(--map-hwy)':'var(--map-road)'}" stroke-width="${rw[r.c]||1}"/>`).join('')+'</g>';
  // rails
  s+='<g>'+MAPDATA.rails.map(r=>`<path class="rd" d="${pathXY(r.p)}" stroke="${RAILCOL(r.n)}" stroke-width="${r.c==='light_rail'?1.4:2}" ${/고속|경부선/.test(r.n)&&!/1호선/.test(r.n)?'stroke-dasharray="6 4"':''} opacity=".9"><title>${r.n}</title></path>`).join('')+'</g>';
  s+='<g id="dyn"></g><g id="markers"></g>';
  svg.innerHTML=s;
  svg.querySelectorAll('.dong').forEach(el=>el.addEventListener('click',ev=>{ if(dragMoved) return; toggleDong(el.dataset.cd); }));
  let drag=null; var dragMoved=false;
  svg.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,vx:VB.x,vy:VB.y}; dragMoved=false; hideTip(); svg.classList.add('drag'); svg.setPointerCapture(e.pointerId);});
  svg.addEventListener('pointermove',e=>{ if(!drag) return; const r=svg.getBoundingClientRect(); const k=VB.w/r.width; const dx=e.clientX-drag.x, dy=e.clientY-drag.y; if(Math.abs(dx)+Math.abs(dy)>3) dragMoved=true; VB.x=drag.vx-dx*k; VB.y=drag.vy-dy*k; svg.setAttribute('viewBox',`${VB.x} ${VB.y} ${VB.w} ${VB.h}`); });
  const end=()=>{ if(drag){drag=null; svg.classList.remove('drag'); drawDynamic();} };
  svg.addEventListener('pointerup',end); svg.addEventListener('pointercancel',end);
  svg.addEventListener('wheel',e=>{ e.preventDefault(); const r=svg.getBoundingClientRect(); const mx=VB.x+(e.clientX-r.left)/r.width*VB.w, my=VB.y+(e.clientY-r.top)/r.height*VB.h; const f=e.deltaY>0?1.25:0.8; const nw=Math.min(1600,Math.max(40,VB.w*f)); const nh=nw*MH/MW; VB.x=mx-(mx-VB.x)*nw/VB.w; VB.y=my-(my-VB.y)*nh/VB.h; VB.w=nw; VB.h=nh; setVB(); },{passive:false});
  setVB();
}
function inView(X,Y,m=30){ return !(X<VB.x-m||X>VB.x+VB.w+m||Y<VB.y-m||Y>VB.y+VB.h+m); }
function drawDynamic(){
  const scale=VB.w/MW; const g=document.getElementById('dyn'); let s='';
  // 구 labels (zoomed out) / 동 labels (zoomed in)
  if(scale>0.42){ for(const k in GUBB){ const bb=GUBB[k]; const X=px((bb[0]+bb[2])/2), Y=py((bb[1]+bb[3])/2); if(!inView(X,Y)) continue; s+=`<text class="gulbl" x="${X}" y="${Y}" text-anchor="middle" font-size="${(15*Math.min(1.3,scale)).toFixed(1)}">${k.replace('수원시 ','').replace('용인시 ','').replace('화성시 ','')}</text>`; } }
  else { DONGS.forEach(b=>{ const bb=DONGBB[b.cd]; const X=px((bb[0]+bb[2])/2), Y=py((bb[1]+bb[3])/2); if(!inView(X,Y)) return; s+=`<text class="dlbl" x="${X}" y="${Y}" text-anchor="middle" font-size="${(11*Math.max(0.45,scale)*1.6).toFixed(1)}">${b.nm}</text>`; }); }
  // stations
  if(scale<0.75){ MAPDATA.stations.forEach(st=>{ const X=px(st.x), Y=py(st.y); if(!inView(X,Y)) return; const r=(3.2*Math.max(0.4,Math.min(1,scale))).toFixed(2); s+=`<g class="stn"><circle cx="${X}" cy="${Y}" r="${r}" fill="var(--card)" stroke="var(--ink)" stroke-width="${(1.4*Math.max(0.4,scale)).toFixed(2)}"/>${scale<0.5?`<text x="${X+ +r+2}" y="${Y-2}" font-size="${(9.5*Math.max(0.5,scale)*1.5).toFixed(1)}">${st.n}</text>`:''}</g>`; }); }
  // 직장
  const WX=px(WORK.lng), WY=py(WORK.lat); const ws=Math.max(0.35,Math.min(1,scale));
  s+=`<g><rect x="${WX-9*ws}" y="${WY-9*ws}" width="${18*ws}" height="${18*ws}" rx="3" fill="var(--ink)"/><text x="${WX}" y="${WY+4*ws}" text-anchor="middle" font-size="${(10*ws).toFixed(1)}" style="fill:var(--card);font-weight:700">직</text><text class="dlbl" x="${WX-12*ws}" y="${WY-13*ws}" text-anchor="end" font-size="${(11*ws).toFixed(1)}">직장 · 광교역 앞</text></g>`;
  g.innerHTML=s;
  document.querelectorAll;
  document.querySelectorAll('.dong').forEach(el=>{ el.classList.toggle('on',S.hj.has(el.dataset.cd)); el.classList.toggle('off',S.hj.size>0&&!S.hj.has(el.dataset.cd)); });
  drawMarkers();
}
function drawMarkers(){
  const g=document.getElementById('markers'); const scale=VB.w/MW; const fs=(11*Math.max(0.45,scale)*1.4).toFixed(1);
  const order=[...C].sort((a,b)=>EV[b.id].worst-EV[a.id].worst);
  const showLbl = scale<0.3;
  let s='';
  order.forEach(c=>{const e=EV[c.id]; const vis=S.filter==='all'||(S.filter==='blue'&&e.status==='blue')||(S.filter==='by'&&e.status!=='red');
    if(!vis && scale>0.5) return;
    const X=px(c.lng), Y=py(c.lat); if(!inView(X,Y,20)) return;
    const col=`var(--${e.status})`; const base=e.status==='blue'?7:(e.status==='yellow'?5.5:(scale>0.6?2.6:4)); const r=(base*Math.max(0.35,Math.min(1,scale))).toFixed(2);
    const op=(e.status==='red'&&scale>0.6&&S.selected!==c.id)?' opacity=".45"':'';
    const lbl=(showLbl && (e.status!=='red'||S.selected===c.id))||S.selected===c.id;
    s+=`<g class="mk ${S.selected===c.id?'sel':''} ${vis?'':'dim'}" data-id="${c.id}"><circle cx="${X}" cy="${Y}" r="${r}" fill="${col}"${op} ${c.approx?'stroke-dasharray="2 1.5"':''}/>${lbl?`<text x="${X+ +r+2}" y="${Y+3}" font-size="${fs}">${c.name}</text>`:''}</g>`;});
  g.innerHTML=s;
  g.querySelectorAll('.mk').forEach(el=>{ el.addEventListener('click',ev=>{ev.stopPropagation(); select(el.dataset.id);}); el.addEventListener('pointerenter',ev=>showTip(el.dataset.id,ev)); el.addEventListener('pointermove',ev=>moveTip(ev)); el.addEventListener('pointerleave',hideTip); });
}
/* ---------------- 툴팁 · 특징 ---------------- */
function traits(c,e){
  const t=[];
  if(c.units) t.push(`${c.units.toLocaleString()}세대 ${c.units>=1500?'초대형 단지':c.units>=1000?'대단지':c.units>=500?'중규모 단지':'소규모 단지'}`);
  if(c.built) t.push(`${c.built}년 준공 · ${2026-c.built}년차${c.built>=2018?' 신축':c.built>=2010?' 준신축':c.built<=2000?' 구축':''}`);
  if(c.st){ const m=Math.round(c.st[1]*1000); t.push(m<=800?`${c.st[0]} ${m}m 역세권(도보 ${Math.max(1,Math.round(m/70))}분)`:m<=1500?`${c.st[0]} ${(m/1000).toFixed(1)}km`:`가까운 역 ${(m/1000).toFixed(1)}km(역 원거리)`); }
  if(e.sz){ t.push(`${e.sz.area}㎡ 방 ${e.rm.txt}`); if(e.sz.n12) t.push(`12개월 거래 ${e.sz.n12}건${e.sz.jmed12&&e.rp?` · 전세가율 ${Math.round(e.sz.jmed12/e.rp.p*100)}%`:''}`); }
  t.push(`출근 자가용 ${c.m.car}분 · 대중교통 ${c.m.transit}분`);
  t.push(`교육 ${e.es}등급${c.m.acad>=4?' · 학원가 접근 좋음':''}${c.m.known?'':' (미평가 동)'}`);
  t.push(c.reg?'규제지역(토허구역)':'비규제지역');
  if(c.ask&&c.ask.dealCnt) t.push(`네이버 매물 ${c.ask.dealCnt}건`);
  if(c.rh) t.push('연립다세대(현 거주)');
  return t;
}
function showTip(id,ev){ const c=C.find(x=>x.id===id); if(!c) return; const e=EV[c.id]; const tip=document.getElementById('tip'); const lab={blue:'적합',yellow:'개선하면 가능',red:'부적합'}[e.status];
  tip.innerHTML=`<b>${c.name}</b> <span class="badge ${e.status}">${lab}</span><div class="small">${c.sggnm||c.sgg} ${c.hj||c.dong}${c.hj&&c.hj!==c.dong?` (법정동 ${c.dong})`:''}</div><div style="margin-top:4px"><b class="num">${e.rp?fmtEok(e.rp.p):'가격 정보 없음'}</b> <span class="small">${e.rp?e.rp.src:''}</span></div><div class="tr">${traits(c,e).map(x=>`<span>· ${x}</span>`).join('')}</div>`;
  tip.hidden=false; moveTip(ev); }
function moveTip(ev){ const tip=document.getElementById('tip'); if(tip.hidden) return; const box=document.getElementById('mapbox').getBoundingClientRect(); let x=ev.clientX-box.left+14, y=ev.clientY-box.top+14; if(x+300>box.width) x=ev.clientX-box.left-300; if(y+tip.offsetHeight+10>box.height) y=ev.clientY-box.top-tip.offsetHeight-10; tip.style.left=x+'px'; tip.style.top=Math.max(4,y)+'px'; }
function hideTip(){ document.getElementById('tip').hidden=true; }
/* ---------------- 지역 트리 (구 → 행정동) ---------------- */
function toggleDong(cd){ if(S.hj.has(cd)) S.hj.delete(cd); else S.hj.add(cd); S.listLimit=60; afterRegionChange(); }
function afterRegionChange(){ refresh(); if(S.hj.size){ let bb=[1e9,1e9,-1e9,-1e9]; S.hj.forEach(cd=>{const b=DONGBB[cd]; if(!b) return; bb=[Math.min(bb[0],b[0]),Math.min(bb[1],b[1]),Math.max(bb[2],b[2]),Math.max(bb[3],b[3])];}); if(bb[0]<1e8) zoomBB(bb,1.3); } }
function renderTree(){
  const save=S.hj; S.hj=new Set(); const base={}; C.forEach(c=>{ base[c.id]=evaluate(c).status; }); S.hj=save;
  const byGu={}; C.forEach(c=>{ if(!c.hjcd) return; const g=byGu[c.sggnm]||(byGu[c.sggnm]={n:0,b:0,y:0,r:0,dongs:{}}); g.n++; g[base[c.id][0]]++; const d=g.dongs[c.hjcd]||(g.dongs[c.hjcd]={nm:c.hj,n:0,b:0,y:0,r:0}); d.n++; d[base[c.id][0]]++; });
  const gus=Object.entries(byGu).sort((a,b)=>b[1].b-a[1].b||b[1].n-a[1].n);
  const open=window._treeOpen||(window._treeOpen=new Set(gus.slice(0,2).map(g=>g[0])));
  const cnt=(o)=>`<span class="cnt"><b style="color:var(--blue)">${o.b}</b>·<b style="color:var(--yellow)">${o.y}</b>·<b style="color:var(--red)">${o.r}</b> / ${o.n}</span>`;
  document.getElementById('tree').innerHTML=`<div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px"><h3>지역 선택 <span class="small">구 → 행정동 · 파랑·노랑·빨강 / 단지수</span></h3><button class="btn" style="padding:3px 9px;font-size:12px" id="treeClear" ${S.hj.size?'':'disabled'}>전체 해제</button></div>
  ${gus.map(([gu,g])=>{ const allOn=Object.keys(g.dongs).every(cd=>S.hj.has(cd)); return `<div class="gu" data-gu="${gu}"><span class="tg">${open.has(gu)?'▾':'▸'}</span><span>${gu}</span><button class="pick" data-gu="${gu}" aria-pressed="${allOn}" title="이 구 전체 선택/해제">구 전체</button>${cnt(g)}</div>
   ${open.has(gu)?`<div class="dongs">${Object.entries(g.dongs).sort((a,b)=>b[1].b-a[1].b||b[1].n-a[1].n).map(([cd,d])=>`<button data-cd="${cd}" aria-pressed="${S.hj.has(cd)}" title="파랑 ${d.b} · 노랑 ${d.y} · 빨강 ${d.r}">${d.nm} <span class="small">${d.n}</span>${d.b?`<i class="st-blue"></i>`:''}${d.y?`<i class="st-yellow"></i>`:''}</button>`).join('')}</div>`:''}`; }).join('')}`;
  document.getElementById('treeClear').addEventListener('click',()=>{S.hj.clear(); refresh(); VB.x=0;VB.y=0;VB.w=MW;VB.h=MH;setVB();});
  document.querySelectorAll('#tree .gu').forEach(el=>el.addEventListener('click',ev=>{ if(ev.target.classList.contains('pick')) return; const gu=el.dataset.gu; if(open.has(gu)) open.delete(gu); else open.add(gu); renderTree(); }));
  document.querySelectorAll('#tree .pick').forEach(el=>el.addEventListener('click',ev=>{ ev.stopPropagation(); const gu=el.dataset.gu; const cds=Object.keys(byGu[gu].dongs); const allOn=cds.every(cd=>S.hj.has(cd)); cds.forEach(cd=>allOn?S.hj.delete(cd):S.hj.add(cd)); S.listLimit=60; afterRegionChange(); }));
  document.querySelectorAll('#tree .dongs button').forEach(el=>el.addEventListener('click',()=>toggleDong(el.dataset.cd)));
}

"""
s = s[:start] + newmap + s[end:]
s = s.replace("  document.querelectorAll;\n", "")
# refresh also renders tree
s = s.replace("function refresh(){ evalAll(); drawMarkers(); renderList(); if(S.selected) renderDetail(); renderCalc(); renderReport(); }",
              "function refresh(){ evalAll(); drawMarkers(); renderTree(); renderList(); if(S.selected) renderDetail(); renderCalc(); renderReport(); }")
# reset button also clears hj
s = s.replace("document.getElementById('nlReset').addEventListener('click',()=>{Object.assign(S,{", "document.getElementById('nlReset').addEventListener('click',()=>{S.hj.clear(); Object.assign(S,{")
# zoom presets sizes for new aspect
s = s.replace("document.getElementById('zAll').addEventListener('click',()=>{VB.x=0;VB.y=0;VB.w=1000;VB.h=1000;setVB();});", "document.getElementById('zAll').addEventListener('click',()=>{VB.x=0;VB.y=0;VB.w=MW;VB.h=MH;setVB();});")
s = s.replace("document.getElementById('zIn').addEventListener('click',()=>{const cx=VB.x+VB.w/2,cy=VB.y+VB.h/2;VB.w*=0.7;VB.h=VB.w;VB.x=cx-VB.w/2;VB.y=cy-VB.h/2;setVB();});", "document.getElementById('zIn').addEventListener('click',()=>{const cx=VB.x+VB.w/2,cy=VB.y+VB.h/2;VB.w*=0.7;VB.h=VB.w*MH/MW;VB.x=cx-VB.w/2;VB.y=cy-VB.h/2;setVB();});")
s = s.replace("document.getElementById('zOut').addEventListener('click',()=>{const cx=VB.x+VB.w/2,cy=VB.y+VB.h/2;VB.w=Math.min(1400,VB.w/0.7);VB.h=VB.w;VB.x=cx-VB.w/2;VB.y=cy-VB.h/2;setVB();});", "document.getElementById('zOut').addEventListener('click',()=>{const cx=VB.x+VB.w/2,cy=VB.y+VB.h/2;VB.w=Math.min(1600,VB.w/0.7);VB.h=VB.w*MH/MW;VB.x=cx-VB.w/2;VB.y=cy-VB.h/2;setVB();});")
# detail: add station + hj line
s = s.replace("""     <dt>준공 · 세대</dt>""", """     <dt>준공 · 세대</dt>""")
s = s.replace("""<span class="small">${c.sgg} ${c.dong}${c.road&&c.road!=='-'?' · '+c.road:''} · ${c.built||'?'}년 · ${c.units?c.units.toLocaleString()+'세대':'세대수 미확인'}${c.approx?' · <b>위치 근사</b>':''}</span></div>""",
"""<span class="small">${c.sggnm||c.sgg} ${c.hj||c.dong}${c.hj&&c.hj!==c.dong?' (법정동 '+c.dong+')':''}${c.road&&c.road!=='-'?' · '+c.road:''} · ${c.built||'?'}년 · ${c.units?c.units.toLocaleString()+'세대':'세대수 미확인'}${c.st?` · 가까운 역 ${c.st[0]} ${Math.round(c.st[1]*1000)}m`:''}${c.approx?' · <b>위치 근사</b>':''}</span></div>
  <div class="tr small" style="margin:2px 0 6px">${traits(c,e).map(x=>`<span style="display:inline-block;margin-right:8px">· ${x}</span>`).join('')}</div>""")
# list item shows 행정동
s = s.replace("""<div class="m">${h.sgg} ${h.dong} · ${h.built||'?'}년""", """<div class="m">${(h.sggnm||h.sgg).replace('수원시 ','').replace('용인시 ','').replace('화성시 ','')} ${h.hj||h.dong} · ${h.built||'?'}년""")
# init: drawMap needs MAPDATA; tree render after refresh — already in refresh. Also hide tip on scroll
s = s.replace("drawMap(); renderFacts(); refresh();", "drawMap(); renderFacts(); refresh(); window.addEventListener('scroll',hideTip,{passive:true});")
open(p, "w", encoding="utf-8").write(s)
print("patched", len(s))
