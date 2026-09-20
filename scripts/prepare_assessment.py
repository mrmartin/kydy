#!/usr/bin/env python3
"""Sestaví přenositelný, zdrojovaný podklad; nevyžaduje import těžkého archivu."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('curation', ROOT / 'research/curation.py')
curation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(curation)


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def prepare(archive):
    data = archive / 'data'
    original = {r['tvrzeni_id']: r for r in rows(data / 'kampane_2026_tvrzeni.csv')}
    sources = {r['id']: r for r in map(json.loads, (data / 'zdroje.jsonl').read_text().splitlines()) if r.get('stav') == 'ok'}
    votes = {r['hlasovani_id']: r for r in rows(data / 'kampane_2026_vybrana_hlasovani.csv')}
    candidates = rows(data / 'kandidati_2026_propojeni.csv')
    # Kompaktní převod již ověřených osobních stavů; šestý stav je bez mandátu.
    packed = json.loads((archive / 'kampane-2026/data.js').read_text().removeprefix('const D=').strip().removesuffix(';'))
    packed_votes = {v['id']: v for v in packed['votes']}
    people = {c['osoba_id']: c for c in candidates if c.get('osoba_id')}
    state_names = ['Ano', 'Ne', 'Zdržel se', 'Nehlasoval', 'Nepřítomen', 'Bez mandátu']
    used = set()

    def references(pairs):
        result = []
        for sid, locator in pairs:
            assert sid in sources, (sid, locator)
            used.add(sid)
            result.append({'source': sid, 'locator': locator})
        return result

    campaigns = []
    for party in packed['parties']:
        number = party['cislo_listiny']
        editorial = curation.CAMPAIGNS[number]
        leader = next(c for c in candidates if int(c['cislo_listiny']) == number and int(c['poradi']) == 1)
        known_old = curation.OLDER_LEADERS.get(number)
        if leader.get('mandat_2022_2026') == 'ano':
            experience = {'status': 'current', 'label': 'Mandát v období 2022–2026', 'note': 'Osobní hlasy lídra jsou součástí archivu.'}
        elif known_old:
            experience = {'status': 'former', 'label': 'Dřívější mandát', 'note': known_old[0], 'references': references(known_old[1])}
        else:
            experience = {'status': 'new', 'label': 'NOVÝ', 'note': 'Bez doloženého mandátu v celoměstském zastupitelstvu: bez mandátu 2022–2026, starší mandát při cílené rešerši nenalezen. Nejde o úplný audit všech historických funkcí ani o tvrzení, že nemá jinou praxi.'}
            if number == 5:
                experience['references'] = references([('b84d55484f37f5a3', 'vlastní popis vstupu do politiky 4. 9. 2026')])
            if number == 14:
                experience['references'] = references([('1cde5a071f4d126b', 'ředitel KAM od 2016 – odborná, nikoli zastupitelská role')])
        experience['references'] = experience.get('references', []) + references([(party['kandidati_zdroj_id'], 'registr kandidátů 2026; propojení s mandáty v archivních CSV')])
        claims = []
        for item in curation.CLAIMS:
            if int(item['key'][1:3]) != number:
                continue
            old = original.get(item['key'], {})
            sid = item['source'] or old['zdroj_id']
            competence, competence_refs = curation.COMPETENCES[item['competence']]
            vids = item['votes'] if item['votes'] is not None else list(filter(None, old.get('hlasovani_ids', '').split(';')))
            vote_details = []
            for vid in vids:
                v = votes[vid]
                personal = []
                for pid, state in zip(packed['pids'], packed_votes[vid]['states']):
                    person = people[pid]
                    if int(person['cislo_listiny']) == number:
                        personal.append({'name': person['jmeno'], 'person': pid, 'position': int(person['poradi']), 'vote': state_names[int(state)]})
                personal.sort(key=lambda r: r['position'])
                vote_details.append({'id': vid, 'date': v['datum'], 'title': v['predmet'], 'meaning': v['vyznam_ano'], 'limit': v['mez_interpretace'], 'result': v['vysledek'], 'all_yes': int(v['ano']), 'all_no': int(v['ne']), 'people': personal, 'references': references([(v['zdroj_id'], 'úplný jmenný protokol'), (v['zapis_zdroj_id'], 'PDF s. ' + v['zapis_pdf_strana'])])})
            history = item['history'] or old.get('poznamka') or 'Přímý osobní návrh nebo realizovaný výsledek odpovídající tomuto slibu nebyl v ověřeném výběru doložen; nejde o důkaz nečinnosti.'
            claims.append({'id': item['key'], 'title': item['title'], 'promise': item['promise'] or old['tvrzeni_parafraze'], 'source': references([(sid, item['locator'] or old['lokator'])])[0], 'verdict': item['verdict'], 'reason': item['why'], 'signal': item['signal'], 'history': history, 'authority': competence, 'practical': item['practical'], 'change': item['change'], 'counterevidence': item['counter'] or 'Budoucí závazek není tvrzení, že stejné opatření již bylo provedeno. Chybějící podklad nepovažujeme za důkaz opaku.', 'references': references(item['references']), 'authority_references': references(competence_refs), 'votes': vote_details, 'updated': curation.DATE, 'review': 'zdrojové posouzení a kontrola mezí interpretace; bez nezávislé externí recenze'})
        claims.sort(key=lambda c: c['id'])
        campaigns.append({'number': number, 'name': party['kratky_nazev'], 'full_name': party['listina'], 'leader': party['lidr'], 'candidates': party['kandidatu'], 'current_members': party['soucasnych_zastupitelu'], 'past_members': party['drzitelu_mandatu_2022_2026'], 'experience': experience, 'summary': editorial['summary'], 'selection': editorial['selection'], 'political': editorial['political'], 'political_references': references(editorial.get('political_refs', [])), 'program_references': references([(s, party['pokryti_kampane']) for s in party['zdroj_ids'].split(';')]), 'claims': claims})
    # Zářijový index a konsolidovaný statut jsou součástí dohledatelné kontroly pokrytí.
    used.update(['26743906971e276a', '67c597f38cf2997b', '9ab34d056564ca37'])
    normalized_sources = {}
    for sid in sorted(used):
        r = sources[sid]
        origin = archive / r['soubor']
        assert hashlib.sha256(origin.read_bytes()).hexdigest() == r['sha256'], sid
        normalized_sources[sid] = {k: r.get(k, '') for k in ['id', 'url', 'nazev', 'stazeno_utc', 'sha256', 'soubor', 'text', 'content_type']}
        normalized_sources[sid]['text_sha256'] = hashlib.sha256((archive / r['text']).read_bytes()).hexdigest() if r.get('text') else ''
    result = {'schema_version': 1, 'updated': curation.DATE, 'campaign_snapshots': '2026-09-19', 'votes_through': '2026-06-23', 'polling': 'K 20. 9. 2026 nebyl v této rešerši ověřen použitelný aktuální brněnský volební model. Neznamená to, že žádný neexistuje. Mandáty neodhadujeme z celostátních průzkumů ani z volebního potenciálu.', 'coverage_note': 'Z9/37 ze dne 15. 9. 2026: zkontrolována stránka jednání a vybrané předložené materiály. V načteném indexu nebyly odkazy na zápis ani jmenné protokoly; návrhy nezaměňujeme za schválená rozhodnutí. Úplná ověřená hlasovací řada končí 23. 6. 2026.', 'campaigns': campaigns, 'sources': normalized_sources, 'changes': [{'date': curation.DATE, 'text': 'První vydání: oddělení slibů, doložených kroků, pravomocí a podmínek; zahrnuty starší role a zářijová koaliční vyjádření. Neuzavřené otázky zůstávají MOŽNÁ.'}]}
    (ROOT / 'research/assessment.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    # Samostatné nové textové kopie jsou dostupné i bez opětovného sestavení 16GB archivu.
    for sid, r in normalized_sources.items():
        if r['text']:
            target = ROOT / 'site' / r['text']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((archive / r['text']).read_bytes())
    print(f"Podklady: {len(campaigns)} kampaní, {sum(len(p['claims']) for p in campaigns)} slibů, {len(used)} pramenů.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, default=ROOT.parent / 'brno-volby-2026')
    prepare(parser.parse_args().archive)
