"""Význam celých rozhodovacích případů; fakta a hodnotový výklad jsou oddělené."""
REVIEWED = '2026-09-27'
AXES = {'kontrola': 'Kontrola moci', 'penize': 'Peníze a výhody', 'vysledky': 'Výsledky slibů'}
# Pravidla vyhledávání neobsahují jména ani strany. Shoda není důkaz pochybení.
SCREENING = {
 'otevrenost': r'tajn|veřejné projedn|otevřen.*dat|zveřej|informativní zpráv|informací|informace o',
 'kontrola': r'audit|kontrol|přezkoum|závěrečn.*úč|hospodár|vlastnick.*politik',
 'funkce': r'odměn|uvolněn|dozorčí|představenstv|volba|jmenov|střet|podjat',
 'majetek': r'prodej|privatiz|dražb|směn|konces|dotac|úvěr|zakáz|výběr.*bank|výběr.*dodavat',
 'sluzby': r'byt|bydlen|škol|senior|sociáln|doprav|tramvaj|lanov|nádraž|hal[ay]|arén|stadion|kulturní centrum|SAKO|odpad|vouch|particip|Dáme na vás|protipovod',
}
CASES = []
def case(id, axis, title, summary, votes, stakes, beneficiaries, outcome, limits, followup, refs=(), claims=(), initiator='', benefit=None):
 CASES.append(dict(id=id,axis=axis,title=title,summary=summary,vote_ids=votes,stakes=stakes,beneficiaries=beneficiaries,outcome=outcome,limitations=limits,followup=followup,references=list(refs),claim_ids=list(claims),initiator=initiator,personal_benefit=benefit or {'status':'neposouzeno','text':'Osobní majetkové vazby a soukromý prospěch rozhodujících osob nejsou v tomto případu ověřené. Hlasování je samo neprokazuje.'}))

case('sako-tajne','kontrola','Kdo chtěl o SAKO hlasovat tajně?',
 'O způsobu hlasování rozhodovali veřejně: 28 zastupitelů podpořilo utajení následné volby, 14 bylo proti.',
 ['Z9-11-007'],
 'Šlo o rozhodování k městské odpadové společnosti SAKO. Při tajné volbě veřejnost nemůže ověřit, jak jednotliví zastupitelé hlasovali. Tento případ hodnotí jen rozhodnutí použít tajnou volbu.',
 'Dohledatelnost osobních rozhodnutí je důležitá pro všechny obyvatele. Z utajení nelze určit příjemce soukromé finanční výhody.',
 'Návrh na tajné hlasování prošel. Následující tajný výsledek jednotlivým politikům nepřipisujeme.',
 'Souhlas s tajnou volbou neprokazuje podporu konkrétní varianty projektu, korupci ani nezákonnost. Pozdější souhlas s kontrolou SAKO SOLAR je samostatný případ a důležitý protidůkaz proti plošnému závěru, že odmítají veškerou kontrolu.',
 'Další veřejná rozhodnutí o utajení a zdůvodnění volby postupu.', claims=['K03-03','K02-05','K15-03'])
case('solar-kontrola','kontrola','Umožnili kontrolu městské solární firmy',
 'Kontrolu SAKO Brno SOLAR schválilo 49 zastupitelů; nikdo nebyl proti.',
 ['Z9-35-005'],
 'Kontrolní výbor potřeboval výslovné pověření zastupitelstva. Měl prověřit výkon vlastnických práv města, hospodárnost, odměňování, zakázky, cíle projektu i externí poradce.',
 'Obyvatelé a město získali možnost kontroly hospodaření společnosti. Samotné zadání kontroly nevypovídá o výsledku ani o úspoře.',
 'Dne 19. 5. 2026 bylo pověření přijato. Rada a zástupci města ve firmách mají poskytnout součinnost; výbor má předložit výsledek a případná opatření.',
 'V tomto souboru nemáme ověřenou závěrečnou zprávu ani provedenou nápravu. Nejde o tutéž firmu a stejné rozhodnutí jako tajná volba o SAKO v roce 2023. Nelze z jejich rozdílu automaticky odvodit dvojí metr.',
 'Dohledat zprávu kontrolního výboru, reakce odpovědných orgánů a uskutečněná opatření.',
 refs=[('0e845920a9ca9f72','PDF s. 7–8 – návrh, diskuse a schválený rozsah kontroly')],initiator='Návrh klubu ANO 2011 představil Miroslav Kubásek. Petr Hladík v rozpravě oznámil podporu a popsal výhrady k fungování firmy.')
