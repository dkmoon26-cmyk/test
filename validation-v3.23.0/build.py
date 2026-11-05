from pathlib import Path
import re,json,hashlib,shutil
from spans import span
v=Path(__file__).parent;base=Path('/workspace/little-tone-v3.22.0-web');out=Path('/workspace/little-tone-v3.23.0-web')
shutil.copytree(base,out,dirs_exist_ok=True)
oldapp=next(base.glob('app-*.js'));s=oldapp.read_text();meta=json.loads(s.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);meta['version']='3.23.0';meta['schema']['version']=28;s='window.GameBuild=Object.freeze('+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+');\n'+s.split('\n',1)[1]
def exact(a,b):
 global s
 assert a in s,a[:120]
 s=s.replace(a,b)
# Wrap baseline behavior where a narrow extension is safer than replacing it.
for name in ['valid','resizeShop','syncEntrance','spawn','refreshLivePanel','wallArtThumb','validateExpansionSave','openMenuSection','criticalAssetKeys']:
 exact('function '+name+'(','function before23'+name[0].upper()+name[1:]+'(')
patch=(v/'patch.js').read_text()
for name in re.findall(r'^function (\w+)\(',patch,re.M):
 if 'function '+name+'(' in s:
  a,b=span(patch,name);x,y=span(s,name);s=s[:x]+patch[a:b]+'\n'+s[y:];patch=patch[:a]+patch[b:]
