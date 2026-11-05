from pathlib import Path
import json,re,hashlib,shutil
from spans import span
v=Path(__file__).parent;base=Path('/workspace/little-tone-v3.23.1-web');out=Path('/workspace/little-tone-v3.24.0-web');shutil.copytree(base,out,dirs_exist_ok=True)
oldapp=next(base.glob('app-*.js'));s=oldapp.read_text();meta=json.loads(s.splitlines()[0][len('window.GameBuild=Object.freeze('):-2]);meta['version']='3.24.0';meta['schema']['version']=29;s='window.GameBuild=Object.freeze('+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+');\n'+s.split('\n',1)[1]
def exact(a,b,n=None):
 global s
 assert a in s,a[:100]
 if n is not None:assert s.count(a)==n,(a,s.count(a))
 s=s.replace(a,b)
for name in ['validateExpansionSave','showSettlement','nextDay','drawPerson','zoomAt','furnitureSprite','before23Spawn','refreshLivePanel','syncTutorialHost','refreshTutorial','drawFullCharacter','gameplayBlocked','largeMenuOpen','beginDesignEdit','drawCatalogPictures','openMenuSection']:
 exact('function '+name+'(','function before24'+name[0].upper()+name[1:]+'(')
patch=(v/'patch.js').read_text()
for name in re.findall(r'^function (\w+)\(',patch,re.M):
 if 'function '+name+'(' in s:
  a,b=span(patch,name);x,y=span(s,name);s=s[:x]+patch[a:b]+'\n'+s[y:];patch=patch[:a]+patch[b:]
exact('// SOURCE: core/state',patch+'\n// SOURCE: core/state')
exact('    ...expansionDefaults(),', '    ...expansionDefaults(),calendar:freshCalendar24(),')
exact('    if(version<27)rules.migrateCraft?.(v,version);','    if(version<27)rules.migrateCraft?.(v,version);\n    if(version<29)rules.migrate24?.(v,version);')
exact('migrateCraft:migrateCraft27,','migrateCraft:migrateCraft27,migrate24,')
exact('  S.day++;\n  deliverOrders(0);','  S.day++;\n  ensureCalendar24();\n  deliverOrders(0);')
exact('function resetInteractionState() {','function resetInteractionState() {introMore24=false;showLocked24=false;')
# Save validation accepts the anniversary ending, preserving legacy viewed endings.
exact("||r.drums<30||r.drums>s.missionStats.sales[26]", "||(version<29?r.drums<30:ending.day<84&&!ending.viewed)||r.drums>s.missionStats.sales[26]")
# Let a daily theme bias existing actor identities without bypassing introduction or regular-customer rules.
exact('  const hana = S.customerBook[\'actor-9\'];',"  if(!firstDrummer&&!introTier&&missionActor===null&&!special)actor=eventActor24(actor,pool);\n  const hana = S.customerBook['actor-9'];")
# Business time and movement simulation remain unchanged under reduced motion.
exact('const walking = !!p.moving || (p.animationWeight ?? 0) > .04;', 'const walking = !reducedMotion24()&&(!!p.moving || (p.animationWeight ?? 0) > .04);')
exact("if (p.state === 'try' && !walking) text('♫', 29, -48 + Math.sin(S.time * 3) * 3", "if (p.state === 'try' && !walking&&!reducedMotion24()) text('♫', 29, -48 + Math.sin(S.time * 3) * 3")
exact("const targetLight = ['open','closing'].includes(S.phase) ? 1 : S.phase === 'settled' ? 0.68 : 0.88;","const targetLight = ['open','closing'].includes(S.phase) ? 1 : S.phase === 'settled' ? 0.68 : 0.88;if(reducedMotion24())shopLight=targetLight;")
exact('  drawStoreFront();','  drawStoreFront();drawWeather24();')
# Current date is compact and the icon carries accessible weather/theme text.
exact("$('day').textContent = S.day + '일차';", "$('day').textContent = calendarLabel24();$('day').title=calendar24().year+'년차 · 누적 '+S.day+'영업일';renderWeather24();")
# Icons still load on demand; locked product lists must be explicitly expanded.
exact("const walking =", "const walking =")
# Common staff controls are delegated once, while per-card dismissal selects its employee.
exact("if(b.dataset.employeeAction==='dismiss'){pendingDismiss={kind:employeeTab,index:selectedEmployee};", "if(b.dataset.employeeAction==='dismiss'){selectedEmployee=Number(b.dataset.employeeIndex??selectedEmployee);pendingDismiss={kind:employeeTab,index:selectedEmployee};")
exact('q=P(g.x,g.y),dir=seat?', 'q=seat?P(chairSeat24(seat).x,chairSeat24(seat).y):P(g.x,g.y),dir=seat?')
exact('for (let f of floaters) {','for (let f of (reducedMotion24()?[]:floaters)) {')
# Final draw controls: preserve painter order of seats, clamp visual overlays after initialization.
exact('  InteriorCatalog,beginDesignEdit,', '  calendar24,ensureCalendar24,eventActor24,reducedMotion24,recordEnding,chairSeat24,\n  InteriorCatalog,beginDesignEdit,')
pos=s.rfind('})();');s=s[:pos]+(v/'events.js').read_text()+'\n'+s[pos:]
exact('13:58,14:55','13:54,14:55')
# Update the first-start wording without changing completed tutorial progress.
exact('손님은 진열대를 보고 시연하거나 계산해요. 안내를 확인하고 영업을 계속해주세요.','첫 판매를 기다려보세요. 손님은 진열대를 둘러보고 계산해요.')
exact('마감 후 매출·상품 매입비·임대료를 확인해요. 매입비는 주문한 날 지출로 기록돼요.','마감 후 수입·지출·남은 금액을 확인해요.')
html=(base/'index.html').read_text().replace('v3.23.1','v3.24.0')
html=html.replace('우리 동네에 선율이 머물다','우리 가게의 첫 번째 생일').replace('한 대의 기타에서 시작한 작은 가게.<br>이제 서른 세트의 전자드럼이<br>누군가의 새로운 리듬을 만들어 갑니다.','작은 가게가 첫 생일을 맞았어요.<br>이제 두 번째 해를 함께 시작해요.')
# New chair sprites are packaged as optional, non-blocking decoration with the existing fallback.
for key in ['chairs']:
 data=(v/(key+'.webp')).read_bytes();name=key+'-v3240-'+hashlib.sha256(data).hexdigest()[:12]+'.webp';(out/'assets'/name).write_bytes(data);html=html.replace('window.GameAssets=Object.freeze({','window.GameAssets=Object.freeze({'+json.dumps('assets/'+key+'-v3240.webp')+':'+json.dumps('assets/'+name)+',')
