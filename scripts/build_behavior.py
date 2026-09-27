#!/usr/bin/env python3
"""Statická prezentace doloženého rozhodování. Bez skóre charakteru nebo motivů."""
import hashlib
import html
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
STATES=['Ano','Ne','Zdržel se','Nehlasoval','Nepřítomen','Bez mandátu']
LABELS={'Ano':'pro','Ne':'proti','Zdržel se':'zdržení','Nehlasoval':'nehlasování','Nepřítomen':'nepřítomnost','Bez mandátu':'bez mandátu'}

def e(s):return html.escape(str(s),quote=True)
def day(s):
    y,m,d=s[:10].split('-');return f'{int(d)}. {int(m)}. {y}'

def validate(data):
    if data['schema_version']!=1:raise ValueError('Neznámé schéma rozhodování')
    if len(data['campaigns'])!=16:raise ValueError('Chybí kandidátka')
    seen=set()
    for c in data['cases']:
        required=['id','title','axis','stakes','beneficiaries','outcome','limitations','followup','opportunity','vote_ids','personal_benefit']
        if any(not c.get(k) for k in required):raise ValueError('Neúplný kontext případu')
        for vid in c['vote_ids']:
            if vid in seen:raise ValueError('Dvojí započtení hlasování')
            seen.add(vid)
            v=data['votes'][vid]
            if not v['references'] or len(v['people'])!=55:raise ValueError('Chybí důkazy či osobní hlasy')
            counts=Counter(p['vote'] for p in v['people'])
            if any(counts[k]!=v['counts'][k] for k in STATES[:5]):raise ValueError('Nesoulad osobních a celkových hlasů')
        if c['personal_benefit']['status']=='dolozena_funkce':
            pid=c['personal_benefit'].get('person')
            if not pid or not c['references']:raise ValueError('Osobní vazba bez osoby nebo pramene')
    for p in data['campaigns']:
        if p['case_count']!=len(p['observations']):raise ValueError('Nesoulad počtu případů')
        observed={o['case_id'] for o in p['observations']}
        if p['case_count'] and (not p.get('finding') or not p.get('finding_cases') or not set(p['finding_cases'])<=observed):raise ValueError('Souhrn bez ověřených případů')
        for obs in p['observations']:
            for record in obs['votes']:
                persons=record['people'];counts=Counter(x['vote'] for x in persons)
                if any(counts[k]!=record['counts'][k] for k in STATES):raise ValueError('Nesoulad hlasů listiny')
                if record['mandates']!=len(persons)-counts['Bez mandátu']:raise ValueError('Bez mandátu nelze započítat jako hlas')
                if any(x['campaign_2026']!=p['number'] for x in persons):raise ValueError('Hlas přiřazen cizí listině')
    return data

def count_text(counts,include_missing=True):
    keys=STATES if include_missing else STATES[:4]
    return ', '.join(f'{counts[k]} {LABELS[k]}' for k in keys if counts.get(k)) or 'žádný zaznamenaný hlas'

def load():
    d=validate(json.loads((ROOT/'research/behavior.json').read_text()))
    d['_cases']={c['id']:c for c in d['cases']}
    d['_campaigns']={p['number']:p for p in d['campaigns']}
    return d

def observation(data,number,cid):
    return next((o for o in data['_campaigns'][number]['observations'] if o['case_id']==cid),None)

def summary(data,number):
    p=data['_campaigns'][number]
    if not p['case_count']:
        return 'V hlasovací řadě 2022–2026 nemáme osobní hlasy dnešních kandidátů; jejich starší nebo jinou praxi uvádíme u slibů.'
    return p['finding']

