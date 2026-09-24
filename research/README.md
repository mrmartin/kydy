# Podklady pro „Slibují to. Udělají to?“

`curation.py` obsahuje česká redakční posouzení, nikoli automaticky odhadnuté pravděpodobnosti. `assessment.json` je úplný přenositelný vstup veřejného generátoru: kampaně, sliby, konkrétní osobní hlasy, prameny a meze závěrů. Připravuje jej `scripts/prepare_assessment.py` z tohoto výběru a místního archivu. Web lze pak znovu sestavit pouze z repozitáře pomocí `python3 scripts/build_assessment.py`.

Výběr vychází z aktuálních programových kapitol a zveřejněných priorit, ne z dostupnosti hlasování. Není statistickým měřením četnosti reklam. Související části jednoho slibu tvoří jednu jednotku; nic se nedoplňuje do neúplných programů. První vydání má společný stav ověření 20. 9. 2026; programové snímky mají vlastní data získání. Hlasovací řada končí 23. 6. 2026. Zářijové předložené materiály jsou samostatné důkazy přípravy, nikoliv náhrada dosud neověřených osobních hlasů.

Hodnocení je úsudek založený na zdrojích. Absence mandátu, opoziční neúspěch, změna postoje ani chybějící doklad nejsou důkaz lži. Nikomu nepřipisujeme úmysl. Chybějící historie omezuje posouzení praxe; sama nedokazuje překážku ani neurčuje hodnocení nového kandidáta.

Při aktualizaci nejprve archivovat nové zdroje, ověřit význam rozhodnutí a protidůkazy, poté změnit posouzení a přidat záznam do historie. Staré znění zůstává v historii Gitu. Kategorie se neurčují podle požadovaného rozložení barev. Každý slib musí mít výslovné redakční zařazení; neznámé nebo chybějící zařazení build odmítne.

Metodika 2 (20. 9. 2026): 57 slibů, 95 použitých pramenů. Otázka „Jakou oporu má tento slib?“ nahrazuje původní prognózu splnění ANO/MOŽNÁ/NE. `evidence_status` má čtyři možné hodnoty: `podlozeno` (Podloženo činy), `podminene` (Podmíněně proveditelné), `rozpor` (Zásadní rozpor nebo překážka), `bez_opory` (Zatím jen slib). Každý z 57 záznamů má explicitní zařazení a důvod v `EVIDENCE_ASSESSMENTS`; žádný výchozí stav. Schéma JSON má verzi 2, veřejný export přidává slovník kategorií a `evidence_counts` kampaní. CSV má samostatný kód a český popis opory. Původní `verdict` je odstraněn, aby nevydával nové kategorie za předpověď.

Kampaň nemá většinový verdikt. Karta ukazuje kategorii u každého slibu a skladbu všech vybraných slibů, takže dílčí rozpor ani chybějící podklady nezmizí v průměru. Počet slibů není skóre kvality kampaně a každý výběr má jiný rozsah. Volební a koaliční podmínky zůstávají v detailu, ale obecná nejistota voleb nepřebarvuje doložené činy. Přesné pravidlo a historie změny jsou v `site/metodika.html`.

Zelená může označovat doložený osobní krok i realizaci městského projektu. Důvod musí výslovně odlišit jejich původ a fázi: smlouva SAKO není osobní zásluha každé kandidátky a kontrolní návrh není dokončený audit. U složených slibů podstatná mezera v jiné části brání zelenému hodnocení celého balíku. Červená vyžaduje zásadní přetrvávající překážku či rozpor; v tomto vydání pro ni nemáme dostatečný podklad. „Jen kydy!“ označuje slib bez dostatečně doložených činů nebo plánu; samo o sobě nejde o důkaz lži.

Přechod používá stejné archivované zdroje; změnila se otázka a interpretace, nikoli doložené výsledky politiků. Staré prognózy jsou dostupné v historii Gitu. Nebyl doplněn chybějící investiční audit ani volební model.

Reprodukce veřejných stránek potřebuje pouze standardní Python. Příprava nového podkladu potřebuje místní původní archiv; stažení zdrojů bylo provedeno jeho existujícím nástrojem `skripty/archiv.py` a zůstává zapsáno v `data/zdroje.jsonl`. Zahrnuty jsou originály i texty. Veřejný podklad nepřepisuje původní hlasovací soubor ani předstíraně nedoplňuje zářijové hlasy.


Metodika 3 (20. 9. 2026) přidává `nevyuzita_moznost` — „Neudělali to, když mohli“. JSON schéma 3 má `governance` u všech 16 kampaní a `accountability` u konkrétních výtek. Pět kategorií zachovává skladbu místo celkového skóre. V CSV jsou navíc `vykonna_role`, `vykonna_odpovednost` a `nevyuzita_moznost_json` včetně zdrojů. Případy bez uzavřeného důkazního řetězce mají `accountability: null`; to není osvědčení bezchybného vládnutí.

První aplikace se týká zachování Dornychu 29/31 v K02-02 a K08-01: jeden případ u dvou kandidátek, nikoli dvě nezávislá selhání. Rozsah je omezen na vlastní souhlas s prodejem, který mohli odpovědní radní odepřít. Netvrdíme samostatné veto, jistý výsledek alternativního hlasování, zajištěné financování rekonstrukce ani porušení totožného slibu z roku 2022. Výtka nesmí být rozšířena na celou bytovou výstavbu; karta i detail zobrazují její rozsah. Dnešní politiku lze legitimně změnit a podpora omezení privatizace v roce 2026 je uvedena jako protidůkaz.

105 použitých pramenů: doplněn původní materiál s přípravou prodeje a tabulkou rady (5. 3. 2025), doklad uskutečnění prodeje (příjem kupní ceny 5. 6. 2025), členství a gesce. Tabulka na PDF s. 7 byla ověřena i vizuálně: Podivinská má pomlčky, proto jí nepřipisujeme hlas rady; její hlas pro je doložen až v ZMB 25. 3. 2025. Oba Petrové Bořečtí mají odlišné identifikátory. Materiál dokládá rovněž stav domů a ekonomické důvody prodeje; navržený převod výnosu do bytového fondu není bez usnesení vydáván za schválený.

U všech kandidátek odlišujeme kontinuitu stran, osobní funkce, tehdejší opozici a jinou veřejnou praxi. Přehled není úplný historický audit všech kandidátů ani všech neuskutečněných opatření. Funkce sama automaticky kategorii nemění. Build odmítne výtku bez osob, období, pravomoci, příležitosti, výsledku, protidůkazů, vymezeného rozsahu a pramenů.

Redakční úprava 24. 9. 2026: štítek `bez_opory` se nyní zobrazuje jako **Jen kydy!**. Doplněna vysvětlení projektů, zkratek a souvislostí hlasování se sliby, zejména prodeje dvou prázdných městských bytových domů Dornych 29 a 31 developerovi. Kategorie, osobní hlasy a datum věcného ověření se nemění. `copy_updated` a historie změn odlišují úpravu textu od aktualizace důkazů. Archivované dokumenty se nepřepisují.
