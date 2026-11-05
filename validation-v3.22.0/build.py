from pathlib import Path
import re,json,hashlib,shutil
v=Path(__file__).parent;base=Path('/workspace/little-tone-v3.21.0-web');out=Path('/workspace/little-tone-v3.22.0-web');shutil.copytree(base,out,dirs_exist_ok=True)
oldapp=next(base.glob('app-*.js'));s=oldapp.read_text();first,rest=s.split('\n',1);meta=json.loads(first[len('window.GameBuild=Object.freeze('):-2]);meta['version']='3.22.0';meta['schema']['version']=27;s='window.GameBuild=Object.freeze('+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+');\n'+rest
# Preserve the baseline functions used by the redesigned renderers.
def exact(old,new,n=1):
 global s
 assert s.count(old)==n,(old[:100],s.count(old),n)
 s=s.replace(old,new)
from spans import span
for name in ['customTexture','loungeFurnitureSprite','showFurnitureQuick','makeCustomMask']:
 exact('function '+name+'(','function legacy'+name[0].upper()+name[1:]+'(')
patch=(v/'patch.js').read_text()
replaced=['customOptionsFor','customBases','customOptionAvailable','normalizedCustomOptions','customQuote','finishCustom','upgradeWorkbench','setCustomDisplay','displayedCustoms','customerCanAfford','chooseRegularExtra','finishBrowse','openWorkshop','renderWorkshop','refreshCustomPreview','setCustomDraftOption','craftHome','customInventoryHTML','openCustomDisplays']
for name in replaced:
 a,b=span(patch,name);body=patch[a:b];x,y=span(s,name);s=s[:x]+body+'\n'+s[y:];patch=patch[:a]+patch[b:]
