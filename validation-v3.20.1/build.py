from pathlib import Path
import re,json,hashlib,shutil,subprocess
v=Path(__file__).parent
removedKeys=['assets/people-everyday-v310.webp','assets/people-regulars-v310.webp','assets/people-story-v310.webp','assets/people-special-v310.webp','assets/people-team-v310.webp','assets/drummer-v350.webp','assets/team-checkout-v3100.webp']
def clean(base,out):
 base=Path(base);out=Path(out);out.mkdir(exist_ok=True);shutil.copytree(base,out,dirs_exist_ok=True)
 metadata=json.loads(subprocess.check_output(['node',str(v/'metadata.cjs'),str(base/'index.html')],text=True));app=base/metadata['app'];s=app.read_text();before=len(s.encode());removed=[]
 def fnspan(name):
  a=re.search(r'^function '+name+r'\(',s,re.M).start();le=s.index('\n',a);b=le if s[a:le].rstrip().endswith('}')else le+re.search(r'^}',s[le:],re.M).end();return a,b
 for name in ['atelierPanel','expansionCard']:
  assert len(re.findall(r'\b'+name+r'\b',s))==1,name
  a,b=fnspan(name);s=s[:a]+s[b:];removed.append(name)
 for name in ['PeopleFrames','PeopleAtlasKeys']:
  s,n=re.subn(r'^const '+name+r'=.*;\n','',s,flags=re.M);assert n==1,name
 s,n=re.subn(r'^const peopleAtlases = PeopleAtlasKeys.map\(runtimeImage\);\n','',s,flags=re.M);assert n==1
 # Keep diagnostic metadata pointed at active images; all rendered poses remain the same.
 marker=re.search(r'^const CheckoutPoses=.*;\n',s,re.M);assert marker
 aliases="const PeopleAtlasKeys=[...NaturalWalkAtlasKeys,CheckoutAtlasKey];\nconst PeopleFrames=Array.from({length:22},(_,actor)=>NaturalWalkFrames[actor]??{atlas:NaturalWalkAtlasKeys.length,rows:[[CheckoutPoses[actor][0]],[CheckoutPoses[actor][1]],[CheckoutPoses[actor][1]]]});\n"
 s=s[:marker.end()]+aliases+s[marker.end():]
 a,b=fnspan('actorAssetKeys');s=s[:a]+"function actorAssetKeys(actor){if(CheckoutPoses[actor])return [CheckoutAtlasKey];const frame=NaturalWalkFrames[actor];if(!frame)throw new RangeError('Unknown character identity');return [NaturalWalkAtlasKeys[frame.atlas]];}"+s[b:]
 a,b=fnspan('walkSprite');s=s[:a]+"""function walkSprite(actor,dir,phase=0,moving=true,playing=false){
 if(CheckoutPoses[actor])return checkoutSprite(actor,dir);
 const row=dir===4||dir===6?2:[2,3,7].includes(dir)?1:0,entry=NaturalWalkFrames[actor];if(!entry)throw new RangeError('Unknown character identity');const count=entry.rows[row].length,frame=moving?((Math.floor(phase*count)%count)+count)%count:1;
 return {image:naturalWalkAtlases[entry.atlas],...entry.rows[row][frame],flip:dir===1||dir===3||dir===6,frame,actor,dir,natural:true};
}"""+s[b:]
 s=s.replace('"version":"3.20.0"','"version":"3.20.1"',1)
 assert not any(k in s for k in removedKeys)
 name='app-'+hashlib.sha256(s.encode()).hexdigest()[:12]+'.js'
 for p in out.glob('app-*.js'):p.unlink()
 (out/name).write_text(s)
 html=(base/'index.html').read_text();match=[m for m in re.finditer(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',html)if 'window.GameAssets='in m.group(1)][0]
 deleted=[]
 for key in removedKeys:
  rel=metadata['assets'].pop(key);p=out/rel;deleted.append({'key':key,'path':rel,'bytes':p.stat().st_size});p.unlink();metadata['packing'].pop(key,None)
 inline='window.GameAssets=Object.freeze('+json.dumps(metadata['assets'],separators=(',',':'))+');window.GameAtlasPacking=Object.freeze('+json.dumps(metadata['packing'],separators=(',',':'))+');window.GameAppURL='+json.dumps(name)+';document.getElementById("loadingRetry").onclick=function(){location.reload()};'
 html=html[:match.start(1)]+inline+html[match.end(1):];(out/'index.html').write_text(html)
 for p in out.glob('test-save-*.json'):
  data=json.loads(p.read_text());data['appVersion']='3.20.1';p.write_text(json.dumps(data,ensure_ascii=False,indent=2))
 for p in out.glob('*.txt'):p.write_text(p.read_text().replace('v3.20.0','v3.20.1'))
 return {'directory':str(out),'oldApp':app.name,'newApp':name,'oldJSBytes':before,'newJSBytes':len(s.encode()),'oldHTMLBytes':len((base/'index.html').read_bytes()),'newHTMLBytes':len(html.encode()),'removedFunctions':removed,'removedImages':deleted,'removedImageBytes':sum(p['bytes']for p in deleted),'remainingImages':len(metadata['assets'])}
report=[clean('/workspace/little-tone-v3.20.0-web','/workspace/little-tone-v3.20.1-web'),clean('/workspace/little-tone-v3.20.0-test-web','/workspace/little-tone-v3.20.1-test-web')]
(v/'cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
