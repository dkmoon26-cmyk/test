from pathlib import Path
import hashlib,json,zipfile,re,shutil,subprocess
v=Path(__file__).parent;app=Path('/workspace/little-tone-v3.26.0-web');repo=Path('/workspace/test');sha=lambda b:hashlib.sha256(b).hexdigest()
names=['module-results','new-sales-results','core-results','ui-results','orders-results','loading-results','startup-results','tutorial-results','zoom-results','new-growth-results','new-late-results','font-results','modular-resume-results','color-results','models-results','font-coverage']
r={n:json.loads((v/(n+'.json')).read_text())for n in names}
for n in ['module-results','new-sales-results','core-results','ui-results','orders-results','loading-results']:assert r[n]['pass'],n
assert r['module-results']['models']==24 and r['module-results']['production']['checks']>=3876
assert len(r['startup-results'])==18 and all(not x['errors']for x in r['startup-results'])
assert len(r['tutorial-results'])==2 and all(x['completed']and not x['errors']for x in r['tutorial-results'])
for n,count in [('new-growth-results',270),('new-late-results',135)]:
 assert len(r[n])==3 and sum(len(x['days'])for x in r[n])==count
 for x in r[n]:assert not x['errors']and not x['findings'],(n,x['seed'])
assert all(x['customComposite']and x['vipComposite']and not x['errors']and all(row['alpha']>0 for row in x['rows'])for x in r['modular-resume-results'])
assert len(r['color-results'])==30 and len(r['models-results'])==24
assert all(not x['missing']for x in r['font-coverage'])
art=json.loads((v/'art.json').read_text());assert len(art['bases'])==24 and all(len(pair)==2 for pair in art['bases'].values());assert[len(art[k])for k in ['parts','motifs','woods']]==[28,10,12]
# Include editable modular source as well as the directly runnable, non-minified game.
source=app/'source'/'custom-workshop';source.mkdir(parents=True,exist_ok=True)
for n in ['config.js','logic.js','premium_render.js','render.js','ui.js','events.js','style.css']:shutil.copy2(v/n,source/n)
(app/'SOURCE-NOTES.md').write_text('게임 실행: index.html과 assets를 함께 사용하세요.\n전체 실행 소스는 app-*.js·boot-*.js·style-*.css이며, 커스텀 제작 편집 원본은 source/custom-workshop에 있습니다.\n고해상도 편집용 이미지와 빌드·검사 도구는 GitHub의 validation-v3.26.0에서 확인할 수 있습니다.\n저장 형식 31 · 기존 버전 저장을 불러올 수 있습니다. 업데이트 전 저장 파일을 백업하세요.\n')
for f in app.glob('*.js'):subprocess.run(['node','--check',str(f)],check=True)
files=[{'path':str(p.relative_to(app)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(app.rglob('*'))if p.is_file()and p.name!='DEPLOY-MANIFEST.json']
m={'version':'3.26.0','schema':31,'edition':'normal','files':files};(app/'DEPLOY-MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');archive=Path('/workspace/little-tone-v3.26.0-web.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted(app.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(app))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for f in files:assert sha(z.read(f['path']))==f['sha256']
 html=z.read('index.html').decode();assert 'v3.26.0'in html and 'v3.25.0'not in html
 for n in re.findall(r'(?:src|href)="([^"]+)"',html):
  if not n.startswith(('http','#','data:')):assert n in z.namelist(),n
 assets=json.loads(html.split('window.GameAssets=Object.freeze(',1)[1].split(');',1)[0]);assert all(n in z.namelist()for n in assets.values())
 assert len(re.findall('as="font"',html))==2
 js=z.read(next(n for n in z.namelist()if re.fullmatch(r'app-[a-f0-9]+\.js',n))).decode();build=json.loads(js.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);assert build['version']=='3.26.0'and build['schema']['version']==31
 assert not any(n.endswith('-fixture.json') or n.endswith('-save.json')for n in z.namelist())
artifact={'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'manifestFiles':len(files),'zipCrc':'passed','fileHashes':'passed'}
report={'version':'3.26.0','schema':31,'artifact':artifact,'art':{'models':24,'frontRearImages':48,'hardware':28,'motifs':10,'materials':12,'webpQuality':95,'alphaQuality':100},'summary':{'optionAndProductionChecks':r['module-results']['production']['checks'],'optionPriceCases':r['module-results']['fieldCases'],'legacyCoreChecks':len(r['core-results']['checks']),'newDesignNormalAndVIPSales':r['new-sales-results'],'coldResumeNewDesignComposites':'passed','naturalGrowthDays':270,'fundedLateDays':135,'startupScenarios':18,'fullTutorialRuns':2,'staffLayouts':12,'fontCoverage':'passed'},'limitations':['Desktop and mobile Chromium viewports; physical phones not tested.','Front/back turntable uses 2D artwork and is not a true 3D model.','Existing completed/in-progress legacy custom products retain their old appearance, options and historical prices. Newly started designs use the modular art.','Long economic tests used the same economic rules, before final art and material-cache refinements. Final option/production, sales, cold resume and UI checks covered the resulting build.','Late-game funds still accumulate quickly under an efficient automated strategy. No arbitrary income reduction was introduced.','The artwork contains generated texture/detail variation; original retail artwork remains unchanged.','No security overhaul or service worker was added. Schema31 saves do not open in older game builds.'],'reports':r}
(repo/'VALIDATION-v3.26.0.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');shutil.copy2(archive,repo/archive.name);shutil.copy2(v/'release_notes.md',repo/'PATCH-v3.26.0.md')
vp=repo/'validation-v3.26.0';vp.mkdir(exist_ok=True)
for n in ['build.py','spans.py','config.js','logic.js','premium_render.js','render.js','ui.js','events.js','style.css','premium_art.py','premium-sources.json','art.json','groups.json','fonts.py','font-chars.txt','module.cjs','core.cjs','ui.cjs','orders.cjs','sales.cjs','resume.cjs','modular-resume.cjs','loading.cjs','startup.cjs','long.cjs','long-harness.js','models.cjs','colors.cjs','smoke.cjs','premium-preview.cjs','package.py','modular-save.json','display-save.json']:
 shutil.copy2(v/n,vp/n)
for n in names:shutil.copy2(v/(n+'.json'),vp/(n+'.json'))
rawdir=vp/'source-art';rawdir.mkdir(exist_ok=True)
for n in json.loads((v/'premium-sources.json').read_text()):shutil.copy2(v/'source-art'/(n+'.png'),rawdir/(n+'.png'))
for n in ['premium-workshop-desktop','premium-workshop-mobile','custom-preview-real','models-audit','color-audit','modular-cold']:
 shutil.copy2(v/(n+'.png'),repo/('ui-v3.26.0-'+n+'.png'))
sums=repo/'SHA256SUMS';sums.write_text('\n'.join(x for x in sums.read_text().splitlines()if not x.endswith('  '+archive.name))+'\n'+sha(archive.read_bytes())+'  '+archive.name+'\n')
(repo/'README.md').write_text('''# 작은 선율 v3.26.0

**[일반 게임 ZIP 다운로드](https://github.com/dkmoon26-cmyk/test/raw/refs/heads/downloads/little-tone-v3.26.0/little-tone-v3.26.0-web.zip)**

커스텀 제작을 외관·부품·문양·마감으로 개편했습니다. 악기 24종의 앞·뒷면 48장, 부품 28종, 문양 10종과 재질 12종을 새로 만들고 바디 명암·광택과 색상을 분리했습니다. 와인색이 분홍빛으로 변하거나 부품이 납작하게 보이던 문제를 보완했습니다.

10색과 악기별 부품·고급 재료, 앞뒤 각 3개 문양 배치, 옵션별 1~3영업일 제작과 실시간 미리보기를 지원합니다. 기존 완성품·제작 중 상품의 옵션·비용·판매가는 유지합니다.

옵션·제작 검사 3,876개, 실제 일반·VIP 판매와 저장 복구, PC·모바일 UI를 검증했습니다. 같은 경제 규칙으로 자연 성장 270일과 후반 135일을 시뮬레이션했습니다. 검사 범위와 한계는 아래 보고서에 기록했습니다.

압축을 모두 풀어 파일을 함께 사용하세요. 실행 소스·이미지와 커스텀 모듈 편집 소스를 포함합니다. **업데이트 전 저장 파일을 백업하세요.**

[패치 내용](./PATCH-v3.26.0.md) · [검사 결과](./VALIDATION-v3.26.0.json) · [실제 제작 화면](./ui-v3.26.0-premium-workshop-desktop.png) · [24종 앞뒤 비교](./ui-v3.26.0-models-audit.png) · [편집용 이미지 원본](./validation-v3.26.0/source-art) · [SHA-256](./SHA256SUMS)
''')
print(json.dumps(artifact,indent=2));print('PACKAGED',len(files),'files')