case('privatizace-kontrola','kontrola','Kontrola prodeje městských bytových domů',
 'Zastupitelé rozšířili zadání kontroly prodejů a schválili je 51 hlasy.',
 ['Z9-04-002','Z9-04-068'],
 'V lednu 2023 se rozhodovalo, zda kontrolní výbor prověří privatizaci městských bytových domů. Diskuse rozšířila původně zmiňované zaměření na vybrané domy v Brně-středu.',
 'Město a obyvatelé získali schválený kontrolní úkol; samotné pověření nevrací majetek ani nedokládá zjištěnou škodu.',
 'Po neplatném pokusu č. 67 bylo konečné pověření přijato v hlasování č. 68 poměrem 51 pro, nikdo proti, jeden se zdržel. Neplatný pokus se nezapočítává.',
 'Robert Kerndl v rozpravě nahlásil podjatost. To je oznámení možné vazby, nikoli prokázání protiprávního obohacení. Zde neuzavíráme výsledky celé kontroly.',
 'Propojit konečnou zprávu kontroly s konkrétními domy a přijatými opatřeními.',
 refs=[('a43c0850f687c0a3','PDF s. 37–38 – rozšíření zadání, oznámení podjatosti a platné hlasování')],initiator='Tomáš Skřička předložil návrh; Petr Hladík navrhl obecnější rozsah kontroly a předkladatel jej přijal.')
case('data-firem','kontrola','Veřejná data městských firem',
 'Pravidla pro zveřejňování dat městských společností získala 49 hlasů.',
 ['Z9-09-016'],
 'Veřejně použitelná data mohou umožnit obyvatelům kontrolovat činnost městských firem. Rozhodovalo se o pravidlech pro jejich zveřejňování.',
 'Obyvatelé, novináři a další uživatelé městských dat; přínos závisí na skutečně zveřejněných údajích.',
 'Zastupitelstvo udělilo souhlas s pravidly. Toto je přijaté pravidlo, nikoli ověřené splnění všech publikačních povinností.',
 'Hlas pro je konkrétní podpora otevřenosti, ale ne důkaz, že firma zveřejnila úplná, aktuální a použitelná data.',
 'Porovnat jednotlivé povinnosti s publikovanými daty, aktualizacemi a výjimkami.',claims=['K08-05'])
case('lanovka-verejnost','kontrola','Veřejné projednání analýz lanovky',
 'Veřejné představení analýz lanovky získalo 14 hlasů a neprošlo; petici město vzalo na vědomí.',
 ['Z9-19-005','Z9-19-006'],
 'Občané požadovali projednání lanovky z Pisárek do univerzitního kampusu v Bohunicích. Jasna Flamiková navrhla veřejně představit odborné analýzy a umožnit o nich diskutovat.',
 'Obyvatelé by získali možnost seznámit se s podklady a diskutovat před dalším rozhodováním.',
 'Návrh veřejného projednání neprošel: 14 pro, 3 proti, 16 se zdrželo, 18 nehlasovalo. Následující vzetí petice na vědomí prošlo 48 hlasy.',
 'Zdržení a nehlasování neposkytly potřebnou podporu, ale nejsou hlasem proti. Neprošel konkrétní návrh debaty; neprokazujeme, že se nikdy nekonalo jiné veřejné jednání. Hlasování nerozhodovalo o stavbě nebo zastavení lanovky.',
 'Ověřit, zda a kdy byly analýzy zveřejněny a veřejná debata proběhla jinou cestou.',
 refs=[('7a2e7987609bcbd0','PDF s. 8–13 – diskuse, přesný návrh a oba výsledky')],claims=['K04-01','K15-01'],initiator='Jasna Flamiková navrhla veřejné projednání odborných podkladů.')
