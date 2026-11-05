from pathlib import Path
import json,re,hashlib,shutil
from spans import span
v=Path(__file__).parent;base=Path('/workspace/little-tone-v3.23.0-web');out=Path('/workspace/little-tone-v3.23.1-web');shutil.copytree(base,out,dirs_exist_ok=True)
oldapp=next(base.glob('app-*.js'));s=oldapp.read_text();first,rest=s.split('\n',1);meta=json.loads(first[len('window.GameBuild=Object.freeze('):-2]);meta['version']='3.23.1';s='window.GameBuild=Object.freeze('+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+');\n'+rest
masks=json.loads((v/'prop-masks.json').read_text());assert hashlib.sha256((base/'assets'/masks['source']).read_bytes()).hexdigest()==masks['sha256']
s=s.replace('const propCache23=new Map();','const propMasks231='+json.dumps(masks['masks'],separators=(',',':'))+';\nconst propCache23=new Map();')
s=s.replace('function syncTutorialHost(','function before231SyncTutorialHost(')
patch=(v/'patch.js').read_text()
for name in ['prop23','criticalAssetKeys']:
 a,b=span(patch,name);x,y=span(s,name);s=s[:x]+patch[a:b]+'\n'+s[y:];patch=patch[:a]+patch[b:]
pos=s.rfind('})();');s=s[:pos]+patch+"\nwindow.addEventListener('resize',positionTutorial231);window.visualViewport?.addEventListener('resize',positionTutorial231);window.visualViewport?.addEventListener('scroll',positionTutorial231);\n"+s[pos:]
for p in out.glob('app-*.js'):p.unlink()
appname='app-'+hashlib.sha256(s.encode()).hexdigest()[:12]+'.js';(out/appname).write_text(s);(v/'app.js').write_text(s)
cssold=next(base.glob('style-*.css'));css=cssold.read_text()+'\n'+(v/'style.css').read_text();cssname='style-'+hashlib.sha256(css.encode()).hexdigest()[:12]+'.css'
for p in out.glob('style-*.css'):p.unlink()
(out/cssname).write_text(css)
oldboot=next(base.glob('boot-*.js'));boot=oldboot.read_text();boot=boot.replace('  let startup=true,slowTimer=0,appRequested=false;',"  const optionalKeys=['assets/materials-v3230.webp','assets/props-v3230.webp'];const startupKeys=Object.keys(window.GameAssets).filter(k=>!optionalKeys.includes(k));\n  let startup=true,slowTimer=0,appRequested=false;")
boot=boot.replace('const keys=Object.keys(window.GameAssets),done=', 'const keys=startupKeys,done=')
boot=boot.replace('await request(Object.keys(window.GameAssets),{priority:0,retry:manual});','await request(startupKeys,{priority:0,retry:manual});\n      request(optionalKeys,{priority:2,retry:manual}).catch(()=>{});')
for p in out.glob('boot-*.js'):p.unlink()
bootname='boot-'+hashlib.sha256(boot.encode()).hexdigest()[:12]+'.js';(out/bootname).write_text(boot)
html=(base/'index.html').read_text().replace(oldboot.name,bootname).replace(oldapp.name,appname).replace(cssold.name,cssname).replace('v3.23.0','v3.23.1');(out/'index.html').write_text(html)
print(appname,cssname)
