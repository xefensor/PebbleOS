# Úprava české diakritiky

Druhá úprava proporcí všech 15 textových fontů českého balíčku. Proti předchozímu návrhu s dlouhými čárkami se změnilo 278 znaků; proti původnímu balíčku 353. Galerie `index.html` porovnává předchozí návrh s aktuální vyváženou verzí a umožňuje zvětšení 1× až 6×. `balanced-native.png` ukazuje všechny fonty ve skutečné pixelové velikosti.

## Výsledek a důležitý limit

Nový balíček je `../cs_CZ-refined-fonts.pbl` (221 525 bajtů). Stejná verze je i v `../cs_CZ-with-fonts.pbl`. SHA-256 je v `package-sha256.txt`. Předchozí návrh s dlouhými čárkami je zachován jako `cs_CZ-long-accents.pbl`; úplně původní balíček jako `cs_CZ-before.pbl`.

**Balíček sám nevynutí použití nových tvarů u znaků, které již obsahuje vestavěný font.** Aktuální firmware v `src/fw/applib/graphics/text_resources.c` volí pro latinské znaky nejdříve základní font. `codepoint_is_latin()` zahrnuje rozsah do U+02AF, tedy všechny české znaky. Jazykové rozšíření se u nich zkouší až při chybějícím znaku v základním fontu. Podrobná tabulka skutečně sestavených fontů je v `firmware-font-routing.json`.

Například Gothic 14–28 a Gothic 36 Bold již obsahují všechny české znaky. Při předchozí revizi byly snímky nabídky aplikací a nastavení po instalaci balíčku pixelově shodné s původní kontrolou. Instalace prošla, ale tyto obrazovky používají původní bitmapy. Chování bylo doloženo na aktuálním PT2 firmwaru `v4.37.0-dirty`, HEAD `9399f564f` s pracovními změnami. Tuto novou verzi balíčku jsme fyzicky netestovali na původním firmwaru 4.36.2; nelze tvrdit, že na něm přepíše vestavěné znaky.

Pro jednotné použití nového vzhledu je nutná změna priority fontů ve firmwaru. Tato změna zatím není provedena; uživatel nyní požaduje nejprve doladit podobu fontů. Předchozí test češtiny potvrzoval čitelnost textů, nikoliv původ každého zobrazeného znaku ve fontu balíčku.

## Co se změnilo

- Čárky a háčky mají v každém fontu shodnou výšku nebo rozdíl nejvýše jeden pixel. Velikost byla posouzena také podle šířky a plochy tahu; háček má dvě ramena, takže nemá mít stejný obdélník jako čárka. U drobných Gothic fontů se značky vejdou do 2–3 řádků pixelů.
- Příliš dlouhé čárky z předchozího návrhu byly zkráceny; tam, kde byly háčky příliš drobné či tenké, byly upraveny také ony. Gothic používá pravidelné bitmapové tahy, Bitham hmotnost odpovídající řezu a Droid Serif čárku s proměnlivou tloušťkou. Spodní konec čárky zůstává nad optickým středem horní části písmene a tah stoupá doprava. Od těla značky odděluje jeden prázdný řádek pixelů.
- Boční háčky u malých ď/ť mají kratší, kompaktnější klínový tvar. Rozestupy těchto znaků se přizpůsobily novému obrysu; ostatní posuny šířky jsou evidované v `glyph-validation.json`.
- Těla českých písmen byla zachována. Všechny ostatní znaky mají nezměněné binární záznamy; kroužky Ů/ů jsou rovněž beze změny.
- Roboto Condensed 21 je nově v `resources/normal/base/lang/cs_CZ/pbf/ROBOTO_CONDENSED_21.pbf`, aby jemné úpravy nezmizely opětovnou rasterizací TTF. `lang_map.json` odkazuje na tento PBF. Jeho výchozí verze pochází z dosavadního balíčku, generovaného z projektového `Roboto-Condensed.ttf`.
- Gothic 09 nemá v jazykovém balíčku vlastní rozšiřující slot. Zde není upravován. Prázdné číselné fontové sloty neobsahují česká písmena.

## Předlohy

