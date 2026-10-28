# Opravená diakritika v PT2 emulátoru

Opravené ť v Bitham 30 Black a Droid Serif 28 Bold: při oddělování bočního háčku se nyní zahazují malé oddělené zbytky příčky referenčního t. Zůstává jeden souvislý háček. Šířka znaku klesla z 25 na 16 px, respektive z 23 na 15 px. U Droid Serif zůstává oproti původním 11 px prostor potřebný pro boční háček.

Test používá qemu_emery (PT2), aplikaci Font Test a všech devět zvolených kandidátů přímo jako základní fontové resources. Tím se při vizuální kontrole obejde přednost původních vestavěných latinských znaků před jazykovým balíčkem. Nejde o test instalace balíčku do běžného firmwaru. Produkční balíček zůstává beze změny.

`embedded-fonts.json` dokládá přesnou binární shodu všech devíti testovacích resources s kandidáty. Zvlášť se přemapovává Droid Serif a Roboto, protože běžně vznikají z TTF. `build_preview.py` po sestavení vždy obnoví dočasně upravené zdrojové soubory. Testovací ELF a SPI flash jsou zkopírované sem.

## Ovládání

- Prostřední tlačítko / pravá šipka: další font.
- Horní / dolní tlačítko nebo šipky: předchozí / další textový vzorek.
- Levá šipka: návrat do nabídky.

Emulátor používá lokální porty 12444 a 12445 a monitor socket v `cmake-build-matrix/qemu_emery-normal/`. `start_preview.py` spouští samostatně uložený firmware bez nového sestavování. Nespouštět druhou instanci současně. Font Test lze otevřít z nabídky nebo konzolovým příkazem `app launch -100`.

[Snímky všech devíti fontů](index.html) byly pořízeny příkazem `pbl screenshot` a zobrazují opravený návrh v běžícím emulátoru. Samotná hlavička snímku určuje zvolený font. Font Test nabízí sedm vzorků; snímky dokumentují první vzorek obsahující tťa, ďá ťá a žluťoučký.
