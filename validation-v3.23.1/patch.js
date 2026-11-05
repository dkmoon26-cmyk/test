// Cached masks are computed once at build time, so local/cross-origin artwork
// never needs a pixel read at runtime.
function prop23(name){
 if(propCache23.has(name))return propCache23.get(name);
 const clip=propClips23[name],mask=propMasks231[name];
 if(!propAtlas23?.complete||!propAtlas23.naturalWidth||!clip||!mask)return null;
 const [x,y,w,h]=clip,cv=document.createElement('canvas');cv.width=w;cv.height=h;
 try{const c=cv.getContext('2d');c.beginPath();for(const [mx,my,mw,mh]of mask.rects)c.rect(mx,my,mw,mh);c.clip();c.drawImage(propAtlas23,x,y,w,h,0,0,w,h);}
 catch(error){console.warn('Optional shop artwork unavailable:',name,error.name);propCache23.set(name,null);return null;}
 propCache23.set(name,cv);return cv;
}
function positionTutorial231(){
 const card=$('tutorialCard'),home=$('tutorialHome');if(!card||!home||card.hidden)return;
 if(card.parentElement!==home){card.style.maxHeight='';card.style.overflowY='';return;}
 const vv=window.visualViewport,w=vv?.width??innerWidth,h=vv?.height??innerHeight,left=vv?.offsetLeft??0,top=vv?.offsetTop??0;
 const width=Math.max(80,Math.min(390,w-24));home.style.position='fixed';home.style.transform='none';home.style.left=(left+12)+'px';home.style.width=width+'px';home.style.maxWidth=width+'px';
 card.style.maxHeight=Math.max(80,h-24)+'px';card.style.overflowY='auto';
 const preferred=innerWidth<=650?134:126,cardHeight=card.getBoundingClientRect().height;
 home.style.top=Math.max(top+12,Math.min(top+preferred,top+h-cardHeight-12))+'px';
}
function syncTutorialHost(){before231SyncTutorialHost();positionTutorial231();}
// Decorative atlases have solid-color / no-prop fallbacks and must not block play.
function criticalAssetKeys(s=S){return before23CriticalAssetKeys(s);}
