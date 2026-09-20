#!/usr/bin/env python3
"""Statické stránky kampaní; žádné rozhodování ani síťové požadavky za běhu."""
import csv
import hashlib
import html
import json
import re
import shutil
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
STATUSES = {
    'podlozeno': {'label': 'Podloženo činy', 'short': 's oporou v činech', 'css': 'yes'},
    'podminene': {'label': 'Podmíněně proveditelné', 'short': 's podmínkami', 'css': 'maybe'},
    'nevyuzita_moznost': {'label': 'Neudělali to, když mohli', 'short': 's nevyužitou možností', 'css': 'missed'},
    'rozpor': {'label': 'Zásadní rozpor nebo překážka', 'short': 'se zásadním rozporem', 'css': 'no'},
    'bez_opory': {'label': 'Zatím jen slib', 'short': 'zatím jen slib', 'css': 'unknown'},
}


def escape(value):
    return html.escape(str(value), quote=True)


def composition(statuses):
    if not statuses or any(v not in STATUSES for v in statuses):
        raise ValueError('Chybí platná posouzení opory slibů')
    counts = Counter(statuses)
    return {key: counts[key] for key in STATUSES}


def validate_accountability(claim):
    """Negativní závěr musí mít úplný důkazní řetězec, ne jen vládní funkci."""
    if claim['evidence_status'] != 'nevyuzita_moznost':
        return
    evidence = claim.get('accountability')
    required = ('scope', 'scope_label', 'period', 'actors', 'authority', 'opportunity', 'outcome', 'limitations', 'references', 'decision_kind')
    if not evidence or any(not evidence.get(k) for k in required):
        raise ValueError('Nevyužitá možnost bez podkladů: ' + claim['id'])
    if any(not all(person.get(k) for k in ('person','name','role','action')) for person in evidence['actors']):
        raise ValueError('Chybí osobní odpovědnost: ' + claim['id'])


def scope_note(claim):
    if a := claim.get('accountability'):
        return f'<small class="scope-note">Rozsah: {escape(a["scope_label"])}</small>'
    return ''


def composition_html(counts):
    total = sum(counts.values())
    segments = ''.join(f'<span class="{STATUSES[k]["css"]}" style="flex:{n}"></span>' for k, n in counts.items() if n)
    labels = ''.join(f'<span class="count-item"><span class="status-dot {STATUSES[k]["css"]}" aria-hidden="true"></span><strong>{n}</strong> {STATUSES[k]["short"]}</span>' for k, n in counts.items() if n)
    return f'<div class="composition" aria-label="Opora {total} vybraných slibů"><div class="composition-bar" aria-hidden="true">{segments}</div><div class="composition-counts">{labels}</div></div>'


def slug(party):
    name = unicodedata.normalize('NFKD', party['name']).encode('ascii', 'ignore').decode().lower()
    return f"{party['number']:02d}-" + re.sub(r'[^a-z0-9]+', '-', name).strip('-')


def badge(status):
    info = STATUSES[status]
    return f'<span class="verdict {info["css"]}"><span aria-hidden="true" class="dot"></span>{info["label"]}</span>'


def date(value):
    year, month, day = value[:10].split('-')
    return f'{int(day)}. {int(month)}. {year}'