def card(data,number):
    p=data['_campaigns'][number]
    if not p['case_count']:
        return '<div class="behavior-preview"><span class="mini">CO UKAZUJE ROZHODOVÁNÍ</span><p>'+e(summary(data,number))+'</p></div>'
    parts=[]
    for label,cid in [('Kontrola','lanovka-verejnost'),('Peníze','dornych'),('Výsledky','kamenna-vrch-bydleni')]:
        ob=observation(data,number,cid)
        v=ob['votes'][-1] if cid=='kamenna-vrch-bydleni' else ob['votes'][0]
        text={'lanovka-verejnost':'veřejná debata o lanovce','dornych':'prodej domů developerovi','kamenna-vrch-bydleni':'výběr banky pro nové byty'}[cid]
        parts.append(f'<li><strong>{label}:</strong> {e(text)} — {v["counts"]["Ano"]} pro / {v["mandates"]} s tehdejším mandátem.</li>')
    return '<div class="behavior-preview"><span class="mini">CO UKAZUJE ROZHODOVÁNÍ</span><p>'+e(summary(data,number))+'</p><ul>'+''.join(parts)+'</ul><p class="fine">Hlasy konkrétních lidí dnešní listiny. Podrobnosti a všechny stavy v detailu.</p></div>'

def references(data,refs):
    links=[]
    for r in refs:
        s=data['sources'][r['source']]
        import re
        m=re.search(r'PDF s\. (\d+)',r['locator']);fragment='#page-'+m[1] if m else ''
        links.append(f'<li><a href="/dukazy-jednani/{e(s["id"])}.html{fragment}">{e(r["locator"])}</a> · <a href="{e(s["url"])}">originál u vydavatele</a></li>')
    return '<ul class="source-links">'+''.join(links)+'</ul>'

def people_table(data,vid,number=None):
    v=data['votes'][vid]
    if number is None:persons=v['people']
    else:
        obs=next(o for o in data['_campaigns'][number]['observations'] if vid in [x['vote_id'] for x in o['votes']])
        persons=next(x for x in obs['votes'] if x['vote_id']==vid)['people']
    rows=[]
    for p in persons:
        now=data['_campaigns'][p['campaign_2026']]['name'] if p['campaign_2026'] else 'Na listinách 2026 není'
        rows.append(f'<tr><th scope="row"><a href="/profily/{e(p["person"])}.html">{e(p["name"])}</a></th><td>{e(p["vote"])}</td><td>{e(p["club_then"] or "V tento den bez mandátu")}</td><td>{e(now)}</td></tr>')
    return '<div class="table-wrap"><table><caption>Osobní hlasy; tehdejší klub a kandidátka pro volby 2026 se mohou lišit.</caption><thead><tr><th scope="col">Člověk</th><th scope="col">Hlas</th><th scope="col">Klub v den hlasování</th><th scope="col">Kandidátka 2026</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

