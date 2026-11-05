from pathlib import Path
import json,re,hashlib,shutil
v=Path(__file__).parent;base=Path('/workspace/little-tone-v3.20.2-web');out=Path('/workspace/little-tone-v3.21.0-web');shutil.copytree(base,out,dirs_exist_ok=True)
a=next(base.glob('app-*.js'));s=a.read_text();first,rest=s.split('\n',1);meta=json.loads(first[len('window.GameBuild=Object.freeze('):-2]);meta['version']='3.21.0';meta['schema']['version']=26;s='window.GameBuild=Object.freeze('+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+');\n'+rest
# Exact replacements fail fast if the baseline changes.
def exact(old,new,n=1):
 global s
 assert s.count(old)==n,(old[:90],s.count(old),n)
 s=s.replace(old,new)
def span(code,name):
 a=re.search(r'^function '+name+r'\(',code,re.M).start();line=code.index('\n',a)
 if name=='renderInterior' and not code[a:line].rstrip().endswith('}'):return a,line+re.search(r'^function ',code[line:],re.M).start()
 b=line if code[a:line].rstrip().endswith('}')else line+re.search(r'^}',code[line:],re.M).end();return a,b
def fn(name,body):
 global s
 a,b=span(s,name);s=s[:a]+body+'\n'+s[b:]
patch=(v/'patch.js').read_text()
for name in ['paintInteriorFloor','renderInterior','addWallItem','vipStatusHTML','vipGuestCards','furnitureCategory','drawVIP']:
 a1,b1=span(patch,name);fn(name,patch[a1:b1]);patch=patch[:a1]+patch[b1:]
