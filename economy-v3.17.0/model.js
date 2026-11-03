(()=>{
const G=Game;
function closeDialogs(){document.querySelectorAll('dialog[open]').forEach(d=>d.close())}
const specs={lean:{name:'예약 기준1개',auto:true,safe:true,qty:1,express:false,at:1},manual:{name:'수동 보충',auto:false,safe:true,qty:1,express:false},automatic:{name:'기본 자동 위임',auto:true,safe:true,qty:1,express:false},express:{name:'기본 자동+긴급 개입',auto:true,safe:true,qty:1,express:true},tuned:{name:'예약 주문량3개',auto:true,safe:true,qty:3,express:false},rush:{name:'빠른 확장+기본 자동',auto:true,safe:false,qty:1,express:false}};
class Economy{
 constructor(mode,seed){this.mode=mode;this.spec=specs[mode];this.seed=seed;this.days=[];this.events=[];this.errors=[];this.firstStage={1:1};this.lastQueue=0;this.departed=new Set;this.totalManualOrders=0;this.manualCosts=0;this.totalAutoOrders=0;this.autoCosts=0;this.totalExpressFees=0;this.endingDay=null;this.nextMorning=0;this.costs={furniture:0,inventoryHire:0,cashierHire:0};this.claimedMoney=0;this.basicIds=G.products.map((p,i)=>i).filter(i=>!G.delayedProduct(i));this.stepCount=0;
 if(G.state.money!==G.Config.startingMoney||G.state.totalSales!==0)throw Error('Not a natural fresh shop');let n=seed;Math.random=()=>{n=(Math.imul(n,1664525)+1013904223)>>>0;return n/4294967296};
 this.place(1);for(let i=0;i<3;i++)this.place(0,i);this.place(4);
 }
 cashFloor(){return this.spec.safe?G.operatingReserve()+(this.spec.auto&&G.state.staffHired?Math.max(...this.basicIds.map(i=>G.purchaseCost(i)*G.state.staffPolicy.products[i].quantity)):0):G.settlementCushion()}
 afford(cost){return G.state.money>=cost+this.cashFloor()}
 event(type,data={}){this.events.push({type,day:G.state.day,stage:G.state.stage+1,money:G.state.money,...data})}
 place(t,product){closeDialogs();const cost=G.types[t].cost;if(G.state.money<cost+G.settlementCushion())return null;const before=G.state.expenses;G.edit(t);if(G.editing!==t)return null;let done=false;for(let dir=0;dir<4&&!done;dir++){const st=G.stageInfo();for(let y=1;y<st.h-1&&!done;y++)for(let x=1;x<st.w-1&&!done;x++){const p=G.previewAt(x,y);if(p?.valid)done=G.confirmPlacement()}if(!done)G.rotatePreview()}
 if(!done){G.endEdit();this.event('no-space',{typeId:t});return null}const f=G.state.furniture.at(-1);G.closeRackPicker();if(product!==undefined){if(t===0)G.setRackProduct(f.id,product);else if(t===5)G.setShelfItems(f.id,product)}closeDialogs();this.costs.furniture+=G.state.expenses-before;return f;
 }
 claim(){for(let pass=0;pass<24;pass++){let changed=false;for(const lane of ['growth','challenge']){const m=G.activeMission(lane);if(m&&G.missionStatus(m).ready){const before=G.state.money;if(G.claimMission(m.id)){this.claimedMoney+=G.state.money-before;this.event('mission',{id:m.id});closeDialogs();changed=true}}}if(!changed)break}}
 expand(){if(G.state.stage>=5||G.state.totalSales<10)return;const next=G.Stages[G.state.stage+1];const wages=G.staffWage()+(this.spec.auto&&G.state.staffHired===0?G.inventoryDailyWage(0):0);const threshold=this.spec.safe?next.cost+G.expansionReserve()+10*(next.rent+wages)+(this.spec.auto&&G.state.staffHired===0?G.inventoryHireCost(0):0):next.cost+G.settlementCushion();if(G.state.money>=threshold&&G.expandShop()){closeDialogs();this.firstStage[G.state.stage+1]=G.state.day;this.event('expand',{rent:next.rent});this.claim()}}
 hire(){const s=G.state;if(this.spec.auto){while(s.staffHired<G.staffSlots()){const wage=G.inventoryDailyWage(),cost=G.inventoryHireCost();const float=Math.max(...this.basicIds.map(i=>G.purchaseCost(i)*s.staffPolicy.products[i].quantity));if(this.spec.safe&&s.money<cost+10*(G.settlementCushion()+wage)+float)break;const before=s.expenses;if(!G.hireStaff())break;this.costs.inventoryHire+=s.expenses-before;this.event('hire-inventory',{count:s.staffHired,wage});}}
 if(this.lastQueue>=2){while(s.cashierHired<G.cashierSlots()){const station=s.furniture.filter(f=>f.t===1)[s.cashierHired+1];const build=station?0:G.types[1].cost;const required=build+G.Config.staff.hireCost+(this.spec.safe?10*(G.settlementCushion()+G.Config.staff.wage):G.settlementCushion()+G.Config.staff.wage);if(s.money<required)break;if(!station&&!this.place(1))break;const before=s.expenses;if(!G.hireCashier())break;this.costs.cashierHire+=s.expenses-before;this.event('hire-cashier',{count:s.cashierHired});}}
 if(this.spec.qty!==1||this.spec.at!==undefined)for(let i=0;i<G.products.length;i++)if(G.delayedProduct(i)&&(s.staffPolicy.products[i].quantity!==this.spec.qty||s.staffPolicy.products[i].at!==(this.spec.at??3)))G.setStaffProduct(i,true,this.spec.qty,this.spec.at??3);
 }
 assortment(){
 const s=G.state,unlocked=G.products.map((p,i)=>({p,i})).filter(({i})=>G.productUnlocked(i));
 for(const {p,i} of unlocked.filter(({p})=>p.kind==='instrument'&&p.family!=='drums')){
  if(G.displayedProductIds().includes(i))continue;
  const seed=G.purchaseCost(i),slots=s.furniture.filter(f=>f.t===0).flatMap(f=>Array.from({length:G.rackLimit()},(_,slot)=>({f,slot}))).filter(({f,slot})=>slot===0?f.p==null:f.p2==null);
  if(slots.length){if(!this.spec.safe||this.afford(seed))G.setRackProduct(slots[0].f.id,i,slots[0].slot)}
  else if(s.furniture.filter(f=>f.t===0).length<9&&this.afford(G.types[0].cost+(this.spec.safe?seed:0)))this.place(0,i);
 }
 const desired=unlocked.filter(({p})=>p.kind!=='instrument').map(({i})=>i);
 for(const i of desired){if(G.displayedProductIds().includes(i))continue;const cabinets=s.furniture.filter(f=>f.t===5),f=cabinets.find(f=>(f.items??[]).length<G.cabinetLimit());if(f)G.setShelfItems(f.id,[...(f.items??[]),i]);else if(this.afford(G.types[5].cost+(this.spec.safe?G.purchaseCost(i):0)))this.place(5,[i]);}
 if(G.drumsUnlocked()&&!s.furniture.some(f=>f.t===6)&&this.afford(G.types[6].cost+(this.spec.safe?G.purchaseCost(26):0)))this.place(6);
 if(G.furnitureUnlocked(7)&&!s.furniture.some(f=>f.t===7)&&this.afford(G.types[7].cost))this.place(7);
 }
 order(i,n,express=false){const unit=express?G.expressCost(i):G.purchaseCost(i),count=Math.min(999,n,Math.max(0,Math.floor((G.state.money-this.cashFloor())/unit)));if(!count)return false;const before=G.state.expenses;if(!G.orderProduct(i,express,false,count))return false;this.totalManualOrders++;this.manualCosts+=G.state.expenses-before;if(express)this.totalExpressFees+=(G.expressCost(i)-G.purchaseCost(i))*count;return true}
 restock(prep=false){
 const ids=G.displayedProductIds();const missionIds=new Set(['growth','challenge'].flatMap(l=>G.activeMission(l)?.goals.flatMap(g=>g.ids??[])??[]));
 ids.sort((a,b)=>Number(G.state.stock[a]>0)-Number(G.state.stock[b]>0)||Number(missionIds.has(b))-Number(missionIds.has(a))||Number(G.delayedProduct(a))-Number(G.delayedProduct(b))||a-b);
 for(const i of ids){const delayed=G.delayedProduct(i),covered=this.spec.auto&&G.state.staffHired>=(delayed?2:1);if(covered){if(this.spec.express&&!prep&&delayed&&G.state.stock[i]===0)this.order(i,1,true);continue}
 if(!prep&&G.state.stock[i]>(delayed?1:2))continue;
 if(delayed&&G.incomingQuantity(i)>0)continue;
 const target=delayed?3:G.products[i].kind==='instrument'?6:5,need=target-G.state.stock[i]-G.incomingQuantity(i);if(need>0)this.order(i,need);
 }
 }
 prepare(){this.claim();this.expand();this.hire();this.assortment();this.restock(true);if(G.state.hanaStory.phase==='offered')G.acceptHanaStory();if(G.state.hanaStory.phase==='accepted'&&G.state.stock[2]>0&&G.state.stock[7]>0){if(G.deliverHanaStory())this.giftCost=(this.giftCost??0)+G.purchaseCost(2)+G.purchaseCost(7)}closeDialogs()}
 validate(){const s=G.state,expected=s.ledgerStart+s.revenue+s.furnitureRevenue+s.missionRevenue-s.expenses;if(Math.abs(s.money-expected)>.01)throw Error('Cash ledger mismatch');if(s.stock.some(x=>!Number.isSafeInteger(x)||x<0))throw Error('Invalid stock');if(s.totalSales!==s.missionStats.sales.reduce((a,b)=>a+b,0))throw Error('Sales ledger mismatch')}
 oneDay(){const s=G.state,day=s.day;this.giftCost=0;const openingCash=s.money,startSales=[...s.missionStats.sales],startManual=this.totalManualOrders,startAuto=this.totalAutoOrders,startFees=this.totalExpressFees,startCap={...this.costs};this.prepare();const afterPrep=s.money;
 if(!G.openShop()){this.errors.push({day,type:'open-failed',message:document.querySelector('#toast').textContent});return false}
 let elapsed=0,nextCheck=10,peakQueue=0,minCash=s.money,emptySecs=0,blockedSecs=0,stockoutDepartures=0,opsMargin=0,stepSales=[...s.missionStats.sales];
 while(s.phase!=='settled'&&elapsed<360){
  const oldStock=[...s.stock],oldIncoming=Array(G.products.length).fill(0),oldSales=[...s.missionStats.sales];for(const o of s.pendingOrders)oldIncoming[o.product]+=o.quantity;
  G.update(.1);elapsed+=.1;this.stepCount++;
  const nowIncoming=Array(G.products.length).fill(0);for(const o of s.pendingOrders)nowIncoming[o.product]+=o.quantity;
  for(let i=0;i<G.products.length;i++){const sold=s.missionStats.sales[i]-oldSales[i];opsMargin+=sold*(G.products[i].price-G.purchaseCost(i));const added=s.stock[i]+nowIncoming[i]-oldStock[i]-oldIncoming[i]+sold;if(added>0){this.totalAutoOrders+=added/s.staffPolicy.products[i].quantity;this.autoCosts+=added*G.purchaseCost(i)}}
  const q=G.customers.filter(p=>p.state==='queue').length;peakQueue=Math.max(peakQueue,q);for(const p of G.customers)if(!p.companion&&p.state==='leave'&&!this.departed.has(p.id)){this.departed.add(p.id);if(!p.bought&&p.stockout)stockoutDepartures++}
  if(Math.round(elapsed*10)%10===0){const ids=G.displayedProductIds();if(ids.some(i=>s.stock[i]===0))emptySecs++;if(s.staffHired&&G.staffOrderPlan().some(r=>r.reason==='10일 운영비 보호'))blockedSecs++;this.validate()}
  if(s.phase==='open'&&elapsed>=nextCheck){this.restock(false);nextCheck+=10}
  minCash=Math.min(minCash,s.money);
 }
 if(s.phase!=='settled'){this.errors.push({day,type:'closing-stuck'});return false}
 this.validate();this.lastQueue=peakQueue;
 const fees=this.totalExpressFees-startFees,inventory=s.stock.reduce((a,n,i)=>a+n*G.purchaseCost(i),0),pipeline=s.pendingOrders.reduce((a,o)=>a+o.quantity*G.purchaseCost(o.product),0);
 const row={day,stage:s.stage+1,money:s.money,openingCash,afterPrep,minCash,revenue:s.revenue,sold:s.sold,visitors:s.visitors,cashNet:s.settlement.net,operatingSurplus:opsMargin-s.settlement.rent-s.settlement.wage-fees-this.giftCost,rent:s.settlement.rent,wages:s.settlement.wage,missionIncome:s.missionRevenue,expenses:s.expenses,inventoryCost:inventory,pendingCost:pipeline,cashPlusStock:s.money+inventory+pipeline,staff:s.staffHired,cashiers:s.cashierHired,manualOrders:this.totalManualOrders-startManual,autoOrders:this.totalAutoOrders-startAuto,expressFees:fees,stockoutDepartures,emptySeconds:emptySecs,blockedSeconds:blockedSecs,peakQueue,capitalCashOut:Object.keys(startCap).reduce((n,k)=>n+this.costs[k]-startCap[k],0),activeMission:G.activeMission()?.id??null,claimed:s.claimedMissions.length,drumsSold:s.missionStats.sales[26],salesByProduct:s.missionStats.sales.map((v,i)=>v-startSales[i]),displayed:G.displayedProductIds(),pendingUnits:s.pendingOrders.reduce((n,o)=>n+o.quantity,0)};this.days.push(row);
 if(s.ending.day&&!this.endingDay)this.endingDay=s.ending.day;
 if(G.endingPending()){G.showEnding();if(!G.continueAfterEnding())throw Error('ending continue failed')}else if(!G.nextDay())throw Error('next day failed');closeDialogs();return true;
 }
 result(){const s=G.state;return {mode:this.mode,label:this.spec.name,seed:this.seed,days:this.days,events:this.events,errors:this.errors,firstStage:this.firstStage,endingDay:this.endingDay,manualOrders:this.totalManualOrders,autoOrders:this.totalAutoOrders,manualInventoryCost:this.manualCosts,autoInventoryCost:this.autoCosts,expressFees:this.totalExpressFees,capitalCosts:this.costs,missionRewards:this.claimedMoney,final:{day:s.day,stage:s.stage+1,money:s.money,sales:s.totalSales,revenue:s.totalRevenue,missions:s.claimedMissions,staff:s.staffHired,cashiers:s.cashierHired,drums:s.missionStats.sales[26],policy:s.staffPolicy},notes:{cashBasis:'includes inventory purchases, furniture, expansion, hiring and settlement',operatingSurplus:'sales minus current unit purchase costs, rent, all wages, express surcharges, story gifts; no ads or optional discount decor used',initialStock:'nine starting instruments supplied by the game; stock valuation at purchase price'},steps:this.stepCount}}
}
window.Economy=Economy;
})();
