"""Regrese politicky významných chybných interpretací a integrity nového rozboru."""
import copy
import csv
import hashlib
import importlib.util
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('behavior',ROOT/'scripts/build_behavior.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
DATA=json.loads((ROOT/'research/behavior.json').read_text())
CASES={c['id']:c for c in DATA['cases']}
CAMPAIGNS={p['number']:p for p in DATA['campaigns']}
def rows(name):
    with (ROOT/'site/data'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

class DecisionEvidence(unittest.TestCase):
    def test_all_roll_calls_reconcile_with_source_data(self):
        original={v['hlasovani_id']:v for v in rows('hlasovani.csv')}
        persons={}
        for p in rows('hlasy_jmenovite.csv'):
            if p['hlasovani_id'] in DATA['votes']:persons[(p['hlasovani_id'],p['osoba_id'])]=p
        for vid,v in DATA['votes'].items():
            self.assertEqual(original[vid]['pouzitelne_pro_statistiky'],'ano')
            self.assertEqual(len(v['people']),55)
            for p in v['people']:
                old=persons[vid,p['person']]
                expected='Nepřítomen' if old['volba']=='nepřít.' else old['volba']
                self.assertEqual(p['vote'],expected)
                self.assertEqual(p['club_then'],old['klub_v_protokolu'])
            for key,col in [('Ano','ano'),('Ne','ne'),('Zdržel se','zdrzel_se'),('Nehlasoval','nehlasoval')]:
                self.assertEqual(v['counts'][key],int(original[vid][col]))

    def test_current_lists_never_replace_historical_clubs(self):
        people={p['osoba_id']:p for p in rows('kandidati_2026_propojeni.csv') if p['osoba_id']}
        for v in DATA['votes'].values():
            for p in v['people']:
                self.assertEqual(p['campaign_2026'],int(people[p['person']]['cislo_listiny']) if p['person'] in people else None)
        borecky={p['person']:p for p in DATA['votes']['Z9-25-057']['people'] if 'Bořecký' in p['name']}
        self.assertEqual(borecky['petr-borecky']['campaign_2026'],8)
        self.assertEqual(borecky['petr-borecky-1']['campaign_2026'],2)
        self.assertIn('ANO',borecky['petr-borecky']['club_then'])

    def test_nonvoting_and_absence_are_not_no_votes(self):
        obs=next(o for o in CAMPAIGNS[6]['observations'] if o['case_id']=='povodne-zpravy')['votes'][0]
        self.assertEqual(obs['counts']['Ne'],0)
        self.assertEqual(obs['counts']['Zdržel se'],2)
        self.assertEqual(obs['counts']['Nehlasoval'],8)
        self.assertEqual(obs['counts']['Bez mandátu'],1)
        self.assertEqual(obs['mandates'],10)
        self.assertIn('2 zdržení',builder.count_text(obs['counts']))
        self.assertNotIn('10 proti',builder.count_text(obs['counts']))

    def test_new_leader_cannot_inherit_team_votes(self):
        for obs in CAMPAIGNS[6]['observations']:
            for v in obs['votes']:
                self.assertFalse(any('Zlatušková' in p['name'] for p in v['people']))
        for n in [1,7,9,10,11,12,13,14]:
            self.assertEqual(CAMPAIGNS[n]['case_count'],0)
            self.assertEqual(CAMPAIGNS[n]['observations'],[])

    def test_episode_deduplication_and_counterevidence_required(self):
        self.assertEqual(len(CASES['tic-vanoce']['vote_ids']),2)
        builder.validate(DATA)
        broken=copy.deepcopy(DATA);broken['cases'].append(broken['cases'][0])
        with self.assertRaises(ValueError):builder.validate(broken)
        broken=copy.deepcopy(DATA);broken['cases'][0]['limitations']=''
        with self.assertRaises(ValueError):builder.validate(broken)
        broken=copy.deepcopy(DATA);broken['votes']['Z9-11-007']['counts']['Ne']=0
        with self.assertRaises(ValueError):builder.validate(broken)

    def test_secret_result_not_inferred_and_solar_counterexample_kept(self):
        self.assertEqual(CASES['sako-tajne']['vote_ids'],['Z9-11-007'])
        self.assertEqual(DATA['votes']['Z9-11-007']['counts']['Ano'],28)
        self.assertEqual(DATA['votes']['Z9-35-005']['counts']['Ano'],49)
        self.assertEqual(DATA['votes']['Z9-35-005']['counts']['Ne'],0)
        self.assertIn('solar-kontrola',DATA['comparison_case_ids'])
        self.assertIn('tajný výsledek jednotlivým politikům nepřipisujeme',CASES['sako-tajne']['outcome'])

    def test_personal_benefit_has_named_recipient_and_actual_votes(self):
        c=CASES['uvolnena-funkce']
        self.assertEqual(c['personal_benefit']['person'],'martin-priborsky')
        for vid in c['vote_ids']:
            person=next(p for p in DATA['votes'][vid]['people'] if p['person']=='martin-priborsky')
            self.assertEqual(person['vote'],'Ano');self.assertEqual(person['campaign_2026'],6)
        self.assertIn('nedokazují zneužití moci',c['limitations'])
        self.assertIn('časovou náročnost',c['limitations'])
        broken=copy.deepcopy(DATA)
        next(c for c in broken['cases'] if c['id']=='uvolnena-funkce')['personal_benefit']['person']=''
        with self.assertRaises(ValueError):builder.validate(broken)

    def test_every_record_is_in_selection_log_including_rejected_attempts(self):
        raw=rows('hlasovani.csv');audit=rows('vyber-rozhodovani.csv')
        self.assertEqual({v['hlasovani_id'] for v in raw},{v['hlasovani'] for v in audit})
        self.assertEqual(len(audit),3261)
        self.assertEqual(sum(v['stav']=='vylouceno_neplatne_nebo_nepouzitelne' for v in audit),6)
        item=next(v for v in audit if v['hlasovani']=='Z9-27-050')
        self.assertEqual(item['stav'],'vylouceno_neplatne_nebo_nepouzitelne')
        self.assertNotIn('Z9-04-067',DATA['votes'])
        self.assertEqual(len(rows('vyber-materialu.csv')),4434)
        for v in audit:
            hits=[key for key,pattern in DATA['screening']['rules'].items() if re.search(pattern,v['predmet'],re.I)]
            self.assertEqual(v['shody'],';'.join(hits))

    def test_source_snapshots_and_derived_zip_attachment(self):
        for sid,s in DATA['sources'].items():
            for path,sha in [(s['original'],s['sha256']),(s['text'],s['text_sha256'])]:
                self.assertEqual(hashlib.sha256((ROOT/'site'/path).read_bytes()).hexdigest(),sha,sid)
            self.assertFalse(s['original'].endswith('.html'),'Originál HTML nesmí spouštět kód na webu')
        s=DATA['sources']['tic-audit-2025']
        import zipfile
        with zipfile.ZipFile(ROOT/'site'/s['container']) as z:
            self.assertEqual(hashlib.sha256(z.read(s['container_member'])).hexdigest(),s['sha256'])
        text=(ROOT/'site'/s['text']).read_text()
        self.assertIn('Neexistence reálného rozpočtu akce',text)
        self.assertIn('výstup kontroly',CASES['tic-vanoce']['outcome'])

    def test_every_reference_has_existing_page_and_local_anchor(self):
        refs=[r for c in DATA['cases'] for r in c['references']]+[r for v in DATA['votes'].values() for r in v['references']]
        for ref in refs:
            src=DATA['sources'][ref['source']]
            page=(ROOT/'site/dukazy-jednani'/f'{src["id"]}.html').read_text()
            match=re.search(r'PDF s\. (\d+)',ref['locator'])
            if match:self.assertIn('id="page-'+match[1]+'"',page)

    def test_public_data_and_csv_cover_every_personal_vote(self):
        public=json.loads((ROOT/'site/data/jednani-kampani.json').read_text())
        self.assertEqual(public['votes'],DATA['votes'])
        self.assertEqual(public['cases'],DATA['cases'])
        self.assertNotIn('score',public)
        expected={(o['case_id'],v['vote_id'],p['number'],a['person'],a['vote']) for p in DATA['campaigns'] for o in p['observations'] for v in o['votes'] for a in v['people']}
        actual={(r['pripad'],r['hlasovani'],int(r['listina_2026']),r['osoba_id'],r['hlas']) for r in rows('jednani-hlasy.csv')}
        self.assertEqual(actual,expected)
        for p in public['campaigns']:self.assertNotIn('score',p)

    def test_existing_claims_not_automatically_recolored(self):
        old=json.loads((ROOT/'research/assessment.json').read_text())
        categories=Counter(c['evidence_status'] for p in old['campaigns'] for c in p['claims'])
        self.assertEqual(categories,{'bez_opory':26,'podminene':24,'podlozeno':5,'nevyuzita_moznost':2})
        home=(ROOT/'site/index.html').read_text()
        self.assertEqual(home.count('class="behavior-preview"'),16)
        for p in json.loads((ROOT/'site/data/hodnoceni-kampani.json').read_text())['campaigns']:
            html=(ROOT/'site'/p['path']).read_text()
            self.assertIn('id="rozhodovani"',html)
            self.assertEqual(p['decision_record']['case_count'],CAMPAIGNS[p['number']]['case_count'])
