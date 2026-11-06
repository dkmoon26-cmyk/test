from pathlib import Path
import json,re,hashlib,shutil,subprocess
from spans import span
v=Path(__file__).parent;base=Path('/workspace/little-tone-v3.24.0-web');out=Path('/workspace/little-tone-v3.25.0-web');shutil.copytree(base,out,dirs_exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()[:12]
s=next(base.glob('app-*.js')).read_text();meta=json.loads(s.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);meta['version']='3.25.0';meta['schema']['version']=30;s='window.GameBuild=Object.freeze('+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+');\n'+s.split('\n',1)[1]
def exact(a,b,n=None):
 global s
 assert a in s,a[:90]
 if n is not None:assert s.count(a)==n,(a,s.count(a))
 s=s.replace(a,b)
exact('initialStock: [3, 3, 3, ...Array(26).fill(0)]','initialStock: [3, 3, 3, ...Array(30).fill(0)]')
# Existing product and fixture IDs remain unchanged. New records append.
data="""
const LegacyCosts25={17:4400000,18:5200000,23:4700000,28:4800000};
for(const [id,cost,price]of [[17,10000000,15000000],[23,11500000,17000000],[28,13000000,19000000],[18,14000000,21000000]])Object.assign(products[id],{cost,price});
products[27].tag='최고급 어쿠스틱 · 시더 그랜드';
products.push(
{id:29,key:'BLACK_ORCHID',name:'블랙 오키드',family:'electric',kind:'instrument',tag:'명품 할로우 기타',unlock:5,cost:15500000,price:23000000,color:'#24252b'},
{id:30,key:'AURORA_BURL_6',name:'오로라 버얼 6',family:'bass',kind:'instrument',tag:'명품 6현 베이스',unlock:5,cost:16500000,price:25000000,color:'#478c9c'},
{id:31,key:'ROYAL_SWAN',name:'로열 스완',family:'acoustic',kind:'instrument',tag:'명품 화이트 펄 어쿠스틱',unlock:5,cost:18000000,price:27000000,color:'#eee5d5'},
{id:32,key:'RED_PHOENIX',name:'레드 피닉스',family:'electric',kind:'instrument',tag:'명품 V형 기타',unlock:5,cost:19500000,price:29000000,color:'#9d2938'});
types.push({id:17,key:'SMALL_PLANT',name:'화분',cost:80000,icon:'❧',w:45,h:35},{id:18,key:'SMALL_AQUARIUM',name:'작은 수족관',cost:200000,icon:'◇',w:55,h:55},{id:19,key:'SMALL_TREE',name:'작은 나무',cost:120000,icon:'❧',w:48,h:58});
types[15].name='명품 진열대';
"""
exact("types[12].w=200;","types[12].w=200;\n"+data)
# Both display types share the smaller walnut case geometry and instrument projection.
a,b=span(s,'loungeFurnitureSprite');case=s[a:b]
case=case.replace("if(f.t!==12)return legacyLoungeFurnitureSprite(f);", "if(![12,15].includes(f.t))return legacyLoungeFurnitureSprite(f);")
case=case.replace("item=S.custom.items.find(i=>i.displayId===f.id)", "item=f.t===15?(Number.isInteger(f.vipSlots?.[0])?{base:f.vipSlots[0]}:null):S.custom.items.find(i=>i.displayId===f.id)")
case=case.replace("['v23',dir", "['v25',f.t,dir")
case=case.replace("miniCustom(c,item,58,dir>=2);", "if(f.t===15)drawProduct(c,item.base,-14,-58,28,58,dir>=2,true);else miniCustom(c,item,58,dir>=2);")
case=case.replace("[0,2].includes(dir)?.5:0", "[0,2].includes(dir)?(f.t===15?1:.5):0").replace("[1,3].includes(dir)?.5:0", "[1,3].includes(dir)?(f.t===15?1:.5):0")
s=s[:a]+case+s[b:]
exact("if(designEditor){e.preventDefault();e.stopImmediatePropagation();}","if(designEditor&&!(designEditor.kind==='art'&&designEditor.moving)){e.preventDefault();e.stopImmediatePropagation();}")
for name in ['quantityControl','orderProduct','deliverOrders','validateExpansionSave','furnitureAssetKeys','furnitureSprite','designTargetAt','designQuote','updateStaffAnimation','updateVIPEmployee']:
 exact('function '+name+'(','function before25'+name[0].upper()+name[1:]+'(')
patch=(v/'patch.js').read_text()
for name in re.findall(r'^function (\w+)\(',patch,re.M):
 if 'function '+name+'(' in s:
  a,b=span(patch,name);x,y=span(s,name);s=s[:x]+patch[a:b]+'\n'+s[y:];patch=patch[:a]+patch[b:]
# Two views packed for each item, fully transparent atlas sheets.
art=json.loads((v/'art.json').read_text());assets={};instrument={};greenery=[];ids=[17,18,23,32,29,30,31]
for kind,cols in [('luxury',7),('greenery',3)]:
 for col in range(cols):
  a,b=art[kind][0][col],art[kind][1][col];name=f'{kind}-{col}-v3250';p=v/(name+'.webp')
  subprocess.run(['convert',str(v/a['file']),str(v/b['file']),'-background','none','-gravity','center','-append','-define','webp:lossless=true',str(p)],check=True)
  w=max(a['w'],b['w']);clips=[[int((w-a['w'])/2),0,a['w'],a['h']],[int((w-b['w'])/2),a['h'],b['w'],b['h']]]
  key='assets/'+name+'.webp';target=name+'-'+sha(p.read_bytes())+'.webp';shutil.copy2(p,out/'assets'/target);assets[key]='assets/'+target
  if kind=='luxury':instrument[ids[col]]={'atlas':4+col,'clips':clips}
  else:greenery.append({'key':key,'clips':clips})
# Update the sprite data as data, not through a runtime-only alternate preview.
m=re.search(r'const InstrumentArtV340=Object.freeze\((\{.*?\})\);',s);defs=json.loads(m[1]);defs.update({str(k):value for k,value in instrument.items()});s=s[:m.start()]+"const InstrumentArtV340=Object.freeze("+json.dumps(defs,separators=(',',':'))+");"+s[m.end():]
exact("instrumentAtlases.push(runtimeImage('assets/acoustics-v3200.webp'));","instrumentAtlases.push(runtimeImage('assets/acoustics-v3200.webp'));for(let i=0;i<7;i++)instrumentAtlases.push(runtimeImage('assets/luxury-'+i+'-v3250.webp'));")
# Precomputed custom recolour masks: no pixel reads at runtime for the added art.
coverage={}
for col,baseid in enumerate(ids):
 for rear in [0,1]:
  a=art['luxury'][rear][col];raw=subprocess.check_output(['convert',str(v/a['file']),'-depth','8','rgba:-']);rows=[];w=a['w'];h=a['h']
  for y in range(int(h*.43),h):
   runs=[];start=None
   for x in range(w+1):
    if x<w:
     r,g,b,alpha=raw[(y*w+x)*4:(y*w+x)*4+4];solid=alpha>128 and not(baseid not in (23,31) and min(r,g,b)>175 and max(r,g,b)-min(r,g,b)<65) and not(r>150 and g>105 and b<g*.8)
    else:solid=False
    if solid and start is None:start=x
    if not solid and start is not None:runs.extend([start,x-start]);start=None
   if runs:rows.append([y,runs])
  coverage[f'{baseid}:{rear}']={'w':w,'h':h,'rows':rows}
# Assignment follows the existing coverage declaration, before the first game frame.
marker='const customCoverageCache=';pos=s.index(marker);s=s[:pos]+'Object.assign(CustomCoverage,'+json.dumps(coverage,separators=(',',':'))+');\n'+s[pos:]
declarations="\nAtelier.profiles.forEach((p,i)=>{p.budget=[30000000,35000000,40000000,45000000,50000000,50000000][i];});\nconst Greenery25="+json.dumps(greenery,separators=(',',':'))+';\nlet greeneryAtlas25=[];\n'
exact('// SOURCE: core/state',patch+declarations+'\n// SOURCE: core/state')
exact('migrate24,','migrate24,migrate25,',1)
exact('    if(version<29)rules.migrate24?.(v,version);','    if(version<29)rules.migrate24?.(v,version);\n    if(version<30)rules.migrate25?.(v,version);')
# Append-only migration precedes every strict catalogue-length check.
exact("!Number.isInteger(r.affinityGain*2)","Math.abs(r.affinityGain*10-Math.round(r.affinityGain*10))>1e-7")
exact('vip.sales>vip.visits','vip.sales>vip.visits*2')
exact("i.slot>=Math.floor((size[i.wall==='x'?0:1]-1)/2)","i.slot>=size[i.wall==='x'?0:1]")
exact("max=Math.floor(((wall==='x'?N:M)-1)/2)","max=wall==='x'?N:M")
# Persist historical craft cost instead of retroactively charging the new model cost.
exact('day:raw.day,madeLevel:level};','day:raw.day,madeLevel:level,pricingVersion:raw.pricingVersion??30};')
exact('!p||p.unlock>s.stage||!Number.isInteger(level)',"!p||p.unlock>s.stage||raw.pricingVersion!==undefined&&![29,30].includes(raw.pricingVersion)||!Number.isInteger(level)")
# New customers can briefly look at nearby props while keeping their existing browse state.
exact('    if(updateRest(p,dt))continue;','    if(updateRest(p,dt))continue;\n    if(updateDecorView25(p,dt)||maybeDecorView25(p))continue;')
# Make the actual model-wide draw path use the precomputed masks for new sprites.
exact("if(CustomCoverage[key])return legacyMakeCustomMask(W,H,rear,bass,base);","if(CustomCoverage[key])return legacyMakeCustomMask(W,H,rear,bass,base);")
exact('if(!assetGate(criticalAssetKeys(),continueGame))return false;',"if(!assetGate(criticalAssetKeys(),continueGame,'가게에 다시 선율이 흐를 준비를 하고 있어요…'))return false;")
# Luxury keeps one owned unit, including allocated displays, even under automatic orders.
a,b=span(s,'staffOrderPlan');plan=s[a:b].replace('const quantity = rule.quantity','const quantity = isVIPProduct(i)?1:rule.quantity').replace("else if (incomingQuantity(i)>0)","else if (isVIPProduct(i)&&stockCount(i)>0) reason='재고 충분';\n    else if (incomingQuantity(i)>0)")
s=s[:a]+plan+s[b:]
exact('if(stockCount(i)>2)return false;','if(stockCount(i)>(isVIPProduct(i)?0:2))return false;')
exact('max="999" data-staff-quantity="${i}"','max="${isVIPProduct(i)?1:999}" ${isVIPProduct(i)?\'readonly\':\'\'} data-staff-quantity="${i}"')
exact('value="${S.staffPolicy.products[i].quantity}"','value="${isVIPProduct(i)?1:S.staffPolicy.products[i].quantity}"')
# Policy recommendation for luxury stays one unit with a zero-stock reorder point.
# Initial and saved stock policy settings are otherwise preserved.
exact("const key=JSON.stringify([S.stage,N,M,ENTRY,S.vip.zone,S.vip.hired", "const key=JSON.stringify([S.stage,N,M,ENTRY,S.vip.zone,S.vip.hired")
exact("sceneCacheKey='';renderDirty=true;clearFurniturePickCache();clearFurnitureBodyCache();","sceneCacheKey='';renderDirty=true;clearFurniturePickCache();clearFurnitureBodyCache();premiumCaseCache.clear();loungeSpriteCache.clear();atelierSprites.clear();customTextureCache.clear();premiumTextureCache.clear();customCoverageCache.clear();")
# Expose the real common paths to validation and UI.
exact('  calendar24,ensureCalendar24,','  autoFillVIP25,pickVIP25,payVIP25,hitWall25,maybeDecorView25,updateDecorView25,updateStaffAnimation,\n  calendar24,ensureCalendar24,')
events=(v/'events.js').read_text();pos=s.rfind('})();');s=s[:pos]+events+'\n'+s[pos:]
# Update old labels throughout the UI.
s=s.replace('최고급·명품','명품').replace('최고급 이상은 VIP실','명품은 VIP실')
for p in out.glob('app-*.js'):p.unlink()
appname='app-'+sha(s.encode())+'.js';(out/appname).write_text(s);(v/'app.js').write_text(s)
# Stable canvas identities survive lazy atlas repacking; game references never point at cleared images.
b=next(base.glob('boot-*.js')).read_text()
b=b.replace("records.set(key,{key,image:new Image(),state:'idle',priority:2,waiters:[],starts:0});","{const image=document.createElement('canvas'),r={key,image,download:new Image(),state:'idle',priority:2,waiters:[],starts:0};Object.defineProperties(image,{naturalWidth:{get:()=>r.state==='ready'?image.width:0},naturalHeight:{get:()=>r.state==='ready'?image.height:0},complete:{get:()=>r.state==='ready'}});records.set(key,r);}")
start=b.index('    if(!err){try{');end=b.index('    active--;',start)
b=b[:start]+"    if(!err){try{const plan=window.GameAtlasPacking?.[r.key],original=r.download,c=r.image;c.width=plan?.width??original.naturalWidth;c.height=plan?.height??original.naturalHeight;const cx=c.getContext('2d');if(plan){for(const region of plan.regions)cx.drawImage(original,...region.source,...region.target,region.source[2],region.source[3]);}else cx.drawImage(original,0,0);original.onload=null;original.onerror=null;original.src='';}catch{err=new Error('이미지를 준비하지 못했어요.');}}\n"+b[end:]
b=b.replace('if(r.image.decode)await r.image.decode();','if(r.download.decode)await r.download.decode();').replace('next.image.onload','next.download.onload').replace('next.image.onerror','next.download.onerror').replace('next.image.src','next.download.src')
for p in out.glob('boot-*.js'):p.unlink()
bootname='boot-'+sha(b.encode())+'.js';(out/bootname).write_text(b)
html=(base/'index.html').read_text().replace(next(base.glob('app-*.js')).name,appname).replace(next(base.glob('boot-*.js')).name,bootname).replace('v3.24.0','v3.25.0')
html=html.replace('window.GameAssets=Object.freeze({','window.GameAssets=Object.freeze({'+','.join(json.dumps(k)+':'+json.dumps(value) for k,value in assets.items())+',')
css=next(base.glob('style-*.css')).read_text()+'\n'+(v/'style.css').read_text();cssname='style-'+sha(css.encode())+'.css'
for p in out.glob('style-*.css'):p.unlink()
(out/cssname).write_text(css);html=html.replace(next(base.glob('style-*.css')).name,cssname);(out/'index.html').write_text(html)
print(appname,bootname,cssname)
