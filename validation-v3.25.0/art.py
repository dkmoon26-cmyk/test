from pathlib import Path
import subprocess,json
v=Path(__file__).parent
sets=[('luxury',str(v/'source-art/instruments.png'),7,2,2172,724),('greenery',str(v/'source-art/decor.png'),3,2,1536,1024)]
info={}
for name,src,cols,rows,W,H in sets:
 clips=[]
 for y in range(rows):
  row=[]
  for x in range(cols):
   a=round(x*W/cols);b=round((x+1)*W/cols);c=round(y*H/rows);d=round((y+1)*H/rows)
   # Atlas extraction only; all artwork and background removal were produced by imagegen.
   target=v/f'{name}-{y}-{x}.webp'
   subprocess.run(['convert',src,'-crop',f'{b-a}x{d-c}+{a}+{c}','+repage','-channel','A','-threshold','80%','+channel','-trim','+repage','-define','webp:lossless=true',str(target)],check=True)
   dims=subprocess.check_output(['identify','-format','%w %h',str(target)]).decode().split();row.append({'file':target.name,'w':int(dims[0]),'h':int(dims[1])})
  clips.append(row)
 info[name]=clips
(v/'art.json').write_text(json.dumps(info,indent=2))
print(info)