case('povodne-zpravy','kontrola','Pravidelné zprávy o ochraně před povodněmi',
 'Návrh zpráv o postupu protipovodňových staveb každé tři měsíce získal 11 hlasů a neprošel.',
 ['Z9-20-040'],
 'Zastupitelé měli pravidelně dostávat zprávy o postupu opatření chránících město před povodněmi. Rozhodovalo se o četnosti informování, ne o financování nebo zastavení staveb.',
 'Zastupitelé a veřejnost by mohli pravidelněji sledovat průběh přípravy a realizace ochrany před povodněmi.',
 'Návrh neprošel: 11 pro, 1 proti, 12 se zdrželo a 29 nehlasovalo.',
 'Vedení v rozpravě uvedlo, že stavby pokračují a připravují se další etapy. Odmítnutí této formy informování není doklad odmítnutí ochrany před povodněmi ani důkaz, že nebyly dostupné jiné zprávy.',
 'Srovnat existující zveřejňování průběhu staveb s navrhovanou tříměsíční pravidelností.',
 refs=[('21185e2ff631d16f','PDF s. 29–30 – argumenty obou stran a hlasování')],claims=['K08-07'],initiator='Jasna Flamiková navrhla pravidelné předkládání zpráv.')
case('tic-vanoce','kontrola','Dvě varianty kontroly vánočních trhů',
 'Pracovní skupina neprošla, externí posouzení prošlo a vznikla zveřejněná závěrečná zpráva.',
 ['Z9-25-075','Z9-25-076'],
 'Zastupitelé porovnávali dvě odlišné cesty: pracovní skupinu městských organizací pro efektivnější pořádání trhů a externí posouzení personálních nákladů a hospodárnosti TIC u Vánoc 2023 a 2024.',
 'Město jako zřizovatel, pořadatelé trhů a veřejnost. Hodnocení nákladů má být spojeno s tím, co akce přináší obyvatelům a návštěvníkům.',
 'Externí zpráva zpracovaná v srpnu 2025 je zveřejněná. Popsala nedostatky v rozpočtování, harmonogramu a zapojení zřizovatele; navrhla pravidelnou kontrolu a otevřenější soutěžení. Doložen je výstup kontroly, nikoli splnění všech doporučení.',
 'Nesouhlas s jednou variantou není odmítnutím každé kontroly. V diskusi zazněly výhrady k návodným otázkám a nejasnému měřítku hospodárnosti. Externí posudek není pravomocné zjištění korupce. Jana Tichá Janulíková vedla TIC; neměla tehdy městský mandát a hlas Tomáše Koláčného není jejím hlasem.',
 'U každého doporučení doložit odpovědnou osobu, termín, přijaté opatření a jeho výsledek.',
 refs=[('e988b29ad183637c','PDF s. 44–51 – obě varianty, výhrady a schválený úkol'),('tic-audit-2025','PDF s. 49–51 – závěry a doporučení externího posudku'),('02da3b602496d94a','PDF s. 1–3 – město rozlišuje veřejnosprávní kontrolu a externí posudek')],claims=['K05-02'],initiator='Tomáš Koláčný navrhl pracovní skupinu; Markéta Vaňková navrhla externí posouzení. Původní podnět k bodu předložil Tomáš Skřička.')
case('charita-vynosy','penize','Výtěžek charity má dostat její příjemce',
 'Zastupitelstvo uložilo, aby podporované charitativní akce posílaly výnosy těm, pro koho se konají.',
 ['Z9-10-007'],
 'Po projednání kontrolním výborem se rozhodovalo o podmínce v městských dotačních programech pro charitativní akce.',
 'Subjekty, pro které je charitativní akce pořádána; město financující podporu akce.',
 'Návrh získal 47 hlasů. Rada dostala úkol doplnit do příslušných dotačních programů závazek, aby veškeré výnosy směřovaly k určeným příjemcům.',
 'Přijetí pravidla není prověření účetnictví každého pořadatele ani důkaz, že někdo dříve peníze odčerpal.',
 'Dohledat změny dotačních podmínek a vyúčtování konkrétních akcí.',refs=[('eb0d7acd8a1bcc62','PDF s. 7 – schválený úkol'),('4f1fc72aed1e37d0','PDF s. 1 – podnět a účel pravidla')],initiator='Návrh navazoval na usnesení kontrolního výboru, předložil jej Tomáš Skřička.')
