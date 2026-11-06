from pathlib import Path
import hashlib,json,zipfile,re,shutil
v=Path(__file__).parent;app=Path('/workspace/little-tone-v3.25.0-web');repo=Path('/workspace/test');sha=lambda b:hashlib.sha256(b).hexdigest()
names=['core-results','ui-results','orders-results','production-results','loading-results','startup-results','tutorial-results','zoom-results','new-growth-results','new-late-results','font-results','font-coverage','results']
r={n:json.loads((v/(n+'.json')).read_text())for n in names}
for n in ['core-results','ui-results','orders-results','production-results','loading-results']:assert r[n]['pass'],n
assert len(r['startup-results'])==18 and all(not x['errors']for x in r['startup-results'])
assert len(r['tutorial-results'])==2 and all(x['completed']and not x['errors']for x in r['tutorial-results'])
assert len(r['new-growth-results'])==3 and sum(len(x['days'])for x in r['new-growth-results'])==270
assert len(r['new-late-results'])==3 and sum(len(x['days'])for x in r['new-late-results'])==135
for n in ['new-growth-results','new-late-results']:
 for x in r[n]:assert not x['errors']and not x['findings'],(n,x['seed'])
for x in r['new-growth-results']:assert x['anniversary']['day']==84 and x['anniversary']['continued']
assert all(x['customComposite']and x['vipComposite']and not x['errors']and all(row['alpha']>0 for row in x['rows'])for x in r['results'])
assert all(not x['missing']for x in r['font-coverage'])
files=[{'path':str(p.relative_to(app)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(app.rglob('*'))if p.is_file()and p.name!='DEPLOY-MANIFEST.json']
m={'version':'3.25.0','schema':30,'edition':'normal','files':files};(app/'DEPLOY-MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');archive=Path('/workspace/little-tone-v3.25.0-web.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted(app.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(app))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for f in files:assert sha(z.read(f['path']))==f['sha256']
 html=z.read('index.html').decode();assert 'v3.25.0'in html
 for name in re.findall(r'(?:src|href)="([^"]+)"',html):
  if not name.startswith(('http','#','data:')):assert name in z.namelist(),name
 assets=json.loads(html.split('window.GameAssets=Object.freeze(',1)[1].split(');',1)[0]);assert all(name in z.namelist()for name in assets.values())
 assert len(re.findall('as="font"',html))==2
 js=z.read(next(n for n in z.namelist()if re.fullmatch(r'app-[a-f0-9]+\.js',n))).decode();build=json.loads(js.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);assert build['version']=='3.25.0'and build['schema']['version']==30
artifact={'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'manifestFiles':len(files),'zipCrc':'passed','fileHashes':'passed'}
report={'version':'3.25.0','schema':30,'artifact':artifact,'summary':{'naturalGrowthDays':270,'fundedLateDays':135,'manufacturingDays':len(r['production-results']['days']),'coreChecks':len(r['core-results']['checks']),'manufacturingChecks':len(r['production-results']['checks']),'orderAndProbabilityChecks':len(r['orders-results']['checks']),'startupScenarios':18,'fullTutorialRuns':2,'staffLayouts':12,'coldResumeFurniturePixels':'passed','coldResumeCustomAndVIPCompositePixels':'passed','VIPTwoPurchasesWithActualReload':'passed','liveCustomModels':7,'newDecorationTypes':3,'wallActualClickMoveAndReload':'passed','fixedFontHangulCoverage':'passed'},'economy':{'growthEndingCash':[x['days'][-1]['money']for x in r['new-growth-results']],'lateEndingCash':[x['days'][-1]['money']for x in r['new-late-results']],'note':'Luxury margins and high-tier ordinary sales accelerate late cash growth. Automated growth runs started with normal funds; late fixtures started at stage7 with100million KRW. No arbitrary profit reduction was applied.'},'limitations':['Chromium desktop/mobile viewports, not physical mobile devices.','Automated strategies do not cover all player layouts, budgets or inventory choices.','Long economy runs used the final economic rules; the final additional composite-cache invalidation affected rendering only. Core, production, orders, real UI, cold resume, startup and loading checks were rerun afterward.','Legacy highest-tier VIP allocations are returned to storage; incompatible custom display assignments are cleared while items and historical costs/prices are preserved.','Existing multiple-unit luxury inventory and pending orders are preserved; new orders enforce one-unit ownership.','Custom finished prices retain the option-based formula and have no newly imposed29000000 KRW cap; the cap applies to base models.','Loading byte comparison is against v3.23.1, not v3.24.0.','No service worker added. Schema30 saves cannot be opened in older builds.'],'reports':r}
(repo/'VALIDATION-v3.25.0.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');shutil.copy2(archive,repo/archive.name)
vp=repo/'validation-v3.25.0';vp.mkdir(exist_ok=True)
for n in ['build.py','spans.py','patch.js','events.js','style.css','art.py','art.json','fonts.py','font-chars.txt','core.cjs','ui.cjs','orders.cjs','production.cjs','resume.cjs','loading.cjs','startup.cjs','long.cjs','long-harness.js','package.py']:
 shutil.copy2(v/n,vp/n)
for n in names:shutil.copy2(v/(n+'.json'),vp/(n+'.json'))
for p in v.glob('*.webp'):shutil.copy2(p,vp/p.name)
shutil.copytree(v/'source-art',vp/'source-art',dirs_exist_ok=True)
for n in ['shop-desktop','luxury-art','craft-red-phoenix','staff-mobile','decor-mobile','390-tutorial-complete']:
 shutil.copy2(v/(n+'.png'),repo/('ui-v3.25.0-'+n+'.png'))
sums=repo/'SHA256SUMS';sums.write_text('\n'.join(x for x in sums.read_text().splitlines()if not x.endswith('  '+archive.name))+'\n'+sha(archive.read_bytes())+'  '+archive.name+'\n')
print(json.dumps(artifact,indent=2));print(json.dumps(report['summary'],indent=2))
