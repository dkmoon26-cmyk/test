from pathlib import Path
import json,statistics as st,hashlib,csv
p=Path('/workspace/little-tone-v3.17.0-economy');r=Path('/workspace/little-tone-v3.17.0-web')
raw=json.loads((p/'results.json').read_text());raw.update(json.loads((p/'extra-results.json').read_text()));assert len(raw)==18
costs=[0,2000000,4500000,10000000,22000000,40000000];rows=[];audits=[];clean={}
for k,a in raw.items():
 assert len(a['days'])==60 and not a['errors'] and not a['runtimeErrors']
 ds=a['days'];d=ds[-1];cap=sum(a['capitalCosts'].values())+sum(costs[int(s)-1] for s in a['firstStage']);cash=5000000+sum(d['revenue']+d['missionIncome']-d['expenses'] for d in ds);wealth=5000000+2160000+sum(d['operatingSurplus']+d['missionIncome'] for d in ds)-cap;actual=d['money']+d['inventoryCost']+d['pendingCost']
 assert abs(cash-d['money'])<.01 and abs(wealth-actual)<.01
 autoSpend=sum(x['expenses']-x['rent']-x['wages'] for x in ds)-cap-a['manualInventoryCost'];assert autoSpend>=0
 audit={'run':k,'cashIdentityDifference':cash-d['money'],'cashAndInventoryIdentityDifference':wealth-actual,'trueAutomaticInventorySpend':autoSpend};audits.append(audit)
 # Opening auto-purchases precede the tick observer. Publish reconciled cash cost; omit incomplete order counts.
 a['sampledAutoOrdersExcludingOpening']=a.pop('autoOrders');a['sampledAutoInventoryCostExcludingOpening']=a.pop('autoInventoryCost');a['autoInventoryCost']=autoSpend
 for day in a['days']:day['sampledAutoOrdersExcludingOpening']=day.pop('autoOrders')
 clean[k]=a
order=['manual','automatic','express','tuned','lean','rush'];names={'manual':'수동 보충','automatic':'기본 자동 위임','express':'기본 자동+긴급 개입','tuned':'예약 수량3개','lean':'예약 기준1개·수량1개','rush':'빠른 확장·적은 예비금'}
for mode in order:
 runs=[a for a in clean.values() if a['mode']==mode];last=[d for a in runs for d in a['days'][-10:]];avg=lambda f:st.mean(f(a) for a in runs)
 row={'mode':mode,'label':names[mode],'runs':3,'finalCashMean':avg(lambda a:a['days'][-1]['money']),'finalCashMin':min(a['days'][-1]['money'] for a in runs),'finalCashMax':max(a['days'][-1]['money'] for a in runs),'finalInventoryMean':avg(lambda a:a['days'][-1]['inventoryCost']+a['days'][-1]['pendingCost']),'stage6Days':[a['firstStage']['6'] for a in runs],'endingDays':[a['endingDay'] for a in runs],'negativeCashDays':sum(d['money']<0 for a in runs for d in a['days']),'zeroSaleDays':sum(d['sold']==0 for a in runs for d in a['days']),'minimumObservedCash':min(d['minCash'] for a in runs for d in a['days']),'stockoutNonpurchaseDeparturesMean':avg(lambda a:sum(d['stockoutDepartures'] for d in a['days'])),'partialAutoCashBlockedSecondsMean':avg(lambda a:sum(d['blockedSeconds'] for d in a['days'])),'manualOrderTransactionsMean':avg(lambda a:a['manualOrders']),'expressFeesMean':avg(lambda a:a['expressFees']),'last10DayOperatingSurplusMean':st.mean(d['operatingSurplus'] for d in last),'last10DayRevenueMean':st.mean(d['revenue'] for d in last),'last10DayFixedCostsMean':st.mean(d['rent']+d['wages'] for d in last)};rows.append(row)
