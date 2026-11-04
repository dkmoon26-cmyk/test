// One fixed-size room, one allocated instrument per case, and shared consultation stations.
function beginVIPEdit(){if(S.stage<4||S.phase!=='prepare'||editing!==null)return false;$('interiorDialog').close();$('management').close();hideFurnitureQuick();vipEditor=true;vipZoneDraft=null;document.body.classList.add('vip-editing');$('vipEditBar').hidden=false;$('vipEditStatus').textContent='8×8 고정 · 구역의 기준 타일을 선택하세요';$('vipEditConfirm').disabled=true;renderDirty=true;return true;}
function finishVIPEdit(commit){if(commit&&!setVIPZone(vipZoneDraft))return false;vipEditor=false;vipZoneDraft=null;document.body.classList.remove('vip-editing');$('vipEditBar').hidden=true;renderDirty=true;openInterior();return true;}
function selectVIPTile(p){
 if(!vipEditor||!Number.isInteger(p.x)||!Number.isInteger(p.y)||p.x<0||p.y<0||p.x>=N||p.y>=M)return;
 const prior=S.vip.zone,sides=[prior?.doorSide,'left','top','right','bottom'].filter(Boolean),side=sides.find(side=>side==='left'?p.x>0:side==='right'?p.x+8<N:side==='top'?p.y>0:p.y+8<M)??'left';vipZoneDraft={x:p.x,y:p.y,w:8,h:8,doorSide:side,doorAt:Math.min(6,Math.max(1,prior?.doorAt??4))};const error=zoneError(vipZoneDraft);$('vipEditStatus').textContent='8×8 고정 · '+(error||'배치 가능 · 확정 후 문 위치를 조절하세요');$('vipEditConfirm').disabled=!!error;renderDirty=true;
}
function drawVIPDraft(){if(!vipEditor||!vipZoneDraft)return;const z=vipZoneDraft,error=zoneError(z);for(let y=z.y;y<z.y+8;y++)for(let x=z.x;x<z.x+8;x++)diamond(x,y,error?'#bc5d4c55':'#72a97c66',error?'#bd6b59':'#467654');const d=vipDoor(z);diamond(d.inside.x,d.inside.y,'#e5cb7c88','#705f3c');}
function vipReservedCount(base){return S.furniture.filter(f=>f.t===15&&f.vipSlots?.[0]===base).length;}
function stockCount(base){return S.stock[base]+vipReservedCount(base);}
function stockLabel(base){return isVIPProduct(base)?'보관 '+S.stock[base]+' · 진열 '+vipReservedCount(base):'재고 '+S.stock[base];}
function setVIPDisplay(id,slot,product){
 if(S.phase!=='prepare'||editing!==null||slot!==0)return false;const f=S.furniture.find(f=>f.id===id&&f.t===15);if(!f)return false;const old=f.vipSlots?.[0]??null;if(product===old)return true;
 if(product!==null&&(!isVIPProduct(product)||!productUnlocked(product)||!wideVIP(f)||S.stock[product]<1))return false;
 if(old!==null&&!Number.isSafeInteger(S.stock[old]+1))return false;if(product!==null&&!assetGate(productAssetKeys(product),()=>{if(setVIPDisplay(id,slot,product)&&$('customDisplayDialog').open)openVIPDisplays();}))return false;
 if(old!==null)S.stock[old]++;if(product!==null)S.stock[product]--;f.vipSlots=[product];expansionChanged();return true;
}
function vipOffers(){
 const out=displayedCustoms().map(i=>({...i,kind:'custom'}));for(const f of S.furniture.filter(f=>f.t===15&&wideVIP(f)&&vipNear(f))){const base=f.vipSlots?.[0];if(!isVIPProduct(base)||!productUnlocked(base))continue;out.push({kind:'normal',base,price:products[base].price,displayId:f.id,displaySlot:0,options:{}});}return out;
}
function openVIPDisplays(){
 hideFurnitureQuick();$('displayHeading').textContent='최고급·명품 진열';$('customDisplayBody').innerHTML=`<p class="sub">악기 1개씩 배정 · 회수하면 보관 재고로 반환 · 판매 시 진열대 비움</p>${S.furniture.filter(f=>f.t===15).map(f=>{const current=f.vipSlots?.[0]??null,inside=wideVIP(f);return `<section class="operation-card"><h3>진열대 #${f.id}${inside?'':' · VIP 구역 밖'}</h3><label class="vip-slot">악기<select data-vip-display="${f.id}:0" ${S.phase!=='prepare'||editing!==null?'disabled':''}><option value="" ${current===null?'selected':''}>${current===null?'비움':'보관으로 회수'}</option>${products.map((p,i)=>({p,i})).filter(({i})=>isVIPProduct(i)&&productUnlocked(i)).map(({p,i})=>`<option value="${i}" ${current===i?'selected':''} ${!inside||current!==i&&S.stock[i]<1?'disabled':''}>${p.name} · 보관 ${S.stock[i]}${current===i?' · 배정됨':''}</option>`).join('')}</select></label></section>`;}).join('')||'<p>최고급·명품 진열대를 먼저 놓아주세요.</p>'}`;if(!$('customDisplayDialog').open)$('customDisplayDialog').showModal();
}
function sellFurniture(id){
 const f=S.furniture.find(q=>q.id===id);if(!canSellFurniture(f)){if(f&&[0,6].includes(f.t))toast('영업에 필요한 마지막 악기 진열대는 유지해주세요.');return false;}
 const product=f.t===15?f.vipSlots?.[0]:null;if(Number.isInteger(product)){if(!Number.isSafeInteger(S.stock[product]+1))return false;S.stock[product]++;}
 const value=Math.floor(types[f.t].cost*.5);S.money+=value;S.furnitureRevenue+=value;S.furniture=S.furniture.filter(q=>q!==f);for(const i of S.custom.items)if(i.displayId===id){i.displayId=null;i.displaySlot=null;}atelierSprites.clear();people=[];selected=null;sceneCacheKey='';hideFurnitureQuick();save();renderPanel();ui();toast('가구를 판매했어요'+(Number.isInteger(product)?' · 진열 악기는 보관으로 회수했어요':''));return true;
}
let vipDeskCacheKey='',vipDeskCache=[];
function vipDeskCandidates(){
 const key=JSON.stringify([N,M,ENTRY,S.vip.zone,S.furniture.map(f=>[f.id,f.t,f.x,f.y,f.dir,f.legacyCompact])]);if(key===vipDeskCacheKey)return vipDeskCache;
 const candidates=[];for(const f of S.furniture.filter(f=>f.t===14&&wideVIP(f))){const customer=Furniture.front(f);if(!vipPath(ENTRY,customer))continue;const [dx,dy]=Furniture.vectors[Furniture.direction(f)];for(const sign of [1,-1]){const staff={x:customer.x+dy*sign,y:customer.y-dx*sign};if(inVIP(staff)&&!S.furniture.some(q=>Furniture.blocks(q,staff.x,staff.y))&&vipPath(ENTRY,staff)){candidates.push({deskId:f.id,customer,staff});break;}}}
 vipDeskCacheKey=key;vipDeskCache=candidates;return candidates;
}
function vipDeskFor(g=S.vip.guest){const all=vipDeskCandidates(),id=g?.consultDeskId??(g?.state==='consult'?g.stationId:null);return all.find(c=>c.deskId===id)??all[0]??null;}
function vipStaffHome(){return vipDeskFor()?.staff??null;}
function cachedVIPRequirements(){
 if(S.stage<4)return ['5단계에서 열려요'];if(!S.vip.zone)return ['VIP 구역 8×8을 지정하세요'];const out=[],error=zoneError(S.vip.zone);if(error)out.push(error);
 for(const [t,label]of [[15,'최고급·명품 진열대'],[13,'VIP 시연석']]){const fs=S.furniture.filter(f=>f.t===t&&wideVIP(f));if(!fs.length)out.push(label+' 배치 필요');else if(!fs.some(f=>vipNear(f)))out.push(label+' 앞 통로 확보');}
 if(!S.furniture.some(f=>f.t===14&&wideVIP(f)))out.push('상담 테이블 배치 필요');else if(!vipDeskCandidates().length)out.push('상담 테이블과 직원 자리 통로 확보');if(!S.vip.hired)out.push('VIP 직원 미채용');return out;
}
function updateVIPEmployee(dt){
 const e=vipEmployee();if(!e)return;const g=S.vip.guest,home=vipStaffHome();let target=home,state='대기';if(g&&g.state!=='leave'){
  if(g.state==='consult'){const desk=vipDeskFor(g);if(desk){target=desk.staff;state='상담·결제';}}
  else{const front=g.state==='enter'?vipDoor().inside:Furniture.front(S.furniture.find(f=>f.id===g.stationId)??{x:g.x,y:g.y,dir:0});state=g.state==='enter'?'입장 안내':g.state==='try'?'시연 안내':'악기 안내';const candidates=[{x:front.x+1,y:front.y},{x:front.x-1,y:front.y},{x:front.x,y:front.y+1},{x:front.x,y:front.y-1}].filter(p=>inVIP(p)&&!S.furniture.some(f=>Furniture.blocks(f,p.x,p.y)));target=candidates.find(p=>e.targetKey===p.x+','+p.y)??candidates.find(p=>vipPath(e,p))??home;}
 }
 if(!target)return;const key=target.x+','+target.y;if(e.targetKey!==key){e.path=vipPath(e,target)??[];e.targetKey=key;}e.state=state;e.lookTarget=g?{x:g.x,y:g.y}:null;Motion.advance(e,dt);
}
function seatRoute(from,via,to){return [...axisConnector(from,via),...axisConnector(via,to)];}
function advanceSeating(p,f,dt,holdSeconds,finishEarly=false){
 p.seatPhase??='approach';if(p.path.length){Motion.advance(p,dt);if(p.path.length)return false;}else Motion.settle(p,dt);
 const front=Furniture.front(f),entry=Furniture.seatEntry(f),seat=Furniture.seat(f);
 if(p.seatPhase==='approach'){p.seatPhase='enter';p.path=seatRoute(p,entry,seat);p.timer=0;p.seated=false;}
 else if(p.seatPhase==='enter'){p.seatPhase='sitting';p.seated=true;p.timer=0;p.lookTarget=front;}
 else if(p.seatPhase==='sitting'){p.timer+=dt;if(p.timer>=holdSeconds||finishEarly){p.seated=false;p.seatPhase='rise';p.timer=0;p.lookTarget=front;}}
 else if(p.seatPhase==='rise'){p.timer+=dt;if(p.timer>=.2){p.seatPhase='exit';p.path=seatRoute(p,entry,front);p.timer=0;}}
 else if(p.seatPhase==='exit'){delete p.seatPhase;delete p.seated;return true;}
 return false;
}
function tryRest(p){if(p.rested||p.companion||p.special||S.phase!=='open'||S.time>90)return false;p.rested=true;if(Math.random()>.3)return false;for(const f of S.furniture.filter(f=>f.t===16&&!inVIP(f)&&!people.some(q=>q!==p&&q.restChair===f.id))){const n=near(f,p);if(!n)continue;p.restChair=f.id;p.restOrigin={state:p.state,stationId:p.stationId,target:p.target};p.path=n.path;p.state='rest';p.seatPhase='approach';p.seated=false;p.timer=0;p.bubble='잠깐 쉬었다 갈게요';return true;}return false;}
function updateRest(p,dt){if(p.state!=='rest')return false;const f=S.furniture.find(f=>f.id===p.restChair&&f.t===16);if(!f){finishRest(p);return true;}if(S.phase==='closing'&&(p.seatPhase??'approach')==='approach'){p.path=[];finishRest(p);return true;}if(advanceSeating(p,f,dt,4,S.phase==='closing'))finishRest(p);return true;}
function finishRest(p){p.seated=false;delete p.seatPhase;delete p.restChair;const origin=p.restOrigin;delete p.restOrigin;p.state=origin?.state??'browse';p.stationId=origin?.stationId??null;p.target=origin?.target??null;p.timer=0;p.path=[];p.bubble='다시 살펴볼까?';finishBrowse(p);}
function drawSeatedCustomer(p){const f=S.furniture.find(f=>f.id===p.restChair);if(!f)return;const q=P(p.x,p.y),dir=Furniture.direction(f),frame=walkSprite(visualActor(p),dir,0,false,false);ctx.save();ctx.translate(q.x,q.y);ctx.scale((p.scale??1)*Config.characterScale,(p.scale??1)*Config.characterScale);paintSeated(ctx,seatedLegacyFrame(frame,dir),59);ctx.restore();}
function drawVIP(g){
 if(!vipSpriteImage?.complete||!people320Atlas?.complete)return;const seat=g.seated&&g.state==='try'?S.furniture.find(f=>f.id===g.stationId&&f.t===13):null,q=P(g.x,g.y),dir=seat?Furniture.direction(seat):g.facing;ctx.save();ctx.translate(q.x,q.y);ctx.scale(Config.characterScale,Config.characterScale);if(seat){const frame=g.profile>=3?people320Frame(g.profile-3,dir,0,false,true):seatedLegacyFrame(vipFrame(g.profile,dir,0,false),dir);paintSeated(ctx,frame,59);}else drawFullCharacter(ctx,vipFrame(g.profile,dir,g.gait,g.moving),77,g.gait,g.moving,g.animationWeight??1);text('VIP',0,seat?-65:-85,10,'#af8b35');if(seat){const item=selectedVIPOffer(g);if(item){if(item.kind==='custom'){ctx.save();ctx.translate(17,-10);miniCustom(ctx,item,35);ctx.restore();}else drawProduct(ctx,item.base,6,-43,24,34,false,true);}text('♫',28,-55,14,'#d4b66a');}if(g.bought)rect(14,-23,12,17,'#ead6aa');ctx.restore();
}
function updateVIP(dt){
 if(S.phase==='open')spawnVIP();const g=S.vip.guest;if(!g)return;const profile=Atelier.profiles[g.profile];
 if(g.state==='try'){
  const seat=S.furniture.find(f=>f.id===g.stationId&&f.t===13);if(!seat){vipLeave(g,'시연석 확인 필요');return;}
  if(advanceSeating(g,seat,dt,5)){Sound.play('try',products[g.product]?.family==='bass'?1:products[g.product]?.family==='acoustic'?2:0);const target=vipDeskFor(g),desk=target&&S.furniture.find(f=>f.id===target.deskId);if(!desk||!vipGo(g,desk,'consult'))vipLeave(g,'상담 테이블과 직원 자리 통로 확인 필요');else g.consultDeskId=desk.id;}return;
 }
 if(g.state==='consult'){const target=vipDeskFor(g);if(!target){vipLeave(g,'상담 테이블과 직원 자리 통로 확인 필요');return;}if(g.stationId!==target.deskId){g.consultDeskId=target.deskId;if(!vipGo(g,S.furniture.find(f=>f.id===target.deskId),'consult'))vipLeave(g,'상담 테이블 통로 확인 필요');return;}}
 Motion.advance(g,dt);if(g.path.length)return;g.timer+=dt;
 if(g.state==='enter'&&g.timer>1){const item=vipOffers().filter(i=>vipMatch(profile,i)).sort((a,b)=>vipPreference(profile,b)-vipPreference(profile,a)||a.price-b.price)[0];if(!item){vipLeave(g,'취향과 예산에 맞는 악기 없음');return;}g.kind=item.kind;g.itemId=item.kind==='custom'?item.id:undefined;g.product=item.base;g.displayId=item.displayId;g.displaySlot=item.displaySlot;const desk=vipDeskFor(g);g.consultDeskId=desk?.deskId;if(!vipGo(g,S.furniture.find(f=>f.id===item.displayId),'browse'))vipLeave(g,'전시대 통로 확인 필요');}
 else if(g.state==='browse'&&g.timer>3){const f=S.furniture.find(f=>f.t===13&&wideVIP(f)&&vipNear(f,g));if(!f||!vipGo(g,f,'try'))vipLeave(g,'시연석 통로 확인 필요');else{g.seatPhase='approach';g.seated=false;}}
 else if(g.state==='consult'&&g.timer>3){const employee=vipEmployee(),desk=vipDeskFor(g);if(!S.vip.hired||!employee||!desk||employee.path.length||Math.hypot(employee.x-desk.staff.x,employee.y-desk.staff.y)>.05){if(g.timer>25)vipLeave(g,'직원 응대 동선을 확인해주세요');return;}const item=selectedVIPOffer(g);if(item&&vipMatch(profile,item)&&!g.bought){if(item.kind==='custom'){S.custom.items=S.custom.items.filter(i=>i.id!==item.id);S.custom.sold++;S.custom.totalRevenue+=item.price;}else{const f=S.furniture.find(f=>f.id===item.displayId);f.vipSlots[item.displaySlot]=null;S.vip.normalSales++;S.vip.normalRevenue+=item.price;noteStockChange(item.base);}S.money+=item.price;S.revenue+=item.price;S.totalRevenue+=item.price;S.sold++;S.totalSales++;S.vip.sales++;S.vip.revenue+=item.price;recordMissionSale([item.base]);g.bought=true;gainReputation(.3);clearFurnitureBodyCache();atelierSprites.clear();Sound.play('sale');vipLeave(g,profile.name+' · '+products[item.base].name+' 구매 '+money(item.price));}else vipLeave(g,profile.name+' · 다음 방문 예정');ui();}
 else if(g.state==='leave'&&g.timer>.3){S.vip.guest=null;S.vip.nextVisitAt=S.time+3;save();renderDirty=true;}
}
function migrateVIPSave(v,version=0){
 if(version<24)migrateLegacyVIPSave(v);
 if(v.vip?.guest?.kind==='custom'&&v.vip.guest.product===undefined)v.vip.guest.product=v.custom?.items?.find(i=>i.id===v.vip.guest.itemId)?.base;
 if(Array.isArray(v.stock)&&Array.isArray(v.furniture))for(const f of v.furniture){if(f.t!==15||!Array.isArray(f.vipSlots)||f.vipSlots.length!==1)continue;const base=f.vipSlots[0];if(!isVIPProduct(base)||!Number.isSafeInteger(v.stock[base])||v.stock[base]<0)continue;if(v.stock[base]>0)v.stock[base]--;else f.vipSlots[0]=null;}
 const migrateSeat=(p,chairId)=>{const f=v.furniture?.find(f=>f.id===chairId);if(!f)return;if(p.seated||p.state==='try'&&!p.path?.length){const seat=Furniture.seat(f);p.x=seat.x;p.y=seat.y;p.path=[];p.seated=true;p.seatPhase='sitting';}else{p.seated=false;p.seatPhase='approach';}};
 for(const p of v.guests??[])if(p.state==='rest')migrateSeat(p,p.restChair);
 if(v.vip?.guest?.state==='try')migrateSeat(v.vip.guest,v.vip.guest.stationId);
}
function validateNewVIPState(v,s){
 const phases=['approach','enter','sitting','rise','exit'],validSeat=(p,f)=>{if(!phases.includes(p.seatPhase)||typeof p.seated!=='boolean'||!f)throw Error('착석 이동 상태');if(p.seated!==(p.seatPhase==='sitting'))throw Error('착석 자세');if(['sitting','rise'].includes(p.seatPhase)){const pos=Furniture.seat(f);if(p.path.length||Math.hypot(p.x-pos.x,p.y-pos.y)>1e-6)throw Error('착석 위치');}};
 const occupied=new Set();for(const p of s.guests){if(p.state==='rest'){const f=s.furniture.find(f=>f.t===16&&f.id===p.restChair);validSeat(p,f);if(occupied.has(f.id))throw Error('휴식 의자 중복');occupied.add(f.id);}else if(p.seatPhase!==undefined)throw Error('이동 상태');}
 if(s.vip.guest){const g=s.vip.guest,raw=v.vip.guest;g.consultDeskId=raw.consultDeskId;if(g.consultDeskId!==undefined&&(!Number.isSafeInteger(g.consultDeskId)||!s.furniture.some(f=>f.id===g.consultDeskId&&f.t===14)))throw Error('VIP 상담 테이블');if(g.state==='try'){g.seatPhase=raw.seatPhase;g.seated=raw.seated;validSeat(g,s.furniture.find(f=>f.t===13&&f.id===g.stationId));}else if(raw.seatPhase!==undefined||raw.seated===true)throw Error('VIP 착석 상태');}
 for(let base=0;base<s.stock.length;base++){const reserved=s.furniture.filter(f=>f.t===15&&f.vipSlots?.[0]===base).length;if(!Number.isSafeInteger(s.stock[base]+reserved))throw Error('보유 재고 수량');}
}