case('uvolnena-funkce','penize','Další funkce vykonávaná na plný úvazek',
 'Počet dlouhodobě uvolněných zastupitelů vzrostl na 15; do nové funkce byl zvolen Martin Příborský, který oba návrhy podpořil.',
 ['Z9-03-111','Z9-03-114'],
 'Dosavadní agenda rozvoje města, spolupráce s okolím a společných investic se změnila na samostatnou uvolněnou funkci, tedy práci politika na plný úvazek. To vytváří konkrétní pozici i náklad na její výkon.',
 'Funkci získal Martin Příborský, dnešní kandidát ODS, TOP 09 a nezávislých. Deklarovaným veřejným přínosem byla kapacita pro rozsáhlou investiční agendu.',
 'Zřízení funkce prošlo 39 hlasy a volba Příborského 40 hlasy. Jeho osobní hlas je v obou protokolech Ano.',
 'Důvodová zpráva uváděla časovou náročnost a očekávaných přibližně 8 miliard Kč přes společné investice ITI. Vytvoření funkce ani hlas pro vlastní volbu samy nedokazují zneužití moci. Nemáme zde vyčíslenou vyplacenou odměnu ani vyhodnocení přínosu funkce.',
 'Doplnit skutečné náklady, náplň práce a výsledky; stejným postupem posoudit další placené funkce.',
 refs=[('cadb7a0036f09596','PDF s. 1 a 4 – zdůvodnění nové uvolněné funkce'),('31d42a3a0b7a27be','PDF s. 67–69 – diskuse, zřízení a volba')],initiator='Návrh zřízení i nominaci předložila primátorka Markéta Vaňková.',benefit={'status':'dolozena_funkce','person':'martin-priborsky','text':'Příborský byl příjemcem nové funkce a hlasoval pro její vytvoření i pro vlastní zvolení. To je doložená vazba na funkci; neoprávněný prospěch nebo protiprávní střet zájmů tím prokázán není.'})
case('dornych','penize','Prodej dvou městských domů developerovi',
 'Brno prodalo dva prázdné bytové domy Dornych 29 a 31 společnosti CTP za 225 milionů Kč.',
 ['Z9-25-057'],
 'Město rozhodovalo o prodeji dvou domů s celkem 40 prázdnými byty. Kupující plánoval jejich odstranění a novou komerční a bytovou výstavbu.',
 'CTP Vlněna Business Park získala nemovitosti a město kupní cenu. Brno ztratilo vlastnictví domů; nešlo o vystěhování 40 obývaných bytů.',
 'Prodej prošel 38 hlasy proti 10 a přijetí kupní ceny je doloženo k 5. 6. 2025. Zářijový materiál navrhoval převod výnosu do Fondu bytové výstavby.',
 'Domy byly ve špatném až průměrném stavu. Podklady obsahují ekonomické zdůvodnění prodeje; neprokazujeme, že oprava byla výhodnější. Navržený převod výnosu není automaticky schválený. Pozdější omezení prodejů může být změnou politiky.',
 'Porovnat skutečné využití výnosu a další rozhodování o prodejích se slibem zachovat městské bydlení.',
 refs=[('ea80e5751d173075','PDF s. 4–7 – domy, kupující, důvody a příprava'),('52f247a38ab38f70','PDF s. 4 – přijetí kupní ceny a navržené využití')],claims=['K02-02','K04-02','K05-03','K08-01','K15-02'])
case('konec-privatizace','penize','Zrušení starého seznamu domů k prodeji',
 'V lednu 2026 město zrušilo dosavadní privatizační postup a seznam domů připravovaných k prodeji.',
 ['Z9-32-036'],
 'Rozhodovalo se o budoucím postupu při prodeji městských bytových domů. Tento krok je třeba ukázat i u politiků, kteří předtím konkrétní prodeje podpořili.',
 'Město si ponechává prostor pro využití domů pro bydlení; konečný dopad závisí na dalších jednotlivých rozhodnutích.',
 'Zrušení postupu i seznamu bylo schváleno. Dříve dokončené prodeje tím nebyly vráceny.',
 'Nejde o obecný zákaz každého budoucího prodeje městské nemovitosti ani o důkaz dokončených nových bytů.',
 'Sledovat jednotlivé nové prodeje a změny pravidel po tomto rozhodnutí.',claims=['K02-02','K04-02','K05-03','K08-01','K15-02'])
