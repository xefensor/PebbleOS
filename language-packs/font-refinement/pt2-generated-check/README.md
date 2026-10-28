# PT2: skutečná generace TTF

Roboto Condensed 21 a Droid Serif 28 Bold jsou zde generované během firmware buildu z TTF a kopie seznamu znaků `../generated-ttf/basic_latin_codepoints.json`. `embedded-fonts.json` dokládá shodu obou výsledných resources s PBF z galerie. Ostatních sedm fontů zůstává z předchozího kandidátního náhledu.

Dočasně upravené zdroje byly po sestavení obnoveny. Běžný jazykový balíček se nemění. Samostatný ELF a flash image jsou uložené v této složce. `start_preview.py` spouští GUI QEMU; `capture_preview.py` otevře Font Test a pořídí snímky. Před opětovným spuštěním je nutné zavřít předchozí QEMU, protože používá stejné lokální porty 12444/12445 a monitor v `cmake-build-matrix/qemu_emery-normal`.

Ovládání: pravá šipka / prostřední tlačítko přepíná fonty, horní a dolní přepínají vzorky. Droid Serif je 8/9 a Roboto 9/9. Zkontrolované snímky ukazují vzorek s tťa / ďá ťá / žluťoučký i skupinu Aa Áá / Ee Éé Ěě / Ii Íí.