manifest=json.loads((r/'DEPLOY-MANIFEST.json').read_text());unchanged=all(hashlib.sha256((r/e['path']).read_bytes()).hexdigest()==e['sha256'] for e in manifest['files']);assert unchanged
summary={'version':'3.17.0','runs':18,'daysPerRun':60,'totalDays':1080,'seeds':[17,2026,731],'startingCash':5000000,'startingGiftInventoryCost':2160000,'moneyOrSalesInjected':False,'gameFilesUnmodified':unchanged,'noAdsOrDiscountDecor':True,'summary':rows,'accountingAudits':audits,'limits':['Three seeds per policy, not a player-population or statistical guarantee.','Bot checks inventory every 10 simulation seconds; manual mode is unusually attentive.','All policies hire cashiers when queues grow, if affordable. Manual mode means no inventory employee.','Assortment expansion, mission rewards, hiring and customer story gifts use normal game actions only.','No optional ads, catalogue, amp, plant, poster or rug; one normal demo seat and unlocked drum demo are used.','Stockout nonpurchase count does not prove those visitors would have bought with stock available.','Cash net includes inventory and capital spending; operating surplus excludes capital spending and values sold units at purchase price. Express surcharges are expensed when ordered.','Opening staff purchases are reconciled from actual cash ledgers; tick-sampled auto-order counts are not used for conclusions.']}
(p/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');(p/'audited-runs.json').write_text(json.dumps(clean,ensure_ascii=False,indent=2)+'\n')
with (p/'daily.csv').open('w',newline='',encoding='utf-8-sig') as f:
 fields=['mode','seed','day','stage','money','inventoryCost','pendingCost','revenue','sold','cashNet','operatingSurplus','rent','wages','stockoutDepartures','blockedSeconds','manualOrders','expressFees'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();
 for a in clean.values():
  for d in a['days']:w.writerow({k:a[k] if k in ['mode','seed'] else d[k] for k in fields})
print('PASS: 18 natural-growth runs, 1080 days; cash and inventory accounting identities exact; source unchanged')
# Export a standard standalone plot.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
font=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');plt.rcParams['font.family']=font.get_name();plt.rcParams['axes.unicode_minus']=False
colors=['#496d8d','#4f7957','#b88b44','#b56355','#348f8b','#9579a7']
fig,axs=plt.subplots(2,1,figsize=(12.5,9.5),gridspec_kw={'height_ratios':[1.4,1]},layout='constrained');fig.patch.set_facecolor('#fffaf0')
for mode,col in zip(order,colors):
 runs=[a for a in clean.values() if a['mode']==mode];means=[st.mean(a['days'][d]['money'] for a in runs)/10000 for d in range(60)];lo=[min(a['days'][d]['money'] for a in runs)/10000 for d in range(60)];hi=[max(a['days'][d]['money'] for a in runs)/10000 for d in range(60)];axs[0].plot(range(1,61),means,label=names[mode],color=col,lw=2);axs[0].fill_between(range(1,61),lo,hi,color=col,alpha=.07)
axs[0].set(title='v3.17.0 경제 시뮬레이션 — 자금·실적 주입 없이 18회, 총 1,080일',xlabel='영업일',ylabel='현금 (만 원)');axs[0].grid(alpha=.2);axs[0].legend(ncol=3,fontsize=9,loc='upper left')
x=list(range(6));cash=[a['finalCashMean']/10000 for a in rows];stock=[a['finalInventoryMean']/10000 for a in rows];axs[1].bar(x,cash,color='#4f7957',label='60일 후 현금');axs[1].bar(x,stock,bottom=cash,color='#d9bc7d',label='재고·입고 예정 (매입가)');axs[1].set_xticks(x,[names[m].replace('·','\n') for m in order],fontsize=9);axs[1].set(ylabel='만 원',title='남은 현금과 재고에 묶인 자금은 구분해야 합니다');axs[1].legend(loc='upper right');axs[1].grid(axis='y',alpha=.2)
for i,cashv in enumerate(cash):axs[1].text(i,cashv/2,f'{cashv:,.0f}',ha='center',va='center',color='white',fontsize=10)
fig.savefig(p/'economy-comparison.png',dpi=160,facecolor=fig.get_facecolor());plt.close(fig)
