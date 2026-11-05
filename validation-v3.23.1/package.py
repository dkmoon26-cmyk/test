from pathlib import Path
import hashlib,json,zipfile,shutil,re
v=Path(__file__).parent;app=Path('/workspace/little-tone-v3.23.1-web');repo=Path('/workspace/test');sha=lambda b:hashlib.sha256(b).hexdigest()
files=[{'path':str(p.relative_to(app)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(app.rglob('*'))if p.is_file()and p.name!='DEPLOY-MANIFEST.json'];manifest={'version':'3.23.1','schema':28,'edition':'normal','files':files};(app/'DEPLOY-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive=Path('/workspace/little-tone-v3.23.1-web.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted(app.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(app))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for f in files:assert sha(z.read(f['path']))==f['sha256']
 html=z.read('index.html').decode();assert 'v3.23.1'in html
 for n in re.findall(r'(?:src|href)="([^"]+)"',html):
  if not n.startswith(('http','#','data:')):assert n in z.namelist(),n
 appjs=z.read(next(n for n in z.namelist()if re.fullmatch(r'app-[a-f0-9]+\.js',n))).decode();build=json.loads(appjs.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);assert build['version']=='3.23.1'and build['schema']['version']==28
reports={n:json.loads((v/(n+'.json')).read_text())for n in ['startup-results','tutorial-results','zoom-results','visual-results','core-results','sales-results']}
assert len(reports['startup-results'])==18 and all(not r['errors']for r in reports['startup-results'])
assert len(reports['tutorial-results'])==2 and all(r['completed']and r['day']==2 and not r['errors']for r in reports['tutorial-results'])
assert len(reports['zoom-results'])==4 and reports['visual-results']['pass']
assert len(reports['visual-results']['rows'])==6 and all(r['alphaMismatch']==0 for r in reports['visual-results']['rows'])
for name in ['core-results','sales-results']:assert not reports[name]['errors']
report={'version':'3.23.1','schema':28,'artifact':{'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'manifestFiles':len(files),'zipCrc':'passed','fileHashes':'passed'},'summary':{'startupScenarios':18,'modes':['normal','cross-origin artwork','all canvas pixel reads denied','prop atlas missing','both decorative atlases missing','prop draw failure'],'viewports':[[1025,672],[1440,900],[390,844]],'completeSevenStepTutorialRuns':2,'visualViewportZoomLevels':[1,1.5,2,3],'unchangedPropImages':6,'saveCompatibilityFields':reports['visual-results']['migration']['checks'],'coreCraftChecks':len(reports['core-results']['checks']),'salesActiveReload':'passed'},'reports':reports,'beforeSecurityError':json.loads((v/'before-security-error.json').read_text()),'limitations':['Chromium with desktop/mobile viewports and visual viewport zoom; not physical phone testing.','Managed browser policy blocks direct file:// navigation. The same pixel-read SecurityError was reproduced using cross-origin artwork, then regression-tested with cross-origin images and a forced global getImageData denial.','The exact original tutorial left-clipping layout was not reproduced; viewport-based placement was added and verified at four zoom levels.','This hotfix has no economic rule or save schema changes. Prior long economy simulations were not repeated; first-day tutorial, crafting and actual sale/reload checks were run.']}
(repo/'VALIDATION-v3.23.1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');shutil.copy2(archive,repo/archive.name)
vp=repo/'validation-v3.23.1';vp.mkdir(exist_ok=True)
for n in ['build.py','spans.py','patch.js','style.css','masks.cjs','prop-masks.json','startup.cjs','visual.cjs','helpers.js','test.cjs','sales.cjs','package.py','before-security-error.json']:shutil.copy2(v/n,vp/n)
for src,dest in [('1025-cross.png','startup-desktop.png'),('390-denied.png','startup-mobile.png'),('390-tutorial-complete.png','tutorial-complete-mobile.png')]:shutil.copy2(v/src,repo/('ui-v3.23.1-'+dest))
sums=repo/'SHA256SUMS';sums.write_text('\n'.join(line for line in sums.read_text().splitlines()if not line.endswith('  '+archive.name))+'\n'+sha(archive.read_bytes())+'  '+archive.name+'\n')
print(json.dumps(report['artifact'],indent=2));print(json.dumps(report['summary'],indent=2))
