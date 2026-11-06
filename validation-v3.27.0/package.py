from pathlib import Path
import hashlib,json,zipfile,re,shutil,subprocess
v=Path(__file__).parent;app=Path('/workspace/little-tone-v3.27.0-web');repo=Path('/workspace/test');sha=lambda b:hashlib.sha256(b).hexdigest()
names=['case-results','color-results','motif-results','interaction-results','module-results','core-results','new-sales-results','modular-resume-results','extended-resume-results','ui-results','orders-results','startup-results','tutorial-results','zoom-results','new-late-results','font-results','font-coverage']
r={n:json.loads((v/(n+'.json')).read_text())for n in names}
for n in ['case-results','color-results','motif-results','interaction-results','module-results','core-results','new-sales-results','ui-results','orders-results']:assert r[n]['pass'],n
assert len(r['color-results']['scenarios'])==2 and all(x['headChanged']and x['neckChanged']and not x['errors']for x in r['color-results']['scenarios'])
assert len(r['motif-results']['checks'])==312
assert r['module-results']['production']['checks']==3876
assert len(r['startup-results'])==18 and all(not x['errors']for x in r['startup-results'])
assert len(r['tutorial-results'])==2 and all(x['completed']and not x['errors']for x in r['tutorial-results'])
for n in ['modular-resume-results','extended-resume-results']:
 assert all(x['customComposite']and x['vipComposite']and not x['errors']and all(row['alpha']>0 for row in x['rows'])for x in r[n])
