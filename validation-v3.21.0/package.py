from pathlib import Path
import hashlib,json,zipfile,shutil,re
v=Path(__file__).parent;app=Path('/workspace/little-tone-v3.21.0-web');repo=Path('/workspace/test');sha=lambda b:hashlib.sha256(b).hexdigest()
files=[{'path':str(p.relative_to(app)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(app.rglob('*'))if p.is_file()and p.name!='DEPLOY-MANIFEST.json']
manifest={'version':'3.21.0','schema':26,'edition':'normal','files':files};(app/'DEPLOY-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive=Path('/workspace/little-tone-v3.21.0-web.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted(app.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(app))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for f in files:assert sha(z.read(f['path']))==f['sha256']
 html=z.read('index.html').decode();assert 'v3.17.0'not in html and 'v3.21.0'in html
 appjs=z.read(next(n for n in z.namelist()if re.fullmatch(r'app-[a-f0-9]+\.js',n))).decode();build=json.loads(appjs.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);assert build['version']=='3.21.0'and build['schema']['version']==26
reports={n:json.loads((v/f'{n}.json').read_text())for n in ['core-results','ui-results','regression-results','fix-results','edge-results','stress-results','regression-days','economy-results']}
for n,d in reports.items():
 if isinstance(d,dict):assert not d.get('errors'),n
 if n=='regression-days':assert len(d)==6 and sum(len(a['days'])for a in d)==99 and all(not a['findings']and not a['errors']for a in d)
 if n=='economy-results':assert len(d)==6 and sum(len(a['days'])for a in d)==60 and all(not a['errors']for a in d)
stats={}
for version in ['old','new']:
 rows=[d for r in reports['economy-results']if r['version']==version for d in r['days']];stats[version]={k:sum(d[k]for d in rows)for k in ['revenue','net','sold','visitors']}
change={k:round((stats['new'][k]/stats['old'][k]-1)*100,2)for k in stats['old']}
report={'version':'3.21.0','schema':26,'artifact':{'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'manifestFiles':len(files),'zipCrc':'passed','fileHashes':'passed'},'economySummary':{'comparison':'3 seeds × 10 days per version; funded stage-7 stores with same displays and all normal identities initialized as regulars; VIP disabled to isolate regular shopping.','totals':stats,'changePercent':change,'generalDays':99,'vipDays':15,'comparisonDays':60,'forcedMultiPurchase':reports['stress-results']['paid']},'reports':reports,'limitations':['Desktop Chromium and emulated mobile viewports/touch; no physical-phone performance measurement.','Later-stage/VIP comparison uses funded/unlocked fixtures; percentage changes do not predict natural early-game profit.','The final build differs from the 99-day/economic run only in catalog entries, pointer handling, tutorial focus and the ornament-count label. Economics code is identical.']}
(repo/'VALIDATION-v3.21.0.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
shutil.copy2(archive,repo/archive.name)
vp=repo/'validation-v3.21.0';vp.mkdir(exist_ok=True)
for name in ['build.py','patch.js','events.js','style.css','helpers.js','check.cjs','ui.cjs','stress.cjs','regression.cjs','fixes.cjs','edges.cjs','run.cjs','harness.js','economy.cjs','package.py']:
 shutil.copy2(v/name,vp/name)
for name in ['catalog-all-mobile.png','catalog-interior-mobile.png','catalog-interior-desktop.png','floor-preview-mobile.png','wall-preview-mobile.png','detail-desktop.png','game-interior-desktop.png']:
 shutil.copy2(v/name,repo/('ui-v3.21.0-'+name))
with(repo/'SHA256SUMS').open('a')as f:f.write(sha(archive.read_bytes())+'  '+archive.name+'\n')
print(json.dumps(report['artifact'],indent=2));print('Economy:',change)
