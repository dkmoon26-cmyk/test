from pathlib import Path
import json,hashlib,re,shutil,subprocess
from spans import span
v=Path(__file__).parent;base=Path('/workspace/little-tone-v3.25.0-web');out=Path('/workspace/little-tone-v3.26.0-web');shutil.copytree(base,out,dirs_exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest()[:12]
for old in (out/'assets').glob('*-v3260-*.webp'):old.unlink()
s=next(base.glob('app-*.js')).read_text();meta=json.loads(s.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);meta['version']='3.26.0';meta['schema']['version']=31;s='window.GameBuild=Object.freeze('+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+');\n'+s.split('\n',1)[1]
def exact(a,b):
 global s
 assert a in s,a[:100];s=s.replace(a,b)
art=json.loads((v/'art.json').read_text());groups=json.loads((v/'groups.json').read_text());assets={};baseDefs={};partDefs=[];markDefs=[];woodDefs=[]
def pack(items,name,cols):
 cw=max(a['w']for a in items)+12;ch=max(a['h']for a in items)+12;tiles=[];clips=[]
 for i,a in enumerate(items):
  p=v/f'tile-{name}-{i}.png';subprocess.run(['convert',str(v/a['file']),'-background','none','-gravity','center','-extent',f'{cw}x{ch}',str(p)],check=True);tiles.append(str(p));clips.append([i%cols*cw+(cw-a['w'])//2,i//cols*ch+(ch-a['h'])//2,a['w'],a['h']])
 output=v/(name+'.webp');subprocess.run(['montage',*tiles,'-tile',str(cols)+'x','-geometry','+0+0','-background','none','-quality','95','-define','webp:alpha-quality=100',str(output)],check=True);filename=name+'-'+sha(output.read_bytes())+'.webp';shutil.copy2(output,out/'assets'/filename);assets['assets/'+name+'.webp']='assets/'+filename
 return clips
for g,ids in enumerate(groups):
 items=[art['bases'][str(i)][rear]for rear in [0,1]for i in ids];clips=pack(items,f'bases-{g}-v3260',6)
 for col,i in enumerate(ids):
  views=[]
  for rear in [0,1]:
   a=dict(art['bases'][str(i)][rear]);a.pop('file');a['clip']=clips[rear*6+col];views.append(a)
  baseDefs[i]={'atlas':g,'views':views}
for key,dest in [('parts',partDefs),('motifs',markDefs),('woods',woodDefs)]:
 clips=pack(art[key],key+'-v3260',5)
 for a,clip in zip(art[key],clips):dest.append({'clip':clip,'w':a['w'],'h':a['h']})
config='const WoodArt26='+json.dumps(woodDefs,separators=(',',':'))+';\n'+'const BaseArt26='+json.dumps(baseDefs,separators=(',',':'))+';\nconst PartArt26='+json.dumps(partDefs,separators=(',',':'))+';\nconst MotifArt26='+json.dumps(markDefs,separators=(',',':'))+';\n'+(v/'config.js').read_text()
for name in ['quoteCustomAt','finishCustom','criticalAssetKeys','customTexture','setCustomDraftOption','drawCustomModel','bindModelDrag']:
 exact('function '+name+'(','function before26'+name[0].upper()+name[1:]+'(')
patch='\n'.join((v/n).read_text()for n in ['logic.js','premium_render.js','render.js','ui.js'])
for name in re.findall(r'^function (\w+)\(',patch,re.M):
 if 'function '+name+'(' in s:
  a,b=span(patch,name);x,y=span(s,name);s=s[:x]+patch[a:b]+'\n'+s[y:];patch=patch[:a]+patch[b:]
exact('// SOURCE: core/state',config+'\n'+patch+'\n// SOURCE: core/state')
# Public shared paths let verification exercise the actual production renderer and quote.
exact('  autoFillVIP25,pickVIP25,', '  C26,Fields26,rows26,clearTexture26,BaseArt26,defaults26,options26,validateDesign26,markValid26,addMark26,setDesign26,changeMark26,removeMark26,activeSide26,designAssets26,\n  get workshopDraft26(){return workshopDraft;},\n  autoFillVIP25,pickVIP25,')
pos=s.rfind('})();');s=s[:pos]+(v/'events.js').read_text()+'\n'+s[pos:]
for p in out.glob('app-*.js'):p.unlink()
appname='app-'+sha(s.encode())+'.js';(out/appname).write_text(s);(v/'app.js').write_text(s)
css=next(base.glob('style-*.css')).read_text()+'\n'+(v/'style.css').read_text();cssname='style-'+sha(css.encode())+'.css'
for p in out.glob('style-*.css'):p.unlink()
(out/cssname).write_text(css)
html=(base/'index.html').read_text().replace(next(base.glob('app-*.js')).name,appname).replace(next(base.glob('style-*.css')).name,cssname).replace('v3.25.0','v3.26.0');html=html.replace('window.GameAssets=Object.freeze({','window.GameAssets=Object.freeze({'+','.join(json.dumps(k)+':'+json.dumps(a)for k,a in assets.items())+',');(out/'index.html').write_text(html)
print(appname,cssname,len(s),len(baseDefs))
