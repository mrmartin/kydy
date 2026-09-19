#!/usr/bin/env python3
"""Samostatně rozbalitelné balíky úplného archivu, každý pod limitem 2 GiB."""
import argparse,gzip,hashlib,json,shutil,tarfile
from pathlib import Path
P=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,default=P.parent/'brno-volby-2026');a=p.parse_args();A=a.archive.resolve();O=P/'release-assets';O.mkdir(exist_ok=True)
manifest=[]
def record(f):
 h=hashlib.sha256()
 with f.open('rb') as inp:
  for b in iter(lambda:inp.read(8*1024*1024),b''):h.update(b)
 r={'name':f.name,'bytes':f.stat().st_size,'sha256':h.hexdigest()};assert r['bytes']<2*1024**3;manifest.append(r);print(f.name,round(r['bytes']/2**20,1),'MiB',flush=True)
# Samostatná databáze pro uživatele, kteří nepotřebují všechny originály.
f=O/'archiv.sqlite.gz'
with f.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,compresslevel=1,mtime=0) as out,(A/'data/archiv.sqlite').open('rb') as inp:shutil.copyfileobj(inp,out,8*1024*1024)
record(f)
files=[f for f in sorted(A.rglob('*')) if f.is_file() and '__pycache__' not in f.parts];groups=[];group=[];size=0
for f in files:
 n=f.stat().st_size
 if group and size+n>1_400_000_000:groups.append(group);group=[];size=0
 group.append(f);size+=n
if group:groups.append(group)
for i,group in enumerate(groups,1):
 f=O/f'archiv-{i:02d}.tar.gz'
 with f.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,compresslevel=1,mtime=0) as zipped,tarfile.open(fileobj=zipped,mode='w|') as tar:
  for source in group:tar.add(source,arcname=str(Path(A.name)/source.relative_to(A)),recursive=False)
 record(f)
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(O/'SHA256SUMS').write_text(''.join(r['sha256']+'  '+r['name']+'\n' for r in manifest))
print('Hotovo:',len(files),'souborů archivu;',len(groups),'samostatných balíků.',flush=True)