def section(data,number):
    p=data['_campaigns'][number]
    intro=f'<section class="behavior-section" id="rozhodovani"><p class="eyebrow">CO UKAZUJE JEJICH ROZHODOVÁNÍ</p><h2>Když měli možnost rozhodnout.</h2><p class="behavior-lead">{e(summary(data,number))}</p>'
    counter=''
    if p['case_count']:
        solar=observation(data,number,'solar-kontrola')['votes'][0]
        counter=f'<p class="behavior-counter"><strong>Také důležité:</strong> kontrola hospodaření městské solární firmy SAKO SOLAR získala později {solar["counts"]["Ano"]} hlasů dnešních kandidátů této listiny. <a href="/rozhodovani/solar-kontrola/">Úplný případ →</a></p>'
    coverage=f'<p class="fine">Osobní hlasy do {day(data["votes_through"])} · rozbor z {day(data["reviewed"])}. Přiřazujeme je dnešním kandidátům, nikoli automaticky celé straně. <a href="/rozhodovani/#metodika">Výběr a meze závěrů</a>.</p>'
    if not p['case_count']:
        return intro+coverage+'<p>Chybějící hlasy nejsou důkazem lepšího ani horšího jednání. Starší role a odpovědnost stran jsou popsány v části „Měli moc to udělat?“.</p></section>'
    blocks=[]
    for axis,label in data['axes'].items():
        obs=[o for o in p['observations'] if data['_cases'][o['case_id']]['axis']==axis]
        items=[]
        for o in obs:
            c=data['_cases'][o['case_id']]
            votes=[]
            for x in o['votes']:
                v=data['votes'][x['vote_id']]
                votes.append(f'<details class="vote"><summary><span class="vote-date">{day(v["date"])}</span><strong>{e(v["meaning"])}</strong><span class="vote-counts">Dnešní listina: {e(count_text(x["counts"]))}</span></summary><p>{e(v["limit"])}</p>{people_table(data,v["id"],number)}{references(data,v["references"])}</details>')
            items.append(f'<article class="behavior-case"><h4><a href="/{e(c["path"])}">{e(c["title"])}</a></h4><p>{e(c["summary"])}</p>'+''.join(votes)+f'<p class="fine">{e(c["limitations"])}</p><a class="case-more" href="/{e(c["path"])}">Komu to pomohlo, výsledek a důkazy →</a></article>')
        blocks.append(f'<details class="behavior-axis"><summary>{e(label)} <span>{len(items)} případů</span></summary>'+''.join(items)+'</details>')
    extra=''
    if number==6:extra='<p class="behavior-alert"><strong>Doložená osobní vazba:</strong> Martin Příborský podpořil zřízení nové uvolněné funkce i vlastní zvolení do ní. <a href="/rozhodovani/uvolnena-funkce/">Zdůvodnění funkce a oba protokoly →</a></p>'
    if number==5:extra='<p class="behavior-alert"><strong>Také odpovědnost za řízení:</strong> Lídryně Jana Tichá Janulíková vedla TIC. Externí zpráva k vánočním trhům popsala nedostatky v řízení a doporučila nápravu. <a href="/rozhodovani/tic-vanoce/">Celý případ včetně kontrolního návrhu Tomáše Koláčného →</a></p>'
    return intro+coverage+counter+extra+''.join(blocks)+'<p><a href="/rozhodovani/#srovnani">Stejné kontrolní případy u všech kandidátek →</a></p></section>'