- [Pebble System Fonts](https://developer.rebble.io/guides/app-resources/system-fonts/) identifikuje Raster Gothic, Gotham/Bitham a Droid Serif jako předlohy systémových fontů.
- [Raster Gothic od Marka Simonsona](https://www.marksimonson.com/fonts/view/raster-gothic/) a jeho [vzorník Eighteen Regular](https://www.marksimonson.com/fonts/view/raster-gothic/eighteen-regular/) dokumentují původní bitmapový charakter a samostatné velikosti.
- [Gotham, Hoefler&Co.](https://www.typography.com/fonts/gotham/styles) je předloha Bithamu podle dokumentace Pebble.
- [Roboto, zdrojový projekt Google Fonts](https://github.com/googlefonts/roboto-2). Pro konkrétní místní předlohy jsou v repozitáři `Roboto-Condensed.ttf` a `DroidSerif-Bold.ttf`.
- [Google Fonts: Diacritic marks](https://googlefonts.github.io/gf-guide/diacritics.html) popisuje sladění velikosti a tloušťky diakritiky s písmem, optické ukotvení a zvláštní úzký boční háček u ď/ť.

Jde o ručně specifikované bitmapové úpravy stávajících PBF; nejde o převzetí nových fontových souborů z komerčních webů.

## Kontrola a reprodukce

- 15 PBF se dekóduje samostatným projektovým nástrojem `pbf_extract.py`.
- Binární porovnání potvrzuje nezměněné nečeské znaky a zachování těl písmen.
- Opakované použití receptu již nic nemění (idempotence).
- Kontrola balíčku ověřila CRC a přesnou shodu každého z 15 fontových slotů se zdrojovým PBF.
- Předchozí revize byla úspěšně nainstalována standardním PutBytes přenosem do PT2 emulátoru. Tato revize byla ověřena zobrazením všech 15 PBF ve skutečné velikosti a zvětšeně a binárními kontrolami; nová instalace do emulátoru se neprováděla, protože priorita vestavěných fontů zůstává nezměněná.
- Pixelové porovnání launcheru a nastavení odhalilo výše popsanou přednost základního fontu. Nejde proto o úspěšné vizuální ověření nového vzhledu na těchto obrazovkách.

`before/` obsahuje původní výchozí PBF, `previous/` předchozí návrh s dlouhými čárkami a `after/` výsledné PBF a jednotlivé PNG porovnání odpovídají konečné verzi. Pomocné skripty `font_work.py` a `refine_try.py` uchovávají pixelové vzory a způsob sestavení. Z kořene repozitáře lze náhledy a `after/` přegenerovat příkazem:

```sh
.venv/bin/python language-packs/font-refinement/refine_try.py
```

Script negeneruje zdrojové PBF z komerčních webů. Vychází z uchovaných `before/` souborů. Výsledky v `after/` je po kontrole nutné přenést do `resources/normal/base/lang/cs_CZ/pbf/` a sestavit balíček příkazem `pbl pack_lang --lang cs_CZ` s příslušným build adresářem.

## Porovnání s online předlohami

[Galerie online předloh](online-comparison/index.html) porovnává čtyři aktuální řezy Raster Gothic od autora s českými PBF a 13 systémových ukázek z dokumentace Pebble. Obsahuje metodiku, zdroje a omezení. Komerční soubory fontů nejsou součástí galerie ani balíčku; ukládají se pouze vykreslené vzorky. Tato kontrola nemění fonty. Generátor `compare_online.py --references ADRESAR` očekává lokálně stažené referenční TTF a PNG.

Galerie nyní obsahuje také české znaky všech pěti ostatních textových fontů: Bitham 30 Black, 42 Bold, 42 Light, Droid Serif 28 Bold a Roboto Condensed 21. Bitham se srovnává s veřejným Gotham **ScreenSmart** 1.301; nejde o potvrzení totožné historické předlohy. Droid Serif a Roboto používají projektové TTF (verze 1.00 a 3.008). Metadata, SHA-256 a zdroje jsou v `online-comparison/other-sources.json`. Velikosti se srovnávají podle výšky H; základní bitmapy se nedeformují.

Vizuální zjištění: Bitham Black/Bold má v našem návrhu příliš subtilní diakritiku vůči hmotnosti písmen, předloha používá plnější a plošší háčky. U Droid Serif jsou naše háčky drobnější než v projektové předloze. Roboto je proporcemi bližší. Jde o podklad k dalšímu ladění, nikoli o provedenou úpravu fontů.

Každá ukázka v online galerii nyní obsahuje tři řádky: předlohu, původní repo a současný český PBF. Původní PBF se čtou z Git HEAD; commit, cesty a kontrolní součty jsou v `online-comparison/original-sources.json`. Roboto se generuje ze vstupů shodných s HEAD a jeho výsledek byl ověřen proti sestavenému systémovému resource. Červené rámečky označují znaky chybějící v původním fontu, nikoli skutečný firmware fallback. Celkem bylo ověřeno 31 trojic (93 obrázků). Fonty a balíček zůstaly beze změny.

## Čtvrtá varianta podle výběru

Online galerie má nyní čtvrtý řádek „Nový návrh“. Gothic 14/14 Bold přebírají české znaky z HEAD, Gothic 18/18 Bold zůstávají beze změny. Bitham 30 Black používá diakritiku Gotham SSm Black s horizontálními tahy zúženými o jeden pixel, Bitham 42 Bold přebírá diakritiku SSm Bold. Bitham 42 Light zachovává všechny dostupné původní české znaky, doplňuje chybějící čárku podle původního Á a tenké háčky; dosavadní kroužky ponechává. Droid Serif a Roboto přebírají diakritiku projektových TTF. Těla písmen Pebble zůstávají zachována.

Návrh generuje `font_candidate.py` při spuštění `compare_online.py`; samostatné PBF jsou pouze v `online-comparison/candidates/`. Produkční zdrojové PBF ani instalační balíček se nemění. `candidate-validation.json` eviduje volby a počty změn. Ověřeno 31 čtveřic (124 obrázků), zachování nečeských znaků, přesná shoda vybraných znaků repo/naše a načtení všech kandidátů nezávislým PBF extraktorem. Fonty bez nového výběru zůstávají ve čtvrtém řádku shodné s třetím.

## Automatická generace TTF

`generated_ttf_preview.py` vytvoří v `generated-ttf/` samostatnou kopii seznamu znaků s 19 chybějícími českými znaky, vygeneruje Roboto Condensed 21 a Droid Serif 28 Bold skutečným firmware generátorem a porovná je s ručním návrhem. Veškeré dosavadní generované znaky zůstávají stejné. Velikost PBF naroste o 607 a 1191 bajtů (nejde o měření výsledného flash image). Droid Serif se od ručního návrhu liší i základními písmeny, protože ruční návrh používá starší PBF těla. Výsledky a kontrolní součty jsou v `generated-ttf/validation.json`; hlavní galerie obsahuje u těchto dvou fontů pátý řádek. Produkční seznam znaků, balíček a běžící emulátor se při této ukázce nemění.