case('stadion','penize','Stadion za Lužánkami: podmínky před konečnou smlouvou',
 'Podpora stadionu byla podmíněná; v červnu 2026 zastupitelé požadovali doplnění podkladů před dalším rozhodnutím.',
 ['Z9-28-030','Z9-36-009'],
 'Město zvažovalo podmínky stadionu za Lužánkami, soukromého investora a nakládání s pozemky. Důležité jsou konečné závazky a rizika, ne jen obecná podpora sportu.',
 'Sportovní kluby, diváci, případný investor a město; bez konečné smlouvy nelze určit celkové rozdělení nákladů a výhod.',
 'V září 2025 byla přijata podmíněná podpora. V červnu 2026 se rozhodovalo o doplnění podkladů k dalšímu postupu, nikoli o konečném prodeji nebo koncesi.',
 'Požadavek podkladů není hlas proti stadionu. Podpora projektu není souhlas s každou budoucí cenou nebo smlouvou.',
 'Dohledat konečnou smlouvu, ocenění majetku, financování infrastruktury a rozdělení rizik.',claims=['K05-01','K06-02','K15-04'])
case('kamenna-drazba','penize','Prodej domu Kamenná 2 v dražbě',
 'Město schválilo prodej domu Kamenná 2 formou elektronické dražby.',
 ['Z9-23-052'],
 'Vedle přímého prodeje Dornychu sledujeme i jiný způsob prodeje městského domu: elektronickou dražbu.',
 'Případný vydražitel a město jako příjemce ceny. Konečný příjemce a cena dokončeného převodu nejsou v tomto případu ověřené.',
 'Schválen byl prodej v elektronické dražbě. Samotné usnesení nedokládá její výsledek a převod vlastnictví.',
 'Dražba sama nezaručuje výhodnost a prodej sám neprokazuje poškození města. Pro hodnocení je nutné znát ocenění, podmínky i výsledek.',
 'Doplnit dražební protokol, konečnou cenu a následný převod.',claims=['K04-02','K15-02'])
case('kamenna-vrch-bydleni','vysledky','Kamenný vrch II: od pravidel k podpisu smlouvy',
 'Po pravidlech a výběru banky následovala v červenci 2026 smlouva na stavbu 353 bytů.',
 ['Z9-26-063','Z9-36-071'],
 'Bytový projekt Kamenný vrch II má více fází: pravidla pro zájemce, financování a smlouvu se zhotovitelem. Započítáváme jej jako jeden případ.',
 'Budoucí obyvatelé bytů; město nese také část finančních závazků a rizik projektu.',
 'Doložená jsou přípravná hlasování a oznámení smlouvy se zhotovitelem ze dne 15. 7. 2026. Zářijový návrh úvěru obsahuje i závazky města při neobsazenosti družstevních bytů.',
 'Podepsaná smlouva není předání hotových bytů. Výběr banky v červnu není zářijové schválení finálního úvěru a jeho podmínek. Výsledek celého projektu nepřipisujeme jedinému hlasujícímu.',
 'Ověřit přijetí a znění úvěru, průběh stavby, skutečné náklady a předání bytů.',
 refs=[('67608a0aa50e0c9a','15. 7. 2026 – oznámení podpisu smlouvy na 353 bytů'),('54680ebc827751f8','PDF s. 1 a příloha – návrh úvěru a závazky města')],claims=['K02-02','K03-01','K06-01','K08-01','K15-02'])
