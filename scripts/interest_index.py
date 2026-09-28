"""Pevná redakční pravidla; výsledek nezávisí na skóre ostatních kandidátek."""
import html
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRESENT = ('Ano', 'Ne', 'Zdržel se', 'Nehlasoval')


def rules(data):
    method = json.loads((ROOT / 'research/interest_index.json').read_text())
    cases = {c['id']: c for c in data['cases']}
    seen = set()
    for dimension in method['dimensions']:
        for rule in dimension['cases']:
            cid, vid = rule['case_id'], rule['vote_id']
            if cid in seen or rule['direction'] not in (-1, 1):
                raise ValueError('Dvojí případ nebo neplatný směr indexu')
            if vid not in cases[cid]['vote_ids'] or not rule['reason']:
                raise ValueError('Index bez přiřazeného hlasu nebo zdůvodnění')
            seen.add(cid)
    if seen & method['excluded'].keys() or seen | method['excluded'].keys() != cases.keys():
        raise ValueError('Každý posouzený případ musí mít zdůvodněné zařazení nebo vyřazení')
    return method


def label(value):
    if value <= -.85: return 'Výrazně k pólu „pro sebe“'
    if value < -.2: return 'Blíže k pólu „pro sebe“'
    if value <= .2: return 'Smíšené hlasování'
    if value < .65: return 'Blíže k pólu „pro lidi“'
    if value < .95: return 'Převážně pro lidi'
    return 'Pro lidi v hodnocených případech'


def calculate(data, campaign, method):
    votes = {v['vote_id']: v for o in campaign['observations'] for v in o['votes']}
    dimensions, values, contributors = [], [], set()
    case_count = 0
    for dimension in method['dimensions']:
        items, case_values = [], []
        for rule in dimension['cases']:
            vote = votes.get(rule['vote_id'])
            counts = vote['counts'] if vote else {k: 0 for k in PRESENT}
            present = sum(counts[k] for k in PRESENT)
            value = Fraction(rule['direction'] * (counts['Ano'] - counts['Ne']), present) if present else None
            if value is not None:
                case_values.append(value)
                case_count += 1
                contributors.update(p['person'] for p in vote['people'] if p['vote'] in PRESENT)
            items.append(dict(**rule, score=round(float(value), 6) if value is not None else None,
                              counts=counts, present=present))
        average = sum(case_values) / len(case_values) if case_values else None
        if average is not None: values.append(average)
        dimensions.append(dict(id=dimension['id'], label=dimension['label'],
                               score=round(float(average), 6) if average is not None else None, cases=items))
    complete = len(values) == len(method['dimensions']) and case_count >= 4
    score = round(float(sum(values) / len(values)), 6) if complete else None
    status = 'scored' if complete else 'insufficient_evidence' if campaign['member_count'] else 'no_mandate'
    return dict(version=method['version'], status=status, score=score,
                label=label(score) if score is not None else None,
                members_in_period=campaign['member_count'], people_count=len(contributors),
                people=sorted(contributors), case_count=case_count, total_cases=7, dimensions=dimensions)


def escape(value): return html.escape(str(value), quote=True)


def gauge(result):
    if result['status'] != 'scored':
        text = ('Dnešní kandidáti v období 2022–2026 nebyli v zastupitelstvu města Brna.'
                if result['status'] == 'no_mandate' else 'Byli v zastupitelstvu, ale pro škálu nemáme dost srovnatelných hlasů.')
        return '<div class="interest-index interest-empty"><span class="mini">PRO SEBE, NEBO PRO LIDI?</span><p>'+text+'</p><span class="interest-note">Bez hodnocení na škále.</span></div>'
    position = (result['score'] + 1) * 50
    return f'''<div class="interest-index"><span class="mini">KDYŽ BYLI V ZASTUPITELSTVU, HLASOVALI…</span>
<p class="interest-verdict">{escape(result['label'])}</p>
<div class="interest-track" role="img" aria-label="Škála pro sebe až pro lidi: {escape(result['label'])}. Podle otevřenosti a veřejné kontroly."><span class="interest-marker" style="--position:{position:.4f}%" aria-hidden="true"></span></div>
<div class="interest-poles" aria-hidden="true"><span>Pro sebe</span><span>Pro lidi</span></div>
<p class="interest-basis">Podle otevřenosti a veřejné kontroly.</p>
<span class="interest-note">Hodnoceno {result['people_count']} z {result['members_in_period']} lidí s mandátem na dnešní listině · {result['case_count']} ze {result['total_cases']} případů.</span>
<span class="interest-limit">Nejde o důkaz osobního prospěchu.</span></div>'''