exact('// SOURCE: core/state',patch+'\n// SOURCE: core/state')
exact("shop:[['영업','business'],['직원','employees'],['미션','missions'],['기록','records']]","shop:[['영업','business'],['직원','employees'],['미션','missions']]")
exact("['이야기','stories'],",'')
exact('z.w>8||z.h>8','z.w>10||z.h>10')
exact('VIP 구역 8×8을 지정하세요','VIP구역을 드래그로 지정하세요')
# Two tile custom cases, preserve compact old single-tile cases.
exact('length:3},(_,n)=>({x:f.x+', 'length:f.t===12?2:3},(_,n)=>({x:f.x+')
exact("wide=[12,15].includes(f.t)&&!f.legacyCompact;return {x:f.x+dx+(wide&&[0,2].includes(d)?1:0),y:f.y+dy+(wide&&[1,3].includes(d)?1:0)}", "wide=[12,15].includes(f.t)&&!f.legacyCompact,offset=f.t===12?.5:1;return {x:f.x+dx+(wide&&[0,2].includes(d)?offset:0),y:f.y+dy+(wide&&[1,3].includes(d)?offset:0)}")
# Path targets must be integer cells; custom frontage uses first of two cells.
exact('offset=f.t===12?.5:1','offset=1')
exact('  root.Interior = Interior;', '  Interior.facade=facade;root.Interior = Interior;')
exact("  Interior.front(ctx, P, ENTRY, doorOpen, S.shopName, N, M, ['open', 'closing'].includes(S.phase));",'  drawStoreFront();')
exact('    ...vipPartitions(),',"    ...vipPartitions(),...(S.entrances??defaultEntrances()).filter(e=>['top','left'].includes(e.side)).map(e=>{const p=entrancePoint(e);return {depth:p.x+p.y-.2,draw:()=>drawStoreDoor(e)};}),")
exact('  drawVIPDraft();drawBenchBadges();','  drawVIPDraft();drawEntranceDraft();drawBenchBadges();')
# Outside path bases follow the actual entry, not a fixed wall.
exact('base = outside ? ENTRY : start,','base = outside ? entryForPoint(start) : start,')
# Preserve geometry while changing the active entrance just for a spawn.
exact('const out = path(p, ENTRY);\n  p.path = out ? [...out, exitPoint()] : [];','const e=nearestEntrance(p),out=path(p,e);\n  p.path = out ? [...out, exitFor(e)] : [];')
exact("g.path=[...(vipPath(g,ENTRY)??[]),exitPoint()]", "g.path=[...(vipPath(g,nearestEntrance(g,true))??[]),exitFor(nearestEntrance(g,true))]")
# Cache keyed by design changes and entry geometry.
exact('    S.phase\n  ].join', '    S.phase,JSON.stringify(S.entrances),JSON.stringify(S.design),vipEditor,JSON.stringify(vipZoneDraft),JSON.stringify(entranceDraft)\n  ].join')
exact("if(vipEditor){e.stopImmediatePropagation();selectVIPTile(tileAt(e));return;}","if(vipEditor||entranceEditor!==null){e.stopImmediatePropagation();return;}")
exact("if(wasDragged||editing!==null||vipEditor)return;", "if(wasDragged||editing!==null||vipEditor||entranceEditor!==null)return;")
exact("return !!designEditor||$('catalogDetail')?.open||vipEditor ||", "return entranceEditor!==null||!!designEditor||$('catalogDetail')?.open||vipEditor ||")
# Settings retain save/audio controls, while historical statistics live nowhere in this UI.
a=s.index("    h = staffManagementShortcut()+`<span class=\"eyebrow\">");b=s.index('    h += `<details class=\"operation-card\">',a)
s=s[:a]+"    h = '<h2>설정</h2>';\n"+s[b:]
exact("report:'운영 기록 · 설정'","report:'설정'")
exact("(tab === 'shop' ? '<div id=\"liveStockWarning\">'+stockWarning()+'</div>' : '') + h",'h')
# Remove stock-state dropdown, reset filter to all on entering stock page.
a=s.index('    h+=`<label class="stock-status-filter">');b=s.index('`;\n',a)+3;s=s[:a]+s[b:]
exact("stockFilter={instruments:'instrument',effects:'effect',supplies:'strings'}[section];", "stockStatus='all';stockFilter={instruments:'instrument',effects:'effect',supplies:'strings'}[section];")
# Dynamic rectangular VIP wall hit-testing and stored material keys.
exact("n<8;n++){if(side===z.doorSide", "n<(['left','right'].includes(side)?z.h:z.w);n++){if(side===z.doorSide")
exact("?Stages[stage].h:8)", "?Stages[stage].h:10)")
# Show the same centered art geometry during construction and after placement.
# Include high-resolution atlas assets in initial loading to prevent placeholders after install.
# New public review hooks and initialization.
exact('  InteriorCatalog,beginDesignEdit,', '  entrancePoints,setEntrance,beginEntranceEdit,finishEntranceEdit,entranceAt,entryForPoint,nearestEntrance,exitFor,materialTexture,\n  InteriorCatalog,beginDesignEdit,')
pos=s.rfind('})();');s=s[:pos]+(v/'events.js').read_text()+'\n'+s[pos:]
html=(base/'index.html').read_text().replace('v3.22.0','v3.23.0')
for key,filename in [('materials','materials.webp'),('props','props.webp')]:
 data=(v/filename).read_bytes();name=key+'-v3230-'+hashlib.sha256(data).hexdigest()[:12]+'.webp';(out/'assets'/name).write_bytes(data);html=html.replace('window.GameAssets=Object.freeze({','window.GameAssets=Object.freeze({'+json.dumps('assets/'+key+'-v3230.webp')+':'+json.dumps('assets/'+name)+',')
for p in out.glob('app-*.js'):p.unlink()
appname='app-'+hashlib.sha256(s.encode()).hexdigest()[:12]+'.js';(out/appname).write_text(s);(v/'app.js').write_text(s);html=html.replace(oldapp.name,appname)
cssold=next(base.glob('style-*.css'));css=cssold.read_text()+'\n'+(v/'style.css').read_text();cssname='style-'+hashlib.sha256(css.encode()).hexdigest()[:12]+'.css'
for p in out.glob('style-*.css'):p.unlink()
(out/cssname).write_text(css);html=html.replace(cssold.name,cssname);(out/'index.html').write_text(html)
print(appname,cssname)
