from pathlib import Path
import hashlib,json,zipfile,shutil,re
v=Path(__file__).parent;app=Path('/workspace/little-tone-v3.23.0-web');repo=Path('/workspace/test');sha=lambda b:hashlib.sha256(b).hexdigest()
files=[{'path':str(p.relative_to(app)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(app.rglob('*'))if p.is_file()and p.name!='DEPLOY-MANIFEST.json']
manifest={'version':'3.23.0','schema':28,'edition':'normal','files':files};(app/'DEPLOY-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive=Path('/workspace/little-tone-v3.23.0-web.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted(app.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(app))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for f in files:assert sha(z.read(f['path']))==f['sha256']
 html=z.read('index.html').decode();assert 'v3.23.0'in html
 appjs=z.read(next(n for n in z.namelist()if re.fullmatch(r'app-[a-f0-9]+\.js',n))).decode();build=json.loads(appjs.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);assert build['version']=='3.23.0'and build['schema']['version']==28
 for n in re.findall(r'(?:src|href)="([^"]+)"',html):
  if not n.startswith(('http','#','data:')):assert n in z.namelist(),n
reports={n:json.loads((v/f'{n}.json').read_text())for n in ['core-results','features-results','advanced-results','ui-results','regression-results','fix-results','regression-days','sales-results','production-results']}
for n,d in reports.items():
 if isinstance(d,dict):assert not d.get('errors'),n
 if n=='regression-days':assert len(d)==6 and sum(len(a['days'])for a in d)==99 and all(not a['findings']and not a['errors']for a in d)
 if n=='production-results':assert len(d)==3 and sum(len(a['days'])for a in d)==54 and all(not a['errors']for a in d)
assert reports['features-results']['touch'] and reports['advanced-results']['pass']
assert len(reports['advanced-results']['days']['report'])==8 and len(reports['fix-results']['days'])==10
report={'version':'3.23.0','schema':28,'artifact':{'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'manifestFiles':len(files),'zipCrc':'passed','fileHashes':'passed'},'summary':{'generalDays':99,'productionDays':54,'vipRegressionDays':10,'variableVIPAllWallEntranceDays':8,'coreChecks':len(reports['core-results']['checks']),'staffOrderRegressionChecks':len(reports['regression-results']['checks']),'vipRegressionChecks':len(reports['fix-results']['checks']),'craftOptionPreviewChanges':len(reports['ui-results']['textures']),'craftLayouts':len(reports['ui-results']['layouts']),'menuLayouts':len(reports['features-results']['layouts']),'noticeLayouts':len(reports['advanced-results']['notices']),'actualTouchVIPAndEntrance':'passed'},'reports':reports,'limitations':['Desktop Chromium and emulated mobile viewports/CDP touch input; no physical-phone performance measurement.','Manufacturing and later-stage VIP tests use funded/unlocked fixtures; results verify ledgers, stock conservation and circulation, not natural-player profit forecasts.','The 99-day run and some regression runs preceded final image, notification and layout refinements. Final production and 8-day VIP tests use the final two-cell display approach, consistent with previous saves. Economy rates/prices are unchanged.']}
(repo/'VALIDATION-v3.23.0.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');shutil.copy2(archive,repo/archive.name)
vp=repo/'validation-v3.23.0';vp.mkdir(exist_ok=True)
for name in ['build.py','spans.py','patch.js','events.js','style.css','helpers.js','test.cjs','features.cjs','advanced.cjs','ui.cjs','sales.cjs','production.cjs','regression.cjs','fixes.cjs','run.cjs','harness.js','package.py','materials.webp','props.webp']:
 shutil.copy2(v/name,vp/name)
for name in ['game-produced.png','materials-wallart.png','vip-drag-mobile.png','business-mobile.png','decor-mobile.png','unlock-mobile.png']:
 shutil.copy2(v/name,repo/('ui-v3.23.0-'+name))
sums=repo/'SHA256SUMS';sums.write_text('\n'.join(line for line in sums.read_text().splitlines()if not line.endswith('  '+archive.name))+'\n'+sha(archive.read_bytes())+'  '+archive.name+'\n')
print(json.dumps(report['artifact'],indent=2));print(json.dumps(report['summary'],indent=2))
