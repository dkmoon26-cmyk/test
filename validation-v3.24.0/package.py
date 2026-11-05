from pathlib import Path
import hashlib,json,zipfile,shutil,re
v=Path(__file__).parent; app=Path('/workspace/little-tone-v3.24.0-web'); repo=Path('/workspace/test')
sha=lambda b:hashlib.sha256(b).hexdigest()
names=['core-results','fix-results','font-results','loading-results','new-growth-results','production-results','regression-days','rules-results','sales-results','startup-results','tutorial-results','zoom-results','layout-results']
reports={n:json.loads((v/(n+'.json')).read_text()) for n in names}
for n in ['fix-results','loading-results','rules-results','sales-results','layout-results']:assert reports[n]['pass'],n
assert len(reports['startup-results'])==18 and all(not r['errors'] for r in reports['startup-results'])
assert len(reports['tutorial-results'])==2 and all(r['completed'] and not r['errors'] for r in reports['tutorial-results'])
for name in ['new-growth-results','production-results','regression-days']:
 for r in reports[name]:
  assert not r.get('errors') and not r.get('findings'),(name,r.get('findings'))
assert sum(len(r['days']) for r in reports['new-growth-results'])==270
assert sum(len(r['days']) for r in reports['production-results'])==54
assert sum(len(r['days']) for r in reports['regression-days'])==99
files=[{'path':str(p.relative_to(app)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(app.rglob('*')) if p.is_file() and p.name!='DEPLOY-MANIFEST.json']
manifest={'version':'3.24.0','schema':29,'edition':'normal','files':files};(app/'DEPLOY-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive=Path('/workspace/little-tone-v3.24.0-web.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(app.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(app))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for f in files:assert sha(z.read(f['path']))==f['sha256']
 html=z.read('index.html').decode();assert 'v3.24.0' in html
 for n in re.findall(r'(?:src|href)="([^"]+)"',html):
  if not n.startswith(('http','#','data:')):assert n in z.namelist(),n
 assert not any(n.endswith('.woff') for n in z.namelist())
 js=z.read(next(n for n in z.namelist() if re.fullmatch(r'app-[a-f0-9]+\.js',n))).decode()
 build=json.loads(js.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);assert build['version']=='3.24.0' and build['schema']['version']==29
artifact={'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'manifestFiles':len(files),'zipCrc':'passed','fileHashes':'passed'}
report={'version':'3.24.0','schema':29,'artifact':artifact,'summary':{'naturalGrowthBusinessDays':270,'generalRegressionBusinessDays':99,'productionBusinessDays':54,'vipRegressionDays':len(reports['fix-results']['days']),'calendarDraws':8400,'coreChecks':len(reports['core-results']['checks']),'startupScenarios':18,'fullTutorialRuns':2,'staffLayouts':18,'ending84Continue85':'passed','activeSaleReload':'passed','loading':reports['loading-results']['summary']},'limitations':['Chromium desktop/mobile viewports; not physical device tests.','8400 days measures deterministic event schedule only, not business/economic play.','Natural growth simulation uses a deterministic automated strategy from normal starting funds. It does not represent every human strategy or guarantee future balance.','Production and VIP regressions use funded advanced-store fixtures to exercise transactions and routes, not to forecast profitability.','Long growth/general simulations preceded final help/catalog asset refinements; core, startup, calendar/ending, sales/reload, loading and responsive layouts were rerun on the packaged build.','Legacy interior atlas wall region is unused by current materials; existing wall/floor art was not regenerated in this patch.','No service worker or server cache configuration added. Offline availability depends on local files or hosting.','New schema29 saves cannot be opened by older builds. Export a backup before upgrading.'],'reports':reports}
(repo/'VALIDATION-v3.24.0.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');shutil.copy2(archive,repo/archive.name)
vp=repo/'validation-v3.24.0';vp.mkdir(exist_ok=True)
for n in ['build.py','spans.py','patch.js','events.js','style.css','fonts.py','font-chars.txt','font-results.json','chairs.webp','test.cjs','helpers.js','startup.cjs','rules.cjs','sales.cjs','loading.cjs','layout.cjs','fixes.cjs','harness.js','run.cjs','long.cjs','long-harness.js','production.cjs','chairs.cjs','package.py']:shutil.copy2(v/n,vp/n)
for n in names:shutil.copy2(v/(n+'.json'),vp/(n+'.json'))
for n in ['calendar-mobile','staff-final-mobile','seated-directions','anniversary-desktop','390-tutorial-complete']:
 shutil.copy2(v/(n+'.png'),repo/('ui-v3.24.0-'+n+'.png'))
sums=repo/'SHA256SUMS';sums.write_text('\n'.join(line for line in sums.read_text().splitlines() if not line.endswith('  '+archive.name))+'\n'+sha(archive.read_bytes())+'  '+archive.name+'\n')
print(json.dumps(artifact,indent=2));print(json.dumps(report['summary'],indent=2))
