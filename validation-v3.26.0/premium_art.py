from pathlib import Path
import json,subprocess,shutil,re
v=Path(__file__).parent;src=v/'source-art';groups=json.loads((v/'groups.json').read_text());sources=json.loads((v/'premium-sources.json').read_text());info={'bases':{},'parts':[],'motifs':[],'woods':[]}
def dims(p):return list(map(int,subprocess.check_output(['identify','-format','%w %h',str(p)]).split()))
def crop(p,cols,rows,prefix,alpha=True):
 w,h=dims(p);out=[]
 for row in range(rows):
  line=[]
  for col in range(cols):
   a=round(col*w/cols)+2;b=round((col+1)*w/cols)-2;c=round(row*h/rows)+2;d=round((row+1)*h/rows)-2;dest=v/f'{prefix}-{row}-{col}.webp'
   cmd=['convert',str(p),'-crop',f'{b-a}x{d-c}+{a}+{c}','+repage']
   if alpha:cmd+=['-channel','A','-threshold','80%','+channel','-trim','+repage']
   cmd+=['-resize','640x640>','-define','webp:lossless=true',str(dest)];subprocess.run(cmd,check=True)
   if prefix.startswith('premium-'):
    report=subprocess.check_output(['convert',str(dest),'-alpha','extract','-threshold','50%','-define','connected-components:verbose=true','-connected-components','8','null:']).decode()
    objects=[]
    for item in report.splitlines():
     m=re.match(r'\s*(\d+): (\d+x\d+\+\d+\+\d+) \S+ ([0-9.]+) .*\((?:255)(?:,255,255)?\)',item)
     if m:objects.append((float(m[3]),m[2]))
    assert objects,report[:200]
    box=max(objects)[1];subprocess.run(['convert',str(dest),'-crop',box,'+repage','-resize','640x640>','-define','webp:lossless=true',str(dest)],check=True)
   line.append(dest)
  out.append(line)
 return out
def runs_for(w,h,fn):
 rows=[]
 for y in range(h):
  seg=[];start=None
  for x in range(w+1):
   solid=x<w and fn(x,y)
   if solid and start is None:start=x
   if not solid and start is not None:seg.extend([start,x-start]);start=None
  if seg:rows.append([y,seg])
 return rows
for g,ids in enumerate(groups):
 for half in range(2):
  k=f'premium-{g*2+half}';p=src/(k+'.png');shutil.copy2(sources[k],p) if not p.exists() else None;rows=crop(p,3,2,k)
  for col,base in enumerate(ids[half*3:half*3+3]):
   pair=[]
   for rear in [0,1]:
    p=rows[rear][col];w,h=dims(p);rgba=subprocess.check_output(['convert',str(p),'-depth','8','rgba:-']);pixel=lambda x,y:rgba[(y*w+x)*4:(y*w+x)*4+4];xs=[x for x in range(w)if pixel(x,int(h*.25))[3]>128];neck=sum(xs)/len(xs)/w if xs else .5
    gap=0;end=.60;begun=False
    for y in range(int(h*.24),int(h*.76)):
     count=sum(1 for x in range(max(0,int((neck-.06)*w)),min(w,int((neck+.06)*w)))if (lambda p:p[3]>200 and p[0]>p[1]*1.10 and p[1]>p[2]*1.04)(pixel(x,y)))
     if count>w*.025:begun=True;gap=0
     elif begun:
      gap+=1
      if gap>=5:end=(y-4)/h;break
    def body(x,y):
     r,gc,b,a=pixel(x,y)
     return a>128 and y/h>.38 and not(y/h<end+.003 and abs(x/w-neck)<.095) and max(r,gc,b)-min(r,gc,b)<32 and (r+gc+b)>105
    mask=runs_for(w,h,body);outline=runs_for(w,h,lambda x,y:pixel(x,y)[3]>128)
    pair.append({'file':p.name,'w':w,'h':h,'neck':round(neck,4),'neckEnd':round(end,4),'mask':mask,'outline':outline})
   info['bases'][base]=pair
for part in ['hardware-a','hardware-b','hardware-extra']:
 if part in sources:
  p=src/(part+'.png');shutil.copy2(sources[part],p) if not p.exists() else None
  for line in crop(p,4 if part=='hardware-extra' else 5,2,part):
   for p in line:
    w,h=dims(p);info['parts'].append({'file':p.name,'w':w,'h':h})
for key,col,row,alpha in [('motifs-premium',5,2,True),('wood-premium',3,2,False),('materials-extra',3,2,False)]:
 if key not in sources:continue
 p=src/(key+'.png');shutil.copy2(sources[key],p) if not p.exists() else None
 for line in crop(p,col,row,key,alpha):
  for p in line:
   w,h=dims(p);info['motifs'if alpha else'woods'].append({'file':p.name,'w':w,'h':h})
(v/'art.json').write_text(json.dumps(info,separators=(',',':')));print('premium art',len(info['bases']),'bases',len(info['parts']),'parts',len(info['motifs']),'motifs',len(info['woods']),'woods')
