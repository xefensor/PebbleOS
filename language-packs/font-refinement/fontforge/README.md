# Ruční audit ve FontForge

Pracovní BDF kopie 13 fontů z `../online-comparison/candidates/`. Obsahují ručně zvolenou a opravenou variantu; Roboto a Droid Serif zde nejsou nově generované TTF varianty. Otevření a export všech 13 fontů přes instalovaný FontForge bylo ověřeno: stejná znaková sada, všechny pixely na stejných pozicích a nezměněné DWIDTH.

1. File → Open → GOTHIC_14.bdf.
2. V nabídce View vyber existující bitmapový řez, pokud není zvolený. Dvojklik na znak otevře bitmapový editor. Pokud se otevře editor křivek, zavři jej a použij Window → Open Bitmap.
3. View → Bitmap Magnification mění zvětšení přehledu; nevytvářej nový strike a nepoužívej Recalculate Bitmaps. Tužka v bitmapovém editoru zapíná/vypíná pixely.
4. Porovnávej A/Á, C/Č, E/Ě, d/ď a t/ť. Sleduj i skutečnou velikost a rozestupy ve slovech.
5. File → Save As uloží pracovní projekt jako například GOTHIC_14-audit.sfd. Pro předání bitmap použij File → Generate Fonts, bez obrysového fontu (No Outline Font), bitmapový formát BDF a nové jméno GOTHIC_14-audit.bdf.

Výška bitmapového řezu v editoru zahrnuje prostor pod základní linkou, například Gothic 14 má BDF strike 16 px. Pixely písmen nejsou zvětšené; jméno souboru zachovává původní označení fontu Pebble. Souřadnice se převádějí podle baseline v sources.json.

Exportér odmítne přepsat existující BDF, aby nezničil ruční práci. Upravené fonty zatím nevracej přímo do firmware: zpětný import do PBF je potřeba doplnit a ověřit. Ověřený je nyní převod PBF → BDF → FontForge → BDF bez editace.

## Porovnání tří verzí

Pro audit repo / předloha / náš návrh používej [samostatné sady v comparison/](comparison/README.md). Původní pracovní soubory v této složce nebyly změněny.
