const fs=require('fs'),vm=require('vm'),assert=require('assert');
const file=fs.readdirSync('/workspace/little-tone-v3.20.2-web').find(f=>/^app-.*\.js$/.test(f));
const source=fs.readFileSync('/workspace/little-tone-v3.20.2-web/'+file,'utf8').split('// SOURCE: systems/motion')[1].split('// SOURCE: render/interior')[0];
const box={module:{exports:{}}};vm.runInNewContext(source,box);const M=box.module.exports;
function person(){return {x:0,y:0,walkSpeed:1.2,stride:.75,path:[{x:.5,y:.5},{x:1,y:0},{x:1.5,y:.5},{x:2,y:0}]}}
function run(h){let p=person();for(let t=0;t<1.5-1e-8;t+=h)M.advance(p,h);return p}
let a=run(1/30),b=run(1/60);assert(Math.hypot(a.x-b.x,a.y-b.y)<1e-9);assert(Math.abs(a.gait-b.gait)<1e-9);
let p=person();let distance=0;for(let i=0;i<600&&p.path.length;i++)distance+=M.advance(p,1/60);assert.equal(p.path.length,0);assert.equal(p.x,2);assert.equal(p.y,0);
let expected=0,prev={x:0,y:0};for(const q of person().path){expected+=Math.hypot((q.x-prev.x-q.y+prev.y)*34,(q.x-prev.x+q.y-prev.y)*17)/Math.hypot(34,17);prev=q}assert(Math.abs(distance-expected)<1e-8);
for(let i=0;i<90;i++)M.settle(p,1/60);assert.equal(p.animationWeight,0);assert(Math.abs(((p.gait-.1875)*2)-Math.round((p.gait-.1875)*2))<1e-5);assert.equal(p.x,2);
let straight={x:0,y:0,path:[{x:10,y:10}]};M.advance(straight,1/60);assert(straight.velocity>0&&straight.velocity<.1);
let c=person();M.advance(c,.45);assert(Number.isFinite(c.x)&&c.path.length>0);assert(M.advance(c,0)===0);
console.log('PASS: 30/60 Hz equivalence, distance across corners, exact arrival, planted-foot settling, gradual start, fast-forward');

for (const route of [[{x:2,y:2}],Array(4).fill({x:2,y:2})]) {const p={x:2,y:2,path:route.slice(),velocity:0};M.advance(p,1/60);assert.equal(p.path.length,0);assert.equal(p.x,2);assert.equal(p.moving,false);}
const duplicate=person();duplicate.path=[{x:0,y:0},...duplicate.path.flatMap(q=>[q,{...q}])];for(let i=0;i<600&&duplicate.path.length;i++)M.advance(duplicate,1/60);assert.equal(duplicate.path.length,0);assert.equal(duplicate.x,2);assert.equal(duplicate.y,0);
console.log('PASS: zero-distance paths and leading/intermediate/trailing duplicate nodes');
