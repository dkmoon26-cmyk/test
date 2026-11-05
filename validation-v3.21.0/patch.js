// v3.21 pictorial catalog and per-surface construction. Quotes never mutate inventory or cash.
const InteriorCatalog={
 floor:{original:{name:'기본 원목',price:500,style:'oak',color:'#d8b17c'},oak:{name:'오크',price:500,style:'oak',color:'#dfc298'},checker:{name:'체커보드',price:800,style:'checker',color:'#e9dfc9'},terrazzo:{name:'테라조',price:1000,style:'terrazzo',color:'#e7dfcd'},herringbone:{name:'헤링본',price:1500,style:'herringbone',color:'#a28257'},marble:{name:'화이트 대리석',price:2000,style:'marble',color:'#ece7db'},blackMarble:{name:'블랙 대리석',price:3000,style:'marble',color:'#29302f'},walnut:{name:'월넛',price:1500,style:'oak',color:'#94704d'}},
 wall:{original:{name:'기본 초록 벽',price:500,style:'plaster',color:'#789185'},cream:{name:'아이보리 회벽',price:500,style:'plaster',color:'#e5d8bb'},sage:{name:'세이지 그린',price:500,style:'plaster',color:'#819986'},beige:{name:'따뜻한 베이지',price:500,style:'plaster',color:'#ceb493'},brick:{name:'빈티지 벽돌',price:800,style:'brick',color:'#ab795e'},acoustic:{name:'녹음실 흡음 패널',price:1000,style:'acoustic',color:'#69736c'},woodPanel:{name:'월넛 우드 패널',price:1200,style:'panel',color:'#8c6d50'},blueBrass:{name:'딥블루 몰딩',price:1500,style:'molding',color:'#384e61'},artdeco:{name:'아르데코',price:2000,style:'artdeco',color:'#435f55'}},
 art:{poster:{name:'공연 포스터',price:10000},record:{name:'레코드 액자',price:25000},guitar:{name:'기타 벽걸이',price:40000},logo:{name:'가게 로고 간판',price:50000},clock:{name:'벽시계',price:20000},lamp:{name:'벽등',price:15000}}
};
let designEditor=null,designStroke=null,catalogDrag=null,suppressCatalogClick=false;
function ensureDesignMaps(){S.design.floorTiles??={};S.design.wallTiles??={};S.design.wallStock??={};}
function validateInterior26(v,s){
 const d=v.design??{},size=Stages[s.stage],fail=()=>{throw Error('인테리어 타일 저장')};
 function map(raw,kind){if(raw===undefined)return {};if(!raw||typeof raw!=='object'||Array.isArray(raw)||Object.keys(raw).length>1200)fail();const result={};for(const [key,id]of Object.entries(raw)){if(!InteriorCatalog[kind][id])fail();if(kind==='floor'){const m=/^(\d+),(\d+)$/.exec(key);if(!m||+m[1]>=size.w||+m[2]>=size.h)fail();}else if(!validWallKey(key,s.stage))fail();result[key]=id;}return result;}
 s.design.floorTiles=map(d.floorTiles,'floor');s.design.wallTiles=map(d.wallTiles,'wall');
 const stock=d.wallStock??{};if(!stock||typeof stock!=='object'||Array.isArray(stock)||Object.keys(stock).some(k=>!InteriorCatalog.art[k]||!Number.isSafeInteger(stock[k])||stock[k]<0||stock[k]>999))fail();s.design.wallStock={...stock};
}
function validWallKey(key,stage=S.stage){const m=/^(x|y|vip:left|vip:right|vip:top|vip:bottom):(\d+)$/.exec(key);return !!m&&+m[2]<(m[1]==='x'?Stages[stage].w:m[1]==='y'?Stages[stage].h:8);}
function materialId(kind,key){const d=S.design;if(kind==='floor'){const [x,y]=key.split(',').map(Number);return d.floorTiles?.[key]??(inVIP({x,y})?d.vipFloor:d.floor);}return d.wallTiles?.[key]??(key.startsWith('vip:')?d.vipWall:d.wall);}
function materialTexture(kind,id){
 const def=InteriorCatalog[kind][id];if(!def)return null;const key=kind+':'+id;if(materialTexture.cache.has(key))return materialTexture.cache.get(key);
 const cv=document.createElement('canvas');cv.width=cv.height=128;const c=cv.getContext('2d');c.fillStyle=def.color;c.fillRect(0,0,128,128);const style=def.style;
 const line=(x,y,a,b,color,width=1)=>{c.strokeStyle=color;c.lineWidth=width;c.beginPath();c.moveTo(x,y);c.lineTo(a,b);c.stroke();};
 if(style==='oak'||style==='panel'){for(let y=0;y<128;y+=32){line(0,y,128,y,'#53351d55');for(let x=(y%64?32:0);x<128;x+=64)line(x,y,x,y+32,'#5f422a66');for(let n=0;n<5;n++)line(0,y+5+n*5,128,y+3+n*5,n%2?'#fff4d51c':'#51371e18');}if(style==='panel')for(let x=0;x<128;x+=16)line(x,0,x,128,'#20180e66',2);}
 if(style==='checker')for(let x=0;x<4;x++)for(let y=0;y<4;y++){c.fillStyle=(x+y)%2?'#4d514b':'#e9dfc9';c.fillRect(x*32,y*32,32,32);}
 if(style==='terrazzo'){for(let n=0;n<90;n++){const x=(n*71+13)%128,y=(n*47+29)%128;c.fillStyle=['#bda68a','#8c9086','#d2b29b','#f9f2e4'][n%4];c.beginPath();c.moveTo(x,y);c.lineTo(x+2+n%4,y+1);c.lineTo(x+1,y+3+n%3);c.closePath();c.fill();}}
 if(style==='herringbone'){c.save();c.translate(64,64);c.rotate(Math.PI/4);for(let y=-128;y<128;y+=16)for(let x=-128;x<128;x+=48){const shift=(y/16%2)*16;c.fillStyle=['#98774e','#b39163','#a58355','#c0a16f'][Math.abs(x/16+y/16)%4];c.fillRect(x+shift,y,47,15);c.strokeStyle='#5b432e77';c.strokeRect(x+shift,y,48,16);}c.restore();}
 if(style==='marble'){for(let n=0;n<7;n++){c.strokeStyle=id==='blackMarble'?'#bea26488':'#a69d8c66';c.lineWidth=n%3===0?1.1:.5;c.beginPath();const y=n*23-10;c.moveTo(-10,y);c.bezierCurveTo(32,y+10,47,y-14,72,y+12);c.bezierCurveTo(91,y+27,112,y+14,140,y+32);c.stroke();}line(0,0,128,0,'#ffffff44');line(0,0,0,128,'#ffffff44');}
 if(style==='brick'){for(let y=0;y<128;y+=24){line(0,y,128,y,'#e5ceb5',3);for(let x=(y%48?24:0);x<128;x+=48)line(x,y,x,y+24,'#e5ceb5',3);}}
 if(style==='acoustic'){for(let x=0;x<128;x+=8)line(x,0,x,128,'#2b383b99',3);for(let y=0;y<128;y+=64)line(0,y,128,y,'#d1c4a366',2);}
 if(style==='molding'){c.strokeStyle='#c3a369';c.lineWidth=2;c.strokeRect(8,8,112,112);c.strokeRect(13,13,102,102);}
 if(style==='artdeco'){for(let y=0;y<144;y+=32)for(let x=0;x<144;x+=32){c.strokeStyle='#c8ad7188';c.beginPath();c.moveTo(x-16,y);c.lineTo(x,y-28);c.lineTo(x+16,y);c.lineTo(x,y+28);c.closePath();c.stroke();}}
 if(style==='plaster')for(let n=0;n<220;n++){c.fillStyle=n%2?'#ffffff0b':'#2b362908';c.fillRect(n*37%128,n*71%128,2,1);}
 materialTexture.cache.set(key,cv);return cv;
}
materialTexture.cache=new Map();
function wallArtThumb(c,type,x=0,y=0,w=160,h=135){
 const clock=type==='clock'||type==='lamp',im=clock?wallDetailAtlas:interiorArtAtlas,clip=clock?WallDetailClips[type==='clock'?0:1]:InteriorArtClips[{poster:0,record:1,guitar:2,logo:3}[type]];if(!im?.complete||!clip)return;const k=Math.min((w-20)/clip[2],(h-12)/clip[3]);c.drawImage(im,...clip,x+(w-clip[2]*k)/2,y+(h-clip[3]*k)/2,clip[2]*k,clip[3]*k);
}
function catalogPicture(key){return key.startsWith('f:')?furnitureIcon(+key.slice(2)):`<canvas width="320" height="270" data-catalog-art="${key}" aria-hidden="true"></canvas>`;}
function drawCatalogPictures(){document.querySelectorAll('[data-catalog-art]').forEach(cv=>{const [kind,id]=cv.dataset.catalogArt.split(':'),c=cv.getContext('2d');c.clearRect(0,0,320,270);if(kind==='art'){wallArtThumb(c,id,0,0,320,270);return;}const im=materialTexture(kind,id);if(!im)return;c.save();if(kind==='floor'){c.translate(160,40);c.transform(1,.5,-1,.5,0,0);c.fillStyle='#9b815c';c.fillRect(0,0,128,136);c.drawImage(im,0,0);}else{c.translate(65,28);c.fillStyle='#9a8765';c.fillRect(4,4,192,214);c.drawImage(im,0,0,192,208);}c.restore();});}
function catalogCard(key,name,installed=null){return `<button class="catalog-card" data-catalog="${key}" ${installed?`data-installed="${installed}"`:''}>${catalogPicture(key)}<b>${escapeHTML(name)}</b></button>`;}
function furnitureCatalogHTML(){
 ensureDesignMaps();let h=`<div class="catalog-toolbar"><div class="filter-bar"><button data-furniture-view="purchase" aria-pressed="${!selected&&furnitureView==='purchase'}">구매</button><button data-furniture-view="placed" aria-pressed="${!!selected||furnitureView==='placed'}">배치한 아이템</button></div><button data-atelier="vip-design" ${S.stage<4?'disabled':''}>VIP 구역</button></div>`;
 if(selected)return h+installedFurnitureDetail();
 h+=`<div class="filter-bar decor-filters">${[['all','전체'],['display','진열대'],['facility','운영 시설'],['decor','소품'],['interior','인테리어']].map(([key,label])=>`<button data-decor-filter="${key}" aria-pressed="${decorFilter===key}">${label}</button>`).join('')}</div><div class="catalog-grid">`;
 if(furnitureView==='purchase'){
  h+=types.map((t,i)=>decorFilter==='all'||furnitureCategory(i)===decorFilter?catalogCard('f:'+i,t.name):'').join('');
  if(['all','decor'].includes(decorFilter))h+=Object.entries(InteriorCatalog.art).map(([id,o])=>catalogCard('art:'+id,o.name)).join('');
  if(['all','interior'].includes(decorFilter))for(const kind of ['floor','wall'])h+=Object.entries(InteriorCatalog[kind]).filter(([id])=>!['beige','walnut'].includes(id)).map(([id,o])=>catalogCard(kind+':'+id,o.name)).join('');
 }else{
  h+=S.furniture.filter(f=>decorFilter==='all'||furnitureCategory(f.t)===decorFilter).map(f=>catalogCard('f:'+f.t,types[f.t].name,'f:'+f.id)).join('');
  if(['all','decor'].includes(decorFilter)){h+=S.design.wallItems.map(i=>catalogCard('art:'+i.type,InteriorCatalog.art[i.type].name,'art:'+i.wall+':'+i.slot)).join('');h+=Object.entries(S.design.wallStock).filter(([,n])=>n>0).map(([id])=>catalogCard('art:'+id,InteriorCatalog.art[id].name)).join('');}
  if(['all','interior'].includes(decorFilter))h+='<p class="empty-note">인테리어는 구매 목록에서 재시공</p>';
 }
 return h+'</div>';
}
function furnitureCategory(t){return [0,5,6,12,15].includes(t)?'display':[1,4,7,11,13,14,16].includes(t)?'facility':'decor';}
function shortFurnitureEffect(t){return DecorDefinitions[t]?.effect??({0:'악기 '+rackLimit()+'종 진열',1:'구매 계산',4:'악기 시연',5:'소품 '+cabinetLimit()+'종 진열',6:'전자드럼 진열',7:'전자드럼 시연',11:'악기 커스텀 제작',12:'커스텀 악기 1개 진열',13:'VIP 악기 시연',14:'VIP 상담·결제',15:'최고급·명품 1개 진열',16:'손님 휴식'})[t];}
function openCatalogDetail(key,installed=null){
 const [kind,id]=key.split(':'),t=+id,o=kind==='f'?types[t]:InteriorCatalog[kind]?.[id];if(!o)return false;const ready=S.phase==='prepare'&&editing===null;
 if(installed?.startsWith('f:')){selected=+installed.slice(2);renderPanel();return true;}
 let body=`${catalogPicture(key)}<h3>${escapeHTML(o.name)}</h3>`;
 if(kind==='f'){const unlocked=furnitureUnlocked(t),reason=!unlocked?([11,12].includes(t)?'7단계 해금':[13,14,15].includes(t)?'5단계 해금':'미션 해금'):!ready?'영업 준비 중 배치':canBuyFurniture(t)?'':'공간·자금 조건 확인';body+=`<dl class="catalog-facts"><div><dt>가격</dt><dd>${money(o.cost)}</dd></div><div><dt>효과</dt><dd>${shortFurnitureEffect(t)??'장식'}</dd></div>${DecorDefinitions[t]?`<div><dt>조건</dt><dd>${DecorDefinitions[t].condition}</dd></div>`:''}${reason?`<div><dt>조건</dt><dd>${reason}</dd></div>`:''}</dl><button class="primary" data-catalog-build="${t}" ${!ready||!canBuyFurniture(t)?'disabled':''}>구매·배치</button>`;
 }else if(kind==='art'){ensureDesignMaps();const stock=S.design.wallStock[id]??0;body+=`<dl class="catalog-facts"><div><dt>가격</dt><dd>${money(o.price)} / 개</dd></div><div><dt>설치</dt><dd>뒤쪽 벽</dd></div>${stock?`<div><dt>보관</dt><dd>${stock}개</dd></div>`:''}</dl><button class="primary" data-design-start="${key}" ${installed?`data-design-moving="${installed}"`:''} ${!ready?'disabled':''}>${installed?'이동':stock?'배치':'구매·배치'}</button>${installed?`<button data-wall-recall="${installed}">회수</button>`:''}`;
 }else body+=`<dl class="catalog-facts"><div><dt>시공비</dt><dd>${money(o.price)} / 칸</dd></div></dl><button class="primary" data-design-start="${key}" ${!ready?'disabled':''}>시공 위치 선택</button>`;
 $('catalogDetailBody').innerHTML=body;drawIcons();drawCatalogPictures();if(!$('catalogDetail').open)$('catalogDetail').showModal();return true;
}
function beginDesignEdit(key,moving=null){
 const [kind,id]=key.split(':');if(!InteriorCatalog[kind]?.[id]||S.phase!=='prepare'||editing!==null||vipEditor)return false;
 resetDesignEditor();hideFurnitureQuick();for(const d of document.querySelectorAll('dialog[open]'))d.close();document.body.classList.remove('menu-open');closeMenu();
 designEditor={kind,id,keys:[],moving:typeof moving==='string'?moving:null};document.body.classList.add('design-editing');$('designEditBar').hidden=false;resizeView();updateDesignBar();invalidateDesign();return true;
}
function resetDesignEditor(){designEditor=null;designStroke=null;catalogDrag=null;document.body.classList.remove('design-editing');if($('designEditBar'))$('designEditBar').hidden=true;sceneCacheKey='';renderDirty=true;}
function invalidateDesign(){sceneCacheKey='';renderDirty=true;draw();}
function designTargetAt(e,kind=designEditor?.kind){
 const q=worldAt(e);
 if(kind==='floor'){const p=tileAt(e);return p.x>=0&&p.y>=0&&p.x<N&&p.y<M?p.x+','+p.y:null;}
 if(kind==='art'){for(const wall of ['x','y']){const origin=P(-.5,-.5),u=(q.x-origin.x)/(wall==='x'?34:-34),height=origin.y+u*17-q.y,n=wall==='x'?N:M;if(u>=0&&u<n&&height>=3&&height<=84){const slot=Math.max(0,Math.min(Math.floor((n-1)/2)-1,Math.floor((u-1)/2+.5)));return wall+':'+slot;}}return null;}
 if(kind==='wall'){
  const z=S.vip.zone;if(z)for(const side of ['left','right','top','bottom'])for(let n=0;n<8;n++){if(side===z.doorSide&&n===z.doorAt)continue;const [a,b]=vipWallEnds(side,n),p=P(a.x,a.y),r=P(b.x,b.y),dx=r.x-p.x;if(Math.abs(dx)<1)continue;const t=(q.x-p.x)/dx,h=p.y+(r.y-p.y)*t-q.y;if(t>=0&&t<1&&h>=0&&h<=28)return 'vip:'+side+':'+n;}
  const origin=P(-.5,-.5);for(const wall of ['x','y']){const u=(q.x-origin.x)/(wall==='x'?34:-34),height=origin.y+u*17-q.y,n=wall==='x'?N:M;if(u>=0&&u<n&&height>=0&&height<=84)return wall+':'+Math.floor(u);}
 }
 return null;
}
function selectDesignTargets(a,b=a){
 if(!designEditor||!a)return false;const keys=[];
 if(designEditor.kind==='floor'){const parse=k=>k.split(',').map(Number),[ax,ay]=parse(a),[bx,by]=parse(b??a);if(![ax,ay,bx,by].every(Number.isInteger))return false;for(let y=Math.min(ay,by);y<=Math.max(ay,by);y++)for(let x=Math.min(ax,bx);x<=Math.max(ax,bx);x++)if(x>=0&&y>=0&&x<N&&y<M)keys.push(x+','+y);}
 else if(designEditor.kind==='wall'){if(!validWallKey(a)||!validWallKey(b??a))return false;const split=k=>[k.slice(0,k.lastIndexOf(':')),Number(k.slice(k.lastIndexOf(':')+1))],[side,start]=split(a),[endSide,end]=split(b??a);if(side!==endSide)return false;for(let n=Math.min(start,end);n<=Math.max(start,end);n++){const z=S.vip.zone;if(side.startsWith('vip:')&&(!z||side==='vip:'+z.doorSide&&n===z.doorAt))continue;keys.push(side+':'+n);}}
 else if(/^[xy]:\d+$/.test(a))keys.push(a);
 designEditor.keys=keys;updateDesignBar();invalidateDesign();return keys.length>0;
}
function designQuote(){
 if(!designEditor)return {valid:false,cost:0,count:0,reason:'위치 선택'};ensureDesignMaps();const {kind,id,keys,moving}=designEditor,o=InteriorCatalog[kind]?.[id];if(!o||!keys.length||S.phase!=='prepare'||editing!==null)return {valid:false,cost:0,count:0,reason:'위치 선택'};
 let changed=keys.filter(k=>kind==='floor'?/^(\d+),(\d+)$/.test(k)&&k.split(',').map(Number).every((n,i)=>n>=0&&n<(i===0?N:M)):kind==='wall'?validWallKey(k):/^[xy]:\d+$/.test(k));if(changed.length!==keys.length)return {valid:false,cost:0,count:0,reason:'위치 확인'};
 if(kind==='art'){const [wall,slot]=keys[0].split(':'),max=Math.floor(((wall==='x'?N:M)-1)/2),source=moving?.split(':');if(keys.length!==1||+slot>=max||moving&&!S.design.wallItems.some(i=>i.wall===source[1]&&i.slot===+source[2]&&i.type===id))return {valid:false,cost:0,count:0,reason:'벽 위치 확인'};const previous=S.design.wallItems.find(i=>i.wall===wall&&i.slot===+slot);if(previous&&(previous.type!==id||moving&&moving!=='art:'+wall+':'+slot)&&(S.design.wallStock[previous.type]??0)>=999)return {valid:false,cost:0,count:0,reason:'소품 보관 가득'};const stock=S.design.wallStock[id]??0,same=S.design.wallItems.some(i=>i.wall===wall&&i.slot===+slot&&i.type===id),cost=moving||stock>0||same?0:o.price;return {valid:true,cost,count:same&&!moving?0:1,keys:[keys[0]],reason:same&&!moving?'변경 없음':''};}
 changed=changed.filter(k=>materialId(kind,k)!==id);return {valid:true,cost:changed.length*o.price,count:changed.length,keys:changed,reason:changed.length?'':'변경 없음'};
}
function commitDesign(){
 const q=designQuote();if(!q.valid||S.money<q.cost)return false;const {kind,id,moving}=designEditor;ensureDesignMaps();
 if(kind==='art'&&q.count){const [wall,slotText]=q.keys[0].split(':'),slot=+slotText;if(moving){const [,oldWall,oldSlot]=moving.split(':');S.design.wallItems=S.design.wallItems.filter(i=>i.wall!==oldWall||i.slot!==+oldSlot);}else if((S.design.wallStock[id]??0)>0)S.design.wallStock[id]--;
  const previous=S.design.wallItems.find(i=>i.wall===wall&&i.slot===slot);if(previous)S.design.wallStock[previous.type]=(S.design.wallStock[previous.type]??0)+1;S.design.wallItems=S.design.wallItems.filter(i=>i.wall!==wall||i.slot!==slot);S.design.wallItems.push({wall,slot,type:id});
 }else if(kind!=='art')for(const key of q.keys)(kind==='floor'?S.design.floorTiles:S.design.wallTiles)[key]=id;
 S.money-=q.cost;S.expenses+=q.cost;resetDesignEditor();expansionChanged();toast(q.count?'적용 완료 · '+money(q.cost):'변경 없음');return true;
}
function updateDesignBar(){if(!designEditor)return;const q=designQuote(),o=InteriorCatalog[designEditor.kind][designEditor.id];$('designEditName').textContent=o.name;$('designEditCost').textContent=q.valid?(q.count+(designEditor.kind==='art'?'개':'칸')+' · '+money(q.cost)):'위치 선택';const b=$('designEditConfirm');b.disabled=!q.valid||S.money<q.cost;b.textContent=S.money<q.cost?'자금 부족':'적용';}
function recallWallItem(wall,slot){if(S.phase!=='prepare'||editing!==null||designEditor)return false;ensureDesignMaps();const i=S.design.wallItems.find(i=>i.wall===wall&&i.slot===slot);if(!i)return false;if((S.design.wallStock[i.type]??0)>=999)return false;S.design.wallStock[i.type]=(S.design.wallStock[i.type]??0)+1;S.design.wallItems=S.design.wallItems.filter(q=>q!==i);expansionChanged();return true;}
function addWallItem(wall,slot,type){if(!beginDesignEdit('art:'+type))return false;if(!selectDesignTargets(wall+':'+slot)){resetDesignEditor();return false;}const result=commitDesign();if(!result)resetDesignEditor();return result;}
function previewMaterial(kind,key){return designEditor?.kind===kind&&designEditor.keys.includes(key)?designEditor.id:materialId(kind,key);}
function paintInteriorFloor(){
 for(let y=0;y<M;y++)for(let x=0;x<N;x++){const key=x+','+y,id=previewMaterial('floor',key);if(id==='original'&&!(designEditor?.kind==='floor'&&designEditor.keys.includes(key)))continue;const im=materialTexture('floor',id);if(!im)continue;const p=P(x,y);ctx.save();ctx.transform(34/128,17/128,-34/128,17/128,p.x,p.y-17);ctx.drawImage(im,0,0);ctx.strokeStyle=designEditor?.kind==='floor'&&designEditor.keys.includes(key)?'#6fbe8d':'#7e71551f';ctx.lineWidth=designEditor?.kind==='floor'&&designEditor.keys.includes(key)?4:1;ctx.strokeRect(0,0,128,128);ctx.restore();}
}
function paintWallSegment(p,q,id,h,selected=false){const im=materialTexture('wall',id);if(!im)return;ctx.save();ctx.translate(p.x,p.y);const dx=q.x-p.x,dy=q.y-p.y;ctx.transform(dx/128,dy/128,0,h/128,0,-h);ctx.drawImage(im,0,0);if(selected){ctx.strokeStyle='#75bd8e';ctx.lineWidth=3;ctx.strokeRect(0,0,128,128);}ctx.restore();}
function paintDesignWalls(){for(const side of ['x','y']){const n=side==='x'?N:M;for(let i=0;i<n;i++){const key=side+':'+i,selected=designEditor?.kind==='wall'&&designEditor.keys.includes(key),id=previewMaterial('wall',key);if(!S.design.wallTiles?.[key]&&!selected)continue;const a=side==='x'?P(i-.5,-.5):P(-.5,i-.5),b=side==='x'?P(i+.5,-.5):P(-.5,i+.5);paintWallSegment(a,b,id,79,selected);}}}
function vipWallEnds(side,i){const z=S.vip.zone;if(side==='left'||side==='right'){const x=side==='left'?z.x-.5:z.x+z.w-.5;return [{x,y:z.y+i-.5},{x,y:z.y+i+.5}];}const y=side==='top'?z.y-.5:z.y+z.h-.5;return [{x:z.x+i-.5,y},{x:z.x+i+.5,y}];}
function paintVIPWallMaterial(p,q,side,i){const key='vip:'+side+':'+i,selected=designEditor?.kind==='wall'&&designEditor.keys.includes(key);if(S.design.wallTiles?.[key]||selected)paintWallSegment(p,q,previewMaterial('wall',key),25,selected);}
function paintWallItemPreview(){if(designEditor?.kind!=='art'||!designEditor.keys.length)return;const [wall,slot]=designEditor.keys[0].split(':'),p=wall==='x'?P(+slot*2+1,-.5):P(-.5,+slot*2+1);ctx.save();ctx.translate(p.x,p.y);ctx.transform(1,wall==='x'?.5:-.5,0,1,0,0);ctx.globalAlpha=.65;wallArtThumb(ctx,designEditor.id,-24,-80,48,48);ctx.strokeStyle='#76bb91';ctx.strokeRect(-24,-80,48,48);ctx.restore();}
function renderInterior(){const z=S.vip.zone,prep=S.phase==='prepare'&&editing===null;$('interiorHeading').textContent='VIP 구역';$('interiorBody').innerHTML=vipStatusHTML()+`<section class="interior-section">${z?`<p>${z.w}×${z.h}칸</p>`:''}<div class="atelier-actions"><button data-atelier="zone" ${!prep||S.stage<4?'disabled':''}>${z?'위치 변경':'구역 지정'}</button>${z?`<button data-atelier="zone-remove" ${!prep?'disabled':''}>구역 해제</button>`:''}</div>${z?`<div class="interior-grid"><label>문 방향<select id="vipDoorSide" ${!prep?'disabled':''}>${[['left','왼쪽'],['right','오른쪽'],['top','위쪽'],['bottom','아래쪽']].map(([id,label])=>`<option value="${id}" ${z.doorSide===id?'selected':''}>${label}</option>`).join('')}</select></label><label>문 위치<input id="vipDoorAt" type="number" min="2" max="7" value="${z.doorAt+1}" ${!prep?'disabled':''}></label><button data-atelier="door-apply" ${!prep?'disabled':''}>적용</button></div>`:''}</section>`;}
function vipStatusHTML(){const missing=vipRequirements();return `<div class="vip-status"><b>${missing.length?'VIP 준비 중':'영업 가능 · 하루 최대 '+vipDailyLimit()+'명'}</b>${missing.length?`<p>${escapeHTML(missing.join(' · '))}</p>`:''}<div class="atelier-actions"><button data-vip-staff="manage">직원</button><button data-atelier="vip-displays">진열</button></div></div>`;}
function vipGuestCards(){return `<section class="vip-guest-list">${vipStatusHTML()}${Atelier.profiles.map((p,i)=>`<div class="vip-profile"><canvas data-vip-portrait="${i}" width="100" height="120"></canvas><div><b>${p.name}</b><small>${p.family==='electric'?'일렉 기타':p.family==='bass'?'베이스':p.family==='acoustic'?'어쿠스틱':'모든 악기'} · ${money(p.budget)}</small>${S.vip.guest?.profile===i?'<span>방문 중</span>':''}</div></div>`).join('')}</section>`;}
function drawVIP(g){
 if(!vipSpriteImage?.complete||!people320Atlas?.complete)return;const seat=g.seated&&g.state==='try'?S.furniture.find(f=>f.id===g.stationId&&f.t===13):null,q=P(g.x,g.y),dir=seat?Furniture.direction(seat):g.facing;ctx.save();ctx.translate(q.x,q.y);ctx.scale(Config.characterScale,Config.characterScale);if(seat){const frame=g.profile>=3?people320Frame(g.profile-3,dir,0,false,true):seatedLegacyFrame(vipFrame(g.profile,dir,0,false),dir);paintSeated(ctx,frame,59);}else drawFullCharacter(ctx,vipFrame(g.profile,dir,g.gait,g.moving),77,g.gait,g.moving,g.animationWeight??1);if(seat){const item=selectedVIPOffer(g);if(item){if(item.kind==='custom'){ctx.save();ctx.translate(17,-10);miniCustom(ctx,item,35);ctx.restore();}else drawProduct(ctx,item.base,6,-43,24,34,false,true);}text('♫',28,-55,14,'#d4b66a');}if(g.bought)rect(14,-23,12,17,'#ead6aa');ctx.restore();
}
function chooseRegularExtra(p){
 const record=S.customerBook[p.customerKey??customerIdentity(p.actor,p.special).key];if(!isRegular(record)||!isInstrument(p.product)||S.phase!=='open'||Math.random()>=.25)return false;
 const families=profileForActor(p.actor).families,choices=offers(false,false).filter(o=>isInstrument(o.i)&&!isVIPProduct(o.i)&&families.includes(products[o.i].family)&&S.stock[o.i]>0&&!p.basket.includes(o.i)&&customerCanAfford(p,o.i));
 choices.sort((a,b)=>Number(products[b.i].family===record.favoriteFamily)-Number(products[a.i].family===record.favoriteFamily)||products[a.i].price-products[b.i].price);
 for(const item of choices)if(go(p,item.f,'browse')){p.product=item.i;p.bubble='다른 악기도 살펴볼까?';p.alternativeChecked=false;return true;}return false;
}
