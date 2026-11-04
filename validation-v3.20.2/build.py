from pathlib import Path
import json,re,hashlib,shutil
v=Path(__file__).parent;base=Path('/workspace/little-tone-v3.20.1-web');out=Path('/workspace/little-tone-v3.20.2-web');out.mkdir(exist_ok=True);shutil.copytree(base,out,dirs_exist_ok=True)
app=next(base.glob('app-*.js'));s=app.read_text();meta,rest=s.split('\n',1);m=json.loads(meta[len('window.GameBuild=Object.freeze('):-2]);m['version']='3.20.2';m['schema']['version']=25;s='window.GameBuild=Object.freeze('+json.dumps(m,ensure_ascii=False,separators=(',',':'))+');\n'+rest
def exact(a,b,n=1):
 global s
 if s.count(a)!=n:raise Exception(('match',a[:100],s.count(a),n))
 s=s.replace(a,b)
def span(code,name):
 a=re.search(r'^function '+name+r'\(',code,re.M).start();le=code.index('\n',a);b=le if code[a:le].rstrip().endswith('}')else le+re.search(r'^}',code[le:],re.M).end();return a,b
def fn(name,body):
 global s
 a,b=span(s,name);s=s[:a]+body+s[b:]
exact('    if(version<24)rules.migrateVIP?.(v);','    if(version<25)rules.migrateVIP?.(v,version);')
exact('function migrateVIPSave(v){','function migrateLegacyVIPSave(v){')
patch=(v/'patch.js').read_text()
replaced=['beginVIPEdit','finishVIPEdit','selectVIPTile','drawVIPDraft','setVIPDisplay','vipOffers','openVIPDisplays','sellFurniture','vipStaffHome','cachedVIPRequirements','updateVIPEmployee','tryRest','updateRest','finishRest','drawSeatedCustomer','drawVIP','updateVIP']
for name in replaced:
 a,b=span(patch,name);body=patch[a:b];fn(name,body);patch=patch[:a]+patch[b:]
exact('// SOURCE: core/state',patch+'\n// SOURCE: core/state')
s=s.replace('z.w<4||z.h<4||z.w>8||z.h>8||z.x<0','z.w!==8||z.h!==8||z.x<0',1)
s=s.replace('vipEditor=false,vipAnchor=null,workshopDraft','vipEditor=false,workshopDraft').replace('vipAnchor=null;','')
exact('function resetInteractionState() {','function resetInteractionState() {\n vipEmployeeActor=null;document.body.classList.remove(\'vip-editing\');')
exact("function vipLeave(g,result){g.state='leave';","function vipLeave(g,result){delete g.seatPhase;delete g.seated;g.state='leave';")
# Reserved stock is drawn directly from the instrument assigned to this case.
exact('item,base,S.stock[base]]','item,base]')
exact("if(item||Number.isInteger(base)&&S.stock[base]>0)","if(item||Number.isInteger(base))")
# The base save validator keeps legacy shapes readable; active seat state uses the new rules.
exact(' validateVIPExtras(v,s,rules);',' validateVIPExtras(v,s,rules);\n validateNewVIPState(v,s);')
# Preserve correct active seat paths when older saves need ordinary route repair.
exact("    if (p.companion) {\n      p.path = [];", "    if(p.state==='rest'&&['enter','sitting','rise','exit'].includes(p.seatPhase))continue;\n    if (p.companion) {\n      p.path = [];")
# Inventory labels separate available warehouse stock from assigned VIP stock.
exact("'재고 '+S.stock[i]+' · '","stockLabel(i)+' · '",2)
exact("stock?.classList.toggle('low',S.stock[i]<=2)","stock?.classList.toggle('low',stockCount(i)<=2)")
exact("${S.stock[i]<=2?'low':''}","${stockCount(i)<=2?'low':''}")
exact("if(stockStatus==='soldout')return S.stock[i]===0;","if(stockStatus==='soldout')return stockCount(i)===0;")
exact('    if(S.stock[i]>2)return false;','    if(stockCount(i)>2)return false;')
exact("if (S.stock[i] === 0) toast(","if (stockCount(i) === 0) toast(")
exact("else if (S.stock[i] === 2) toast(","else if (stockCount(i) === 2) toast(")
exact("(S.stock[i] === 0 ? '품절' : S.stock[i] <= 2 ? '재고 부족' : '판매 준비')","(stockCount(i) === 0 ? '품절' : stockCount(i) <= 2 ? '재고 부족' : '판매 준비')")
exact("${S.stock[i] === 0 ? '품절' : S.stock[i] + '개 남음'}","${stockCount(i) === 0 ? '품절' : stockCount(i) + '개 남음'}")
exact("<small>재고 ${S.stock[i]} · ${incomingQuantity(i)?deliveryText(i):'입고 예정 0'}</small>","<small>${stockLabel(i)} · ${incomingQuantity(i)?deliveryText(i):'입고 예정 0'}</small>")
# Failed dropdown changes must immediately restore the actual assigned instrument.
exact("if(!setVIPDisplay(id,slot,e.target.value===''?null:Number(e.target.value)))toast('영업 준비 중 VIP 구역 안에서 변경할 수 있어요.');", "if(!setVIPDisplay(id,slot,e.target.value===''?null:Number(e.target.value)))toast(S.phase!=='prepare'?'영업 준비 중에 변경할 수 있어요.':'진열할 보관 재고와 VIP 구역을 확인해주세요.');openVIPDisplays();")
exact('  TierNames,VIPStaff,','  stockCount,stockLabel,vipReservedCount,vipDeskCandidates,vipDeskFor,advanceSeating,drawVIP,\n  TierNames,VIPStaff,')
exact('  Atelier,saveRules,','  zoneDraft:()=>vipZoneDraft,\n  Atelier,saveRules,')
# Current design instructions now ask for one anchor click, not two corners.
s=s.replace('원하는 위치에 8×8칸으로 지정하세요.','크기는 8×8 고정 · 기준 타일을 한 번 선택하세요.').replace('위치 · 크기 다시 지정','위치 다시 지정')
for p in out.glob('app-*.js'):p.unlink()
name='app-'+hashlib.sha256(s.encode()).hexdigest()[:12]+'.js';(out/name).write_text(s);(v/'app.js').write_text(s)
style=next(base.glob('style-*.css'));css=style.read_text()+'\n'+(v/'style.css').read_text();cssname='style-'+hashlib.sha256(css.encode()).hexdigest()[:12]+'.css'
for p in out.glob('style-*.css'):p.unlink()
(out/cssname).write_text(css)
html=(base/'index.html').read_text().replace(app.name,name).replace(style.name,cssname);(out/'index.html').write_text(html)
print(name,'schema25')
