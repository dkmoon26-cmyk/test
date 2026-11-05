from pathlib import Path
import hashlib,json,zipfile,shutil,re
v=Path(__file__).parent;app=Path('/workspace/little-tone-v3.22.0-web');repo=Path('/workspace/test');sha=lambda b:hashlib.sha256(b).hexdigest()
files=[{'path':str(p.relative_to(app)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(app.rglob('*'))if p.is_file()and p.name!='DEPLOY-MANIFEST.json']
manifest={'version':'3.22.0','schema':27,'edition':'normal','files':files};(app/'DEPLOY-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive=Path('/workspace/little-tone-v3.22.0-web.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted(app.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(app))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for f in files:assert sha(z.read(f['path']))==f['sha256']
 html=z.read('index.html').decode();assert 'v3.17.0'not in html and 'v3.22.0'in html
 appjs=z.read(next(n for n in z.namelist()if re.fullmatch(r'app-[a-f0-9]+\.js',n))).decode();build=json.loads(appjs.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);assert build['version']=='3.22.0'and build['schema']['version']==27
reports={n:json.loads((v/f'{n}.json').read_text())for n in ['core-results','ui-results','regression-results','fix-results','boundaries-results','regression-days','sales-results','production-results']}
for n,d in reports.items():
 if isinstance(d,dict):assert not d.get('errors'),n
 if n=='regression-days':assert len(d)==6 and sum(len(a['days'])for a in d)==99 and all(not a['findings']and not a['errors']for a in d)
 if n=='production-results':assert len(d)==3 and sum(len(a['days'])for a in d)==54 and all(not a['errors']for a in d)
production=[{'seed':r['seed'],'days':len(r['days']),'started':len(r['started']),'completed':r['days'][-1]['crafted'],'sold':r['days'][-1]['sold'],'ordinarySold':r['days'][-1]['normalSold'],'vipSold':r['days'][-1]['vipSold'],'customRevenue':r['days'][-1]['customRevenue'],'saveRoundTrips':r['roundTrips']}for r in reports['production-results']]
report={'version':'3.22.0','schema':27,'artifact':{'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'manifestFiles':len(files),'zipCrc':'passed','fileHashes':'passed'},'summary':{'generalDays':99,'vipRegressionDays':10,'productionDays':54,'production':production,'coreChecks':len(reports['core-results']['checks']),'migrationBoundaryChecks':len(reports['boundaries-results']['checks'])+len(reports['boundaries-results']['migration']),'uiOptionChanges':len(reports['ui-results']['textures']),'uiLayouts':len(reports['ui-results']['layouts'])},'reports':reports,'limitations':['Desktop Chromium and emulated mobile viewports; no physical-phone performance measurement.','Production simulations use funded stage-7 fixtures and preloaded raw inventory; they verify economic ledgers and item conservation, not natural-player profit forecasts.','The 99-day and 10-day runs preceded final visual and quick-popup positioning refinements; economic code is unchanged. Final core, production, sales and UI checks use the final build.']}
(repo/'VALIDATION-v3.22.0.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
shutil.copy2(archive,repo/archive.name)
vp=repo/'validation-v3.22.0';vp.mkdir(exist_ok=True)
for name in ['build.py','spans.py','patch.js','events.js','style.css','helpers.js','test.cjs','ui.cjs','sales.cjs','production.cjs','boundaries.cjs','regression.cjs','fixes.cjs','run.cjs','harness.js','package.py','premium-showcase.webp']:
 shutil.copy2(v/name,vp/name)
for name in ['workshop-bass-desktop.png','workshop-acoustic-mobile.png','d3-mobile.png','game-produced.png']:
 shutil.copy2(v/name,repo/('ui-v3.22.0-'+name))
with(repo/'SHA256SUMS').open('a')as f:f.write(sha(archive.read_bytes())+'  '+archive.name+'\n')
print(json.dumps(report['artifact'],indent=2));print(json.dumps(report['summary'],indent=2))
