# kydy.cz – Brno před komunálními volbami 2026

Repozitář: https://github.com/mrmartin/kydy. Původní projekt je zachován ve větvi [archive/pred-brno-2026-09-19](https://github.com/mrmartin/kydy/tree/archive/pred-brno-2026-09-19), commit `f18cc08d689804767e92ad85e8c1ee84835b6aba`. Historie není přepsaná.

Připravený statický web je v `site/`. Jeho velikost je přibližně 561 MiB. Úplný původní archiv má asi 16 GB a je uložen odděleně; soubory pro GitHub Releases připravuje `scripts/package_archive.py`. Repozitář neobsahuje přístupové údaje a workflow nepotřebuje vlastní tajné klíče.

## Co je potřeba od vlastníka

1. Cílový repozitář je veřejný `mrmartin/kydy`; GitHub Pages lze použít i na GitHub Free.
2. V místním terminálu provést `gh auth login --hostname github.com --web --git-protocol https`. Je-li již přihlášen jiný účet, vybrat správný. Token se neposílá do konverzace. Pro nasazení je potřeba přístup k vytvoření nebo správě repozitáře a jeho nastavení Pages.
3. Mít přístup k DNS kydy.cz. Kontrola 19. 9. 2026 zjistila autoritativní servery `ns1.ename.net` a `ns2.ename.net`; apex i www nyní odkazují na `cs.ename.net`.

## Postup nasazení po přihlášení

Záměr: veřejný repozitář pod potvrzeným vlastníkem. Repozitář se znovu používá, historie zůstává zachována. DNS se těmito skripty nemění.

- Publikační web je uložen ve větvi `main`; původní projekt je zachován v archivní větvi uvedené nahoře.
- V repozitáři **Settings → Pages → Build and deployment → Source: GitHub Actions**. Pro Actions musí být povoleno spouštění workflow. Je dodáno `.github/workflows/pages.yml`, které publikuje výhradně adresář `site/`.
- Ve stejném nastavení Pages uložit **Custom domain: kydy.cz**. Soubor `site/CNAME` je přiložen pro přenositelnost; u nasazení Actions rozhoduje nastavení repozitáře, samotný soubor doménu nenastaví.
- Teprve po připojení domény v GitHub Pages změnit DNS podle následující tabulky.
- Po úspěšné kontrole DNS a vystavení certifikátu zapnout **Enforce HTTPS**. Propagace DNS a dostupnost certifikátu mohou trvat až 24 hodin.

| Typ | Název | Hodnota |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | mrmartin.github.io |

`VLASTNIK` je GitHub uživatel nebo organizace, nikoliv název repozitáře. TTL může zůstat výchozí. Nahradit současné parkovací CNAME pro `@` a `www`; ponechat záznamy pro e-mail a jiné služby. Případné původní AAAA pro tyto názvy musí odpovídat novému hostingu; při dnešní kontrole nebyly nalezeny samostatné adresy AAAA. IPv6 není pro tento postup vyžadováno.

Doporučené ověření vlastnictví: v **nastavení účtu/organizace → Pages → Add a domain** přidat kydy.cz, vytvořit přesný TXT záznam vygenerovaný GitHubem a stisknout Verify. Hodnotu nelze připravit předem bez cílového účtu. TXT ponechat i po ověření.

## Úplný archiv ke stažení

Připravené soubory v `release-assets/` jsou z Gitu vyloučeny. Každý je menší než 2 GiB; odpovídají limitu jednotlivých příloh GitHub Releases. Databáze je také samostatně v `archiv.sqlite.gz`.

Nejprve nahrát soubory do vydání `archiv-2026-09-19` cílového repozitáře, včetně `manifest.json` a `SHA256SUMS`. Balíky `archiv-XX.tar.gz` jsou samostatné a rozbalují se do stejného nadřazeného adresáře; všechny společně obnoví původní adresář `brno-volby-2026/` včetně databáze. Není nutné je binárně spojovat.

Po nahrání vydání aktualizovat veřejné odkazy příkazem:

```sh
python3 scripts/build_site.py --repository mrmartin/kydy
python3 scripts/check_site.py
```

Výchozí build bez `--repository` nezobrazuje neexistující odkazy ke stažení. Originály dokumentů na webu odkazují přímo k vydavatelům, všechny dostupné textové kopie jsou součástí webu. CSV manifest zachovává místní cesty do úplného archivu. Na původní dokumenty se vztahují podmínky jejich vydavatelů.

## Obnova a kontrola

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
python3 -m http.server 8000 --directory site
```

Pak otevřít http://localhost:8000. Build vychází ze sousedního `../brno-volby-2026/`, případně použít `--archive /cesta/k/archivu`. V GitHub Actions se archiv znovu nestahuje: publikuje se již připravená statická verze. Aktualizace analýzy se provádí v původním archivu a znovu vygeneruje tímto buildem.

Kontrola ověřuje limit velikosti, všechny místní HTML odkazy a datové vazby interaktivního srovnání. Interaktivní filtry byly navíc ověřeny v jsdom včetně přesměrování na původní vydavatele.

Oficiální dokumentace: [limity Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [vlastní doména a DNS](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site), [ověření domény](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages), [limity Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).

Pro nahrání připravených balíků po přihlášení: `python3 scripts/publish_release.py --assets ../web-github/release-assets`. Skript ověří otisky, nahraje draft a zveřejní ho až po úspěšném přenosu všech souborů.
