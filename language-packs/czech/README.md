# Czech sideload pack

Install `../cs_CZ-with-fonts.pbl` using the companion app's language-pack
installation function. This is a local draft; it has not been published or tested
on a physical watch.

Updated on 2026-10-28 against firmware `de23235b2` and translation tools
`f7bd685`. Firmware sources live under `fw/`. Translation assets and tools are
maintained separately in `../pebbleos-translations`. No firmware preference
change is required to use an installed language pack.

`tintin.po` merges the universal POT extracted from the current firmware. Its
831 active entries exactly match the official translation repository's source
keys. It contains 828 translated messages; three intentionally empty template
suffixes remain empty. This update adds 37 entries, including a recovered older
translation, and retires six entries. All 794 retained translations are unchanged.
The additions cover workout screens, heart-rate charts, SpO2 settings, wind units
and shutdown instructions. New wording needs human Czech review before
publication. `new-translations.csv` lists the additions for review.

The layout review shortened 12 of these additions for narrow workout fields,
the countdown and the two-line shutdown dialog. Catalog/pack revision 42
includes those changes. `layout-check/check_fit.py` checks all 37 additions
against firmware PBF advances and source-defined widths, including 144-pixel
screens and the paused workout's action bar. It also checks the shutdown line
count and gauge-heading buffer lengths. Five unchanged time formats and units
retain the firmware's existing adaptive formatting or wrapping. The results are
in `layout-check/fit-report.json`; wording changes and the previous pack are in
`layout-check/wording-changes.csv` and `layout-check/before/`.

PT2 QEMU screenshots in `layout-check/` confirm the countdown, active and
completed workout labels, pause/end confirmation and SpO2 settings. The earlier
countdown showed `STA...` and the gauge shortened `PRŮM. BPM`; the revised labels
display fully. These emulator checks do not replace physical-watch testing.

The previous catalog, template, builder and pack are saved in
`backups/2026-10-28-before-update/`. The current catalog is also copied to
`../pebbleos-translations/cs_CZ/tintin.po`.

The pack includes extensions only for characters absent from each built-in font:
Bitham 30 Black, Bitham 42 Bold/Light, Roboto Condensed 21 and Droid Serif 28 Bold.
The updated built-in Gothic fonts cover Czech without extensions. All required
catalog and Czech baseline characters are covered in all 15 general text styles.
Numeric and unit subset styles retain their existing specialized coverage.
`coverage.json` records each slot.

Font inputs use the original matching bitmap variants from
`../font-refinement/before`, rather than the experimental accent candidates.
Bitham carons and side carons use the earlier matching versions, with original
system letter bodies. Ý and Ů/ů reuse each font's existing acute and ring
bitmaps. Roboto and Droid Serif use the firmware's own TTFs at the original sizes
with compatibility 2.7, including the en dash. Bitham en dashes retain the
built-in hyphen's stroke weight and vertical position. `font-selection.json`
records the original font preparation and glyph preservation checks; this
update reuses those saved font inputs.

To reproduce font preparation before building:

```sh
.venv/bin/python language-packs/czech/prepare_matching_fonts.py
.venv/bin/python language-packs/czech/add_missing_dash.py
```

Build from the firmware repository root:

```sh
.venv/bin/python language-packs/czech/build_pack.py
```

The builder uses the checked-out translation tools and their `polib` dependency,
normalizes watch-compatible catalog headers, subsets the saved PBF sources,
preserves all 29 positional font slots and verifies pack CRCs. The nine LECO
number-font slots use the built-in fonts. The coverage snapshot was extracted
from the updated firmware's committed font inputs.
`pebbleos.pot` is the current universal firmware source template; its input file
list is saved alongside it. `package-sha256.txt` identifies the output.

Validated: gettext syntax and format placeholders, exact catalog/template entry
match, no fuzzy translations, all general-text character requirements, glyph
buffer limits, pack manifest and every resource CRC. These checks do not validate
on-watch text layout or appearance.

## Making Czech publicly available

1. Sign in at [Pebble translations](https://translate.repebble.com/). Open the
   watch translation component and select Czech. If it is absent, use the
   new-language setup or ask a project maintainer to enable it.
2. Review `new-translations.csv` and the existing catalog. In Czech's **Files →
   Upload translation** menu, upload `tintin.po`. Use **Add as translation** for
   wording you have reviewed, or **Add as suggestion** to request review. Keep
   existing approved translations when resolving conflicts.
3. Check the watch previews and build a draft pack. Test the complete screens on
   a watch, especially the new workout labels.
4. Ask the project maintainers to arrange a Czech language reviewer and enable
   publication. Official published updates require at least 80% approved strings,
   passing build checks, and approval of any custom fonts with their licenses.
   Only approved strings ship. Built-in fonts need no manual approval.

The upload workflow is documented in
[Weblate's file guide](https://docs.weblate.org/en/latest/user/files.html#uploading-translations).
Publication rules are maintained in the
[translation repository](https://github.com/coredevices/pebbleos-translations#contributing)
and [Peblate](https://github.com/coredevices/peblate#publication). A local `.pbl`
can be shared for sideload testing; uploading a catalog or building a draft does
not publish an official pack.

## Restoring this GitHub backup

The `i18n/czech-language-pack` branch on `xefensor/PebbleOS` saves the catalogs,
matching font inputs, installable packs, scripts and layout screenshots. Build
directories and emulator flash images are generated locally and are not stored
on the branch. Older font experiments are retained in `../font-refinement` as
historical reference; the current pack uses `fonts/` here.

After cloning this branch, initialize only the translation-tools submodule:

```sh
git submodule update --init --depth 1 -- language-packs/pebbleos-translations
python3 -m venv .venv
.venv/bin/python -m pip install -r language-packs/czech/requirements.txt
```

Use Python 3.11 or newer and install GNU gettext so `msgfmt`, `msgmerge` and
`xgettext` are on `PATH`. The committed `.pbl` can be installed immediately;
rebuilding it needs no firmware build or emulator:

```sh
.venv/bin/python language-packs/czech/build_pack.py
.venv/bin/python language-packs/czech/layout-check/check_fit.py
msgfmt --check --check-format --statistics \
  -o /tmp/pebbleos-czech-checked.mo language-packs/czech/tintin.po
sha256sum -c language-packs/czech/package-sha256.txt
```

The submodule is pinned to the translation tools used for this pack. To prepare
its optional Czech working copy for those tools:

```sh
mkdir -p language-packs/pebbleos-translations/cs_CZ
cp language-packs/czech/tintin.po language-packs/pebbleos-translations/cs_CZ/tintin.po
```

The emulator helper uses local test ports 13444/13445 and expects a configured
QEMU build in `layout-check/build-pt2`. Recreate that build using the repository's
[emulator workflow](../../docs/development/emulation/emulator.md); SDK paths are
machine-specific. Historical preview scripts can refer to older SDK locations.
