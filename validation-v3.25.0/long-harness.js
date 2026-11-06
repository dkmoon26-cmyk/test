(() => {
const G=Game,days=[],findings=[],events=[],blocked=new Set();let initialCash=G.state.money,initialAssets=0,firstRegular=null,firstStory=null,midChecks=0,saleChecks=0;const stageDays={1:G.state.day};
const dialogs=()=>{for(const d of document.querySelectorAll('dialog[open]'))d.close()};
function issue(type,detail){if(findings.filter(x=>x.type===type).length<10)findings.push({type,day:G.state.day,detail})}
function reserve(){return G.operatingReserve()}
function afford(cost,buffer=0){return G.state.money>=cost+reserve()+buffer}
function place(t,preferred=null){
 dialogs();if(!G.furnitureUnlocked(t)||!afford(G.types[t].cost))return null;const signature=[G.state.stage,G.state.furniture.length,t,preferred?.x,preferred?.y].join(':');if(blocked.has(signature))return null;
 G.edit(t);if(G.editing!==t)return null;let found=false;
 if(preferred){for(let n=0;n<(preferred.dir??0);n++)G.rotatePreview();if(G.previewAt(preferred.x,preferred.y)?.valid)found=G.confirmPlacement();}
 else for(let dir=0;dir<4&&!found;dir++){for(let y=1;y<G.stageInfo().h-1&&!found;y++)for(let x=1;x<=Math.min(8,G.stageInfo().w-2)&&!found;x++){const p=G.previewAt(x,y);if(p?.valid&&Furniture.cells({t,x,y,dir}).every(p=>p.x<=8))found=G.confirmPlacement();}if(!found)G.rotatePreview();}
 if(!found){G.endEdit();blocked.add(signature);dialogs();return null;}const f=G.state.furniture.at(-1);G.closeRackPicker();dialogs();return f;
}
function claim(){for(let n=0;n<30;n++){let claimed=false;for(const lane of ['growth','challenge']){const m=G.activeMission(lane);if(m&&G.missionStatus(m).ready){G.claimMission(m.id);claimed=true;dialogs();}}if(!claimed)break;}}
function book(){return Object.values(G.state.customerBook)}
function assets(){const s=G.state;let pending=0;for(const o of s.pendingOrders)pending+=G.products[o.product]?.cost*(o.quantity??o.qty??0)||0;return s.money+s.stock.reduce((v,n,i)=>v+n*G.products[i].cost,0)+s.furniture.filter(f=>f.t===15&&Number.isInteger(f.vipSlots?.[0])).reduce((v,f)=>v+G.products[f.vipSlots[0]].cost,0)+pending+s.custom.items.reduce((v,i)=>v+i.cost,0)+s.furniture.reduce((v,f)=>v+G.types[f.t].cost*.5,0);}
function staff(){if(G.state.stage<1)return;while(G.state.staffHired<G.staffSlots()){const cost=G.state.staffHired?2000000:500000;if(!afford(cost,1500000)||!G.hireStaff())break;}while(G.state.cashierHired<G.cashierSlots()&&afford(2500000,2000000)){const target=G.state.cashierHired+2;if(G.checkoutStations().length<target&&!place(1))break;if(!G.hireCashier())break;}}
function racks(){
 const ids=G.products.map((p,i)=>({p,i})).filter(({p,i})=>p.kind==='instrument'&&p.family!=='drums'&&!G.isVIPProduct(i)&&G.productUnlocked(i)).map(r=>r.i);
 for(const i of ids){if(G.state.furniture.some(f=>G.rackProducts(f).includes(i)))continue;let f=G.state.furniture.find(f=>f.t===0&&(f.p===null||f.p===undefined||G.rackLimit()===2&&(f.p2===null||f.p2===undefined)));
  if(!f)f=place(0);if(f){const slot=f.p==null?0:1;G.setRackProduct(f.id,i,slot);}}
 const addons=G.products.map((p,i)=>({p,i})).filter(({p,i})=>p.kind!=='instrument'&&G.productUnlocked(i)).map(r=>r.i),size=G.cabinetLimit();for(let n=0;n<addons.length;n+=size){let f=G.state.furniture.filter(f=>f.t===5)[Math.floor(n/size)];if(!f)f=place(5);if(f)G.setShelfItems(f.id,addons.slice(n,n+size));}
 if(G.drumsUnlocked()&&!G.state.furniture.some(f=>f.t===6))place(6);if(G.furnitureUnlocked(7)&&!G.state.furniture.some(f=>f.t===7))place(7);
}
function vipSetup(){
 if(G.state.stage<4)return;if(!G.state.vip.zone){const x=G.state.stage>=6?15:G.state.stage===5?13:11;if(!G.setVIPZone({x,y:1,w:8,h:8,doorSide:'left',doorAt:4})){issue('operator-vip-zone',document.querySelector('#toast').textContent);return;}}
 const z=G.state.vip.zone;for(const [t,n,spots]of[[15,3,[[z.x,2],[z.x+4,2],[z.x,4]]],[13,1,[[z.x+6,7]]],[14,1,[[z.x+3,7]]]]){for(let k=G.state.furniture.filter(f=>f.t===t).length;k<n;k++){const [x,y]=spots[k];if(!place(t,{x,y}))break;}}
 if(!G.state.vip.hired&&G.state.furniture.filter(f=>f.t===15).length===3&&G.state.furniture.some(f=>f.t===13)&&G.state.furniture.some(f=>f.t===14)&&afford(800000,4000000))G.hireVIPStaff();
}
function chosenVIP(){return ['electric','bass','acoustic'].map(family=>G.products.map((p,i)=>({p,i})).filter(({p,i})=>p.family===family&&G.isVIPProduct(i)&&G.productUnlocked(i)).sort((a,b)=>b.p.tier-a.p.tier||a.p.price-b.p.price)[0]?.i).filter(Number.isInteger)}
function refill(){const wanted=[...new Set([...G.displayedProductIds(),...(G.state.vip.hired?chosenVIP():[])])];for(const i of wanted){const goal=G.isVIPProduct(i)?1:G.delayedProduct(i)?3:8;const n=Math.max(0,goal-G.stockCount(i)-G.incomingQuantity(i));if(n&&afford(G.products[i].cost*n)&&G.orderProduct(i,false,false,n)){};}
 if(G.state.vip.hired){const fs=G.state.furniture.filter(f=>f.t===15),ids=chosenVIP();for(let n=0;n<fs.length;n++){const i=ids[n%ids.length];if(i!==undefined&&G.state.stock[i]>0)G.setVIPDisplay(fs[n].id,0,i);}}
}
function setup(mode){
 if(mode==='late'){const raw=JSON.parse(G.exportSaveData()),s=raw.state;s.stage=6;s.money=s.ledgerStart=100000000;s.dayRent=G.Stages[6].rent;s.pendingIntroductions=[];s.claimedMissions=G.MissionDefinitions.map(m=>m.id);s.introducedMissionGuests=G.MissionDefinitions.filter(m=>m.reward.actor!==undefined).map(m=>m.reward.actor);s.pendingMissionGuests=[];s.newFeatures=[];s.featureNotices=[];s.expansionNotice=null;if(!G.importSaveData(JSON.stringify(raw)))throw Error('late fixture rejected');initialCash=G.state.money;delete stageDays[1];stageDays[7]=1;}
 dialogs();place(1);for(const i of [0,1,2]){const f=place(0);if(f)G.setRackProduct(f.id,i);}place(4);dialogs();initialAssets=assets();
}
function prepare(mode){
 dialogs();claim();if(G.state.hanaStory.phase==='offered')G.acceptHanaStory();if(G.state.hanaStory.phase==='accepted')G.deliverHanaStory();
 if(mode==='growth'&&G.state.stage<6){const next=G.Stages[G.state.stage+1],extra=G.state.stage===3?10000000:2000000;if(afford(next.cost+next.rent*10,extra)&&G.expandShop()){stageDays[G.state.stage+1]=G.state.day;events.push({day:G.state.day,type:'expand',stage:G.state.stage+1,money:G.state.money});dialogs();}}
 racks();if(!G.state.furniture.some(f=>f.t===4))place(4);staff();vipSetup();for(const t of [2,3,8])if(!G.state.furniture.some(f=>f.t===t)&&afford(G.types[t].cost,3000000))place(t);refill();dialogs();
 if(mode==='late'&&G.beginDesignEdit&&G.state.day%30===0){if(G.beginDesignEdit('floor:'+(G.state.day%60?'marble':'blackMarble'))){const z=G.state.vip.zone;if(z){G.selectDesignTargets(z.x+','+z.y,(z.x+7)+','+(z.y+7));if(!G.commitDesign())G.resetDesignEditor();}else G.resetDesignEditor();}}
}
function invariant(){const s=G.state;if(!Number.isSafeInteger(s.money)||s.stock.some(n=>!Number.isSafeInteger(n)||n<0))throw Error('invalid money/stock');if(s.money!==s.ledgerStart+s.revenue+s.furnitureRevenue+s.missionRevenue-s.expenses)throw Error('cash ledger mismatch');if(s.totalSales!==s.missionStats.sales.reduce((v,n)=>v+n,0))throw Error('sales counter mismatch');saleChecks++;for(const p of G.customers)if(!p.companion){const cost=p.basket.reduce((v,i)=>v+G.products[i].price,0);if(new Set(p.basket).size!==p.basket.length||cost>(p.budget??Infinity))throw Error('basket budget/duplicate violation');if(p.basket.some(G.isVIPProduct))throw Error('VIP item in ordinary basket');}}
function canonical(x){if(Array.isArray(x))return x.map(canonical);if(x&&typeof x==='object')return Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])]));return x;}
function saveCheck(){const raw=G.exportSaveData(),before=JSON.parse(raw).state;try{SaveStore.decode(raw,JSON.parse(raw).state,G.saveRules());}catch(e){throw Error('save validation '+e.message)}if(!G.importSaveData(raw))throw Error('save restore failed');const after=JSON.parse(G.exportSaveData()).state;if(G.InteriorCatalog)for(const key of ['floorTiles','wallTiles','wallStock'])before.design[key]??={};for(const key of ['money','stock','totalSales','customerBook','vip','custom','design'])if(JSON.stringify(canonical(before[key]))!==JSON.stringify(canonical(after[key]))){if(key==='vip'){if(before.vip.sales!==after.vip.sales||before.vip.revenue!==after.vip.revenue)throw Error('VIP restore ledger');}else throw Error('restore changed '+key);}dialogs();midChecks++;}
function day(mode){prepare(mode);const s0=G.state,beforeRegular=book().filter(r=>r.regular).length,stockouts=new Set(),multi=new Map(),paid=new Set(),startMoney=s0.money,initialSold=s0.totalSales;let maxBasket=0,totalMulti=0,maxAffinity=0,elapsed=0,mid=false;const vipBefore=s0.vip.sales;
 if(!G.openShop()){issue('open-failed',{money:s0.money,ready:G.shopReady(),toast:document.querySelector('#toast').textContent});return false;}dialogs();
 while(G.state.phase!=='settled'&&elapsed<600){G.update(.1);elapsed+=.1;for(const p of G.customers){maxBasket=Math.max(maxBasket,p.basket.length);if(p.stockout)stockouts.add(p.id);if(p.bought&&!paid.has(p.id)){paid.add(p.id);const n=p.basket.filter(i=>G.products[i].kind==='instrument').length;if(n>1){multi.set(p.id,n);totalMulti++;}}}if(Math.round(elapsed*10)%40===0){invariant();const rs=book();if(firstRegular===null&&rs.some(r=>r.regular)){firstRegular=G.state.day;events.push({type:'first-regular',day:G.state.day});}if(firstStory===null&&G.state.hanaStory.phase!=='locked'){firstStory=G.state.day;events.push({type:'hana-story',day:G.state.day});}}
 if(!mid&&G.state.day%10===0&&elapsed>=60){saveCheck();mid=true;}}
 if(G.state.phase!=='settled'){issue('day-stuck',{elapsed,people:G.customers.map(p=>({id:p.id,state:p.state,path:p.path.length}))});return false;}
 invariant();const s=G.state,r=s.settlement,rs=book();if(s.money!==s.ledgerStart+r.net||r.net!==r.income-r.expenses)throw Error('settlement mismatch');if(s.totalSales-initialSold!==s.sold)throw Error('daily sales mismatch');
 const ordinarySales=paid.size;const row={day:s.day,stage:s.stage+1,money:s.money,revenue:s.revenue,expenses:s.expenses,net:r.net,sold:s.sold,visitors:s.visitors,ordinaryBuyingVisits:ordinarySales,multiBuyingVisits:totalMulti,maxBasket,stockoutVisitors:stockouts.size,regulars:rs.filter(r=>r.regular).length,regularShare:rs.filter(r=>r.regular).length/Math.max(1,rs.length),customers:rs.length,avgAffinity:rs.reduce((v,r)=>v+r.satisfaction,0)/Math.max(1,rs.length),vipSales:s.vip.sales-vipBefore,vipRevenue:s.vip.revenue,staff:s.staffHired+s.cashierHired+Number(s.vip.hired),operatingReserve:reserve(),belowReserve:s.money<reserve(),warehouseValue:s.stock.reduce((v,n,i)=>v+n*G.products[i].cost,0),assets:assets(),pendingOrders:s.pendingOrders.length,closeSeconds:+(elapsed-120).toFixed(1),hana:s.hanaStory.phase,claimed:s.claimedMissions.length};days.push(row);
 if(s.day%10===0)saveCheck();dialogs();if(G.endingPending()){G.showEnding();if(!G.continueAfterEnding())throw Error('ending resume');}else if(!G.nextDay())throw Error('next day');dialogs();return true;
}
window.Long={setup,day,days,findings,events,invariant,saveCheck,summary(){return {days,findings,events,initialCash,initialAssets,firstRegular,firstStory,stageDays,saveChecks:midChecks,invariantChecks:saleChecks,finalBook:book(),final:{cash:G.state.money,stage:G.state.stage+1,totalSales:G.state.totalSales,vip:G.state.vip,hana:G.state.hanaStory,staff:G.state.staffHired+G.state.cashierHired+Number(G.state.vip.hired)}}}};
})();
