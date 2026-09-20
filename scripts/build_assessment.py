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
LABELS = {'ANO': 'yes', 'MOŽNÁ': 'maybe', 'NE': 'no'}


def escape(value):
    return html.escape(str(value), quote=True)


def aggregate(verdicts):
    if not verdicts or any(v not in LABELS for v in verdicts):
        raise ValueError('Chybí platná posouzení slibů')
    for v in ['ANO', 'NE']:
        if verdicts.count(v) > len(verdicts) / 2:
            return v
    return 'MOŽNÁ'


def slug(party):
    name = unicodedata.normalize('NFKD', party['name']).encode('ascii', 'ignore').decode().lower()
    return f"{party['number']:02d}-" + re.sub(r'[^a-z0-9]+', '-', name).strip('-')


def badge(verdict):
    return f'<span class="verdict {LABELS[verdict]}"><span aria-hidden="true" class="dot"></span>{verdict}</span>'


def date(value):
    year, month, day = value[:10].split('-')
    return f'{int(day)}. {int(month)}. {year}'


def page(title, body, path, description='Sliby brněnských kampaní, osobní hlasy a ověřitelné důvody hodnocení.'):
    footer = '''<footer class="footer"><a class="wordmark" href="/">kydy<span>.cz</span></a><p>Podklady pro vlastní rozhodnutí.</p><nav aria-label="Patička"><a href="/metodika.html">Jak hodnotíme</a><a href="/mapa-webu.html">Mapa webu a celý archiv</a><a href="/data/hodnoceni-kampani.json">Data JSON</a><a href="/data/hodnoceni-slibu.csv">Data CSV</a><a href="https://github.com/mrmartin/kydy/issues">Nahlásit chybu se zdrojem</a></nav><p class="fine">Veřejné podklady zpracované s pomocí AI. Posouzení neprošlo nezávislou externí recenzí. Budoucí chování nelze zaručit.</p></footer>'''
    return f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · kydy.cz</title><meta name="description" content="{escape(description)}"><meta name="theme-color" content="#f7f5ef"><link rel="canonical" href="https://kydy.cz/{escape(path)}"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:type" content="website"><meta property="og:locale" content="cs_CZ"><link rel="stylesheet" href="/assets/kydy.css"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"></head><body><a class="skip" href="#obsah">Přejít na obsah</a><header class="masthead"><a class="wordmark" href="/" aria-label="Kydy.cz – všechny kampaně">kydy<span>.cz</span></a><span class="edition">BRNO <span aria-hidden="true">/</span> VOLBY 2026</span></header><main id="obsah">{body}</main>{footer}</body></html>'''


def build():
    d = json.loads((ROOT / 'research/assessment.json').read_text())
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
        p['verdict'] = aggregate([c['verdict'] for c in p['claims']])
        p['path'] = f'kampan/{slug(p)}/index.html'
        promises = ''.join(f'<li>{escape(c["title"])}</li>' for c in p['claims'])
        cards.append(f'''<a class="campaign-card" href="/{p['path']}" aria-labelledby="nazev-{p['number']}"><div class="card-top"><span class="list-number">{p['number']:02d}</span><span class="mini">KANDIDÁTKA</span><span class="arrow" aria-hidden="true">↗</span></div><h2 id="nazev-{p['number']}">{escape(p['name'])}</h2><p class="leader">{escape(p['leader'])} {experience(p, True)}</p><p class="team-note">{p['current_members']} současných zastupitelů na listině</p><ul class="promise-list">{promises}</ul><div class="card-conclusion">{badge(p['verdict'])}<p>{escape(p['summary'])}</p><span class="read-more">Proč si to myslíme <span aria-hidden="true">→</span></span></div></a>''')
    same = len({p['verdict'] for p in campaigns}) == 1
    honesty = '<p class="same-verdict">Proč zatím všude MOŽNÁ? U žádné kampaně nemáme uzavřené podklady pro většinu slibů. Rozdíly jsou v doložených krocích, rozporech a podmínkách — najdete je v rozborech.</p>' if same and campaigns[0]['verdict']=='MOŽNÁ' else ''
    home = f'''<section class="hero" data-kydy-home><div><p class="eyebrow">SLIBY POD DROBNOHLEDEM</p><h1>Slibují to.<br><em>Udělají to?</em></h1></div><div class="hero-copy"><p>Co chtějí změnit.<br>Co už pro to udělali.<br>A co jim stojí v cestě.</p><p class="muted">{len(campaigns)} kampaní. {sum(len(p['claims']) for p in campaigns)} vybraných slibů.<br>Ke každému závěru dohledatelný důvod.</p></div></section><section class="reading-key" aria-label="Jak číst hodnocení"><span>{badge('ANO')} podklady podporují splnění</span><span>{badge('MOŽNÁ')} záleží na podmínkách</span><span>{badge('NE')} zásadní překážka či rozpor</span></section>{honesty}<div class="section-top"><h2>Co slibují Brnu</h2><span class="muted">Ověřováno k {date(d['updated'])} · pořadí volebních čísel</span></div><p class="novice-key">{experience({'experience':{'status':'new'}})} u lídra = bez doloženého mandátu v zastupitelstvu města. Může mít jinou praxi i zkušený tým. <a href="/metodika.html#novi">Co přesně štítek znamená</a>.</p><div class="campaign-grid">{''.join(cards)}</div><p class="archive-invitation">Chcete prozkoumat i celé hlasovací období? <a href="/mapa-webu.html">Původní analýzy a data jsou v archivu →</a></p>'''
    index.write_text(page('Slibují to. Udělají to?', home, '', '16 brněnských kampaní. Co slibují, co už udělali a co jim stojí v cestě. S důkazy, které si můžete ověřit.'))

    for p in campaigns:
        counts = Counter(c['verdict'] for c in p['claims'])
        nav = ''.join(f'<a href="#{c["id"]}">{escape(c["title"])}</a>' for c in p['claims'])
        blocks = []
        for c in p['claims']:
            vote_html = []
            for v in c['votes']:
                cnt = Counter(person['vote'] for person in v['people'])
                count_text = ', '.join(f'{n} {state.lower()}' for state,n in cnt.items()) or 'bez osobních hlasů této listiny'
                people_rows = ''.join(f'<tr><th scope="row"><a href="/profily/{person["person"]}.html">{escape(person["name"])}</a></th><td>{escape(person["vote"])}</td></tr>' for person in v['people'])
                table = '<div class="table-wrap"><table><caption>Dnešní kandidáti této listiny a jejich tehdejší osobní hlasy</caption><thead><tr><th scope="col">Kandidát/ka 2026</th><th scope="col">Tehdejší hlas</th></tr></thead><tbody>'+people_rows+'</tbody></table></div>' if people_rows else '<p>Jde o kontext rozhodování města. Žádný doložený osobní hlas nynější kandidátky v tomto protokolu.</p>'
                vote_html.append(f'<details class="vote"><summary><span class="vote-date">{date(v["date"])}</span><strong>{escape(v["meaning"])}</strong><span class="vote-counts">{escape(count_text)}</span></summary><p>{escape(v["title"])} · {escape(v["id"])}</p><p><strong>Výsledek celého zastupitelstva:</strong> {escape(v["result"])}; {v["all_yes"]} ano, {v["all_no"]} ne.</p><p class="interpretation">{escape(v["limit"])}</p>{table}{refs(v["references"])}</details>')
            blocks.append(f'''<article class="claim" id="{c['id']}"><header class="claim-heading"><span class="eyebrow">SLIB {len(blocks)+1:02d}</span><h2>{escape(c['title'])}</h2><p class="exact-promise">{escape(c['promise'])}</p><p class="fine">Parafráze programu, nikoli doslovná citace.</p>{refs([c['source']])}</header><div class="claim-verdict">{badge(c['verdict'])}<p>{escape(c['reason'])}</p></div><div class="evidence-grid"><section><h3>Co už udělali</h3><p class="signal">{escape(c['signal'])}</p><p>{escape(c['history'])}</p>{''.join(vote_html)}{refs(c['references'])}</section><section><h3>Co mohou rozhodnout</h3><p>{escape(c['authority'])}</p>{refs(c['authority_references'])}<h3>Co musí vyjít</h3><p>{escape(c['practical'])}</p><p><a href="#politicka-podpora">Volební a koaliční podmínky této kampaně ↓</a></p></section></div><div class="limits-grid"><section><h3>Co závěr oslabuje</h3><p>{escape(c['counterevidence'])}</p></section><section><h3>Co by hodnocení změnilo</h3><p>{escape(c['change'])}</p></section></div><p class="fine">Posouzení k {date(c['updated'])} · <a href="#{c['id']}">Odkaz na tento slib</a></p></article>''')
        body = f'''<a class="back" href="/">← Všech 16 kampaní</a><section class="campaign-hero"><p class="eyebrow">KANDIDÁTKA {p['number']:02d}</p><h1>{escape(p['name'])}</h1><p class="detail-leader">{escape(p['leader'])} {experience(p)}</p><p class="muted">{escape(p['full_name'])} · {p['candidates']} kandidátů · {p['current_members']} současných zastupitelů</p><div class="overall">{badge(p['verdict'])}<p>{escape(p['summary'])}</p></div><p class="fine">Souhrn {len(p['claims'])} slibů: {counts['ANO']} ANO · {counts['MOŽNÁ']} MOŽNÁ · {counts['NE']} NE. Barvu určuje nadpoloviční většina; jinak MOŽNÁ.</p></section><nav class="promise-nav" aria-label="Sliby kampaně">{nav}</nav>{''.join(blocks)}<section class="context" id="politicka-podpora"><p class="eyebrow">PODMÍNKY PRO CELOU KAMPAŇ</p><h2>Získají podporu?</h2><p>{escape(p['political'])}</p>{refs(p['political_references'])}<p>{escape(d['polling'])}</p><p>Bez dostatečné volební a politické opory zůstává prognóza nejistá, i když je samotné opatření v pravomoci města. Shoda programů není dohoda o koalici; dnešní počet zastupitelů není volební model.</p><h3>Praxe lídra a týmu</h3><p>{escape(p['experience']['note'])}</p>{refs(p['experience']['references'])}<p>Na dnešní listině je {p['past_members']} lidí s mandátem v období 2022–2026. Jejich hlasy nevydáváme za osobní výsledky ostatních kandidátů.</p><h3>Proč právě tyto sliby</h3><p>{escape(p['selection'])}</p>{refs(p['program_references'])}<h3>Meze podkladů</h3><p>{escape(d['coverage_note'])}</p><p>Výběr hlavních slibů je redakční, nikoli úplný audit programu nebo měření četnosti reklamy. U „není doloženo“ označujeme mezeru v této rešerši, ne důkaz, že podklad neexistuje.</p><h3>Historie hodnocení</h3><p>{date(d['updated'])}: první vydání. <a href="https://github.com/mrmartin/kydy/commits/main/research/curation.py">Podrobná historie změn</a>.</p></section><a class="back" href="/">← Zpět ke všem kampaním</a>'''
        target = SITE / p['path']; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(p['name']+' – sliby a skutečné kroky', body, p['path'], p['verdict']+' — '+p['summary']))

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

    methodology = f'''<a class="back" href="/">← Kampaně</a><article class="prose"><p class="eyebrow">METODIKA · VERZE 1</p><h1>Jednoduchá barva.<br>Dohledatelný důvod.</h1><p class="lead">Hodnotíme oporu slibů, jejich uskutečnitelnost a politické podmínky. Nehodnotíme, zda s nimi máte souhlasit.</p><h2>Jak číst ANO, MOŽNÁ a NE</h2><p><strong>ANO:</strong> Relevantní jednání a doložená cesta ke splnění slib podporují, bez zásadní nevyřešené překážky.</p><p><strong>MOŽNÁ:</strong> Smíšené důkazy, podstatné nevyřešené podmínky, chybějící historie nebo příliš neurčitý závazek.</p><p><strong>NE:</strong> Doložená zásadní překážka slíbenému výsledku nebo opakované přímo protichůdné jednání bez doložené změny přístupu. Jeden starý hlas sám nestačí.</p><p>Barva je redakční úsudek o budoucnosti, nikoli záruka ani procentní pravděpodobnost. V prvním vydání jsou všechna posouzení MOŽNÁ: máme konkrétní rozdíly v praxi, ale nikoli uzavřené důkazy pro budoucí splnění či nesplnění. Barvy nevyrábíme kvůli pestřejšímu přehledu.</p><h2>Jak vzniká barva kampaně</h2><p>Každý vybraný hlavní slib má stejnou váhu. Nadpoloviční většina ANO dává ANO, nadpoloviční většina NE dává NE. Ve všech ostatních případech vychází MOŽNÁ. Nevyhodnotitelné sliby se nevyhazují: jsou MOŽNÁ. Příklad: ANO, ANO, MOŽNÁ → ANO; ANO, NE, MOŽNÁ → MOŽNÁ. Zásadní výjimku je nutné uvést v souhrnné větě.</p><h2>Co porovnáváme</h2><p>Všech 16 celoměstských kandidátek, obvykle 3–5 závazků na listinu. Jsou vybrané podle výslovných priorit a tematických kapitol aktuální kampaně. Nevybíráme jen sliby s dostupným hlasováním. Pokud nemáme tři odlišné konkrétní závazky, počet nenavyšujeme. Související části jednoho balíku tvoří jeden hodnocený slib; jejich rozdíly vysvětlujeme v detailu. Nejde o úplný audit programu ani placené reklamy.</p><h2 id="novi">Co znamená NOVÝ</h2><p>Štítek se týká <strong>lídra a celoměstského zastupitelstva</strong>, nikoli stáří strany nebo všech lidí na listině. Znamená, že nemáme doložen jeho celoměstský mandát: nebyl mezi držiteli mandátu 2022–2026 a při cílené starší rešerši jsme dřívější mandát nenalezli. Starší historie není plošně kompletní; jde o stav důkazů, ne jistotu o celé kariéře.</p><p>Nový lídr může mít zkušený tým, mandát v městské části, krajskou či parlamentní praxi nebo výsledky při vedení instituce. Nedoložená minulost omezuje možnost dát ANO; sama neprokazuje menší schopnost ani není důvodem pro NE. Říhu, Kratochvíla, Vokřála a Liptákovou evidujeme jako dřívější držitele městské funkce.</p><h2>Hlas není hotový výsledek</h2><p>Rozlišujeme návrh, přijaté usnesení, financování, podepsanou smlouvu, stavbu a provoz. U hlasu uvádíme přesný význam, datum, jednotlivé lidi a mez výkladu. Rozlišujeme nesouhlas, zdržení, nehlasování, nepřítomnost a neexistující mandát. Tajný hlas se nedomýšlí. Přípravný nebo souhrnný rozpočtový hlas neprokazuje každou dílčí politiku.</p><p>Hlasování přiřazujeme lidem na dnešních listinách, i když tehdy působili pod jinou značkou. Výsledek celého města nepřičítáme jedinému politikovi bez doložené odpovědnosti. Nový budoucí závazek může znamenat legitimní změnu politiky.</p><h2>Pravomoci, peníze a termíny</h2><p>Rozlišujeme město, městské části, kraj, stát a městské společnosti. Slovo „prosadíme“ nepřepisujeme na „sami rozhodneme“. Opravený byt není novostavba; připravený projekt není hotová stavba; tempo na konci období není stejný výkon každý rok. U peněz odlišujeme rozpočet od skutečnosti, provoz od investic a prostředky firmy od volných peněz města. Chybějící výpočet znamená nejistotu, ne automaticky nemožnost.</p><h2>Volební a koaliční šance</h2><p>{escape(d['polling'])}</p><p>Uvádíme datované výroky o spolupráci včetně odmítnutí druhé strany. Programový průnik není koalice. Dosavadní počet mandátů není předpověď. Nejistota politické cesty se promítá do posouzení jednotlivých slibů.</p><h2>Rozpor není automaticky lež</h2><p>Odlišujeme nepravdivý ověřitelný údaj, rozpor se starším jednáním, nedoloženou předpověď a vědomé klamání. Úmysl bez důkazu nikomu nepřipisujeme. Každý rozbor obsahuje také protidůkazy a popis toho, co by hodnocení změnilo.</p><h2>Pokrytí a kontrola</h2><p>{escape(d['coverage_note'])}</p><p>Programové snímky převážně z 19. 9. 2026, doplňující rešerše do 20. 9. 2026. U každého dokumentu uvádíme skutečný čas získání, původní URL, lokátor a SHA-256. Kopie textu zachovává obsah získaného podkladu; extrakce PDF může poškodit tabulky.</p><p>Texty byly připraveny s pomocí AI a zdrojově kontrolovány při zpracování. Neprošly nezávislou externí recenzí. První vydání obsahuje otevřené otázky, nikoli definitivní audit všech investic. Opravu lze navrhnout přes GitHub s odkazem na důkaz.</p><h2>Data a historie</h2><p><a href="/data/hodnoceni-kampani.json">Úplný podklad JSON</a> · <a href="/data/hodnoceni-slibu.csv">Sliby CSV</a> · <a href="/data/zdroje-hodnoceni.csv">Použité prameny CSV</a> · <a href="https://github.com/mrmartin/kydy/commits/main/research/curation.py">Historie změn</a>.</p><p>Podklad ke každému slibu obsahuje formulaci, programový zdroj, osobní hlasy, pravomoc, proveditelnost, nejistoty, protidůkazy a datum. Neprobíhá automatické známkování návštěvníků ani doporučování podle jejich osobních údajů.</p></article>'''
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
        w=csv.writer(f);w.writerow(['id','cislo_listiny','kampan','slib','hodnoceni','duvod','dosavadni_jednani','pravomoc','proveditelnost','politicke_podminky','protidukazy','co_by_zmenilo_zaver','zdroj_url','lokator','dalsi_zdroje','hlasovani','overeno'])
        for p in campaigns:
            for c in p['claims']:
                w.writerow([c['id'],p['number'],p['name'],c['promise'],c['verdict'],c['reason'],c['history'],c['authority'],c['practical'],p['political'],c['counterevidence'],c['change'],d['sources'][c['source']['source']]['url'],c['source']['locator'],';'.join(r['source'] for r in c['references']+c['authority_references']),';'.join(v['id'] for v in c['votes']),c['updated']])
    with (SITE/'data/zdroje-hodnoceni.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(next(iter(d['sources'].values())).keys()));w.writeheader();w.writerows(d['sources'].values())
    paths=sorted(p.relative_to(SITE).as_posix() for p in SITE.rglob('*.html') if 'dukazy/' not in p.relative_to(SITE).as_posix())
    (SITE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://kydy.cz/'+escape(quote(path))+'</loc></url>' for path in paths)+'</urlset>')
    print(f"Sestaveno: {len(campaigns)} kampaní, {sum(len(p['claims']) for p in campaigns)} slibů, {len(d['sources'])} ověřitelných pramenů; archiv zachován.")


if __name__ == '__main__':
    build()