def build_pages(data,page,campaigns):
    bynum={p['number']:p for p in campaigns}
    for c in data['cases']:
        comparisons=[]
        for p in data['campaigns']:
            ob=observation(data,p['number'],c['id'])
            cells=''.join(f'<td>{e(count_text(x["counts"]))}</td>' for x in ob['votes']) if ob else '<td colspan="'+str(len(c['vote_ids']))+'">Bez osobních hlasů v této řadě</td>'
            comparisons.append(f'<tr><th scope="row"><a href="/{e(bynum[p["number"]]["path"])}#rozhodovani">{e(p["name"])}</a></th>{cells}</tr>')
        headings=''.join(f'<th scope="col">{day(data["votes"][vid]["date"])}<br>{e(data["votes"][vid]["meaning"])}</th>' for vid in c['vote_ids'])
        table='<div class="table-wrap"><table><caption>Hlasy tehdejších zastupitelů, kteří kandidují v roce 2026. Nehlasování, zdržení a nepřítomnost se nepřevádějí na hlas proti.</caption><thead><tr><th scope="col">Dnešní kandidátka</th>'+headings+'</tr></thead><tbody>'+''.join(comparisons)+'</tbody></table></div>'
        votes=[]
        for vid in c['vote_ids']:
            v=data['votes'][vid]
            votes.append(f'<details class="vote" id="{e(vid)}"><summary><span class="vote-date">{day(v["date"])}</span><strong>{e(v["meaning"])}</strong><span class="vote-counts">Celé zastupitelstvo: {e(count_text(v["counts"]))} · {e(v["result"])}</span></summary><p>{e(v["title"])} · {e(vid)}</p><p>{e(v["limit"])}</p>{people_table(data,vid)}{references(data,v["references"])}</details>')
        related=[]
        for p in campaigns:
            for claim in p['claims']:
                if claim['id'] in c['claim_ids']:related.append(f'<li><a href="/{e(p["path"])}#{e(claim["id"])}">{e(p["name"])}: {e(claim["title"])}</a></li>')
        fields=[('Co se rozhodovalo a proč na tom záleží',c['stakes']),('Kdo mohl jednat',c['opportunity']),('Kdo návrh přinesl',c['initiator']),('Komu to pomohlo a kdo nese náklady',c['beneficiaries']),('Co následovalo',c['outcome']),('Co víme o osobním prospěchu',c['personal_benefit']['text']),('Co závěr omezuje nebo zpochybňuje',c['limitations']),('Co ještě ověřit',c['followup'])]
        body='<a class="back" href="/rozhodovani/">← Všechny případy</a><article class="prose decision-page"><p class="eyebrow">'+e(data['axes'][c['axis']])+'</p><h1>'+e(c['title'])+'</h1><p class="lead">'+e(c['summary'])+'</p><p class="fine">Rozbor '+day(data['reviewed'])+' · '+e(data['coverage'])+'</p>'+''.join(f'<h2>{e(title)}</h2><p>{e(value)}</p>' for title,value in fields if value)+references(data,c['references'])+'<h2>Jak hlasovali dnešní kandidáti</h2>'+table+'<h2>Všechna jména a původní protokoly</h2>'+''.join(votes)+('<h2>Souvislost s dnešními sliby</h2><ul>'+''.join(related)+'</ul>' if related else '')+'<p><a href="/rozhodovani/#metodika">Jak vybíráme případy a pracujeme s důkazy</a> · <a href="/data/jednani-kampani.json">Úplné podklady JSON</a></p></article>'
        target=SITE/c['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_text(page(c['title'],body,c['path'],c['summary']))

    # Zdroje mají stejné principy jako dosavadní důkazy: hash, čas, originál,
    # číslované stránky/řádky, bezpečné textové zobrazení.
    (SITE/'dukazy-jednani').mkdir(exist_ok=True)
    for sid,s in data['sources'].items():
        origin=SITE/s['original'];txt=SITE/s['text']
        if hashlib.sha256(origin.read_bytes()).hexdigest()!=s['sha256']:raise ValueError('Změněný originál '+sid)
        if hashlib.sha256(txt.read_bytes()).hexdigest()!=s['text_sha256']:raise ValueError('Změněný text '+sid)
        content=txt.read_text();parts=[];line=0
        for pn,part in enumerate(content.split('\f'),1):
            parts.append(f'<span class="page-marker" id="page-{pn}">Strana {pn}</span>')
            for value in part.splitlines():
                line+=1;parts.append(f'<span class="source-line" id="L{line}"><a href="#L{line}">{line}</a>{e(value)}</span>')
        package=''
        if s.get('container'):
            assert hashlib.sha256((SITE/s['container']).read_bytes()).hexdigest()==s['container_sha256']
            package=f'<p>PDF je příloha {e(s["container_member"])} z <a href="/{e(s["container"])}">původního ZIPu</a>. SHA-256 ZIPu: <code>{e(s["container_sha256"])}</code>.</p>'
        body=f'<a class="back" href="/rozhodovani/">← Rozhodování</a><section class="source-document"><h1>{e(s["title"])}</h1><p><a href="{e(s["url"])}">Originál u vydavatele</a> · <a href="/{e(s["original"])}" download>Stáhnout uložený originál</a></p><p>Staženo {e(s["downloaded"])}. Textová extrakce může obsahovat chyby; rozhodující je originál.</p><details><summary>Kontrola kopie</summary><p>SHA-256 originálu: <code>{e(s["sha256"])}</code></p><p>SHA-256 textu: <code>{e(s["text_sha256"])}</code></p>{package}</details><pre class="source-text">'+ '\n'.join(parts)+'</pre></section>'
        path=f'dukazy-jednani/{sid}.html';(SITE/path).write_text(page('Podklad rozhodování '+sid,body,path))

    tiles=[]
    for axis,label in data['axes'].items():
        cards=''.join(f'<a class="decision-tile" href="/{e(c["path"])}"><h3>{e(c["title"])}</h3><p>{e(c["summary"])}</p><span>Osobní hlasy a důkazy →</span></a>' for c in data['cases'] if c['axis']==axis)
        tiles.append(f'<section id="{e(axis)}"><h2>{e(label)}</h2><div class="decision-grid">{cards}</div></section>')
    # Stejné případy a stejná pravidla pro všechny; plné stavy místo skóre.
    matrix=[]
    for cid in data['comparison_case_ids']:
        c=data['_cases'][cid]
        entries=[]
        for p in data['campaigns']:
            o=observation(data,p['number'],cid)
            text='; '.join(e(data['votes'][v['vote_id']]['meaning'])+': '+e(count_text(v['counts'])) for v in o['votes']) if o else 'Bez osobních hlasů v této řadě'
            entries.append(f'<tr><th scope="row"><a href="/{e(bynum[p["number"]]["path"])}#rozhodovani">{e(p["name"])}</a></th><td>{text}</td></tr>')
        matrix.append(f'<details class="comparison-case"><summary>{e(c["title"])}</summary><p>{e(c["summary"])}</p><div class="table-wrap"><table><caption>Všech 16 listin, stejný případ. Počty jsou hlasy jednotlivých lidí, nikoli známka strany.</caption><thead><tr><th scope="col">Kandidátka 2026</th><th scope="col">Osobní hlasy</th></tr></thead><tbody>'+''.join(entries)+f'</tbody></table></div><p><a href="/{e(c["path"])}">Kontext, alternativy a všechna jména →</a></p></details>')
    s=data['screening']
    methods=f'''<section class="prose" id="metodika"><h2>Jak tento přehled vzniká</h2><p>Celkem jsme stejnými tematickými pravidly prohledali názvy {s['total_votes']} protokolů a {s['materials']} indexovaných materiálů. {s['usable_votes']} protokolů je použitelných; šest neplatných či zvláštních záznamů se do osobních souhrnů nezařazuje. Jde o automatické hledání v názvech, ne o přečtení všech příloh.</p><p><strong>Vydání obsahuje {s['cases']} vysvětlených případů a {s['reviewed_votes']} hlasování.</strong> Případy vybíráme podle rozhodování o kontrole, majetku, funkcích a uskutečňování slibů. Výběr zahrnuje spory i široce podpořená rozhodnutí. Není reprezentativním vzorkem; četnost podpory v něm nepřevádíme na procento poctivosti.</p><p><a href="/data/vyber-rozhodovani.csv">Úplný seznam výběru: všech {s['total_votes']} protokolů CSV</a> · <a href="/data/vyber-materialu.csv">Prohledané názvy všech materiálů CSV</a>. Záznam rozlišuje ověřený kontext, vyřazení, dosud neposouzenou shodu a názvy bez shody. Bez shody neznamená bez problému. U {s['statuses'].get('k_dalsimu_posouzeni',0)} tematicky zachycených hlasování kontext v této nové vrstvě zatím posouzen není.</p><h3>Jeden případ, více rozhodnutí</h3><p>Pracovní skupina a externí posudek TIC patří k jedinému případu, stejně jako pravidla a financování Kamenného vrchu. Procedurální hlasy nenásobí počet zásluh nebo výtek. Ukazujeme účinek hlasu, výsledek, alternativy, další vývoj a otevřené otázky.</p><h3>Co smí závěr říkat</h3><p>Hlas pro utajení je doklad souhlasu s utajením. Hlas pro kontrolu dokládá podporu jejího zadání. Zdržení, nehlasování a nepřítomnost zůstávají odlišné; chybějící podpora návrhu není automaticky hlas proti ani důkaz úmyslu. Souhlas s celým rozpočtem nevykládáme jako osobní souhlas s každou jeho položkou.</p><p>Vazbu na vlastní funkci uvádíme pouze s konkrétní osobou a rozhodnutím. Nezaměňujeme ji za protiprávní prospěch. U prodeje ukazujeme příjemce i protiplnění městu; bez srovnání ceny a alternativ neoznačujeme prodej za škodu. Samotná koaliční shoda neprokazuje klientelismus.</p><h3>Stejná měřítka a protidůkazy</h3><p>Kontrolní případy výše ukazujeme u všech listin ve stejném pořadí. Vedle utajení SAKO je i široce schválená kontrola SAKO SOLAR; vedle prodeje Dornychu i pozdější zrušení privatizačního postupu. Různé předměty a jiné pravomoci brání automatickému závěru o dvojím metru. Opakované chování lze popsat jen s konkrétním seznamem srovnatelných případů, nikdy z jednoho hlasu.</p><h3>Čas a přiřazení odpovědnosti</h3><p>{e(data['coverage'])} Rozbor byl připraven {day(data['reviewed'])}; čas pořízení je u každého pramene zvlášť. Tým kandidující v roce 2026 není totožný s původním klubem. Každý řádek proto uchovává obě příslušnosti. Starší veřejné role jsou v dosavadním hodnocení kampaní; nepřevádíme je na neexistující hlasy v tomto období.</p><h3>Co stále neumíme doložit</h3><ul>'''+''.join(f'<li>{e(x)}</li>' for x in data['limitations'])+'''</ul><p>Tento přehled nemá bodové hodnocení osobní morálky. Je podkladem pro vlastní úsudek o doloženém chování a o hodnotách, které jednotlivá rozhodnutí vyjadřují.</p><h3>Data pro vlastní kontrolu</h3><p><a href="/data/jednani-kampani.json">Případy, hlasy, prameny a metodika JSON</a> · <a href="/data/jednani-hlasy.csv">Osobní hlasy dnešních kandidátů CSV</a> · <a href="https://github.com/mrmartin/kydy/commits/main/research/behavior_curation.py">Historie redakčních změn</a>.</p></section>'''
    body=f'<a class="back" href="/">← Kampaně a sliby</a><section class="campaign-hero"><p class="eyebrow">ROZHODOVÁNÍ 2022–2026</p><h1>Když měli moc.<br>Co s ní udělali?</h1><p class="behavior-lead">Kdo podpořil kontrolu, kdo utajení a komu pomohla konkrétní rozhodnutí. Každé zjištění vede ke jménům a původnímu dokumentu.</p><p class="fine">{s["cases"]} případů · {s["reviewed_votes"]} hlasování · osobní hlasy do {day(data["votes_through"])}</p><p><a href="#srovnani">Porovnat stejné případy</a> · <a href="#metodika">Rozsah a pravidla výběru</a></p></section>'+''.join(tiles)+'<section id="srovnani"><h2>Stejné otázky pro všechny</h2><p>Rozbalte případ a porovnejte osobní hlasy všech dnešních kandidátek. Nejde o celkové skóre otevřenosti.</p>'+''.join(matrix)+'</section>'+methods
    path='rozhodovani/index.html';(SITE/path).parent.mkdir(exist_ok=True);(SITE/path).write_text(page('Co ukazuje jejich rozhodování',body,path))
    # Exportovat i jednu větu z přehledu; pomocné indexy do JSON nepatří.
    for p in data['campaigns']:p['summary']=summary(data,p['number'])
    public={k:v for k,v in data.items() if not k.startswith('_')}
    (SITE/'data/jednani-kampani.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