def page(title, body, path, description='Sliby brněnských kampaní, osobní hlasy a ověřitelné důvody hodnocení.'):
    footer = '''<footer class="footer"><a class="wordmark" href="/">kydy<span>.cz</span></a><p>Podklady pro vlastní rozhodnutí.</p><nav aria-label="Patička"><a href="/metodika.html">Jak hodnotíme</a><a href="/mapa-webu.html">Mapa webu a celý archiv</a><a href="/data/hodnoceni-kampani.json">Data JSON</a><a href="/data/hodnoceni-slibu.csv">Data CSV</a><a href="https://github.com/mrmartin/kydy/issues">Nahlásit chybu se zdrojem</a></nav><p class="fine">Veřejné podklady zpracované s pomocí AI. Posouzení neprošlo nezávislou externí recenzí. Budoucí chování nelze zaručit.</p></footer>'''
    return f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · kydy.cz</title><meta name="description" content="{escape(description)}"><meta name="theme-color" content="#f7f5ef"><link rel="canonical" href="https://kydy.cz/{escape(path)}"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:type" content="website"><meta property="og:locale" content="cs_CZ"><link rel="stylesheet" href="/assets/kydy.css"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"></head><body><a class="skip" href="#obsah">Přejít na obsah</a><header class="masthead"><a class="wordmark" href="/" aria-label="Kydy.cz – všechny kampaně">kydy<span>.cz</span></a><span class="edition">BRNO <span aria-hidden="true">/</span> VOLBY 2026</span></header><main id="obsah">{body}</main>{footer}</body></html>'''


def build():
    d = json.loads((ROOT / 'research/assessment.json').read_text())
    assert d['schema_version'] == 3 and d['methodology_version'] == 3
    d['evidence_categories'] = STATUSES
    campaigns = d['campaigns']
    assert len(campaigns) == 16 and sorted(p['number'] for p in campaigns) == list(range(1, 17))
    (SITE / 'assets').mkdir(exist_ok=True)
    for f in (ROOT / 'assets').iterdir():
        if f.is_file(): shutil.copyfile(f, SITE / 'assets' / f.name)
    # Původní rozcestník zůstává na stejné úrovni, proto nepotřebuje přepis relativních cest.
    index = SITE / 'index.html'
    if index.exists() and 'data-kydy-home' not in index.read_text():
        shutil.copyfile(index, SITE / 'archiv.html')

    def refs(items):
        if not items: return ''
        links = []
        for r in items:
            s = d['sources'][r['source']]
            url = s['url']
            match = re.search(r'PDF s\. (\d+)', r['locator'])
            if match: url += '#page=' + match[1]
            local = f'/dukazy/{r["source"]}.html'
            if match: local += '#page-' + match[1]
            links.append(f'<li><a href="{escape(url)}">{escape(r["locator"])}</a> <a class="copy-link" href="{local}">uložený podklad ↗</a></li>')
        return '<ul class="source-links">' + ''.join(links) + '</ul>'

    def experience(p, short=False):
        e = p['experience']
        if e['status'] == 'new':
            return '<span class="new-tag" title="Bez doloženého celoměstského mandátu; nejde o hodnocení jiné praxe">NOVÝ<span aria-hidden="true">*</span></span>'
        if short: return ''
        return f'<span class="experience-tag">{escape(e["label"])}</span>'

    cards = []
    for p in campaigns:
        for c in p['claims']:
            validate_accountability(c)
        p['evidence_counts'] = composition([c['evidence_status'] for c in p['claims']])
        p['path'] = f'kampan/{slug(p)}/index.html'
        promises = ''.join(f'<li><span class="status-dot {STATUSES[c["evidence_status"]]["css"]}" aria-hidden="true"></span><span>{escape(c["title"])}<small>{STATUSES[c["evidence_status"]]["label"]}</small>{scope_note(c)}</span></li>' for c in p['claims'])
        cards.append(f'''<a class="campaign-card" href="/{p['path']}" aria-labelledby="nazev-{p['number']}"><div class="card-top"><span class="list-number">{p['number']:02d}</span><span class="mini">KANDIDÁTKA</span><span class="arrow" aria-hidden="true">↗</span></div><h2 id="nazev-{p['number']}">{escape(p['name'])}</h2><p class="leader">{escape(p['leader'])} {experience(p, True)}</p><p class="team-note">{p['current_members']} současných zastupitelů na listině</p><p class="power-note">{escape(p['governance']['label'])}</p><ul class="promise-list">{promises}</ul><div class="card-conclusion">{composition_html(p['evidence_counts'])}<p>{escape(p['summary'])}</p><span class="read-more">Proč si to myslíme <span aria-hidden="true">→</span></span></div></a>''')
    home = f'''<section class="hero" data-kydy-home><div><p class="eyebrow">SLIBY A JEJICH OPORA</p><h1>Slibují to.<br><em>Udělají to?</em></h1></div><div class="hero-copy"><p>Co chtějí změnit.<br>Co už pro to udělali.<br>A co jim stojí v cestě.</p><p class="muted">{len(campaigns)} kampaní. {sum(len(p['claims']) for p in campaigns)} vybraných slibů.<br>Co udělali. Co mohli udělat. Co jen slibují.</p></div></section><section class="reading-key" aria-label="Jak číst oporu slibů">{''.join(badge(k) for k in STATUSES)}</section><p class="method-note"><strong>Barva ukazuje oporu slibu, ne jistotu splnění.</strong> Zohledňujeme i to, kdo měl moc jednat a nevyužil ji. Každý závěr má uvedený rozsah a důkazy. <a href="/metodika.html">Jak hodnotíme →</a></p><div class="section-top"><h2>Co slibují Brnu</h2><span class="muted">Ověřováno k {date(d['updated'])} · pořadí volebních čísel</span></div><p class="novice-key">{experience({'experience':{'status':'new'}})} u lídra = bez doloženého mandátu v zastupitelstvu města. Může mít jinou praxi i zkušený tým. <a href="/metodika.html#novi">Co přesně štítek znamená</a>.</p><div class="campaign-grid">{''.join(cards)}</div><p class="archive-invitation">Chcete prozkoumat i celé hlasovací období? <a href="/mapa-webu.html">Původní analýzy a data jsou v archivu →</a></p>'''
    index.write_text(page('Slibují to. Udělají to?', home, '', '16 brněnských kampaní. Co slibují, co už udělali a co jim stojí v cestě. S důkazy, které si můžete ověřit.'))

    for p in campaigns:
        nav = ''.join(f'<a href="#{c["id"]}"><span class="status-dot {STATUSES[c["evidence_status"]]["css"]}" aria-hidden="true"></span>{escape(c["title"])}<span class="sr-only"> — {STATUSES[c["evidence_status"]]["label"]}</span></a>' for c in p['claims'])
        blocks = []
        for c in p['claims']:
            accountability_html = ''
            if a := c.get('accountability'):
                actor_list = ''.join(f'<li><a href="/profily/{escape(person["person"])}.html">{escape(person["name"])}</a> — {escape(person["role"])}. {escape(person["action"])}.</li>' for person in a['actors'])
                accountability_html = f'''<section class="accountability" aria-labelledby="odpovednost-{c['id']}"><p class="eyebrow">ODPOVĚDNOST ZA VLASTNÍ ROZHODNUTÍ</p><h3 id="odpovednost-{c['id']}">Co mohli udělat a neudělali</h3><p><strong>Rozsah výtky:</strong> {escape(a['scope'])}</p><p><strong>Kdy:</strong> {escape(a['period'])}</p><h4>Kdo měl pravomoc</h4><ul>{actor_list}</ul><p>{escape(a['authority'])}</p><h4>Jakou měli skutečnou příležitost</h4><p>{escape(a['opportunity'])}</p><h4>Co se prokazatelně stalo</h4><p>{escape(a['outcome'])}</p><h4>Protidůkazy a meze výtky</h4><p>{escape(a['limitations'])}</p>{refs(a['references'])}</section>'''
            vote_html = []
            for v in c['votes']:
                cnt = Counter(person['vote'] for person in v['people'])
                count_text = ', '.join(f'{n} {state.lower()}' for state,n in cnt.items()) or 'bez osobních hlasů této listiny'
                people_rows = ''.join(f'<tr><th scope="row"><a href="/profily/{person["person"]}.html">{escape(person["name"])}</a></th><td>{escape(person["vote"])}</td></tr>' for person in v['people'])
                table = '<div class="table-wrap"><table><caption>Dnešní kandidáti této listiny a jejich tehdejší osobní hlasy</caption><thead><tr><th scope="col">Kandidát/ka 2026</th><th scope="col">Tehdejší hlas</th></tr></thead><tbody>'+people_rows+'</tbody></table></div>' if people_rows else '<p>Jde o kontext rozhodování města. Žádný doložený osobní hlas nynější kandidátky v tomto protokolu.</p>'
                vote_html.append(f'<details class="vote"><summary><span class="vote-date">{date(v["date"])}</span><strong>{escape(v["meaning"])}</strong><span class="vote-counts">{escape(count_text)}</span></summary><p>{escape(v["title"])} · {escape(v["id"])}</p><p><strong>Výsledek celého zastupitelstva:</strong> {escape(v["result"])}; {v["all_yes"]} ano, {v["all_no"]} ne.</p><p class="interpretation">{escape(v["limit"])}</p>{table}{refs(v["references"])}</details>')
            blocks.append(f'''<article class="claim" id="{c['id']}"><header class="claim-heading"><span class="eyebrow">SLIB {len(blocks)+1:02d}</span><h2>{escape(c['title'])}</h2><p class="exact-promise">{escape(c['promise'])}</p><p class="fine">Parafráze programu, nikoli doslovná citace.</p>{refs([c['source']])}</header><div class="claim-verdict">{badge(c['evidence_status'])}<p>{escape(c['reason'])}</p></div>{accountability_html}<div class="evidence-grid"><section><h3>Jaké kroky jsou doložené</h3><p class="signal">{escape(c['signal'])}</p><p>{escape(c['history'])}</p>{''.join(vote_html)}{refs(c['references'])}</section><section><h3>Co mohou rozhodnout</h3><p>{escape(c['authority'])}</p>{refs(c['authority_references'])}<h3>Co musí vyjít</h3><p>{escape(c['practical'])}</p><p><a href="#politicka-podpora">Volební a koaliční podmínky této kampaně ↓</a></p></section></div><div class="limits-grid"><section><h3>Co závěr oslabuje</h3><p>{escape(c['counterevidence'])}</p></section><section><h3>Co by hodnocení změnilo</h3><p>{escape(c['change'])}</p></section></div><p class="fine">Posouzení k {date(c['updated'])} · <a href="#{c['id']}">Odkaz na tento slib</a></p></article>''')
        body = f'''<a class="back" href="/">← Všech 16 kampaní</a><section class="campaign-hero"><p class="eyebrow">KANDIDÁTKA {p['number']:02d}</p><h1>{escape(p['name'])}</h1><p class="detail-leader">{escape(p['leader'])} {experience(p)}</p><p class="muted">{escape(p['full_name'])} · {p['candidates']} kandidátů · {p['current_members']} současných zastupitelů</p><div class="overall">{composition_html(p['evidence_counts'])}<p>{escape(p['summary'])}</p></div><p class="fine">Skladba {len(p['claims'])} vybraných slibů, nikoli celková známka kandidátky. <a href="/metodika.html">Barva vyjadřuje oporu v důkazech, ne záruku splnění.</a></p></section><details class="governance" id="vykonna-odpovednost"><summary>Měli moc to udělat? <span>{escape(p['governance']['label'])}</span></summary><p><strong>{escape(p['governance']['label'])}</strong></p><p>{escape(p['governance']['summary'])}</p>{refs(p['governance']['references'])}<p>Výkonná funkce je výchozí bod kontroly, nikoli automatický důkaz selhání. U konkrétní výtky výše uvádíme období, vlastní rozhodnutí a výsledek. Pokud takový blok chybí, neznamená to, že jsme prokázali bezchybný výkon; tento rozbor nemá uzavřený audit všech neuskutečněných opatření.</p></details><nav class="promise-nav" aria-label="Sliby kampaně">{nav}</nav>{''.join(blocks)}<section class="context" id="politicka-podpora"><p class="eyebrow">PODMÍNKY PRO CELOU KAMPAŇ</p><h2>Získají podporu?</h2><p>{escape(p['political'])}</p>{refs(p['political_references'])}<p>{escape(d['polling'])}</p><p>K prosazení opatření obvykle potřebují mandáty a politickou podporu. Tuto podmínku posuzujeme zvlášť: nejistý výsledek voleb nemaže doloženou práci. Vlastní hlas může zastupitel ovlivnit i v opozici. Shoda programů není dohoda o koalici; dnešní počet zastupitelů není volební model.</p><h3>Praxe lídra a týmu</h3><p>{escape(p['experience']['note'])}</p>{refs(p['experience']['references'])}<p>Na dnešní listině je {p['past_members']} lidí s mandátem v období 2022–2026. Jejich hlasy nevydáváme za osobní výsledky ostatních kandidátů.</p><h3>Proč právě tyto sliby</h3><p>{escape(p['selection'])}</p>{refs(p['program_references'])}<h3>Meze podkladů</h3><p>{escape(d['coverage_note'])}</p><p>Výběr hlavních slibů je redakční, nikoli úplný audit programu nebo měření četnosti reklamy. U „není doloženo“ označujeme mezeru v této rešerši, ne důkaz, že podklad neexistuje.</p><h3>Historie hodnocení</h3><p>{date(d['updated'])}: metodika 3 — přidána kontrola skutečné výkonné odpovědnosti a kategorie „Neudělali to, když mohli“; dva případy podloženy i hlasováním rady a dokladem uskutečněného prodeje. <a href="https://github.com/mrmartin/kydy/commits/main/research/curation.py">Podrobná historie změn</a>.</p></section><a class="back" href="/">← Zpět ke všem kampaním</a>'''
        target = SITE / p['path']; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(p['name']+' – sliby a skutečné kroky', body, p['path'], p['summary']))

    # Neměnná textová kopie s čísly řádků, hash originálu a přímý odkaz na vydavatele.
    (SITE / 'dukazy').mkdir(exist_ok=True)
    for sid, s in d['sources'].items():
        source_file = SITE / s['text'] if s['text'] else None
        text = source_file.read_text() if source_file and source_file.exists() else 'Textová extrakce není k dispozici; použijte originál u vydavatele.'
        if s['text_sha256']:
            assert hashlib.sha256(source_file.read_bytes()).hexdigest() == s['text_sha256'], sid
        # Žádné převzaté HTML, skripty ani neescapovaný obsah zdroje.
        chunks=[]; line_number=0
        for page_number, chunk in enumerate(text.split('\f'),1):
            chunks.append(f'<span class="page-marker" id="page-{page_number}">'+(f'PDF · strana {page_number}' if '\f' in text else 'Textová kopie')+'</span>\n')
            for line in chunk.splitlines():
                line_number+=1
                chunks.append(f'<span class="source-line" id="L{line_number}"><a href="#L{line_number}" aria-label="Řádek {line_number}">{line_number}</a>{escape(line)}</span>\n')
        lines=''.join(chunks)
        body = f'<a class="back" href="/">← Kampaně</a><section class="source-document"><p class="eyebrow">ULOŽENÝ PODKLAD</p><h1>{escape(s["nazev"] or sid)}</h1><p><a href="{escape(s["url"])}">Originál u vydavatele ↗</a></p><p>Staženo {escape(s["stazeno_utc"])}. Textová extrakce může mít chyby v tabulkách a pořadí sloupců; rozhodující je původní dokument.</p><details><summary>Identifikace a kontrolní součty</summary><p>ID {sid}</p><p>SHA-256 originálu: <code>{s["sha256"]}</code></p><p>SHA-256 textu: <code>{s["text_sha256"]}</code></p></details><pre class="source-text">{lines}</pre></section>'
        (SITE / 'dukazy' / f'{sid}.html').write_text(page('Podklad '+sid,body,f'dukazy/{sid}.html'))

    red_note = 'U současného výběru tato kategorie zatím nemá položku; nevytváříme ji kvůli barevnosti.' if not any(p['evidence_counts']['rozpor'] for p in campaigns) else 'Každý zásadní rozpor je popsán u konkrétního slibu, včetně protidůkazů.'
    methodology = f'''<a class="back" href="/">← Kampaně</a><article class="prose"><p class="eyebrow">METODIKA · VERZE 3</p><h1>Jednoduchá barva.<br>Dohledatelný důvod.</h1><p class="lead">Otázka zní: jakou oporu má tento slib? Ukazujeme doložené kroky, cestu k provedení a chybějící podmínky. Barva není předpověď voleb ani doporučení, s čím máte souhlasit.</p><h2>Pět různých stavů důkazů</h2><p>{badge('podlozeno')} Relevantní konkrétní jednání nebo realizace slibu už jsou doložené a existuje cesta k pokračování bez známé zásadní překážky. Může jít o osobní hlas, kontrolní návrh, podepsanou realizační smlouvu nebo probíhající stavbu. Vždy říkáme, čí krok to je a v jaké fázi; zelená neznamená hotovo, připsání celé zásluhy kampani ani záruku dalšího chování.</p><p>{badge('podminene')} Existuje konkrétní základ: příbuzná doložená praxe, probíhající příprava nebo použitelný nástroj. Pro slíbený rozsah zbývá podstatná pojmenovaná podmínka, například nové financování, souhlas jiného investora nebo konečná smlouva. Samotná zákonná pravomoc bez postupu k provedení nestačí.</p><p>{badge('nevyuzita_moznost')} Doložená nevyužitá příležitost při skutečném výkonu moci: konkrétní lidé měli příslušnou pravomoc, čas a proveditelnou možnost jednat, ale požadovaný krok neudělali nebo sami podpořili opačné rozhodnutí. Musí být doložen výsledek, nikoli pouze chybět zpráva o splnění. Rozsah výtky vždy pojmenujeme; u složeného slibu se nemusí týkat všech jeho částí.</p><p>{badge('rozpor')} Doložená zásadní překážka brání slíbenému výsledku nebo přímo protichůdné jednání přetrvává bez vysvětlené změny. Chybějící podklad, starý odlišný hlas nebo nutnost dohodnout se se státem samy nestačí. {red_note}</p><p>{badge('bez_opory')} V této rešerši chybí dostatečná relevantní praxe nebo konkrétní cesta k provedení; případně je slib příliš neurčitý. I přesné číslo může zůstat jen slibem, pokud nemá plán. Není to důkaz nečinnosti, nemožnosti ani lži.</p><h2>Kdy lze říct „Neudělali to, když mohli“</h2><p>Dokládáme konkrétní osoby a jejich vazbu na dnešní kandidátku, tehdejší funkci a pravomoc, rozhodovací příležitost či uplynulou lhůtu, dostupný proveditelný krok, výsledek a protidůkazy. U nákladné služby nestačí kompetence: potřebujeme i reálné zdroje a čas. U vlastního hlasu posuzujeme rozhodnutí, které člověk skutečně ovládal; nepředstíráme, že měl sám většinu nebo veto.</p><p>Rozlišujeme nesplněný tehdejší závazek a nevyužitou dřívější možnost postupovat podle dnešního programu. Dvě nynější položky se týkají druhého případu: souhlasu s prodejem Dornychu, nikoli prokázaného porušení totožného slibu z roku 2022. Jde o jeden společný případ u dvou kandidátek, ne o dvě nezávislá selhání. Zaznamenáváme i ekonomické důvody prodeje a pozdější omezení privatizace; oprávněnost dnešní změny politiky tím nevylučujeme.</p><p>Nezaměňujeme výkon městské vlády za opoziční mandát, kontrolní výbor, radu městské části či vedení odborné instituce. U původního ANO sledujeme přesun lidí do Brnoklidem; u nových lídrů nezmizí institucionální odpovědnost jejich stran, ale cizí hlas se nestane jejich osobním hlasem. Starší role mají vlastní období. Samotná opakovaná kandidatura nic z toho nedokazuje.</p><h2>Jak vybíráme kategorii</h2><p>Nejdřív hledáme přímé důkazy a protidůkazy. Doložená nevyužitá možnost při výkonu moci má vlastní kategorii a přednost před dílčím pozitivním krokem; ostatní zásadní nevyřešené rozpory řadíme do kategorie rozporu. Bez něj posoudíme, zda činy přímo podpírají vybraný závazek, zda máme jen základ s konkrétní otevřenou podmínkou, nebo zda taková opora chybí. Neurčujeme cílový počet zelených či červených položek.</p><p>Související části slibu zůstávají jedním balíkem: hotová příprava arény například sama nezazelení i nevyřešený stadion. Podstatnou mezeru v balíku uvedeme v důvodu. Doklad práce městské společnosti může podpořit proveditelnost pokračování projektu, ale nedokazuje osobní zásluhu kandidátů. Pro osobní jednání naopak stačí odpovídající osobní důkaz; prosazení vlastního hlasu nevyžaduje většinu.</p><h2>Skladba místo jedné známky</h2><p>U kampaně zobrazujeme počty slibů v jednotlivých kategoriích a jednu shrnující větu. Žádné průměrování ani většinový verdikt: zásadní rozpor by nezmizel mezi několika snadnými sliby. Délka barevných dílků odpovídá počtu vybraných slibů, ne jejich ceně, důležitosti nebo podílu celého programu. Čísla nejsou žebříčkem kampaní; různě velké výběry nejsou přímo srovnatelným skóre.</p><h2>Co se změnilo oproti prvnímu vydání</h2><p>Původní ANO/MOŽNÁ/NE odhadovalo budoucí splnění včetně volebních šancí. Všech 57 slibů proto zůstalo MOŽNÁ. Verze 2 ze dne 20. 9. 2026 odpovídá na užší otázku o opoře slibu ve stejných archivovaných důkazech. Každý slib byl znovu jednotlivě posouzen; nejde o automatické přebarvení ani o nově zjištěné výsledky politiků. Původní znění zůstává v historii Gitu.</p><p>Verze 3 doplňuje vládní odpovědnost, pátou kategorii a podrobný řetězec důkazů u dvou slibů. Přehled rolí pokrývá všech 16 listin, cílená kontrola konkrétní nevyužité příležitosti zatím neznamená úplný audit všech minulých selhání.</p><h2>Co porovnáváme</h2><p>Všech 16 celoměstských kandidátek, obvykle 3–5 závazků na listinu. Jsou vybrané podle výslovných priorit a tematických kapitol aktuální kampaně. Nevybíráme jen sliby s dostupným hlasováním. Pokud nemáme tři odlišné konkrétní závazky, počet nenavyšujeme. Související části jednoho balíku tvoří jeden hodnocený slib; jejich rozdíly vysvětlujeme v detailu. Nejde o úplný audit programu ani placené reklamy.</p><h2 id="novi">Co znamená NOVÝ</h2><p>Štítek se týká <strong>lídra a celoměstského zastupitelstva</strong>, nikoli stáří strany nebo všech lidí na listině. Znamená, že nemáme doložen jeho celoměstský mandát: nebyl mezi držiteli mandátu 2022–2026 a při cílené starší rešerši jsme dřívější mandát nenalezli. Starší historie není plošně kompletní; jde o stav důkazů, ne jistotu o celé kariéře.</p><p>Nový lídr může mít zkušený tým, mandát v městské části, krajskou či parlamentní praxi nebo výsledky při vedení instituce. Nedoložená minulost omezuje hodnocení dosavadní práce; sama neprokazuje menší schopnost ani automaticky neurčuje kategorii. Doložený projekt může existovat i při novém lídrovi. Říhu, Kratochvíla, Vokřála a Liptákovou evidujeme jako dřívější držitele městské funkce.</p><h2>Hlas není hotový výsledek</h2><p>Rozlišujeme návrh, přijaté usnesení, financování, podepsanou smlouvu, stavbu a provoz. U hlasu uvádíme přesný význam, datum, jednotlivé lidi a mez výkladu. Rozlišujeme nesouhlas, zdržení, nehlasování, nepřítomnost a neexistující mandát. Tajný hlas se nedomýšlí. Přípravný nebo souhrnný rozpočtový hlas neprokazuje každou dílčí politiku.</p><p>Hlasování přiřazujeme lidem na dnešních listinách, i když tehdy působili pod jinou značkou. Výsledek celého města nepřičítáme jedinému politikovi bez doložené odpovědnosti. Nový budoucí závazek může znamenat legitimní změnu politiky.</p><h2>Pravomoci, peníze a termíny</h2><p>Rozlišujeme město, městské části, kraj, stát a městské společnosti. Slovo „prosadíme“ nepřepisujeme na „sami rozhodneme“. Opravený byt není novostavba; připravený projekt není hotová stavba; tempo na konci období není stejný výkon každý rok. U peněz odlišujeme rozpočet od skutečnosti, provoz od investic a prostředky firmy od volných peněz města. Chybějící výpočet znamená nejistotu, ne automaticky nemožnost.</p><h2>Volební a koaliční šance</h2><p>{escape(d['polling'])}</p><p>Uvádíme datované výroky o spolupráci včetně odmítnutí druhé strany. Programový průnik není koalice. Dosavadní počet mandátů není předpověď. Volební a koaliční podmínky uvádíme samostatně v detailu každé kampaně. Obecná nejistota příští většiny nemění hodnocení již doložené práce; konkrétní nezajištěná dohoda nutná pro realizaci se projeví u daného slibu.</p><h2>Rozpor není automaticky lež</h2><p>Odlišujeme nepravdivý ověřitelný údaj, rozpor se starším jednáním, nedoloženou předpověď a vědomé klamání. Úmysl bez důkazu nikomu nepřipisujeme. Každý rozbor obsahuje také protidůkazy a popis toho, co by hodnocení změnilo.</p><h2>Pokrytí a kontrola</h2><p>{escape(d['coverage_note'])}</p><p>Programové snímky převážně z 19. 9. 2026, doplňující rešerše do 20. 9. 2026. U každého dokumentu uvádíme skutečný čas získání, původní URL, lokátor a SHA-256. Kopie textu zachovává obsah získaného podkladu; extrakce PDF může poškodit tabulky.</p><p>Texty byly připraveny s pomocí AI a zdrojově kontrolovány při zpracování. Neprošly nezávislou externí recenzí. První vydání obsahuje otevřené otázky, nikoli definitivní audit všech investic. Opravu lze navrhnout přes GitHub s odkazem na důkaz.</p><h2>Data a historie</h2><p><a href="/data/hodnoceni-kampani.json">Úplný podklad JSON</a> · <a href="/data/hodnoceni-slibu.csv">Sliby CSV</a> · <a href="/data/zdroje-hodnoceni.csv">Použité prameny CSV</a> · <a href="https://github.com/mrmartin/kydy/commits/main/research/curation.py">Historie změn</a>.</p><p>Podklad ke každému slibu obsahuje formulaci, programový zdroj, osobní hlasy, pravomoc, proveditelnost, nejistoty, protidůkazy a datum. Neprobíhá automatické známkování návštěvníků ani doporučování podle jejich osobních údajů.</p></article>'''
    (SITE / 'metodika.html').write_text(page('Jak hodnotíme', methodology, 'metodika.html'))
    # Úplná lidská mapa starých i nových HTML stránek, ne jen XML pro roboty.
    groups = [('Srovnání kampaní', [SITE/'index.html', SITE/'metodika.html']+[SITE/p['path'] for p in campaigns]), ('Původní přehledy', [SITE/'archiv.html', *sorted((SITE/'analyzy').glob('*.html')), *sorted((SITE/'kampane-2026').glob('*.html'))]), ('Profily všech zastupitelů', sorted((SITE/'profily').glob('*.html'))), ('Datové slovníky a archiv', [SITE/'zdroje.html', SITE/'ke-stazeni.html', *sorted((SITE/'data').glob('*.html'))]), ('Podklady k novému hodnocení', sorted((SITE/'dukazy').glob('*.html')))]
    included = {f.resolve() for _, fs in groups for f in fs}
    groups.append(('Další stránky archivu', [f for f in sorted(SITE.rglob('*.html')) if f.resolve() not in included and f.name != 'mapa-webu.html']))
    sections=[]
    for name, files in groups:
        if not files: continue
        links=[]
        for f in files:
            if not f.exists(): continue
            title=re.search(r'<title>(.*?)</title>',f.read_text(),re.S)
            label=html.unescape(title[1]).removesuffix(' · kydy.cz') if title else f.stem
            links.append(f'<li><a href="/{escape(f.relative_to(SITE).as_posix())}">{escape(label)}</a></li>')
        sections.append(f'<details open><summary>{escape(name)} <span class="muted">({len(links)})</span></summary><ul class="sitemap-list">'+''.join(links)+'</ul></details>')
    (SITE/'mapa-webu.html').write_text(page('Mapa webu a archiv','<article class="prose"><h1>Všechno zůstává dohledatelné.</h1><p>Nové srovnání i všechny původní analýzy, profily a datové stránky.</p>'+''.join(sections)+'</article>','mapa-webu.html'))
    (SITE/'data/hodnoceni-kampani.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    with (SITE/'data/hodnoceni-slibu.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['id','cislo_listiny','kampan','slib','opora_kod','opora_popis','duvod','dosavadni_jednani','pravomoc','proveditelnost','politicke_podminky','protidukazy','vykonna_role','vykonna_odpovednost','nevyuzita_moznost_json','co_by_zmenilo_zaver','zdroj_url','lokator','dalsi_zdroje','hlasovani','overeno'])
        for p in campaigns:
            for c in p['claims']:
                w.writerow([c['id'],p['number'],p['name'],c['promise'],c['evidence_status'],STATUSES[c['evidence_status']]['label'],c['reason'],c['history'],c['authority'],c['practical'],p['political'],c['counterevidence'],p['governance']['label'],p['governance']['summary'],json.dumps(c['accountability'],ensure_ascii=False) if c.get('accountability') else '',c['change'],d['sources'][c['source']['source']]['url'],c['source']['locator'],';'.join(r['source'] for r in c['references']+c['authority_references']+p['governance']['references']+(c['accountability']['references'] if c.get('accountability') else [])),';'.join(v['id'] for v in c['votes']),c['updated']])
    with (SITE/'data/zdroje-hodnoceni.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(next(iter(d['sources'].values())).keys()),lineterminator='\n');w.writeheader();w.writerows(d['sources'].values())
    paths=sorted(p.relative_to(SITE).as_posix() for p in SITE.rglob('*.html') if 'dukazy/' not in p.relative_to(SITE).as_posix())
    (SITE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://kydy.cz/'+escape(quote(path))+'</loc></url>' for path in paths)+'</urlset>')
    print(f"Sestaveno: {len(campaigns)} kampaní, {sum(len(p['claims']) for p in campaigns)} slibů, {len(d['sources'])} ověřitelných pramenů; archiv zachován.")


if __name__ == '__main__':
    build()
