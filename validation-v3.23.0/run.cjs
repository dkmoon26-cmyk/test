const {chromium}=require('/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),http=require('http'),path=require('path');
const root='/workspace/little-tone-v3.23.0-web',out='/workspace/little-tone-v3.23.0-validation';
(async()=>{const server=http.createServer((q,r)=>{try{const f=path.join(root,q.url==='/'?'index.html':q.url);r.setHeader('Content-Type',f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':f.endsWith('.webp')?'image/webp':'text/html');r.end(fs.readFileSync(f))}catch{r.statusCode=404;r.end()}}).listen(8873,'127.0.0.1');const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const results=[];try{
for(const mode of ['organic','stages'])for(const seed of [17,2026,731]){
 const context=await browser.newContext({viewport:{width:seed===731?390:1440,height:seed===731?844:900}});const p=await context.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.addInitScript(seed=>{let n=seed;Math.random=()=>{n=(Math.imul(n,1664525)+1013904223)>>>0;return n/4294967296}},seed);
 await p.goto('http://127.0.0.1:8873');await p.click('#newGame');await p.click('#createShop');await p.click('#start');await p.evaluate(()=>Game.skipTutorial());await p.evaluate(()=>{window.requestAnimationFrame=()=>0});await p.waitForTimeout(50);await p.evaluate(fs.readFileSync(out+'/harness.js','utf8'));await p.evaluate(()=>Sim.setup());
 for(let i=0;i<(mode==='organic'?15:18);i++){
  if(mode==='stages'&&i%3===0){if(i>0)await p.evaluate(()=>{Sim.fixtureUnlock();if(!Game.expandShop())Sim.findings.push({type:'expansion-failed',day:Game.state.day});Sim.dialogs();Sim.coverage.expansions++});await p.evaluate(()=>{Sim.enrich();for(const t of [2,3,8,10])if(!Game.state.furniture.some(f=>f.t===t))Sim.place(t);if(!Game.state.furniture.some(f=>f.t===9)){const seat=Game.state.furniture.find(f=>f.t===4);if(seat){Game.edit(9);const v=Game.previewAt(seat.x,seat.y);if(!v?.valid||!Game.confirmPlacement())throw Error('Rug placement failed')}else Sim.place(9)}Sim.dialogs()});}
  const success=await p.evaluate(({i,mode,seed})=>Sim.day({dt:seed===731?1/30:.1,saveMid:i%3===0,restock:mode==='stages'||i!==5}),{i,mode,seed});
  if(!success)break;
 }
 const result=await p.evaluate(()=>({days:Sim.days,coverage:Sim.coverage,findings:Sim.findings,final:{day:Game.state.day,stage:Game.state.stage+1,money:Game.state.money,sales:Game.state.totalSales,missions:Game.state.claimedMissions}}));result.mode=mode;result.seed=seed;result.errors=errors;results.push(result);fs.writeFileSync(out+'/regression-days.json',JSON.stringify(results,null,2));console.log(JSON.stringify({mode,seed,days:result.days.length,coverage:result.coverage,findings:result.findings,errors}));await context.close();
}
}finally{await browser.close();server.close()}})().catch(e=>{console.error(e);process.exitCode=1});
