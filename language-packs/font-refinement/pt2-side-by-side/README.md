# Dvě varianty současně v PT2

`start_comparison.py` otevře dva samostatné emulátory vedle sebe. Vlevo **PT2 - 1 Manualni upravy**, vpravo **PT2 - 2 Generovano z TTF**. Obě okna začínají na Droid Serif 28 Bold, vzorek 1. Pravá šipka v každém okně přepne na Roboto Condensed 21; šipky nahoru/dolů mění vzorek. Okna se ovládají nezávisle, pro srovnání je nutné nastavit stejný font a vzorek v obou.

Každá varianta má vlastní kopii již ověřeného testovacího firmwaru a flash. Ruční varianta používá porty 12544/12545 a monitor v `cmake-build-matrix/qemu_emery-normal/qemu-mon.sock`; generovaná varianta porty 12644/12645 a monitor `generated/qemu-mon.sock` v této složce. Předchozí samostatný testovací emulátor byl ukončen. Produkční zdroje ani jazykový balíček se nemění.
