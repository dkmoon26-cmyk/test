from pathlib import Path
import sys,hashlib,json,re
v=Path(__file__).parent;sys.path.insert(0,'/workspace/little-tone-v3.24.0-validation/python-deps')
from fontTools import subset
from fontTools.ttLib import TTFont
app=Path('/workspace/little-tone-v3.26.0-web');base=Path('/workspace/little-tone-v3.23.1-web');csspath=next(app.glob('style-*.css'));css=csspath.read_text();html=(app/'index.html').read_text();chars=''.join(p.read_text() for p in app.glob('*')if p.suffix in ['.js','.css','.html']);chars=''.join(sorted(set(chars)));(v/'font-chars.txt').write_text(chars);report=[]
for p in (app/'assets').glob('noto-kr-*.woff2'):p.unlink()
for kind in ['regular','bold']:
 src=base/'assets'/('noto-kr-'+kind+'.woff');font=TTFont(src);options=subset.Options();options.flavor='woff2';options.notdef_glyph=True;options.notdef_outline=True;options.recommended_glyphs=True;sub=subset.Subsetter(options=options);sub.populate(text=chars);sub.subset(font);font.flavor='woff2';tmp=v/(kind+'.woff2');font.save(tmp);data=tmp.read_bytes();name='noto-kr-'+kind+'-'+hashlib.sha256(data).hexdigest()[:12]+'.woff2';(app/'assets'/name).write_bytes(data);css=re.sub(r'noto-kr-'+kind+r'-[a-f0-9]+\.woff2',name,css);report.append({'kind':kind,'before':src.stat().st_size,'after':len(data),'file':name,'glyphs':len(font.getGlyphOrder())})
cssname='style-'+hashlib.sha256(css.encode()).hexdigest()[:12]+'.css';csspath.unlink();(app/cssname).write_text(css);html=html.replace(csspath.name,cssname);html=re.sub(r'<link rel="preload" href="assets/noto-kr-[^"]+"[^>]*>','',html);preloads=''.join('<link rel="preload" href="assets/'+r['file']+'" as="font" type="font/woff2" crossorigin>'for r in report);html=html.replace('</head>',preloads+'</head>');(app/'index.html').write_text(html);(v/'font-results.json').write_text(json.dumps({'fixedCharacters':len(chars),'fonts':report},indent=2));print(report)
