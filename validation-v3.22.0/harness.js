(() => {
 const G=Game, findings=[], days=[], coverage={specials:{},states:{},peak:0,saveChecks:0,orders:0,claims:0,expansions:0};
 const baseline=JSON.parse(G.exportSaveData()).state;
 function issue(type,detail){if(findings.filter(f=>f.type===type).length<5)findings.push({type,day:G.state.day,stage:G.state.stage+1,detail});}
 function dialogs(){for(const d of document.querySelectorAll('dialog[open]'))d.close();}
 function checkSave(label){
  const raw=G.exportSaveData(), before=JSON.parse(raw).state;
  if(!G.importSaveData(raw)){
   let error='unknown';try{SaveStore.decode(raw,baseline,G.saveRules());}catch(e){error=e.message}
   issue('save-import-failed',{label,error,toast:document.querySelector('#toast').textContent});return false;
  }
  const after=JSON.parse(G.exportSaveData()).state;
  for(const key of ['day','stage','phase','money','totalSales','stock','pendingOrders','claimedMissions'])if(JSON.stringify(before[key])!==JSON.stringify(after[key]))issue('save-mismatch',{label,key,before:before[key],after:after[key]});
  coverage.saveChecks++;dialogs();return true;
 }
 function place(t,product){
  dialogs();G.edit(t);
  if(G.editing!==t){issue('placement-start-failed',{t});return null;}
  let found=false;
  for(let dir=0;dir<4&&!found;dir++){
   const st=G.stageInfo();
   for(let y=1;y<st.h-1&&!found;y++)for(let x=1;x<st.w-1&&!found;x++){
    const v=G.previewAt(x,y);if(v?.valid){found=G.confirmPlacement();}
   }
   if(!found)G.rotatePreview();
  }
  if(!found){G.endEdit();issue('placement-no-space',{t});return null;}
  const f=G.state.furniture.at(-1);G.closeRackPicker();
  if(product!==undefined){if(t===0)G.setRackProduct(f.id,product);else if(t===5)G.setShelfItems(f.id,product);}
  dialogs();return f.id;
 }
 function claimReady(){for(let n=0;n<20;n++){let progress=false;for(const lane of ['growth','challenge']){const m=G.activeMission(lane);if(m&&G.missionStatus(m).ready){if(G.claimMission(m.id)){coverage.claims++;progress=true;dialogs()}}}if(!progress)break}}
 function refill(target=10){for(const i of G.displayedProductIds()){const n=target-G.state.stock[i]-G.incomingQuantity(i);if(n>0&&G.state.money>=G.products[i].cost*n+G.settlementCushion()){if(G.orderProduct(i,false,false,n))coverage.orders++;}}}
 function validate(){
  const s=G.state;
  if(!Number.isFinite(s.money)||s.stock.some(n=>!Number.isSafeInteger(n)||n<0))throw Error('Invalid money/stock');
  const expected=s.ledgerStart+s.revenue+s.furnitureRevenue+s.missionRevenue-s.expenses;
  if(Math.abs(s.money-expected)>.01)issue('cash-ledger-mismatch',{actual:s.money,expected});
  if(s.totalSales!==s.missionStats.sales.reduce((a,b)=>a+b,0))issue('sales-ledger-mismatch',{total:s.totalSales,detail:s.missionStats.sales.reduce((a,b)=>a+b,0)});
  for(const p of G.customers){if(!Number.isFinite(p.x+p.y+(p.gait??0)+(p.animationWeight??0)))throw Error('Invalid character motion');if(Math.hypot(p.avoidX??0,p.avoidY??0)>.261)issue('offset-limit',{id:p.id});}
 }
 function day({dt=.1,saveMid=true,restock=true}={}){
  dialogs();if(restock)refill();claimReady();dialogs();
  if(!G.openShop()){issue('open-failed',{ready:G.shopReady(),toast:document.querySelector('#toast').textContent});return false}
  let elapsed=0,mid=false;const stalls=new Map();let maxPathAge=0;
  while(G.state.phase!=='settled'&&elapsed<360){
   G.update(dt);elapsed+=dt;
   for(const p of G.customers){coverage.states[p.state]=(coverage.states[p.state]??0)+1;if(p.special)coverage.specials[p.special]=(coverage.specials[p.special]??0)+1;
    const prev=stalls.get(p.id);const still=prev&&Math.hypot(p.x-prev.x,p.y-prev.y)<1e-5;const age=still?prev.age+dt:0;stalls.set(p.id,{x:p.x,y:p.y,age});if(p.path.length)maxPathAge=Math.max(maxPathAge,age);
   }
   coverage.peak=Math.max(coverage.peak,G.customers.length);
   if(Math.round(elapsed/dt)%20===0){validate();G.draw()}
   if(saveMid&&!mid&&elapsed>60){checkSave('midday');mid=true;}
  }
  if(G.state.phase!=='settled'){issue('day-stuck',{elapsed,phase:G.state.phase,guests:G.customers.map(p=>({id:p.id,state:p.state,x:p.x,y:p.y,path:p.path.length,companion:p.companion}))});return false}
  validate();const s=G.state,r=s.settlement;
  if(r.net!==r.income-r.expenses||Math.abs(s.money-(s.ledgerStart+r.net))>.01)issue('settlement-ledger-mismatch',r);
  days.push({day:s.day,stage:s.stage+1,sold:s.sold,visitors:s.visitors,money:s.money,net:r.net,closeSeconds:+(elapsed-120).toFixed(2),maxPathStall:+maxPathAge.toFixed(2)});
  checkSave('settled');dialogs();
  if(G.endingPending()){G.showEnding();if(!G.continueAfterEnding()){issue('ending-resume-failed',{});return false}}
  else if(!G.nextDay()){issue('next-day-failed',{});return false}
  dialogs();return true;
 }
 function setup(){place(1);for(let i=0;i<3;i++)place(0,i);place(4);validate();}
 function fixtureUnlock(){
  const s=G.state;const grant=1e9-s.money;s.money+=grant;s.ledgerStart+=grant;
  for(let pass=0;pass<5;pass++){
   for(let i=0;i<G.products.length;i++)if(G.productUnlocked(i))s.missionStats.sales[i]=Math.max(100,s.missionStats.sales[i]);
   s.totalSales=s.missionStats.sales.reduce((a,b)=>a+b,0);s.missionStats.bestDay=100;claimReady();
  }
 }
 function enrich(){
  fixtureUnlock();
  for(let i=0;i<G.products.length;i++)if(G.productUnlocked(i)){
   const p=G.products[i];if(p.kind==='instrument'&&p.family!=='drums'&&!G.isVIPProduct(i)&&!G.state.furniture.some(f=>G.rackProducts(f).includes(i))&&G.state.furniture.filter(f=>f.t===0).length<9)place(0,i);
  }
  if(!G.state.furniture.some(f=>f.t===5))place(5,[3,4,6].filter(i=>G.productUnlocked(i)));
  if(G.drumsUnlocked()&&!G.state.furniture.some(f=>f.t===6))place(6);
  if(G.furnitureUnlocked(7)&&!G.state.furniture.some(f=>f.t===7))place(7);
  while(G.state.staffHired<G.staffSlots())if(!G.hireStaff())break;
  while(G.checkoutStations().length<1+G.cashierSlots())if(!place(1))break;
  while(G.state.cashierHired<G.cashierSlots())if(!G.hireCashier())break;
  if(G.adUnlocked())G.bookAd();refill(20);dialogs();
 }
 window.Sim={setup,day,enrich,fixtureUnlock,checkSave,findings,days,coverage,dialogs,validate,place};
})();
