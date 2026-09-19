# DNS pro kydy.cz

Kontrola 19. 9. 2026: DNS u WEDOS / VEDOS. kydy.cz a www.kydy.cz mají A 89.221.222.140. GitHub už přesměrovává mrmartin.github.io/kydy na kydy.cz; zbývá DNS a HTTPS.

V zákaznické administraci: DNS → kydy.cz → DNS záznamy.

1. Odstranit nebo nahradit původní A záznam pro hlavní doménu a pro www s hodnotou 89.221.222.140.
2. Nastavit následující záznamy. Pro hlavní doménu je ve WEDOS / VEDOS Název prázdný; nezadávat doslova @.

| Typ | Název | Data |
| --- | --- | --- |
| A | prázdné | 185.199.108.153 |
| A | prázdné | 185.199.109.153 |
| A | prázdné | 185.199.110.153 |
| A | prázdné | 185.199.111.153 |
| CNAME | www | mrmartin.github.io |

3. TTL ponechat výchozí. Po jednotlivém uložení záznamů použít **Aplikovat změny**. MX a ostatní poštovní záznamy ponechat.
4. V https://github.com/mrmartin/kydy/settings/pages počkat na úspěšnou kontrolu DNS, případně použít Check again. Jakmile je dostupné **Enforce HTTPS**, zapnout.

CNAME neobsahuje https:// ani /kydy. Nameservery není třeba měnit. GitHub při správně nastaveném www přesměruje www.kydy.cz na hlavní kydy.cz. Propagace DNS a certifikát mohou trvat až 24 hodin.

[GitHub: oficiální IP a vlastní doména](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) · [VEDOS: DNS manuál](https://kb.vedos.cz/dns-manual/).
