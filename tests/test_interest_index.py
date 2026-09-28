"""Pevná škála, správné jmenovatele a žádné známky bez doložených hlasů."""
import copy
import json
import runpy
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = runpy.run_path(str(ROOT/'scripts/interest_index.py'))
DATA = json.loads((ROOT/'research/behavior.json').read_text())
METHOD = INDEX['rules'](DATA)


def score(campaign, data=DATA):
    return INDEX['calculate'](data, campaign, METHOD)


class TextOnly(HTMLParser):
    def __init__(self, value):
        super().__init__(); self.parts = []; self.feed(value)
    def handle_data(self, value): self.parts.append(value)


class InterestIndex(unittest.TestCase):
    def test_known_formula_and_equal_dimension_weights(self):
        # ODS: (0.05 + 0 + (0.9 + 1 + 1)/3)/3; nepřítomný je vynechán.
        ods = score(DATA['campaigns'][5])
        self.assertAlmostEqual(ods['score'], (.05 + 0 + 2.9/3)/3, places=6)
        self.assertEqual([d['score'] for d in ods['dimensions']], [.05, 0, .966667])
        self.assertEqual(ods['people_count'], 11)
        self.assertEqual(ods['case_count'], 7)

    def test_opposite_votes_map_to_fixed_endpoints_without_ranking(self):
        for sign in (-1, 1):
            p = copy.deepcopy(DATA['campaigns'][14])
            desired = {r['vote_id']: 'Ano' if sign*r['direction'] == 1 else 'Ne'
                       for d in METHOD['dimensions'] for r in d['cases']}
            for obs in p['observations']:
                for v in obs['votes']:
                    if v['vote_id'] not in desired: continue
                    choice = desired[v['vote_id']]
                    for person in v['people']: person['vote'] = choice
                    v['counts'] = {k: len(v['people']) if k == choice else 0 for k in v['counts']}
            self.assertEqual(score(p)['score'], sign)
            self.assertEqual(score(p, dict(DATA, campaigns=[p]))['score'], sign)

    def test_neutral_missing_and_absent_are_distinct(self):
        p = copy.deepcopy(DATA['campaigns'][14])
        for obs in p['observations']:
            for v in obs['votes']:
                for person in v['people']: person['vote'] = 'Zdržel se'
                v['counts'] = {k: len(v['people']) if k == 'Zdržel se' else 0 for k in v['counts']}
        self.assertEqual(score(p)['score'], 0)
        for obs in p['observations']:
            for v in obs['votes']:
                v['counts']['Nepřítomen'] = v['counts'].pop('Zdržel se')
                v['counts']['Zdržel se'] = 0
                for person in v['people']: person['vote'] = 'Nepřítomen'
        result = score(p)
        self.assertIsNone(result['score'])
        self.assertEqual(result['status'], 'insufficient_evidence')
        self.assertNotIn('nebyli v zastupitelstvu', INDEX['gauge'](result))

    def test_no_mandate_is_not_zero_or_good_score(self):
        for p in DATA['campaigns']:
            r = score(p)
            if p['member_count'] == 0:
                self.assertEqual(r['status'], 'no_mandate')
                self.assertIsNone(r['score'])
                self.assertNotIn('interest-track', INDEX['gauge'](r))
            else:
                self.assertTrue(-1 <= r['score'] <= 1)
        # Za Lužánky: jeden člověk, šest případů; nový lídr jeho hlasy nedědí.
        r = score(DATA['campaigns'][4])
        self.assertEqual((r['people_count'], r['case_count']), (1, 6))
        self.assertEqual(r['people'], ['tomas-kolacny'])

    def test_case_selection_is_complete_and_procedures_not_doubled(self):
        ids = [r['case_id'] for d in METHOD['dimensions'] for r in d['cases']]
        votes = [r['vote_id'] for d in METHOD['dimensions'] for r in d['cases']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids) | METHOD['excluded'].keys(), {c['id'] for c in DATA['cases']})
        self.assertIn('Z9-04-068', votes)
        self.assertNotIn('Z9-04-002', votes)
        for cid in ['tic-vanoce', 'dornych', 'uvolnena-funkce']:
            self.assertTrue(METHOD['excluded'][cid])

    def test_visual_scale_has_no_printed_score_and_exports_are_reproducible(self):
        public = json.loads((ROOT/'site/data/jednani-kampani.json').read_text())
        assessment = json.loads((ROOT/'site/data/hodnoceni-kampani.json').read_text())
        self.assertEqual(public['interest_index_method'], METHOD)
        for p, out, a in zip(DATA['campaigns'], public['campaigns'], assessment['campaigns']):
            result = score(p)
            self.assertEqual(result, out['interest_index'])
            self.assertEqual(result, a['decision_record']['interest_index'])
            markup = INDEX['gauge'](result)
            text = ' '.join(TextOnly(markup).parts)
            if result['score'] is not None:
                self.assertNotIn(str(result['score']), text)
                self.assertIn('role="img"', markup)
                self.assertIn(result['label'], text)
        home = (ROOT/'site/index.html').read_text()
        self.assertEqual(home.count('class="interest-track"'), 8)
        self.assertEqual(home.count('class="interest-index interest-empty"'), 8)
        self.assertIn('/rozhodovani/#skala', home)
        for a in assessment['campaigns']:
            page = (ROOT/'site'/a['path']).read_text()
            if a['decision_record']['interest_index']['score'] is not None:
                self.assertIn('id="rozklad-skaly"', page)
