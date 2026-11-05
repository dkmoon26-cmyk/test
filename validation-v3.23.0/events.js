// Runtime atlas readiness invalidates thumbnails and static world caches once.
for(const [key,set]of [['materials',im=>{materialAtlas23=im;materialTexture.cache.clear();}],['props',im=>{propAtlas23=im;propCache23.clear();}]]){const im=new Image();im.onload=()=>{set(im);sceneCacheKey='';clearFurnitureBodyCache();premiumCaseCache.clear();renderDirty=true;if($('management').open)renderPanel();};im.src=GameAssets['assets/'+key+'-v3230.webp'];}
document.body.insertAdjacentHTML('beforeend','<div id="entranceEditBar" class="world-edit-bar" hidden><span id="entranceEditStatus"></span><button id="entranceEditCancel">취소</button><button id="entranceEditConfirm" disabled>확정</button></div>');
$('entranceEditCancel').onclick=()=>finishEntranceEdit(false);$('entranceEditConfirm').onclick=()=>finishEntranceEdit(true);
document.addEventListener('click',e=>{const b=e.target.closest('[data-entrance-edit],[data-unlock-go]');if(!b)return;e.stopImmediatePropagation();if(b.dataset.entranceEdit!==undefined)beginEntranceEdit(+b.dataset.entranceEdit);else{closeUnlockNotice();openMenuSection(b.dataset.unlockGo);}},true);
for(const type of ['pointerdown','pointermove','pointerup','pointercancel'])canvas.addEventListener(type,e=>{if(!vipEditor&&entranceEditor===null)return;e.stopImmediatePropagation();e.preventDefault();if(type==='pointerdown'){canvas.setPointerCapture?.(e.pointerId);if(vipEditor){vipDragStart=tileAt(e);selectVIPTile(vipDragStart);}else previewEntrance(e);}if(type==='pointermove'&&e.buttons){if(vipEditor&&vipDragStart)selectVIPTile(tileAt(e));else if(entranceEditor!==null)previewEntrance(e);}if(type==='pointerup'||type==='pointercancel'){if(vipEditor&&vipDragStart&&type==='pointerup')selectVIPTile(tileAt(e));vipDragStart=null;wasDragged=true;activePointers.clear();drag=null;pinch=null;}},true);
canvas.addEventListener('click',e=>{if(vipEditor||entranceEditor!==null){e.preventDefault();e.stopImmediatePropagation();}},true);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&entranceEditor!==null){e.preventDefault();finishEntranceEdit(false);}},true);
// Status summaries remain live while the business sheet is open.
const originalRefresh23=Game.refreshLivePanel;Game.refreshLivePanel=refreshLivePanel;

$('vipEditBar').querySelector('b').textContent='VIP구역 설정';
$('vipEditStatus').insertAdjacentHTML('afterend','<div class="vip-door-tools"><label>문 방향 <select id="vipDraftSide"><option value="left">왼쪽</option><option value="top">위쪽</option><option value="right">오른쪽</option><option value="bottom">아래쪽</option></select></label><label>위치 <input id="vipDraftAt" type="number" min="2" max="9" value="3"></label></div>');
$('vipDraftSide').onchange=updateVIPDraftDoor;$('vipDraftAt').onchange=updateVIPDraftDoor;
$('missionPanel').addEventListener('click',e=>{const b=e.target.closest('[data-story]');if(!b||b.disabled)return;e.stopImmediatePropagation();if(b.dataset.story==='accept')acceptHanaStory();else if(b.dataset.story==='deliver')deliverHanaStory();renderMissions();},true);

$('closeUnlock').textContent='확인';
