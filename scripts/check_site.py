#!/usr/bin/env python3
"""Bez závislostí: limit Pages, soubory v Gitu a všechny místní HTML odkazy."""
import json,re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
P=Path(__file__).resolve().parents[1];S=P/'site'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src'] and v:self.links.append(v)
files=[p for p in S.rglob('*') if p.is_file()];size=sum(p.stat().st_size for p in files)
assert size<900_000_000,(size,'Limit Pages')
assert all(p.stat().st_size<95_000_000 for p in files),'Limit jednotlivého souboru Git'
assert (S/'CNAME').read_text().strip()=='kydy.cz'
count=0;missing=[]
for p in S.rglob('*.html'):
 parser=Links();parser.feed(p.read_text())
 for url in parser.links:
  u=urlsplit(url)
  if u.scheme or u.netloc or not u.path:continue
  target=S/unquote(u.path.lstrip('/')) if u.path.startswith('/') else p.parent/unquote(u.path)
  count+=1
  if not target.exists():missing.append((str(p.relative_to(S)),url))
assert not missing,missing[:30]
s=(S/'kampane-2026/data.js').read_text();d=json.loads(s.removeprefix('const D=').strip().removesuffix(';').replace('<\/','</'))
assert len(d['candidates'])==828 and len(d['votes'])==3255
for r in d['sources'].values():
 assert r['soubor'].startswith('https://'),r
 if r.get('text'):assert (S/r['text']).exists()
print(f'OK: {len(files)} souborů, {size/2**20:.1f} MiB, {count} místních odkazů; 828 kandidátů a 3255 protokolů.')
