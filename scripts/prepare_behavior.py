#!/usr/bin/env python3
"""Přenosný podklad rozhodování a úplný protokol výběru. Žádné odhady motivů."""
import argparse
import csv
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
spec = importlib.util.spec_from_file_location('behavior_curation', ROOT/'research/behavior_curation.py')
curation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(curation)
STATES = ['Ano','Ne','Zdržel se','Nehlasoval','Nepřítomen','Bez mandátu']

def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path, records):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(records)

def prepare(archive):
    data=archive/'data'
    raw_votes=rows(data/'hlasovani.csv')
    all_votes={v['hlasovani_id']:v for v in raw_votes}
    meanings={v['hlasovani_id']:v for v in rows(data/'kampane_2026_vybrana_hlasovani.csv')}
    candidates=rows(data/'kandidati_2026_propojeni.csv')
    current={c['osoba_id']:c for c in candidates if c['osoba_id']}
    people={p['osoba_id']:p for p in rows(data/'osoby.csv')}
    sources={s['id']:s for s in map(json.loads,(data/'zdroje.jsonl').read_text().splitlines()) if s.get('stav')=='ok'}
    source_out={}
    dest=SITE/'podklady-jednani';dest.mkdir(exist_ok=True)

    def source(sid):
        if sid in source_out:return sid
        if sid=='tic-audit-2025':
            parent=sources['45d5d4685d0136be']
            original=archive/parent['soubor']
            assert hashlib.sha256(original.read_bytes()).hexdigest()==parent['sha256']
            zip_dest=dest/'tic-audit-2025.zip';shutil.copyfile(original,zip_dest)
            with zipfile.ZipFile(original) as z:
                # Konkrétní ověřená příloha; neextrahovat cesty dodané ZIPem.
                content=z.read('Příloha č. 1.pdf')
            pdf=dest/'tic-audit-2025.pdf';pdf.write_bytes(content)
            txt=dest/'tic-audit-2025.txt'
            subprocess.run(['pdftotext','-layout',str(pdf),str(txt)],check=True)
            source_out[sid]=dict(id=sid,title='Závěrečná zpráva externího posouzení Brněnských Vánoc 2023 a 2024',url=parent['url'],downloaded=parent['stazeno_utc'],original=pdf.relative_to(SITE).as_posix(),text=txt.relative_to(SITE).as_posix(),sha256=hashlib.sha256(content).hexdigest(),text_sha256=hashlib.sha256(txt.read_bytes()).hexdigest(),container=zip_dest.relative_to(SITE).as_posix(),container_sha256=parent['sha256'],container_member='Příloha č. 1.pdf')
        else:
            s=sources[sid];original=archive/s['soubor']
            assert hashlib.sha256(original.read_bytes()).hexdigest()==s['sha256'],sid
            suffix = '.html.txt' if original.suffix == '.html' else original.suffix
            out=dest/(sid+suffix);shutil.copyfile(original,out)
            txt=dest/(sid+'.txt');shutil.copyfile(archive/s['text'],txt)
            source_out[sid]=dict(id=sid,title=s.get('nazev') or ('Úřední podklad '+sid),url=s['url'],downloaded=s['stazeno_utc'],original=out.relative_to(SITE).as_posix(),text=txt.relative_to(SITE).as_posix(),sha256=s['sha256'],text_sha256=hashlib.sha256(txt.read_bytes()).hexdigest())
        return sid

    def refs(pairs):
        return [dict(source=source(sid),locator=locator) for sid,locator in pairs]

    wanted={v for c in curation.CASES for v in c['vote_ids']}
    personal=defaultdict(list)
    for r in rows(data/'hlasy_jmenovite.csv'):
        if r['hlasovani_id'] not in wanted:continue
        assert r['pouzitelne_pro_statistiky']=='ano'
        c=current.get(r['osoba_id'])
        vote='Nepřítomen' if r['volba']=='nepřít.' else r['volba']
        assert vote in STATES, vote
        personal[r['hlasovani_id']].append(dict(person=r['osoba_id'],name=people[r['osoba_id']]['jmeno'],club_then=r['klub_v_protokolu'],campaign_2026=int(c['cislo_listiny']) if c else None,position_2026=int(c['poradi']) if c else None,vote=vote))
    votes={}
    for vid in sorted(wanted):
        v=all_votes[vid];assert v['pouzitelne_pro_statistiky']=='ano'
        persons=personal[vid]
        assert len(persons)==55 and len({p['person'] for p in persons})==55,vid
        if vid in curation.EXTRA_VOTES:
            meaning,sid,pageno=curation.EXTRA_VOTES[vid]
            limit='Výklad a meze tohoto rozhodnutí jsou uvedeny u celého případu.'
        else:
            m=meanings[vid];meaning=m['vyznam_ano'];sid=m['zapis_zdroj_id'];pageno=int(m['zapis_pdf_strana']);limit=m['mez_interpretace']
        counts=Counter(p['vote'] for p in persons)
        for key,field in [('Ano','ano'),('Ne','ne'),('Zdržel se','zdrzel_se'),('Nehlasoval','nehlasoval')]:assert counts[key]==int(v[field]),(vid,key)
        assert sum(counts[k] for k in STATES[:4])==int(v['pritomno']),vid
        votes[vid]=dict(id=vid,date=v['datum'],title=v['predmet'],meaning=meaning,limit=limit,result=v['vysledek'],counts={k:counts[k] for k in STATES[:5]},people=sorted(persons,key=lambda p:p['name']),references=refs([(v['zdroj_id'],'Jmenný protokol '+vid),(sid,f'PDF s. {pageno} – usnesení a výsledek')]))

    cases=[]
    for original in curation.CASES:
        c=dict(original)
        c['references']=refs(c['references'])
        c['path']='rozhodovani/'+c['id']+'/index.html'
        c['date_from']=min(votes[v]['date'] for v in c['vote_ids'])
        c['date_to']=max(votes[v]['date'] for v in c['vote_ids'])
        c['opportunity']='O uvedených návrzích rozhodovalo celoměstské zastupitelstvo. Každý tehdejší zastupitel mohl ovlivnit vlastní hlas; samotný mandát mu nedával samostatnou většinu ani pravomoc řídit městskou firmu. Předkladatele a konkrétní výkonné kroky uvádíme jen tam, kde jsou doložené.'
        cases.append(c)

    assessment=json.loads((ROOT/'research/assessment.json').read_text())
    known_claims={c['id'] for p in assessment['campaigns'] for c in p['claims']}
    assert all(set(c['claim_ids'])<=known_claims for c in cases)
    campaign_data=[]
    export=[]
    for p in assessment['campaigns']:
        number=p['number'];observations=[]
        for c in cases:
            entries=[]
            for vid in c['vote_ids']:
                v=votes[vid]
                on_list=[person for person in v['people'] if person['campaign_2026']==number]
                # Jmenovitě ukázat i dnešní kandidáty s jiným datem nástupu/odchodu.
                no_mandate=[dict(person=a['osoba_id'],name=a['jmeno'],club_then='',campaign_2026=number,position_2026=int(a['poradi']),vote='Bez mandátu') for a in candidates if a['osoba_id'] and int(a['cislo_listiny'])==number and a['osoba_id'] not in {r['person'] for r in v['people']}]
                counts=Counter(r['vote'] for r in on_list)
                counts['Bez mandátu']=len(no_mandate)
                entries.append(dict(vote_id=vid,mandates=len(on_list),present=sum(counts[k] for k in STATES[:4]),counts={k:counts[k] for k in STATES},people=sorted(on_list+no_mandate,key=lambda a:a['position_2026'])))
                for a in on_list+no_mandate:
                    export.append(dict(pripad=c['id'],oblast=curation.AXES[c['axis']],hlasovani=vid,datum=v['date'],vyznam_ano=v['meaning'],listina_2026=number,osoba_id=a['person'],jmeno=a['name'],klub_tehdy=a['club_then'],hlas=a['vote']))
            if any(e['mandates'] for e in entries):observations.append(dict(case_id=c['id'],votes=entries))
        campaign_data.append(dict(number=number,name=p['name'],member_count=p['past_members'],case_count=len(observations),finding=curation.FINDINGS.get(number,''),finding_cases=['sako-tajne','lanovka-verejnost','povodne-zpravy']+(['tic-vanoce'] if number==5 else []) if number in curation.FINDINGS else [],observations=observations))

    # Úplný reprodukovatelný záznam: i bez shody, neplatné a dosud neposouzené.
    case_by_vote={v:c['id'] for c in cases for v in c['vote_ids']}
    assert len(case_by_vote)==sum(len(c['vote_ids']) for c in cases),'Jedno hlasování nesmí být více nezávislých případů'
    screening=[]
    for v in raw_votes:
        hits=[k for k,pat in curation.SCREENING.items() if re.search(pat,v['predmet'],re.I)]
        vid=v['hlasovani_id'];note='';reference=''
        if v['pouzitelne_pro_statistiky']!='ano':status='vylouceno_neplatne_nebo_nepouzitelne';note=v['omezeni'] or v['platnost_dle_zapisu']
        elif vid in case_by_vote:status='kontext_overen';note='Součást případu '+case_by_vote[vid]
        elif vid in curation.REVIEW_EXCLUSIONS:
            note,sid,pageno=curation.REVIEW_EXCLUSIONS[vid];source(sid);status='kontext_overen_bez_hodnoceni';reference=f'/dukazy-jednani/{sid}.html#page-{pageno}'
        elif re.search(r'Volba.*(Kontrolního výboru|Kontrolního výbor)|Změna ve složení Kontrolního',v['predmet'],re.I):status='personalni_bod_bez_vykladu';note='Obsazování nebo postup volby; bez ověření pravomocí, vazeb a důsledků nedokládá účinnost kontroly.'
        elif hits:status='k_dalsimu_posouzeni';note='Tematická shoda, význam a souvislosti zatím nejsou posouzené.'
        else:status='bez_shody_v_nazvu';note='Pravidla nezachytila téma v názvu. Nevylučuje významné rozhodnutí v obsahu.'
        screening.append(dict(hlasovani=vid,datum=v['datum'],predmet=v['predmet'],pouzitelne=v['pouzitelne_pro_statistiky'],shody=';'.join(hits),stav=status,pripad=case_by_vote.get(vid,''),duvod=note,zdroj=v['url'],kontext=reference))
    materials=[]
    material_cases=defaultdict(list)
    for c in cases:
        for r in c['references']:
            material_cases[source_out[r['source']]['url']].append(c['id'])
    for m in rows(data/'materialy_zmb_index.csv'):
        hits=[k for k,pat in curation.SCREENING.items() if re.search(pat,m['nazev'],re.I)]
        linked=sorted(set(material_cases.get(m['url'],[])))
        materials.append(dict(zasedani=m['zasedani'],nazev=m['nazev'],shody=';'.join(hits),stav='zdroj_overeneho_pripadu' if linked else 'tematicka_shoda_neovereny_obsah' if hits else 'bez_shody_v_nazvu',pripad=';'.join(linked),zdroj=m['url']))
    write_csv(SITE/'data/vyber-rozhodovani.csv',screening)
    write_csv(SITE/'data/vyber-materialu.csv',materials)
    write_csv(SITE/'data/jednani-hlasy.csv',export)
    d=dict(schema_version=1,reviewed=curation.REVIEWED,votes_from=min(v['date'] for v in votes.values()),votes_through=max(v['datum'] for v in raw_votes if v['pouzitelne_pro_statistiky']=='ano'),coverage='Rozbor historického rozhodování 2022–2026. Úplná načtená jmenná řada končí 23. 6. 2026; vybrané pozdější dokumenty doplňují výsledky, nikoli chybějící osobní hlasy. Nejde o povolební přehled ani aktualizaci volebních výsledků.',axes=curation.AXES,cases=cases,votes=votes,campaigns=campaign_data,sources=source_out,screening=dict(rules=curation.SCREENING,total_votes=len(raw_votes),usable_votes=sum(v['pouzitelne_pro_statistiky']=='ano' for v in raw_votes),reviewed_votes=len(wanted),cases=len(cases),statuses=dict(Counter(r['stav'] for r in screening)),materials=len(materials),material_hits=sum(bool(m['shody']) for m in materials)),comparison_case_ids=curation.CONTROL_CASES,limitations=['Výběr je tematický a redakčně ověřený, nikoli náhodný nebo úplný audit každého rozhodnutí.','Automatické vyhledávání prochází názvy všech protokolů a indexovaných materiálů. Nevydáváme jej za přečtení všech příloh.','Osobní zájem, protiprávnost ani motivaci neodvozujeme z hlasovací shody. Náklady a veřejné přínosy nejsou obecně srovnané.','Role v městské vládě je doložená samostatně u kampaně; hlasovací tabulka uchovává klub z konkrétního dne. Dnešní listina není tehdejší klub.','Nováčkům ani lidem bez mandátu nepřičítáme cizí hlasy. Nulový počet případů není pozitivní hodnocení.'],inputs={name:hashlib.sha256((data/name).read_bytes()).hexdigest() for name in ['hlasovani.csv','hlasy_jmenovite.csv','kandidati_2026_propojeni.csv','materialy_zmb_index.csv']})
    (ROOT/'research/behavior.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    (SITE/'data/jednani-kampani.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    print(f"Rozhodování: {len(cases)} případů, {len(votes)} hlasování, {len(source_out)} pramenů; prohledáno {len(raw_votes)} protokolů a {len(materials)} materiálů.")

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path,default=ROOT.parent/'brno-volby-2026')
    prepare(parser.parse_args().archive)