case('mostecka-druzstvo','vysledky','Stávající městský dům do družstva',
 'U Mostecké 16 se rozhodovalo o družstvu pro existující dům, ne o nové bytové výstavbě.',
 ['Z9-36-073'],
 'Převod stávajícího městského domu Mostecká 16 do družstevního projektu má jiný dopad na městské vlastnictví než stavba nových družstevních bytů.',
 'Budoucí členové družstva a město; konkrétní podmínky určují rozdělení práv, nákladů a rizik.',
 'Zastupitelstvo schválilo založení družstva, postup a kritéria projektu.',
 'Hlas proti tomuto převodu není automaticky odpor k družstevnímu bydlení obecně. Schválení postupu samo nedokládá uskutečněný převod.',
 'Ověřit převod majetku, smluvní podmínky a výsledné postavení obyvatel domu.',claims=['K15-02'])
case('arena','vysledky','Aréna na výstavišti: financování a stavba',
 'Financování arény bylo schváleno a stavba je doložená; konečný účet a plný provoz tento archiv nepotvrzuje.',
 ['Z9-08-094'],
 'Rozhodovalo se o úvěrové a finanční dokumentaci pro novou víceúčelovou halu na výstavišti.',
 'Budoucí návštěvníci, sportovní a kulturní pořadatelé; město a jeho společnost nesou finanční závazky.',
 'Finanční dokumentace získala 40 hlasů. Městská zpráva z 10. 9. 2026 dokládá stavbu před dokončením a plánované prohlídky.',
 'Prohlídky stavby nejsou plný provoz. Zde pracujeme se zářijovým snímkem, nikoli s ověřením otevření k 27. 9. 2026. Úvěrový hlas není konečný účet ani důkaz, že projekt je pro veřejnost výhodnější než alternativy.',
 'Doplnit skutečné otevření, konečné náklady včetně infrastruktury, provozní výsledek a využití haly.',
 refs=[('d4b6a96177052aff','10. 9. 2026 – oznámení prohlídek před dokončením')],claims=['K06-02'])
case('pravidla-bytu','vysledky','Pravidla startovacích a sociálních bytů',
 'Zastupitelé změnili pravidla nájmu městských bytů, včetně startovacího a sociálního bydlení.',
 ['Z9-17-060'],
 'Pravidla určují, jak město pracuje s existujícím bytovým fondem a přístupem žadatelů k bydlení.',
 'Žadatelé o městské bydlení. Bez rozboru jednotlivých podmínek nelze tvrdit, že změna pomohla všem skupinám stejně.',
 'Změna pravidel byla schválena. To je uskutečněné rozhodnutí o pravidlech, nikoli počet nově postavených nebo přidělených bytů.',
 'Hlas pro celý soubor změn neprokazuje souhlas s každou jednotlivou podmínkou. Dostupnost se musí ověřit podle skutečných přidělení a čekacích dob.',
 'Porovnat konkrétní změny podmínek, počty žadatelů, přidělení a čekací doby.',claims=['K06-01','K07-01','K12-03'])
case('rodicovske-vouchery','vysledky','Příspěvky dětem na aktivity',
 'Město změnilo podmínky rodičovských voucherů, tedy finančních příspěvků na aktivity dětí.',
 ['Z9-18-115'],
 'Rozhodovalo se o parametrech existující podpory od července 2024.',
 'Rodiny splňující pravidla programu a poskytovatelé dětských aktivit; skutečný dosah závisí na čerpání.',
 'Změna programu byla schválena. Doložené je rozhodnutí o podmínkách, ne vyhodnocení všech vyplacených příspěvků.',
 'Podpora tohoto programu není hlas pro dnešní nový slib 1 000 Kč ročně na sport za jiných podmínek.',
 'Doplnit počet příjemců, nevyčerpané prostředky a srovnání s novým slibem.',claims=['K04-03','K12-05'])
case('dame-na-vas','vysledky','Peníze na projekty vybrané obyvateli',
 'Město vytvořilo fond pro projekty Dáme na vás; tím samo neschválilo dnešní slib 50 milionů ročně.',
 ['Z9-20-042'],
 'Obyvatelé v Dáme na vás navrhují a vybírají městské projekty. Fond umožňuje spravovat jejich peníze i mezi jednotlivými roky.',
 'Obyvatelé využívající vybrané projekty a zapojení navrhovatelé. Konkrétní přínos závisí na dokončení projektů.',
 'V říjnu 2024 bylo schváleno zřízení fondu k 1. 1. 2025 spolu s rozpočtovými změnami.',
 'Zřízení fondu není nové přidělení 50 milionů Kč ročně ani důkaz, že jsou všechny vítězné projekty dokončené.',
 'Propojit vítězné projekty s termíny, skutečnými výdaji a dokončením.',claims=['K03-04'])