exact('// SOURCE: core/state',patch+'\n// SOURCE: core/state')
# Migration happens with the original version before state is validated.
exact("    if(version<25)rules.migrateVIP?.(v,version);","    if(version<25)rules.migrateVIP?.(v,version);\n    if(version<27)rules.migrateCraft?.(v,version);")
exact('validateExpansion: validateExpansionSave,migrateVIP: migrateVIPSave,','validateExpansion: validateExpansionSave,migrateVIP: migrateVIPSave,migrateCraft:migrateCraft27,')
a=s.index(' const c=v.custom??def.custom;');b=s.index(' let guest=null;',a)
s=s[:a]+" const c=v.custom??def.custom;s.vip={zone:z};validateCustom27(v,s,fail);\n"+s[b:]
exact('(vip.dailyCount??0)>3','(vip.dailyCount??0)>3')
exact('(vip.normalSales??0)+s.custom.sold!==s.vip.sales||(vip.normalRevenue??0)+s.custom.totalRevenue!==s.vip.revenue','(vip.normalSales??0)+s.custom.vipSold!==s.vip.sales||(vip.normalRevenue??0)+s.custom.vipRevenue!==s.vip.revenue')
exact("if(![27,28].includes(item.base))return electricCustomTexture(item,rear);","if(products[item.base].family!=='acoustic')return electricCustomTexture(item,rear);")
# A custom display can live in either market; populated cases must remain in their eligible market.
exact("if([12,13,14,15].includes(f.t)&&", "if(f.t===12){const item=S.custom.items.find(i=>i.displayId===f.id);if(item&&!customDisplayAllowed(item,f))return '커스텀 등급에 맞는 판매 구역을 선택해주세요';if(Furniture.cells(f).some(p=>inVIP(p))&&!wideVIP(f))return '진열대 전체를 같은 구역에 놓아주세요';}if([13,14,15].includes(f.t)&&")
exact("  if(t===11&&S.furniture.some(f=>f.t===11))return false;\n",'')
exact(" return !!f&&S.phase==='prepare'&&editing===null&&", " return !!f&&S.phase==='prepare'&&editing===null&&!(f.t===11&&benchJob(f.id))&&")
exact("const value=Math.floor(types[f.t].cost*.5);S.money+=value;", "if(f.t===11){ensureCraftState();delete S.custom.levels[f.id];delete S.custom.ready[f.id];}const value=Math.floor(types[f.t].cost*.5);S.money+=value;")
# Advance only once during a genuine close, then release completed jobs on the next prepare day.
exact('  const wage = staffWage();\n  S.money -=', '  advanceCrafts();\n  const wage = staffWage();\n  S.money -=')
exact("  S.phase = 'prepare';\n  S.opened = false;\n  S.time = 0;", "  S.phase = 'prepare';\n  releaseCompletedCrafts();\n  S.opened = false;\n  S.time = 0;")
exact('workshopDraft=null;if($(\'vipEditBar\'))', "workshopDraft=null;workshopBenchId=null;if($('vipEditBar'))")
# Existing NPC accounting and mission code process raw and custom sales in one transaction.
exact("const affordable = list.filter((o) => products[o.i].price <= profile.budget);", "const affordable = list.filter((o) => offerPrice(o) <= profile.budget);")
exact('    product: choice.i,\n    wantedProduct:', '    product: choice.i,\n    customProductId:choice.customId??null,customBasket:[],\n    wantedProduct:')
exact('      products[choice.i].price <= profile.budget &&', '      offerPrice(choice) <= profile.budget &&')
exact("  return S.furniture\n    .filter((f) => f.t === FurnitureId.GUITAR_RACK", "  return [...S.furniture\n    .filter((f) => f.t === FurnitureId.GUITAR_RACK")
exact("    .filter((o) => near(o.f, ENTRY));", "    .filter((o) => near(o.f, ENTRY)),...(accessory===true?[]:ordinaryCustomOffers())];")
exact("          S.stock[p.product] === 0\n", "          !(p.customProductId?customSelectionAvailable(p):S.stock[p.product]>0)\n")
exact("          S.stock[p.product] > 0 &&\n          (isInstrument", "          (p.customProductId?customSelectionAvailable(p):S.stock[p.product]>0) &&\n          (isInstrument")
exact("      if (value) {\n        S.money += value;", "      const customSale=sellCustomBasket(p,(p.budget??Infinity)-value);value+=customSale.value;soldItems.push(...customSale.bases);\n      if (value) {\n        S.money += value;")
exact("S.custom.sold++;S.custom.totalRevenue+=item.price;", "S.custom.sold++;S.custom.vipSold++;S.custom.totalRevenue+=item.price;S.custom.vipRevenue+=item.price;")
exact('    drawProduct(ctx,p.product,13,-54,24,52,[2,3,7].includes(dir),true);', "    const custom=S.custom.items.find(i=>i.id===p.customProductId);if(custom){ctx.save();ctx.translate(22,-5);miniCustom(ctx,custom,52,[2,3,7].includes(dir));ctx.restore();}else drawProduct(ctx,p.product,13,-54,24,52,[2,3,7].includes(dir),true);")
exact('  drawVIPDraft();', '  drawVIPDraft();drawBenchBadges();')
# Clicks go straight to the particular bench or display's context actions.
exact("if(f?.t===11){e.stopImmediatePropagation();setTab('craft');}else if(f?.t===12){e.stopImmediatePropagation();openCustomDisplays();}","if(f?.t===11){e.stopImmediatePropagation();openWorkshop(f.id);}else if(f?.t===12){e.stopImmediatePropagation();showFurnitureQuick(f);}")
exact("if(action==='workshop')openWorkshop();", "if(action==='workshop')openWorkshop(S.furniture.find(f=>f.id===selected&&f.t===11)?.id??null);")
# New generated base sprite; original instrument images still render on top.
exact("if([12,15,16].includes(f.t))return [", "if(f.t===12)return ['assets/premium-showcase-v3220.webp',...products.map((p,i)=>i).filter(i=>isInstrument(i)).flatMap(productAssetKeys)];\n  if([15,16].includes(f.t))return [")
# Any installed case invalidates its own sprite when the displayed item changes.
exact('  Config,MenuSections,', '  benchLevel,currentWorkbench,benchJob,benchBadge,advanceCrafts,releaseCompletedCrafts,normalizedCustomOptions,quoteCustomAt,ordinaryCustomOffers,offerPrice,basketValue,customDisplayAllowed,isVIPCustom,enoughShoppingTime,clearDisplay,showFurnitureQuick,canSellFurniture,\n  Config,MenuSections,')
pos=s.rfind('})();');s=s[:pos]+(v/'events.js').read_text()+'\n'+s[pos:]
for p in out.glob('app-*.js'):p.unlink()
appname='app-'+hashlib.sha256(s.encode()).hexdigest()[:12]+'.js';(out/appname).write_text(s);(v/'app.js').write_text(s)
cssold=next(base.glob('style-*.css'));css=cssold.read_text()+'\n'+(v/'style.css').read_text();cssname='style-'+hashlib.sha256(css.encode()).hexdigest()[:12]+'.css'
for p in out.glob('style-*.css'):p.unlink()
(out/cssname).write_text(css)
art=(v/'premium-showcase.webp').read_bytes();artname='premium-showcase-v3220-'+hashlib.sha256(art).hexdigest()[:12]+'.webp';(out/'assets'/artname).write_bytes(art)
html=(base/'index.html').read_text().replace(oldapp.name,appname).replace(cssold.name,cssname).replace('v3.21.0','v3.22.0');html=html.replace('window.GameAssets=Object.freeze({','window.GameAssets=Object.freeze({'+json.dumps('assets/premium-showcase-v3220.webp')+':'+json.dumps('assets/'+artname)+',');(out/'index.html').write_text(html)
print(appname,cssname,artname)
