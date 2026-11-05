from pathlib import Path
import sys,hashlib,json,re
v=Path(__file__).parent;sys.path.insert(0,str(v/'python-deps'))
from fontTools import subset
from fontTools.ttLib import TTFont
app=Path('/workspace/little-tone-v3.24.0-web');base=Path('/workspace/little-tone-v3.23.1-web');csspath=next(app.glob('style-*.css'));css=csspath.read_text();html=(app/'index.html').read_text();chars=(v/'font-chars.txt').read_text();report=[]
for p in (app/'assets').glob('noto-kr-*'):
 if p.suffix in ['.woff','.woff2']:p.unlink()
for kind in ['regular','bold']:
 src=base/'assets'/('noto-kr-'+kind+'.woff');font=TTFont(src);options=subset.Options();options.flavor='woff2';options.notdef_glyph=True;options.notdef_outline=True;options.recommended_glyphs=True;sub=subset.Subsetter(options=options);sub.populate(text=chars);sub.subset(font);font.flavor='woff2';tmp=v/(kind+'.woff2');font.save(tmp);data=tmp.read_bytes();name='noto-kr-'+kind+'-'+hashlib.sha256(data).hexdigest()[:12]+'.woff2';(app/'assets'/name).write_bytes(data);css=css.replace('noto-kr-'+kind+'.woff',name).replace("format('woff')","format('woff2')").replace('format("woff")','format("woff2")');report.append({'kind':kind,'before':src.stat().st_size,'after':len(data),'file':name,'glyphs':len(font.getGlyphOrder())})
cssname='style-'+hashlib.sha256(css.encode()).hexdigest()[:12]+'.css';csspath.unlink();(app/cssname).write_text(css);html=html.replace(csspath.name,cssname)
preloads=''.join('<link rel="preload" href="assets/'+r['file']+'" as="font" type="font/woff2" crossorigin>'for r in report)
assets=json.loads(html.split('window.GameAssets=Object.freeze(',1)[1].split(');',1)[0]);preloads+='<link rel="preload" href="'+assets['assets/title-v1.webp']+'" as="image">';html=html.replace('</head>',preloads+'</head>');(app/'index.html').write_text(html);(v/'font-results.json').write_text(json.dumps({'fixedCharacters':len(set(chars)),'fonts':report},indent=2));print(json.dumps(report))