assert len(r['new-late-results'])==3 and sum(len(x['days'])for x in r['new-late-results'])==135
for x in r['new-late-results']:assert not x['errors']and not x['findings']
assert all(not x['missing']for x in r['font-coverage'])
(app/'SOURCE-NOTES.md').write_text('게임 실행: index.html과 assets를 함께 사용하세요.\n전체 실행 소스는 app-*.js·boot-*.js·style-*.css입니다. source/custom-workshop은 기본 커스텀 모듈이고, source/display-and-custom-v327은 이번 진열대·색상·문양 변경 소스입니다.\n새 진열대 고해상도 PNG와 빌드·검사 도구는 GitHub의 validation-v3.27.0에서 확인할 수 있습니다.\n저장 형식32 · 이전 버전 저장을 불러올 수 있습니다. 업데이트 전 파일 백업을 권장합니다.\n')
for f in app.glob('*.js'):subprocess.run(['node','--check',str(f)],check=True)
files=[{'path':str(p.relative_to(app)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(app.rglob('*'))if p.is_file()and p.name!='DEPLOY-MANIFEST.json']
m={'version':'3.27.0','schema':32,'edition':'normal','files':files};(app/'DEPLOY-MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');archive=Path('/workspace/little-tone-v3.27.0-web.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted(app.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(app))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for f in files:assert sha(z.read(f['path']))==f['sha256']
 html=z.read('index.html').decode();assert'v3.27.0'in html and'v3.26.0'not in html
 for n in re.findall(r'(?:src|href)="([^"]+)"',html):
  if not n.startswith(('http','#','data:')):assert n in z.namelist(),n
 assets=json.loads(html.split('window.GameAssets=Object.freeze(',1)[1].split(');',1)[0]);assert all(n in z.namelist()for n in assets.values())
 assert len(re.findall('as="font"',html))==2
 js=z.read(next(n for n in z.namelist()if re.fullmatch(r'app-[a-f0-9]+\.js',n))).decode();build=json.loads(js.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);assert build['version']=='3.27.0'and build['schema']['version']==32
 assert not any(n.endswith('-fixture.json')or n.endswith('-save.json')for n in z.namelist())
artifact={'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'manifestFiles':len(files),'zipCrc':'passed','fileHashes':'passed'}
report={'version':'3.27.0','schema':32,'artifact':artifact,'summary':{'optionAndProductionChecks':3876,'extendedMotifChecks':312,'actualInteractionChecks':r['interaction-results']['checks'],'headAndNeckColorsNormalAndPixelReadFailure':'passed','oldAndExpandedDesignColdResume':'passed','lateEconomyDays':135,'startupScenarios':18,'fullTutorialRuns':2},'scale':{'caseWorldSize':[32,54],'ordinaryRackWorldSize':[44.4190775,47.2057198],'characterWorldHeight':61.6,'caseInstrumentHeight':34,'placementCellsAndCoordinates':'unchanged'},'limitations':['Chromium desktop/mobile viewports; physical phones not tested.','The managed browser blocked direct file:// navigation, so pixel-read failure was explicitly injected on HTTP to verify the head/rear-neck fallback path.','Artwork uses 2D front/back views and mirroring, not a true3D glass model.','Logical legacy display footprints are retained even though the visual cabinet is smaller.','New motif range applies to the body. Neck and head are not new motif targets.','Efficient late-game strategies still accumulate cash quickly; income rules were not rebalanced.','Schema32 saves cannot be opened in older builds. No security overhaul or service worker was added.'],'reports':r}
(repo/'VALIDATION-v3.27.0.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');shutil.copy2(archive,repo/archive.name);shutil.copy2(v/'PATCH.md',repo/'PATCH-v3.27.0.md')
vp=repo/'validation-v3.27.0';vp.mkdir(exist_ok=True)
for n in ['build.py','spans.py','custom.js','cases.js','events.js','fonts.py','font-chars.txt','package.py','cases.cjs','colors.cjs','motifs.cjs','interactions.cjs','module.cjs','core.cjs','sales.cjs','modular-resume.cjs','extended-resume.cjs','ui.cjs','orders.cjs','startup.cjs','long.cjs','long-harness.js','extended-display-save.json']:
 shutil.copy2(v/n,vp/n)
for n in names:shutil.copy2(v/(n+'.json'),vp/(n+'.json'))
shutil.copytree(v/'source-art',vp/'source-art',dirs_exist_ok=True)
for n in ['scale-comparison','shop-desktop','shop-mobile','motif-mobile','neck-preview','extended-cold']:
 shutil.copy2(v/(n+'.png'),repo/('ui-v3.27.0-'+n+'.png'))
(repo/'README.md').write_text('''# 작은 선율 v3.27.0

**[일반 게임 ZIP 다운로드](https://github.com/dkmoon26-cmyk/test/raw/refs/heads/downloads/little-tone-v3.27.0/little-tone-v3.27.0-web.zip)**

VIP는 아치형 전체 유리·금색·월넛·버건디, 커스텀은 각진 전체 유리·검정·원목·초록으로 새로 제작했습니다. 낮은 가로 받침에 악기를 세워 전시하고, 일반 진열대·계산대·앰프·캐릭터와 같은 배율로 크기를 맞췄습니다. 기존 배치 칸 수·좌표·방향·가격은 유지합니다.

헤드·뒷넥 색상이 즉시 반영되도록 보완하고, 뒷넥 색상 선택 시 자동으로 뒷면을 보여줍니다. 문양은 바디 전체에서 움직이고4~180%까지 키울 수 있습니다. 바디 밖·사운드홀을 제외하고 픽업·픽가드·현 등 부품 뒤로 가려집니다.

옵션·제작3,876검사, 확대 문양312검사, 실제 클릭·모바일 조작·색상 실패 조건·진열·판매·저장·첫 이어하기와 후반135영업일을 검증했습니다. 검사 범위와 한계는 보고서에 기록합니다.

압축을 모두 풀어 파일을 함께 사용하세요. 실행 소스와 사용 이미지, 변경 모듈 원본을 포함합니다. **업데이트 전 저장을 파일로 백업하세요.**

[패치 내용](./PATCH-v3.27.0.md) · [실제 비율 비교](./ui-v3.27.0-scale-comparison.png) · [게임 화면](./ui-v3.27.0-shop-desktop.png) · [검사 결과](./VALIDATION-v3.27.0.json) · [새 원화](./validation-v3.27.0/source-art) · [SHA-256](./SHA256SUMS)
''')
(repo/'SHA256SUMS').write_text((repo/'SHA256SUMS').read_text().rstrip()+'\n'+sha(archive.read_bytes())+'  '+archive.name+'\n')
(vp/'README.md').write_text('''# v3.27.0 빌드·검사 자료

이 폴더를 /workspace/little-tone-v3.27.0-validation에, 이전 일반 게임 ZIP을 /workspace/little-tone-v3.26.0-web에 풀어 둔 환경을 기준으로 build.py를 실행합니다. ImageMagick과 Python이 필요합니다. fonts.py는 fontTools·Brotli와 이전 폰트 원본 경로를 실행 환경에 맞춰 지정합니다.

source-art에는 새 진열대 앞뒤 원화가 있습니다. cases.js는 실제 비율·진열·선택 판정, custom.js는 색상 합성과 문양 범위, events.js는 이미지 준비 후 캐시 갱신을 처리합니다. 최종 실행 소스 전체는 일반 게임 ZIP의 app-*.js에 포함됩니다.

검사 .cjs는 Chromium·Playwright와 /workspace의 이전 버전 검사 픽스처 경로를 사용합니다. 해당 의존성·경로를 조정한 뒤 실행하세요. extended-display-save.json은 검사 전용이며 일반 게임 ZIP에는 포함하지 않습니다.

후반 경제 검사는 long.cjs late new 45 17,2026,731로 실행했습니다. 자세한 결과와 한계는 상위 VALIDATION-v3.27.0.json을 참고하세요.
''')
print(json.dumps(artifact,indent=2))