def explanation(data, result):
    if result['status'] != 'scored': return ''
    cases = {c['id']: c for c in data['cases']}
    sections = []
    for dimension in result['dimensions']:
        items = []
        for item in dimension['cases']:
            case = cases[item['case_id']]
            counts = item['counts']
            breakdown = ', '.join(f'{counts.get(k, 0)} {text}' for k, text in [
                ('Ano', 'pro'), ('Ne', 'proti'), ('Zdržel se', 'zdržení'), ('Nehlasoval', 'nehlasování'),
                ('Nepřítomen', 'nepřítomnost'), ('Bez mandátu', 'bez mandátu')])
            direction = ('Bez přítomného zastupitele; nezapočteno.' if item['score'] is None else
                         'Posouvá k „pro lidi“.' if item['score'] > 0 else
                         'Posouvá k „pro sebe“.' if item['score'] < 0 else 'V tomto případě uprostřed škály.')
            items.append(f'<li><a href="/{escape(case["path"])}#{escape(item["vote_id"])}">{escape(case["title"])}</a><p>{escape(breakdown)}. <strong>{direction}</strong></p><p>{escape(item["reason"])}</p></li>')
        sections.append(f'<h4>{escape(dimension["label"])}</h4><ul>'+''.join(items)+'</ul>')
    return '<details class="interest-explanation" id="rozklad-skaly"><summary>Proč jsou na tomto místě škály?</summary><p>Počítají se osobní hlasy uvedených členů dnešní kandidátky, nikoli hlasy nového lídra nebo celé tehdejší strany. Všechny tři oblasti mají stejnou váhu.</p>'+''.join(sections)+'<p>Zdržení a nehlasování mají neutrální příspěvek; nepřítomnost a chybějící mandát se vynechávají. Chybějící případy tak mohou ovlivnit srovnatelnost. Úplné podrobnosti včetně zdrojů jsou po rozkliknutí případu.</p><p><a href="/rozhodovani/#skala">Přesný výpočet, výběr případů a jeho omezení →</a></p></details>'


def methodology(data, method):
    cases = {c['id']: c for c in data['cases']}
    selected = ''.join('<li><strong>'+escape(d['label'])+'</strong>: '+
                       ', '.join(f'<a href="/{escape(cases[r["case_id"]]["path"])}">{escape(cases[r["case_id"]]["title"])}</a>' for r in d['cases'])+'.</li>' for d in method['dimensions'])
    excluded = ''.join(f'<li><a href="/{escape(cases[cid]["path"])}">{escape(cases[cid]["title"])}</a>: {escape(reason)}</li>' for cid, reason in method['excluded'].items())
    return '''<section class="prose interest-method" id="skala"><h2>Škála „pro sebe ↔ pro lidi“</h2>
<p><strong>Je to redakční index otevřenosti a veřejné kontroly, nikoli měření úmyslů politiků.</strong> Pravý pól vyjadřuje podporu dohledatelných rozhodnutí, veřejné debaty a kontroly peněz. Levý pól vyjadřuje opak těchto postojů. Označení „pro sebe“ je zkratka pro menší veřejnou kontrolu politiků, nikoli zjištění, že se někdo obohatil. O výsledcích celého vládnutí ani o splnění všech slibů index nevypovídá.</p>
<h3>Stejný výpočet pro každou kandidátku</h3><p>Verze 1 z 28. 9. 2026 používá sedm hlasování ze sedmi již rozebraných případů. Výběr je redakční, není reprezentativním vzorkem celého období. Tři oblasti mají každá třetinu celkové váhy; uvnitř oblasti mají případy stejné váhy. Více podobných kontrolních hlasování tak nepřeváží zbývající oblasti jen svým počtem.</p><ul>'''+selected+'''</ul>
<p>U každého případu spočítáme rozdíl hlasů ve směru veřejné kontroly a proti němu a vydělíme jej počtem přítomných členů dnešní kandidátky. Souhlas s tajnou volbou má opačné znaménko než souhlas s otevřenými daty nebo kontrolou. Zdržení a nehlasování přispívají nulou a zůstávají ve jmenovateli; nejde o hlas proti. Nepřítomní a lidé bez tehdejšího mandátu jsou vynecháni. Jeden případ bez přítomných se nepočítá; zbývající případy v téže oblasti mají stejné váhy.</p>
<p>Průměr případů vytvoří výsledek oblasti a průměr tří oblastí určí polohu značky. Levý a pravý konec mají pevný význam; škálu nepřizpůsobujeme nejhorší a nejlepší kandidátce. Stejné jednání může dát stejný výsledek. Počet členů týmu nerozmnožuje váhu případu.</p>
<p>Pro zveřejnění potřebujeme alespoň čtyři případy a zastoupení všech tří oblastí. Na kartě uvádíme počet skutečně hodnocených lidí i případů. Malý tým nebo vynechané případy omezují srovnání. Plné vychýlení k „pro lidi“ znamená shodný směr v hodnocených případech, nikoli potvrzení bezchybnosti politika.</p>
<h3>Proč se některé případy nepočítají</h3><p>Hlasování o prodeji, výstavbě nebo placené funkci může současně sloužit různým zájmům. Kde neumíme doložit převahu přínosu nebo újmy, případ zůstává v rozboru s důkazy, ale nedostává znaménko.</p><details><summary>Všech 12 vynechaných případů a důvody</summary><ul>'''+excluded+'''</ul></details>
<p>Jde o naše výslovně uvedené hodnotové měřítko: větší otevřenost a kontrolu pokládáme za přínos obyvatelům. Odmítnutí konkrétního návrhu může mít legitimní důvody; uvádíme je v jednotlivých případech. Škála nehodnotí efektivitu všech veřejných výdajů, pravdivost člověka ani osobní zisk.</p>
<p><a href="/data/jednani-kampani.json">Stáhnout výpočet, pravidla i osobní hlasy v JSON</a> · <a href="https://github.com/mrmartin/kydy/blob/main/research/interest_index.json">Verzovaná pravidla indexu</a>. Číslo se počítá v intervalu od záporné do kladné jedničky; na stránkách zobrazujeme jen jeho polohu a slovní hodnocení.</p></section>'''
