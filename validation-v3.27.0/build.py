from pathlib import Path
import json,hashlib,re,subprocess,shutil
from spans import span,balanced_end
v=Path(__file__).parent;base=Path('/workspace/little-tone-v3.26.0-web');out=Path('/workspace/little-tone-v3.27.0-web');shutil.copytree(base,out,dirs_exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest()[:12]
for p in(out/'assets').glob('showcases-v3270-*.webp'):p.unlink()
entries=[];tiles=[];cw=0;ch=0
for kind in ['custom','vip']:
 p=v/'source-art'/(kind+'.png');W,H=map(int,subprocess.check_output(['identify','-format','%w %h',str(p)]).split());views=[]
 for rear in range(2):
  dest=v/f'{kind}-{rear}.webp';x=round(rear*W/2)+2;w=round((rear+1)*W/2)-x-2
  subprocess.run(['convert',str(p),'-crop',f'{w}x{H-4}+{x}+2','+repage','-channel','A','-threshold','70%','+channel','-trim','+repage','-resize','512x512>','-define','webp:lossless=true',str(dest)],check=True)
  w,h=map(int,subprocess.check_output(['identify','-format','%w %h',str(dest)]).split());cw=max(cw,w+12);ch=max(ch,h+12);views.append({'file':str(dest),'w':w,'h':h})
 entries.append(views)
for row,views in enumerate(entries):
 for col,a in enumerate(views):
  p=v/f'tile-{row}-{col}.png';subprocess.run(['convert',a['file'],'-background','none','-gravity','center','-extent',f'{cw}x{ch}',str(p)],check=True);tiles.append(str(p));a['clip']=[col*cw+(cw-a['w'])//2,row*ch+(ch-a['h'])//2,a['w'],a['h']];del a['file']
p=v/'showcases-v3270.webp';subprocess.run(['montage',*tiles,'-tile','2x2','-geometry','+0+0','-background','none','-quality','95','-define','webp:alpha-quality=100',str(p)],check=True);asset='showcases-v3270-'+sha(p.read_bytes())+'.webp';shutil.copy2(p,out/'assets'/asset)
s=next(base.glob('app-*.js')).read_text();meta=json.loads(s.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);meta['version']='3.27.0';meta['schema']['version']=32;s='window.GameBuild=Object.freeze('+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+');\n'+s.split('\n',1)[1]
for name in ['furnitureAssetKeys','criticalAssetKeys','furniturePickSprite']:
 s=s.replace('function '+name+'(','function before27'+name[0].upper()+name[1:]+'(')
patch=(v/'custom.js').read_text()+'\n'+(v/'cases.js').read_text()
for name in re.findall(r'^function (\w+)\(',patch,re.M):
 if'function '+name+'('in s:
  a,b=span(patch,name);x,y=span(s,name);s=s[:x]+patch[a:b]+s[y:];patch=patch[:a]+patch[b:]
s=re.sub(r'f.t===9\?-1000:f.x\s*\+\s*f.y','furnitureDepth27(f)',s)
# Split the movable surface motif below the pickguard and every mounted part.
a,b=span(s,'customTexture26');f=s[a:b];start=f.index(" if(!rear&&d.guard!=='none')");end=balanced_end(f,f.index('{',start),'{','}');guard=f[start:end];f=f[:start]+f[end:];f=f.replace("const metal=d.metal", "drawGuard27(c,base,d,rear);const metal=d.metal")
f=f.replace("if(rear)tintRegionPremium26(c,a,neckColor,(x,y,r,gg,b)=>Math.abs(x-g.x)<.11&&y>.13&&y<g.neckEnd&&r>gg*1.08);", "if(rear)paintRegion27(c,base,rear,'neck',neckColor);")
f=f.replace("tintRegionPremium26(c,a,headColor,(x,y)=>y<.16);", "paintRegion27(c,base,rear,'head',headColor);")
s=s[:a]+f+s[b:]
patch+='\nfunction drawGuard27(c,base,d,rear){const a=BaseArt26[base].views[rear?1:0],W=a.w,H=a.h,g=modelGeometry26(base,rear),p=bodyPath26(base,rear);'+guard+'}\n'
s=s.replace("d[key]=value;if(key==='pickupShape'", "d[key]=value;if(key==='neckColor'){workshopAngle=180;selectedMark26=-1;}if(key==='pickupShape'")
s=s.replace('min="8" max="48"','min="4" max="180"').replace('바디 안에서 부품을 피해서 배치해주세요','문양 일부가 바디 안에 보이도록 배치해주세요')
s=s.replace("function clearTexture26(){", "function clearTexture26(){tintLayers27.clear();")
s=s.replace('// SOURCE: core/state', 'const CaseArt27='+json.dumps(entries,separators=(',',':'))+';\n'+patch+'\n// SOURCE: core/state',1)
s=s.replace('  C26,Fields26,', '  CaseArt27,caseAsset27,regionPath27,paintRegion27,\n  C26,Fields26,')
pos=s.rfind('})();');s=s[:pos]+(v/'events.js').read_text()+'\n'+s[pos:]
for p in out.glob('app-*.js'):p.unlink()
name='app-'+sha(s.encode())+'.js';(out/name).write_text(s);(v/'app.js').write_text(s)
html=(base/'index.html').read_text().replace(next(base.glob('app-*.js')).name,name).replace('v3.26.0','v3.27.0').replace('window.GameAssets=Object.freeze({','window.GameAssets=Object.freeze({"assets/showcases-v3270.webp":"assets/'+asset+'",');(out/'index.html').write_text(html)
source=out/'source'/'display-and-custom-v327';source.mkdir(exist_ok=True)
for n in ['custom.js','cases.js','events.js']:shutil.copy2(v/n,source/n)
print(name,asset,'case asset bytes',p.stat().st_size if p.exists()else'')