# Nově přečtené protokoly mají výslovný výklad; ostatní používají existující
# kontrolovaný slovník, nikdy automatický úsudek z titulku.
EXTRA_VOTES = {
 'Z9-35-005': ('Pověřit kontrolní výbor kontrolou SAKO Brno SOLAR', '0e845920a9ca9f72',8),
 'Z9-04-002': ('Zařadit návrh pověření kontrolního výboru do programu', 'a43c0850f687c0a3',2),
 'Z9-04-068': ('Pověřit kontrolní výbor kontrolou privatizace městských bytových domů', 'a43c0850f687c0a3',38),
 'Z9-10-007': ('Vyžadovat předání výnosů podporovaných charitativních akcí určeným příjemcům', 'eb0d7acd8a1bcc62',7),
 'Z9-03-111': ('Zřídit další uvolněnou funkci pro strategický rozvoj a společné investice', '31d42a3a0b7a27be',68),
 'Z9-03-114': ('Zvolit Martina Příborského do nové uvolněné funkce', '31d42a3a0b7a27be',69),
}
# Vysvětlené vyřazení potenciálních kontrolních případů z hlavního srovnání.
REVIEW_EXCLUSIONS = {
 'Z9-29-006': ('Změna podmínky pro místopředsedy výborů: už nemusí být zastupiteli; sama nedokládá oslabení kontroly.', 'af870d56898ecc01',7),
}
CONTROL_CASES = ['sako-tajne','solar-kontrola','privatizace-kontrola','data-firem','lanovka-verejnost','povodne-zpravy','tic-vanoce']

# Čtenářský souhrn se vztahuje jen k uvedeným případům a dnešním kandidátům.
# Všechny stavy hlasu, i protidůkaz v podobě kontroly SOLAR, zůstávají v detailu.
FINDINGS = {
 2: 'Osm dnešních kandidátů odmítlo utajení hlasování o městské odpadové firmě SAKO, ale pravidelné zprávy o protipovodňových stavbách nepodpořil žádný z jejich devíti přítomných zastupitelů.',
 3: 'Dvě jejich tehdejší zastupitelky odmítly utajení hlasování o městské odpadové firmě SAKO a podpořily veřejnou debatu o lanovce i pravidelné zprávy o ochraně před povodněmi.',
 4: 'Dva dnešní kandidáti podpořili utajení hlasování o městské odpadové firmě SAKO; při rozhodování o veřejné debatě o lanovce a pravidelných povodňových zprávách nehlasovali.',
 5: 'Tomáš Koláčný odmítl utajení hlasování o městské odpadové firmě SAKO a podpořil veřejnou debatu o lanovce; u kontroly vánočních trhů navrhl pracovní skupinu a při hlasování o externím posouzení se zdržel.',
 6: 'Devět dnešních kandidátů podpořilo utajení hlasování o městské odpadové firmě SAKO; veřejnou debatu o lanovce ani pravidelné povodňové zprávy nepodpořil nikdo z jejich přítomných zastupitelů.',
 8: 'Sedm dnešních kandidátů podpořilo utajení hlasování o městské odpadové firmě SAKO; u veřejné debaty o lanovce se jejich hlasy rozdělily a pravidelné povodňové zprávy nikdo z nich nepodpořil.',
 15: 'Oba přítomní dnešní kandidáti odmítli utajení hlasování o městské odpadové firmě SAKO, všichni tři podpořili veřejnou debatu o lanovce i pravidelné povodňové zprávy.',
 16: 'Dva dnešní kandidáti se u utajení hlasování o městské odpadové firmě SAKO zdrželi; veřejná debata o lanovce i pravidelné povodňové zprávy dostaly po jednom jejich hlasu pro.',
}
