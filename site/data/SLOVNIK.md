# Datový slovník

| Soubor | Obsah a význam |
| --- | --- |
| osoby.csv | 61 držitelů mandátu, původní listina a hlasy, nástup a konec, současná funkce, klub a prameny |
| zmeny_mandatu.csv | Šest výměn, osoba před a po, dny zániku/nástupu, zdroj |
| soucasni_zastupitele.csv | Snímek 55 položek oficiálního městského seznamu |
| clenstvi_organy.csv | Nalezená aktuální členství zastupitelů ve výborech a komisích; nejde o úplnou historickou tabulku |
| hlasovani.csv | Jeden protokol na řádek: datum, předmět, agregace, výsledek, zdroj, platnost a možnost statistického použití |
| hlasy_jmenovite.csv | Jeden řádek osoba × hlasování. Volba Ano/Ne/Zdržel se/Nehlasoval/nepřít. dle protokolu; volba_original uchovává VK. Pro statistiky filtrovat pouzitelne_pro_statistiky=ano; důvod výjimky je v omezeni_protokolu |
| statistiky_hlasovani.csv | Osobní souhrny; bez neplatných pokusů a zvláštního Z9/11 č. 12 |
| osoby_pasaze_zapisu.csv | Pomocné výskyty jmen v pasážích, strana PDF; priorita_rejstriku je technické řazení, nikoli skóre osoby |
| vybrana_hlasovani*.csv | Kurátorský výběr 12 významných hlasování a jejich osobní rozpis |
| finance_srovnatelna_rada.csv | Stejný rozpočtový rozsah; tisíce Kč, plán a skutečnost odděleny |
| temata_bilance.csv | 26 ručně zpracovaných témat s milníkem, omezením závěru a prameny |
| programove_zavazky.csv | Všech 140 očíslovaných bodů společného programového prohlášení, vazba na posouzená témata |
| zasedani.csv, materialy_zmb_index.csv | Vazby zasedání → materiál → URL |
| projekty_index.csv, projekty_udalosti.csv | 31 projektů a jejich veřejně uvedená časová osa; jedna událost může patřit k více projektům |
| zdroje.csv, zdroje.jsonl | Poslední stav zdrojů, resp. historie pokusů; URL, datum stažení, cesta, velikost, SHA-256 |
| kontrola_*.csv, pokryti_zasedani.csv | Výsledky automatických kontrol a známé mezery |
| csu_kvrk_brno_2022.csv | 668 kandidátů; MANDAT=A znamená zvolen; PORADINAHR původní náhradnictví, nikoli doklad pozdějšího nástupu |
| csu_kvros_brno_2022.csv | 14 kandidátek; MAND_STR mandáty, PROCHLSTR přepočtené procento bez zaokrouhlení dle schématu ČSÚ |
| csu_kvrzcoco_brno_2022.csv | Územní pokrytí celoměstských voleb; řádky MČ nejsou jejich samostatná zastupitelstva |
| csu_schema_*.json | Původní schémata CSV z balíku ČSÚ |

Identifikátory dvou Bořeckých: petr-borecky = architekt, kandidátka ANO 2022; petr-borecky-1 = kandidátka Lidovci a Starostové. Karin Karasová, Karin Podivinská a Karin Podivinská Karasová mají společné osoba_id karin-podivinska-karasova.
