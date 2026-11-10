from pathlib import Path
import json,hashlib,re,zipfile
p=Path('/workspace/little-tone-v3.28.0-web');base=Path('/workspace/little-tone-v3.27.0-uipack-input/little-tone-v3_27_0-web-uipack');out=Path('/workspace/little-tone-v3.28.0-validation')
sha=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((p/'DEPLOY-MANIFEST.json').read_text());assert m['version']=='3.28.0'and m['schema']==32
for f in m['files']:
 d=(p/f['path']).read_bytes();assert len(d)==f['bytes']and sha(d)==f['sha256'],f['path']
listed={x['path']for x in m['files']};assert listed=={x.relative_to(p).as_posix()for x in p.rglob('*')if x.is_file()and x.name!='DEPLOY-MANIFEST.json'}
h=(p/'index.html').read_text();refs=re.findall(r'(?:src|href)=[\"\']([^\"\']+)',h)
for r in refs:
 if not r.startswith(('http:','https:','#','data:')):assert (p/r).exists(),r
c=next(p.glob('style*')).read_text()
for r in re.findall(r'url\([\"\']?([^\"\')]+)',c):
 if not r.startswith('data:'):assert (p/r).exists(),r
s=next(p.glob('app*')).read_text();assert '"version":"3.28.0"'in s and 'v3.28.0'in h
# Original supplied artwork is retained exactly; only font assets are replaced.
art=[]
for f in (base/'assets').glob('*'):
 if f.suffix in ['.png','.webp','.svg','.jpg']:
  assert (p/'assets'/f.name).read_bytes()==f.read_bytes(),f.name;art.append(f.name)
# Check the uploaded gameplay changes remain in the game.
assert re.search(r'capacity[\"\']?:\s*24',s)
for name in ['guestPaceLT','laneOffsetLT','stockValueLT','ledgerLT','watchMissionsLT']:assert 'function '+name+'('in s
for f in p.rglob('*'):assert '__pycache__'not in str(f)
zp=Path('/workspace/little-tone-v3.28.0-web.zip')
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for f in sorted(p.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(p).as_posix())
with zipfile.ZipFile(zp)as z:
 assert z.testzip()is None
 for e in m['files']:assert sha(z.read(e['path']))==e['sha256']
report={'pass':True,'version':'3.28.0','schema':32,'base':'user-uploaded little-tone-v3_27_0-web-uipack.zip','files':len(m['files'])+1,'zipBytes':zp.stat().st_size,'sha256':sha(zp.read_bytes()),'originalArtworkUnchanged':len(art),'htmlReferences':len(refs),'manifestVerified':True,'zipCRC':True,'fonts':[{ 'file':f.name,'bytes':f.stat().st_size}for f in sorted((p/'assets').glob('little-tone-ui-*.woff2'))]}
(out/'package-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report,ensure_ascii=False))
