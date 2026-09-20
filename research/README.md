# Podklady pro „Slibují to. Udělají to?“

`curation.py` obsahuje česká redakční posouzení, nikoli automaticky odhadnuté pravděpodobnosti. `assessment.json` je úplný přenositelný vstup veřejného generátoru: kampaně, sliby, konkrétní osobní hlasy, prameny a meze závěrů. Připravuje jej `scripts/prepare_assessment.py` z tohoto výběru a místního archivu. Web lze pak znovu sestavit pouze z repozitáře pomocí `python3 scripts/build_assessment.py`.

Výběr vychází z aktuálních programových kapitol a zveřejněných priorit, ne z dostupnosti hlasování. Není statistickým měřením četnosti reklam. Související části jednoho slibu tvoří jednu jednotku; nic se nedoplňuje do neúplných programů. První vydání má společný stav ověření 20. 9. 2026; programové snímky mají vlastní data získání. Hlasovací řada končí 23. 6. 2026. Zářijové předložené materiály jsou samostatné důkazy přípravy, nikoliv náhrada dosud neověřených osobních hlasů.

Hodnocení je úsudek založený na zdrojích. Absence mandátu, opoziční neúspěch, změna postoje ani chybějící doklad nejsou důkaz lži. Nikomu nepřipisujeme úmysl. Chybějící historie omezuje posouzení praxe; sama nedokazuje překážku ani neurčuje hodnocení nového kandidáta.

Při aktualizaci nejprve archivovat nové zdroje, ověřit význam rozhodnutí a protidůkazy, poté změnit posouzení a přidat záznam do historie. Staré znění zůstává v historii Gitu. Kategorie se neurčují podle požadovaného rozložení barev. Každý slib musí mít výslovné redakční zařazení; neznámé nebo chybějící zařazení build odmítne.

Metodika 2 (20. 9. 2026): 57 slibů, 95 použitých pramenů. Otázka „Jakou oporu má tento slib?“ nahrazuje původní prognózu splnění ANO/MOŽNÁ/NE. `evidence_status` má čtyři možné hodnoty: `podlozeno` (Podloženo činy), `podminene` (Podmíněně proveditelné), `rozpor` (Zásadní rozpor nebo překážka), `bez_opory` (Zatím jen slib). Každý z 57 záznamů má explicitní zařazení a důvod v `EVIDENCE_ASSESSMENTS`; žádný výchozí stav. Schéma JSON má verzi 2, veřejný export přidává slovník kategorií a `evidence_counts` kampaní. CSV má samostatný kód a český popis opory. Původní `verdict` je odstraněn, aby nevydával nové kategorie za předpověď.

Kampaň nemá většinový verdikt. Karta ukazuje kategorii u každého slibu a skladbu všech vybraných slibů, takže dílčí rozpor ani chybějící podklady nezmizí v průměru. Počet slibů není skóre kvality kampaně a každý výběr má jiný rozsah. Volební a koaliční podmínky zůstávají v detailu, ale obecná nejistota voleb nepřebarvuje doložené činy. Přesné pravidlo a historie změny jsou v `site/metodika.html`.

Zelená může označovat doložený osobní krok i realizaci městského projektu. Důvod musí výslovně odlišit jejich původ a fázi: smlouva SAKO není osobní zásluha každé kandidátky a kontrolní návrh není dokončený audit. U složených slibů podstatná mezera v jiné části brání zelenému hodnocení celého balíku. Červená vyžaduje zásadní přetrvávající překážku či rozpor; v tomto vydání pro ni nemáme dostatečný podklad. Zatím jen slib označuje mezeru v rešerši, ne lež.

Přechod používá stejné archivované zdroje; změnila se otázka a interpretace, nikoli doložené výsledky politiků. Staré prognózy jsou dostupné v historii Gitu. Nebyl doplněn chybějící investiční audit ani volební model.

Reprodukce veřejných stránek potřebuje pouze standardní Python. Příprava nového podkladu potřebuje místní původní archiv; stažení zdrojů bylo provedeno jeho existujícím nástrojem `skripty/archiv.py` a zůstává zapsáno v `data/zdroje.jsonl`. Zahrnuty jsou originály i texty. Veřejný podklad nepřepisuje původní hlasovací soubor ani předstíraně nedoplňuje zářijové hlasy.
