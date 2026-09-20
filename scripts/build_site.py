#!/usr/bin/env python3
"""Publikační kopie archivu pro Pages; původní rešerši nijak nemění."""
import argparse,html,json,re,shutil
from pathlib import Path
from urllib.parse import urlsplit,unquote,quote
P=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,default=P.parent/'brno-volby-2026');p.add_argument('--repository',default='');a=p.parse_args()
if a.repository and not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',a.repository):p.error('Repozitář má formát vlastník/název')
A=a.archive.resolve();S=P/'site';S.mkdir(exist_ok=True)
rs={x['url']:x for x in map(json.loads,(A/'data/zdroje.jsonl').read_text().splitlines())}
originals={r['soubor']:r['url'] for r in rs.values() if r.get('soubor')}
for directory in ['analyzy','profily','kampane-2026','texty','data']:
 for source in (A/directory).rglob('*'):
  if not source.is_file() or source.suffix=='.sqlite' or source.name=='zdroje.jsonl':continue
  rel=source.relative_to(A);dest=S/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
for name in ['index.html','styl.css','zdroje.html','SHA256SUMS']:shutil.copyfile(A/name,S/name)
def link(url,rel):
 # Absolutní URL původního vydavatele; místní textové kopie zůstávají dostupné.
 parts=urlsplit(html.unescape(url))
 if parts.scheme or not parts.path:return url
 absolute=(A/rel.parent/unquote(parts.path)).resolve()
 try:key=absolute.relative_to(A).as_posix()
 except ValueError:return url
 if key in originals:return html.escape(originals[key]+('#'+parts.fragment if parts.fragment else ''),quote=True)
 if key=='data/archiv.sqlite':
  import os
  return os.path.relpath(S/'ke-stazeni.html',S/rel.parent)+'#databaze'
 return url
for f in [*S.rglob('*.html'),*S.rglob('*.md')]:
 rel=f.relative_to(S);t=f.read_text()
 if f.suffix=='.html':
  t=re.sub(r'((?:href|src)=["\'])(.*?)(["\'])',lambda m:m[1]+link(m[2],rel)+m[3],t)
  t=t.replace('uložený originál','originál u vydavatele').replace('Uložený originál','Originál u vydavatele')
  note='<p class="note">Veřejná verze rešeršního archivu: analýzy, data a textové kopie. Originály odkazují na vydavatele. <a href="'+('' if rel.parent==Path('.') else '../')+'ke-stazeni.html">Stažení archivu a databáze</a>.</p>'
  if rel.as_posix() in ['index.html','zdroje.html']:t=t.replace('</nav>','</nav>'+note,1)
 else:t=re.sub(r'(\]\()([^\s)]+)(\))',lambda m:m[1]+link(m[2],rel)+m[3],t)
 f.write_text(t)
# Katalog generuje odkazy za běhu. Původní manifest CSV zachovává cesty do úplného archivu.
f=S/'zdroje.html';t=f.read_text();m=re.search(r'const data=(.*?);const norm=',t,re.S);assert m
catalog=json.loads(m[1])
for r in catalog:
 if r.get('soubor'):r['soubor']=r['url']
t=t[:m.start(1)]+json.dumps(catalog,ensure_ascii=False,separators=(',',':')).replace('</','<\/')+t[m.end(1):]
t=t.replace("[['Originál',x.soubor]","[['Originál u vydavatele',x.soubor]");f.write_text(t)
f=S/'kampane-2026/data.js';d=json.loads(f.read_text().removeprefix('const D=').strip().removesuffix(';').replace('<\/','</'))
for r in d['sources'].values():r['soubor']=r['url']
f.write_text('const D='+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\/')+';\n')
f=S/'kampane-2026/index.html';t=f.read_text().replace('href="../\'+esc(r.soubor)','href="\'+esc(r.soubor)').replace('href="../\'+esc(D.sources[v.minutes].soubor)','href="\'+esc(D.sources[v.minutes].soubor)');f.write_text(t)
# Funkční stránka i před publikováním Releases; žádné neexistující odkazy.
manifest=P/'release-assets/manifest.json'
if not manifest.exists():manifest=P.parent/'web-github/release-assets/manifest.json'
assets=json.loads(manifest.read_text()) if manifest.exists() else []
release=('https://github.com/'+a.repository+'/releases/tag/archiv-2026-09-19') if a.repository else ''
rows=[]
for item in assets:
 url='https://github.com/'+a.repository+'/releases/download/archiv-2026-09-19/'+quote(item['name']) if a.repository else ''
 name='<a href="'+url+'">'+html.escape(item['name'])+'</a>' if url else html.escape(item['name'])
 rows.append('<tr><td>'+name+'</td><td>'+f'{item["bytes"]/2**20:.1f} MiB'+'</td><td><code>'+item['sha256']+'</code></td></tr>')
body='<h1>Stažení podkladů</h1><p>Analýzy, CSV a textové kopie jsou přímo na webu. Celý rešeršní archiv včetně původních souborů má přibližně 16 GB.</p><h2 id="databaze">Úplný archiv a SQLite</h2>'
body+=('<p><a href="'+release+'">Otevřít vydání archivu na GitHubu</a>. Tabulka níže uvádí připravené soubory; dostupnost vydání ověřte na GitHubu.</p>' if release else '<p>Soubory jsou připraveny místně. Veřejné odkazy doplníme po nahrání archivu na GitHub Releases.</p>')
body+='<p>Databáze je archiv.sqlite.gz. Po rozbalení ji lze otevřít v SQLite nebo DB Browser for SQLite. Samostatné balíky archiv-XX.tar.gz obsahují různé části původního archivu; všechny rozbalte do stejné složky. Nejde o dělený soubor vyžadující spojování.</p><div class="scroll"><table><tr><th>Soubor</th><th>Velikost</th><th>SHA-256</th></tr>'+''.join(rows)+'</table></div><p>CSV katalog zachovává původní místní cesty uvnitř úplného archivu. Původní dokumenty mají podmínky svých vydavatelů; nejde o jednotně licencovanou sadu.</p>'
(S/'ke-stazeni.html').write_text('<!doctype html><html lang="cs"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stažení podkladů · kydy.cz</title><link rel="stylesheet" href="styl.css"><body><nav><a href="index.html">Brno · přehled</a> · <a href="kampane-2026/index.html">Kampaně a hlasy</a></nav>'+body+'</body></html>')
(S/'CNAME').write_text('kydy.cz\n');(S/'.nojekyll').touch()
(S/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://kydy.cz/sitemap.xml\n')
paths=['index.html','kampane-2026/index.html','analyzy/kampane_2026.html','analyzy/prehled.html','analyzy/temata.html']
(S/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://kydy.cz/'+p+'</loc></url>' for p in paths)+'</urlset>')
# Poslední krok vždy obnoví nový rozcestník a zachová původní pod archiv.html.
import subprocess
subprocess.run(['python3',str(P/'scripts/build_assessment.py')],check=True)
files=[f for f in S.rglob('*') if f.is_file()];total=sum(f.stat().st_size for f in files)
assert total<900_000_000,'Web je příliš blízko limitu Pages'
assert all(f.stat().st_size<95_000_000 for f in files),'Soubor je příliš velký pro běžný Git'
report={'files':len(files),'bytes':total,'domain':'kydy.cz','repository':a.repository,'archive':str(A),'source_links':'původní vydavatelé; textové kopie místně'}
(P/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