for p in out.glob('app-*.js'):p.unlink()
appname='app-'+hashlib.sha256(s.encode()).hexdigest()[:12]+'.js';(out/appname).write_text(s);(v/'app.js').write_text(s);html=html.replace(oldapp.name,appname)
oldboot=next(base.glob('boot-*.js'));boot=oldboot.read_text();boot=boot.replace("const startupKeys=Object.keys(window.GameAssets).filter(k=>!optionalKeys.includes(k));", "const startupKeys=['assets/title-v1.webp'];")
# No automatic background download of later-stage sets.
boot=boot.replace('      request(optionalKeys,{priority:2,retry:manual}).catch(()=>{});','')
for p in out.glob('boot-*.js'):p.unlink()
bootname='boot-'+hashlib.sha256(boot.encode()).hexdigest()[:12]+'.js';(out/bootname).write_text(boot);html=html.replace(oldboot.name,bootname)
cssold=next(base.glob('style-*.css'));css=cssold.read_text()+'\n'+(v/'style.css').read_text()
# Font subsetting uses every fixed character in current game, boot and UI.
(v/'font-chars.txt').write_text(''.join(sorted(set(s+html+css+boot+''.join(chr(n)for n in range(32,127))))))
for p in out.glob('style-*.css'):p.unlink()
cssname='style-'+hashlib.sha256(css.encode()).hexdigest()[:12]+'.css';(out/cssname).write_text(css);html=html.replace(cssold.name,cssname);(out/'index.html').write_text(html)
print(appname,cssname,bootname)

import subprocess
subprocess.run(['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python',str(v/'fonts.py')],check=True)
