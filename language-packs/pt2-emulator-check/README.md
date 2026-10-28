# Kontrola českého balíčku v PT2 emulátoru

> Doplnění po úpravě diakritiky: tato kontrola prokázala zobrazení českých textů, ale ne to, že každý znak pochází z fontu balíčku. Firmware dává u existujících latinských znaků přednost vestavěným fontům. Viz [nové zjištění a porovnání fontů](../font-refinement/README.md).

Datum: 2026-09-08. Výsledek: na níže uvedených obrazovkách funguje čeština z instalovaného balíčku; při vizuální kontrole nebyla nalezena rozbitá česká diakritika ani zjevné nechtěné oříznutí textu. Nejde o důkaz správnosti všech 774 překladových záznamů a všech stavů firmwaru.

## Prostředí a instalace

- QEMU `pebble-emery` (PT2), SDK 0.1.8.
- Build `cmake-build-matrix/qemu_emery-normal`, aktuální pracovní změny nad HEAD `9399f564f`; firmware se hlásí jako `v4.37.0-dirty`.
- Sestavení cílů `qemu_image_micro` a `qemu_image_spi` proběhlo úspěšně. Viz `build.log`.
- Tehdy testovaný balíček: `../font-refinement/cs_CZ-before.pbl`, 222 549 bajtů (původně pojmenovaný `cs_CZ-with-fonts.pbl`).
- SHA-256: `27f98dfe320a5e8b1596c2e1a72dd0beed404abcb44f30ffb14e2a4ec482cfc8`.
- Instalace standardním PutBytes přenosem souboru `lang`, včetně fontů; bez zabudování češtiny do firmwarových resources.
- Po instalaci i po resetu emulátoru vrací WatchVersion jazyk `cs_CZ`, verzi katalogu `36`. Viz `restart-info.txt` a `restart-launcher.png`.
- Screenshoty byly pořízeny příkazem `pbl screenshot` a vizuálně prohlédnuty. `index.html` je místní galerie; otevřete ji v prohlížeči.

## Ověřené obrazovky

- Nabídka aplikací: Nastavení, Hudba, Oznámení, Budíky, Ciferníky, Trénink, Zdraví, Časová osa.
- Nastavení: hlavní seznam, Bluetooth, oznámení, displej včetně `Jazyk / Čeština`, zdraví, aplikace na pozadí a systémové informace.
- Počasí: hlavní grafická předpověď, vícedenní textová předpověď, DNES/ZÍTRA/PÁTEK a další zobrazené dny, Slabý déšť/Polojasno/Déšť se sněhem, výstraha, věty o větru a srážkách, směry SV/V/J, UV index, Aktualizováno, Západ slunce, DÉŠŤ, výběr města a uložená místa.
- Počasí používá syntetická data pro `Praha – Žižkov`, doručená standardním BlobDB protokolem jako záznam v4.5 a preference `weatherApp`. Oba zápisy potvrdil firmware úspěchem. Script `weather-fixture.py` dokumentuje přesný formát; není zdrojem reálné meteorologické předpovědi.
- Oznámení: prázdný seznam `Žádná oznámení`.
- Budíky: úvodní dialog chytrého budíku, založení budíku a výběr Jednou/Každý den/Pracovní dny/Víkendy/Vlastní.
- Zdraví: výzva při vypnutém sledování, zapnutí sledování v nastavení, nový přeložený úvodní dialog `Psst! Chcete chytré tipy…`, hlavní karta a spánková karta bez dat.
- Trénink: výzva při vypnutém sledování, pokyn k nasazení hodinek, Běh, aktivní trénink (TEP/TRVÁNÍ), pozastavení, PRŮM. TEMPO a potvrzení `Ukončit trénink?`. Po potvrzení ukončení se aplikace vrátila na výchozí/souhrnnou obrazovku s českým názvem `Běh`; podrobné statistiky delšího tréninku nejsou pokryté.
- Hudba byla otevřena, ale bez připojeného přehrávače neměla textová metadata k ověření.
- Po restartu zůstaly český katalog a zobrazení české nabídky funkční.

## Omezení

- Testována je tato konfigurace PT2 a aktuální upravený firmware, nikoliv původní firmware 4.36.2. Uživatelův dřívější fyzický test diakritiky na PT2/4.36.2 se týkal dřívějšího balíčku.
- Nejsou pokryty všechny dialogy, všech 28 výstrah počasí, všechny délky textů ani všechny fontové sloty. Neověřoval se nouzový text prázdné jednotlivé notifikace, Ping, automatické rozpoznání cvičení ani všechny množné tvary času přímo v UI.
- Barevné motivy v této konfiguraci nejsou zapnuté (`CONFIG_THEMING`); obrazovka Aplikace na pozadí je v `background-settings.png`.
- Není tím ověřena lokalizace samostatně instalovaných aplikací z obchodu.
- Testovací předpověď používá jednotky aktuálně nastavené v emulátoru (míle/mph), čas je ve 12hodinovém formátu. Jazykový balíček sám tyto preference nepřepíná.
- Zdrojový kód nebyl během této kontroly měněn. Změněn byl stav vlastního emulátoru a přidány tyto testovací podklady.
