# Podklady pro „Slibují to. Udělají to?“

`curation.py` obsahuje česká redakční posouzení, nikoli automaticky odhadnuté pravděpodobnosti. `assessment.json` je úplný přenositelný vstup veřejného generátoru: kampaně, sliby, konkrétní osobní hlasy, prameny a meze závěrů. Připravuje jej `scripts/prepare_assessment.py` z tohoto výběru a místního archivu. Web lze pak znovu sestavit pouze z repozitáře pomocí `python3 scripts/build_assessment.py`.

Výběr vychází z aktuálních programových kapitol a zveřejněných priorit, ne z dostupnosti hlasování. Není statistickým měřením četnosti reklam. Související části jednoho slibu tvoří jednu jednotku; nic se nedoplňuje do neúplných programů. První vydání má společný stav ověření 20. 9. 2026; programové snímky mají vlastní data získání. Hlasovací řada končí 23. 6. 2026. Zářijové předložené materiály jsou samostatné důkazy přípravy, nikoliv náhrada dosud neověřených osobních hlasů.

Hodnocení je úsudek založený na zdrojích. Absence mandátu, opoziční neúspěch, změna postoje ani chybějící doklad nejsou důkaz lži. Nikomu nepřipisujeme úmysl. Chybějící historie snižuje možnost spolehlivě dát ANO; sama nestačí pro NE.

Při aktualizaci nejprve archivovat nové zdroje, ověřit význam rozhodnutí a protidůkazy, poté změnit posouzení a přidat záznam do historie. Staré znění zůstává v historii Gitu. Není dovoleno záměrně vyrábět rozdílné barvy, jestliže podklady opravňují pouze MOŽNÁ.

První vydání: 57 slibů, 95 použitých pramenů. Mezi zjištěními jsou opravený součet neobsazených bytů, smlouva na Kamenný vrch a potenciální závazek města splácet při neobsazenosti, už podepsaná smlouva SAKO, skutečný postup stavby JKC a navzájem nekompatibilní koaliční vyjádření. Všechna prognostická hodnocení zatím zůstávají MOŽNÁ: nepředstíráme uzavřený investiční audit ani volební model. Štítky doloženého jednání umožňují rozeznat konkrétní práci od samotného příslibu i při stejné souhrnné barvě.

Reprodukce veřejných stránek potřebuje pouze standardní Python. Příprava nového podkladu potřebuje místní původní archiv; stažení zdrojů bylo provedeno jeho existujícím nástrojem `skripty/archiv.py` a zůstává zapsáno v `data/zdroje.jsonl`. Zahrnuty jsou originály i texty. Veřejný podklad nepřepisuje původní hlasovací soubor ani předstíraně nedoplňuje zářijové hlasy.