# Catalog replaces only the furniture page, preserving installed furniture actions separately.
a1=s.index("  if (tab === 'furniture') {",s.index('function renderPanel()'));b1=s.index("  } else if (tab === 'stock') {",a1)
old=s[a1:b1];sa=old.index('    if (selected) {');sb=old.index("    if (!selected && furnitureView === 'placed')",sa)
selected=old[sa:sb];patch+='\nfunction installedFurnitureDetail(){let h=\'\';\n'+selected+'\nreturn h;}\n'
s=s[:a1]+"  if (tab === 'furniture') {\n    h=furnitureCatalogHTML();\n"+s[b1:]
exact("// SOURCE: core/state",patch+'\n// SOURCE: core/state')
# Save extensions and real fractional affinity increments.
exact("(p.basket ?? []).length > 2", "((p.basket ?? []).length > rules.productCount || new Set(p.basket??[]).size!==(p.basket??[]).length)")
exact("![r.affinityDay, r.affinityGain, r.lastStockoutDay, r.stockoutStreak].every(integer)","(![r.affinityDay,r.lastStockoutDay,r.stockoutStreak].every(integer)||!Number.isFinite(r.affinityGain)||r.affinityGain<0||!Number.isInteger(r.affinityGain*2))")
exact("    purchase: 5,\n    premiumPurchase: 8,\n    preference: 2,","    purchase: 2.5,\n    premiumPurchase: 4,\n    preference: 1,")
exact("    request: 3,\n    dailyCap: 10,","    request: 1.5,\n    dailyCap: 5,")
exact("    Config.affinity.dailyCap - r.affinityGain,","    Math.max(0,Config.affinity.dailyCap - r.affinityGain),")
exact("if (p.actor !== 9 || p.special || !isRegular(S.customerBook['actor-9'])) return;","if(p.actor!==9||p.special||((S.customerBook['actor-9']?.satisfaction??0)<50&&S.hanaStory.phase!=='delivered'))return;")
exact("hana?.regular && ['locked','delivered']", "hana && (hana.satisfaction>=50||S.hanaStory.phase==='delivered') && ['locked','delivered']")
exact("호감도 100 달성 후 다음 방문", "호감도 50 달성 후 다음 방문")
s=s.replace('하나의 단골 이야기가 열렸어요 · 매장 메뉴','하나의 이야기 시작 · 손님 → 이야기')
exact("!story.startedDay || !s.customerBook['actor-9']?.regular","!story.startedDay || !s.customerBook['actor-9']")
# Allocate a budget at arrival; no arbitrary count cap. Each further instrument is a new 25% choice.
exact("  let list = offers(actor===12?false:Math.random() < 0.35, false);","  if(isRegular(S.customerBook[identity.key]))profile.budget=Math.round(profile.budget*1.5);\n  let list = offers(actor===12?false:Math.random() < 0.35, false);")
exact("  if (!p.basket.includes(p.product)) p.basket.push(p.product);", "  if (!p.basket.includes(p.product)) p.basket.push(p.product);\n  if(chooseRegularExtra(p))return;")
# New data is validated only after old fields are normalized; preserves legacy global skins.
exact(" validateNewVIPState(v,s);"," validateNewVIPState(v,s);\n validateInterior26(v,s);")
# Per-tile wall render overlays behind furniture; preview invalidates background cache.
exact("  paintInteriorFloor();paintWallDecor();","  paintInteriorFloor();paintDesignWalls();paintWallDecor();paintWallItemPreview();")
exact("draw:()=>paintPartition(a,b,door)","draw:()=>paintPartition(a,b,door,side,i)")
exact("function paintPartition(a,b,door){","function paintPartition(a,b,door,side,index){")
exact("const h=28;poly([p,q", "const h=28;poly([p,q") # retained geometry
exact("for(const v of[p,q]){ctx.fillStyle='#8b7048';", "paintVIPWallMaterial(p,q,side,index);for(const v of[p,q]){ctx.fillStyle='#8b7048';")
# Text weight only; preserve bubble dimensions, colors and placement.
exact("function text(s, x, y, size, c, align = 'center') {\n  ctx.font = `${size}px", "function text(s, x, y, size, c, align = 'center',weight=400) {\n  ctx.font = `${weight} ${size}px")
exact("text(s, q.x, q.y - 105 * scale + 15, 9, '#6b7258');","text(s, q.x, q.y - 105 * scale + 15, 9, '#6b7258','center',700);")
# Remove unpaid legacy design mutation paths. All application goes through quote and commit.
start=s.index(" if(el.dataset.design&&");end=s.index(" if(el.id==='wallSide')",start);s=s[:start]+s[end:]
# Legacy wall removal recalls instead of discarding.
exact("S.design.wallItems=S.design.wallItems.filter(i=>i.wall!==wall||i.slot!==+slot);expansionChanged();renderInterior();","recallWallItem(wall,+slot);renderInterior();")
exact("function resetInteractionState() {","function resetInteractionState() {\n resetDesignEditor();")
exact("function gameplayBlocked(){return vipEditor", "function gameplayBlocked(){return !!designEditor||$('catalogDetail')?.open||vipEditor")
exact("function largeMenuOpen(){return [", "function largeMenuOpen(){return $('catalogDetail')?.open||[")
s=s.replace('drawIcons();','drawIcons();drawCatalogPictures();')
# Smaller copy, keep the data people need for a decision.
s=s.replace('드래그해서 회전 · 기존 악기 원본 사용','드래그해서 회전').replace('<small>2D 원본 기반 · 정면 / 뒷면 보기</small>','')
s=s.replace('<small>기본 악기 기준 원가 포함 32% 가산 · 제작비만 현금 차감</small>','').replace('<small>기본 악기 원가 포함 · 완료할 때 제작비만 차감</small>','')
s=s.replace('<small>옵션 변경과 회전은 무료 · 완성품 최대 12개 보관</small>','<small>보관 ${S.custom.items.length}/12</small>')
s=s.replace("'<p>모든 제작 옵션을 사용할 수 있어요.</p>'","''")
s=s.replace("'<p class=\"sub\">완성 악기는 커스텀 전용 진열대에 1개씩 가로로 놓을 수 있어요.</p>'","'<p class=\"sub\">완성 악기 없음</p>'")
s=s.replace("${l===1?'일반급 악기 · 월넛 · 노이즈리스 · 블랙 · 글로스':'모든 등급 · 마호가니 · 액티브 · 골드 · 에이징'} 추가","${l===1?'일반급 · 옵션 추가':'모든 등급 · 옵션 추가'}")
s=s.replace('<p>정장 차림으로 입장 안내·시연·상담·결제를 전담해요.</p>','').replace('<small>VIP 직원이 있어야 VIP 영업 가능 · 일반 매장 영업은 별도</small>','')
s=s.replace('입문자 하나의 호감도 50 달성 후 다음 방문에 이야기가 시작돼요.','시작 조건: 호감도 50 · 다음 방문').replace(' · 기한 없이 진행','')
s=s.replace('전달하면 재고를 사용해요. 판매 수익·판매 횟수는 발생하지 않아요.','재고 소모 · 판매 실적 제외').replace('영업 준비 중에 전달할 수 있어요. 기한은 없어요.','영업 준비 중 전달 가능')
s=s.replace('전자드럼 실제 누적 판매 30세트 달성 후, 그날 정산을 마치면 엔딩이 열려요. 엔딩 후에도 계속 운영할 수 있어요.','30세트 판매 후 정산 시 이야기 완료 · 계속 운영 가능')
s=s.replace('서로 다른 악기를 최대 \' + rackLimit() + \'종 진열할 수 있어요. 재고는 창고에서 함께 관리해요.','최대 \' + rackLimit() + \'종 진열')
s=s.replace("<p class=\"regular-letter\">“다시 찾아오고 싶은 가게예요.”</p>",'')
s=s.replace('<div class="note">영업 10:00~20:00 · 하루 약 2분<br>임대료와 직원 일급은 마감 정산 때 한 번 차감돼요.<br>정산은 현금 기준이에요. 주문비는 결제한 날 지출에 포함돼요.</div>','<details class="operation-card"><summary>운영 규칙</summary><p>10:00~20:00 · 하루 약 2분</p><p>임대료·일급은 마감 시 차감 · 주문비는 결제일 지출</p></details>')
s=s.replace("'<h2 class=\"stock-heading\">상품 구매</h2><p class=\"stock-intro\">준비 중 예약하면 오늘 15시, 영업 중 예약하면 내일 오픈 전에 입고돼요.</p>'", "'<h2 class=\"stock-heading\">상품 구매</h2>'+(products.some((p,i)=>delayedProduct(i)&&productUnlocked(i)&&p.kind===stockFilter)?'<p class=\"stock-intro\">예약 입고: 준비 중 → 오늘 15시 · 영업 중 → 다음 날 오픈 전</p>':'')")
exact("p.kind === 'instrument' && p.family!=='drums' && (rackFilter","p.kind === 'instrument' && !isVIPProduct(i) && p.family!=='drums' && (rackFilter")
# Normal rack cannot list VIP-only models. Hide quantity controls unless ordering a shortage.
exact("${quantityControl(i)}<p class=\"closing-warning\"", "${S.stock[i]===0?quantityControl(i):''}<p class=\"closing-warning\"")
# Tutorials must navigate to the new catalog cards rather than removed inline buy buttons.
s=s.replace("document.querySelector('#panel [data-build=\"'+(step===0?1:0)+'\"]')", "document.querySelector('#panel [data-catalog=\"f:'+ (step===0?1:0)+'\"]')")
s=s.replace('#panel [data-build="1"]','#panel [data-catalog="f:1"]').replace('#panel [data-build="0"]','#panel [data-catalog="f:0"]')
# New editor testable API is also used by UI event paths.
exact("  Config,MenuSections,", "  InteriorCatalog,beginDesignEdit,designQuote,commitDesign,resetDesignEditor,selectDesignTargets,designTargetAt,openCatalogDetail,recallWallItem,chooseRegularExtra,recordPurchase,spawn,\n  get designEditor(){return designEditor;},\n  Config,MenuSections,")
# Remove unused stale version label, derive from the one build value at runtime.
pos=s.rfind('})();')
s=s[:pos]+(v/'events.js').read_text()+"\ndocument.querySelector('.title-footer').innerHTML='LITTLE TONE <span>·</span> v'+Config.version;\n"+s[pos:]
for p in out.glob('app-*.js'):p.unlink()
name='app-'+hashlib.sha256(s.encode()).hexdigest()[:12]+'.js';(out/name).write_text(s);(v/'app.js').write_text(s)
c=next(base.glob('style-*.css'));css=c.read_text()+'\n'+(v/'style.css').read_text();cn='style-'+hashlib.sha256(css.encode()).hexdigest()[:12]+'.css'
for p in out.glob('style-*.css'):p.unlink()
(out/cn).write_text(css)
h=(base/'index.html').read_text().replace(a.name,name).replace(c.name,cn).replace('v3.17.0','v3.21.0');(out/'index.html').write_text(h)
print(name,cn)
