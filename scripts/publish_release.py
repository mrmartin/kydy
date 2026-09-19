#!/usr/bin/env python3
"""Nahraje předem vytvořený archiv do draftu; zveřejní až kompletní vydání."""
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
P=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--repository',default='mrmartin/kydy');p.add_argument('--assets',type=Path,default=P/'release-assets');a=p.parse_args()
TAG='archiv-2026-09-19'
def gh(*args,capture=False):return subprocess.run(['gh',*args],check=True,text=True,capture_output=capture)
gh('auth','status','--hostname','github.com')
manifest=json.loads((a.assets/'manifest.json').read_text())
for r in manifest:
 f=a.assets/r['name'];h=hashlib.sha256()
 with f.open('rb') as inp:
  for b in iter(lambda:inp.read(8*1024*1024),b''):h.update(b)
 assert f.stat().st_size==r['bytes'] and h.hexdigest()==r['sha256'],f
probe=subprocess.run(['gh','release','view',TAG,'--repo',a.repository,'--json','isDraft'],capture_output=True,text=True)
if probe.returncode==0:
 if not json.loads(probe.stdout)['isDraft']:raise SystemExit('Vydání už je veřejné; nepřepisuji existující archiv.')
else:
 notes='Brno před komunálními volbami 2026. Celoměstská úroveň; kampaně k 19. 9. 2026, registr kandidátů k 15. 9. 2026, osobní hlasy do 23. 6. 2026.\n\nBalíky archiv-XX.tar.gz rozbalte všechny do stejného adresáře. Každý je samostatně rozbalitelný; nejde o dělený soubor. Dohromady obnoví celý archiv brno-volby-2026 včetně originálů, textů, dat, analýz a skriptů. archiv.sqlite.gz je navíc samostatná databáze. Otisky jsou v SHA256SUMS.\n\nPůvodní materiály mají podmínky svých vydavatelů; nejde o jednotně licencovanou sadu.'
 with tempfile.NamedTemporaryFile(mode='w',suffix='.md',encoding='utf-8') as tmp:
  tmp.write(notes);tmp.flush();gh('release','create',TAG,'--repo',a.repository,'--target','main','--draft','--title','Brno 2026 – úplný rešeršní archiv','--notes-file',tmp.name)
for name in [r['name'] for r in manifest]+['manifest.json','SHA256SUMS']:
 print('Nahrávám',name,flush=True);gh('release','upload',TAG,str(a.assets/name),'--repo',a.repository,'--clobber')
remote=json.loads(gh('release','view',TAG,'--repo',a.repository,'--json','assets',capture=True).stdout)
assets={x['name']:x for x in remote['assets']}
for r in manifest:assert r['name'] in assets and assets[r['name']]['size']==r['bytes'],r
# Zveřejnění proběhne až po všech úspěšných přenosech.
gh('release','edit',TAG,'--repo',a.repository,'--draft=false')
print('Vydání je veřejné. Nyní sestavte web s --repository '+a.repository+' a nahrajte změnu stránky ke stažení.')
