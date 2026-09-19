# Kampaně 2026: datový slovník a orientace

Uzávěrka kampaní 19. 9. 2026, registr ČSÚ 15. 9. 2026, osobní hlasování do 23. 6. 2026. Pouze celoměstská úroveň. [Interaktivní přehled](../kampane-2026/index.html) · [Analýza a omezení](../analyzy/kampane_2026.html).

| Soubor | Jeden řádek představuje | Důležitá pole |
| --- | --- | --- |
| kandidati_2026_propojeni.csv | Kandidáta/ku registrovanou pro město Brno; 828 řádků | kandidat_id, cislo_listiny, poradi, jmeno, osoba_id, mandat_2022_2026, soucasny_zastupitel, metoda_spojeni |
| zastupitele_bez_kandidatury_2026.csv | Jednoho z 17 držitelů mandátu v období, kteří na listinách 2026 nejsou | Původní osoba_id; počet zahrnuje bývalé i současné zastupitele |
| kampane_2026_strany.csv | Jednu ze 16 letošních listin | Oficiální i zkrácený název, lídr, počty propojených lidí, dostupnost programu, zdroj_ids |
| kampane_2026_tvrzeni.csv | Jedno ze 47 vybraných tvrzení kampaní | Parafráze, lokator v prameni, zdroj_id, hlasovani_ids, vztah_k_hlasovani, poznamka, typ_zdroje |
| kampane_2026_vybrana_hlasovani.csv | Jeden z 30 protokolů s posouzeným kontextem | vyznam_ano, mez_interpretace, zapis_zdroj_id, zapis_pdf_strana (fyzická strana PDF, kde je výsledek; rozprava může začínat dříve) |
| kampane_2026_hlasy_kandidatu.csv | Jeden kandidát × jedno použitelné historické hlasování | 124 395 řádků; původní hlas a klub z protokolu doplněný o listinu a pořadí 2026 |
| kampane_2026_agregace_hlasovani.csv | Jeden protokol × jedna letošní listina | 52 080 řádků; ano, ne, zdrzel_se, nehlasoval, nepritomen, bez_mandatu; součet je kandidatu_celkem |
| kampane_2026_zdroje.csv | Jednu dohledanou adresu v rešerši kampaní | 69 řádků; URL, místní originál, text, datum stažení UTC, otisk SHA-256 a upozornění na starý či nečitelný obsah |
| kampane_2026_shrnuti.json | Souhrn celé agregace | Počty a tři různá data uzávěrky |
| csu_kvrk_brno_2026.csv / csu_kvros_brno_2026.csv | Původní řádek otevřeného registru ČSÚ pro Brno | Původní kódy; význam sloupců v připojených csu_schema_*_2026.json |

Názvy souborů bez přípony odpovídají tabulkám v archiv.sqlite. CSV: UTF-8 s BOM, oddělovač čárka. Prázdné osoba_id znamená, že nebyla nalezena totožná osoba mezi 61 držiteli mandátu končícího období. Neznamená absenci zkušenosti ze starších období nebo jiné veřejné funkce. Kandidátka není totéž co politický klub ani stranické členství.

Klíče: zdroj_id → zdroje.id; hlasovani_id → hlasovani.hlasovani_id; osoba_id → osoby.osoba_id; kandidat_id → kandidati_2026_propojeni.kandidat_id. Více zdrojů a hlasování v jedné buňce je odděleno středníkem. Číslo listiny má platnost pouze pro volby 2026.

Bez mandátu zahrnuje nové kandidáty i lidi, kteří v konkrétní den ještě nenastoupili nebo už odešli. Nepřítomen je naproti tomu stav osoby uvedené v tehdejším 55členném protokolu. Nehlasoval znamená přítomnost bez zaznamenaného hlasu; nelze jej zaměňovat se zdržením ani s nepřítomností. Sloupec primy_doklad_minuleho_hlasu v tabulce tvrzení říká, zda jsou k tvrzení připojeny protokoly a listina má propojené mandáty; neříká, že hlas dokazuje pravdivost tvrzení. Rozhodující je vztah_k_hlasovani a poznamka.

Všechny tabulky jsou v SQLite uloženy jako TEXT pro zachování původních hodnot. Pro součty použijte CAST(ano AS INTEGER) apod. Seznam všech 3 255 protokolů má UI v místním data.js; do DOM se při obecné volbě zobrazuje prvních 300 výsledků hledání, proto je možné dotaz dále zpřesnit. Úplné CSV nemá toto zobrazovací omezení.
