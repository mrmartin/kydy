"""Regrese pro politicky významné chyby a pravidla souhrnu."""
import csv
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_assessment',ROOT/'scripts/build_assessment.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
DATA=json.loads((ROOT/'research/assessment.json').read_text())
PARTIES={p['number']:p for p in DATA['campaigns']}
CLAIMS={c['id']:c for p in DATA['campaigns'] for c in p['claims']}

class Composition(unittest.TestCase):
    def test_mix_preserves_missing_evidence_and_conflict(self):
        self.assertEqual(builder.composition(['podlozeno','podlozeno','rozpor','bez_opory']),
                         {'podlozeno':2,'podminene':0,'rozpor':1,'bez_opory':1})
        self.assertEqual(builder.composition(['bez_opory'])['bez_opory'],1)
    def test_invalid_or_old_scale_rejected(self):
        for values in [[],['UNKNOWN'],['MOŽNÁ'],['podlozeno',None]]:
            with self.assertRaises(ValueError):builder.composition(values)
    def test_public_schema_has_no_future_prediction(self):
        self.assertEqual(DATA['schema_version'],2)
        self.assertEqual(DATA['methodology_version'],2)
        public=json.loads((ROOT/'site/data/hodnoceni-kampani.json').read_text())
        for p in public['campaigns']:
            self.assertNotIn('verdict',p)
            self.assertEqual(p['evidence_counts'],builder.composition([c['evidence_status'] for c in p['claims']]))
            for c in p['claims']:
                self.assertNotIn('verdict',c)
                self.assertIn(c['evidence_status'],builder.STATUSES)
                self.assertTrue(c['reason'])
    def test_csv_preserves_all_categories_and_reasons(self):
        with (ROOT/'site/data/hodnoceni-slibu.csv').open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual({r['id'] for r in rows},set(CLAIMS))
        for r in rows:
            c=CLAIMS[r['id']]
            self.assertEqual(r['opora_kod'],c['evidence_status'])
            self.assertEqual(r['opora_popis'],builder.STATUSES[c['evidence_status']]['label'])
            self.assertEqual(r['duvod'],c['reason'])
    def test_evidence_not_election_uncertainty_determines_category(self):
        self.assertEqual(CLAIMS['K03-03']['evidence_status'],'podlozeno')
        self.assertNotIn('volební zastoupení',CLAIMS['K03-03']['reason'])
        self.assertEqual(CLAIMS['K02-01']['evidence_status'],'podminene')
        self.assertEqual(CLAIMS['K16-01']['evidence_status'],'bez_opory')
        # Celý balík sportovišť nezezelená jen díky aréně.
        self.assertEqual(CLAIMS['K06-02']['evidence_status'],'podminene')
        self.assertEqual(CLAIMS['K06-05']['evidence_status'],'podlozeno')
    def test_cards_label_every_promise_without_relying_on_color(self):
        home=(ROOT/'site/index.html').read_text()
        self.assertEqual(home.count('<small>'),len(CLAIMS))
        self.assertEqual(home.count('class="composition"'),16)
        self.assertNotIn('všude MOŽNÁ',home)
        self.assertIn('Barva ukazuje oporu slibu',home)
        for status in builder.STATUSES.values():self.assertIn(status['label'],home)

class Evidence(unittest.TestCase):
    def vote(self,claim,vid):return next(v for v in CLAIMS[claim]['votes'] if v['id']==vid)
    def test_complete_lists_and_bounded_claim_selection(self):
        self.assertEqual(set(PARTIES),set(range(1,17)))
        self.assertEqual(sum(p['candidates'] for p in PARTIES.values()),828)
        for n,p in PARTIES.items():
            self.assertTrue(1<=len(p['claims'])<=5)
            if n not in [1,11]:self.assertGreaterEqual(len(p['claims']),3)
            self.assertTrue(p['selection'])
    def test_old_mandates_not_badged_new(self):
        for n in [7,9,12,13]:
            self.assertEqual(PARTIES[n]['experience']['status'],'former')
            self.assertTrue(PARTIES[n]['experience']['references'])
        self.assertEqual(PARTIES[6]['experience']['status'],'new')
        self.assertEqual(PARTIES[6]['current_members'],11)
    def test_secret_procedure_not_secret_result(self):
        v=self.vote('K03-03','Z9-11-007')
        self.assertIn('tajné hlasování',v['meaning'])
        self.assertIn('následně',v['limit'])
        states={p['person']:p['vote'] for p in v['people']}
        self.assertEqual(states['jana-drapalova'],'Ne')
        self.assertEqual(states['jasna-flamikova'],'Ne')
        self.assertEqual(states['matous-vencalek'],'Bez mandátu')
    def test_dornych_actual_date_and_party_switches(self):
        v=self.vote('K08-01','Z9-25-057')
        self.assertEqual(v['date'],'2025-03-25')
        self.assertEqual(sum(p['vote']=='Ano' for p in v['people']),7)
        self.assertEqual(next(p['vote'] for p in v['people'] if p['person']=='petr-levicek'),'Zdržel se')
        self.assertEqual(next(p['vote'] for p in v['people'] if p['person']=='sabina-benesova'),'Bez mandátu')
        self.assertEqual(sum(p['vote']=='Ne' for p in self.vote('K15-02','Z9-25-057')['people']),3)
    def test_audit_alternatives_not_same_proposal(self):
        a=self.vote('K05-02','Z9-25-075');b=self.vote('K05-02','Z9-25-076')
        self.assertIn('pracovní skupinu',a['meaning'])
        self.assertIn('externímu',b['meaning'])
        self.assertEqual(a['people'][0]['vote'],'Ano')
        self.assertEqual(b['people'][0]['vote'],'Zdržel se')
    def test_source_traceability_and_snapshot_integrity(self):
        for c in CLAIMS.values():
            self.assertTrue(c['counterevidence'] and c['change'] and c['authority'])
            for r in [c['source']]+c['references']+c['authority_references']:
                self.assertIn(r['source'],DATA['sources']);self.assertTrue(r['locator'])
        for sid,s in DATA['sources'].items():
            self.assertEqual(len(s['sha256']),64)
            self.assertTrue(s['url'].startswith('https://'))
            if s['text_sha256']:
                self.assertEqual(hashlib.sha256((ROOT/'site'/s['text']).read_bytes()).hexdigest(),s['text_sha256'],sid)
    def test_no_national_poll_projection_or_invented_late_votes(self):
        self.assertIn('neodhadujeme',DATA['polling'])
        self.assertIn('návrhy nezaměňujeme',DATA['coverage_note'])
        self.assertTrue(all(v['date']<=DATA['votes_through'] for c in CLAIMS.values() for v in c['votes']))
        self.assertIn('odmítají',PARTIES[4]['political'])
    def test_old_sources_cannot_overwrite_current_home(self):
        self.assertIn('data-kydy-home',(ROOT/'site/index.html').read_text())
        self.assertNotIn('data-kydy-home',(ROOT/'site/archiv.html').read_text())

if __name__=='__main__':unittest.main()
