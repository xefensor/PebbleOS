# Tři verze pro FontForge

Každý soubor a jeho rodina mají jednoznačné označení:

- `1_REPO`: původní PBF z Git HEAD; u Robota původní výstup firmware generátoru.
- `2_PREDLOHA`: rasterizovaná předloha při velikosti odpovídající galerii.
- `3_NASE`: náš poslední opravený ruční návrh.

Úplné trojice: Gothic 14, 14 Bold, 18, 18 Bold, Bitham 30 Black, 42 Bold, 42 Light, Droid Serif 28 Bold a Roboto Condensed 21. Gothic 24/24 Bold/28/28 Bold mají pouze repo a naši verzi; nemáme pro ně přímou online referenci.

Bitham používá referenci Gotham ScreenSmart, nikoli ověřenou totožnou historickou verzi. Droid Serif a Roboto používají projektové TTF; nejde o nově stažené aktuální online fonty. U Droid Serif `1_REPO` znamená starší PBF uložený v repozitáři, nikoli současný TTF build. Reference obsahuje dostupné znaky srovnávaných PBF. Chybějící znaky nejsou nahrazované jiným fontem. Cesty, revize a hashe jsou v sources.json.

## Jak porovnávat

Otevři přes File → Open stejný font ze všech tří složek. Rozlišuj okna podle přípon `1_REPO`, `2_PREDLOHA`, `3_NASE`. V každém okně dvojklikni na stejný znak (například č) a nastav stejné zvětšení bitmap. Okna editorů můžeš umístit vedle sebe; jejich posouvání není automaticky synchronizované.

Neupravuj referenční sady 1_REPO a 2_PREDLOHA. Změny dělej v 3_NASE a ukládej přes Save As do nového SFD souboru. Tyto soubory jsou oddělené od dosavadních pracovních BDF o úroveň výš. Náhledová velikost strike může zahrnovat místo pod základní linkou; pixely nebyly škálované.

Všech 35 souborů bylo otevřeno a exportováno FontForge; kontrola potvrdila stejnou znakovou sadu, pixely, polohy a rozestupy. Zpětný import ručních úprav do PBF zatím není součástí tohoto postupu.
