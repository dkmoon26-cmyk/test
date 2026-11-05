// Catalog actions share the same quote/commit paths used by simulation.
document.body.insertAdjacentHTML('beforeend',`<dialog id="catalogDetail" aria-labelledby="catalogDetailTitle"><header class="atelier-header"><h2 id="catalogDetailTitle">아이템</h2><button id="catalogDetailClose" aria-label="닫기">×</button></header><div id="catalogDetailBody"></div></dialog><aside id="designEditBar" hidden><div><b id="designEditName"></b><span id="designEditCost" role="status"></span></div><div><button id="designEditCancel">취소</button><button id="designEditConfirm" class="primary" disabled>적용</button></div></aside>`);
$('catalogDetailClose').onclick=()=>$('catalogDetail').close();$('designEditCancel').onclick=()=>{resetDesignEditor();setTab('furniture');};$('designEditConfirm').onclick=()=>{if(commitDesign())setTab('furniture');};
document.addEventListener('click',e=>{
 const card=e.target.closest('[data-catalog]');if(card){e.preventDefault();e.stopImmediatePropagation();if(!suppressCatalogClick)openCatalogDetail(card.dataset.catalog,card.dataset.installed);return;}
 const build=e.target.closest('[data-catalog-build]');if(build&&!build.disabled){$('catalogDetail').close();edit(+build.dataset.catalogBuild);return;}
 const start=e.target.closest('[data-design-start]');if(start&&!start.disabled){beginDesignEdit(start.dataset.designStart,start.dataset.designMoving);return;}
 const recall=e.target.closest('[data-wall-recall]');if(recall){const [,wall,slot]=recall.dataset.wallRecall.split(':');if(recallWallItem(wall,+slot)){$('catalogDetail').close();renderPanel();}return;}
},true);
function designPointerFinish(e,cancelled){
 if(!designEditor||!designStroke||e.pointerId!==designStroke.id)return false;const start=designStroke.start;if(!cancelled){const target=designTargetAt(e);if(target&&start)selectDesignTargets(start,target);}else {designEditor.keys=[];updateDesignBar();invalidateDesign();}designStroke=null;catalogDrag=null;return true;
}
document.addEventListener('pointerdown',e=>{
 const card=e.target.closest('[data-catalog]');if(card&&!card.dataset.installed&&!card.dataset.catalog.startsWith('f:')&&S.phase==='prepare'){catalogDrag={key:card.dataset.catalog,x:e.clientX,y:e.clientY,id:e.pointerId};}
 if(!designEditor||e.target!==canvas)return;e.preventDefault();e.stopImmediatePropagation();const target=designTargetAt(e);designStroke={id:e.pointerId,start:target};if(target)selectDesignTargets(target);
},true);
document.addEventListener('pointermove',e=>{
 if(catalogDrag&&e.pointerId===catalogDrag.id&&!designEditor&&Math.hypot(e.clientX-catalogDrag.x,e.clientY-catalogDrag.y)>10&&(e.pointerType!=='touch'||Math.abs(e.clientX-catalogDrag.x)>Math.abs(e.clientY-catalogDrag.y)*1.3)){const pending={...catalogDrag};if(beginDesignEdit(pending.key)){catalogDrag=pending;suppressCatalogClick=true;designStroke={id:e.pointerId,start:null};}}
 if(!designEditor||!designStroke||e.pointerId!==designStroke.id)return;e.preventDefault();e.stopImmediatePropagation();const target=designTargetAt(e);if(target){designStroke.start??=target;selectDesignTargets(designStroke.start,target);}
},true);
document.addEventListener('pointerup',e=>{if(designPointerFinish(e,false)){e.preventDefault();e.stopImmediatePropagation();setTimeout(()=>suppressCatalogClick=false,0);}else catalogDrag=null;},true);
document.addEventListener('pointercancel',e=>{if(designPointerFinish(e,true)){e.preventDefault();e.stopImmediatePropagation();}catalogDrag=null;suppressCatalogClick=false;},true);
canvas.addEventListener('click',e=>{if(designEditor){e.preventDefault();e.stopImmediatePropagation();}},true);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&designEditor){e.preventDefault();e.stopImmediatePropagation();resetDesignEditor();setTab('furniture');}},true);
