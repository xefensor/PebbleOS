# Czech sideload pack

Install `../cs_CZ-with-fonts.pbl` using the companion app's language-pack
installation function. This is a local draft; it has not been published or tested
on a physical watch.

The firmware checkout was fast-forwarded to upstream `63769a1e6`. Firmware sources,
including preferences, now live under `fw/`, rather than `src/fw/`. Translation
assets and tools are maintained separately in `../pebbleos-translations`.
No firmware preference change is required to use an installed language pack.

`tintin.po` recovers the previous Czech catalog from the existing compiled pack,
merges the universal POT extracted from the current firmware, and translates the
new settings, notifications and weather strings. It contains 797 translated
messages. Three intentionally empty template suffixes remain empty. Existing
wording was preserved. New wording needs human Czech review before publication.

The pack includes extensions only for characters absent from each built-in font:
Gothic 36, Bitham 30 Black, Bitham 42 Bold/Light, Roboto Condensed 21 and Droid
Serif 28 Bold. All required catalog and Czech baseline characters are covered in
all 15 general text styles. Numeric and unit subset styles retain their existing
specialized coverage. `coverage.json` records each slot.

Font inputs now use the original matching bitmap variants from
`../font-refinement/before`, rather than the experimental accent candidates.
Existing system glyph records remain byte-for-byte unchanged. Gothic 36 carons
reuse the built-in Š/š accent bitmaps. The new Ý and Ů/ů use the same font's
existing acute and ring bitmaps, retaining the exact original Y/U/u bodies.
Bitham carons and side carons use the earlier matching versions, with original
system letter bodies. Roboto and Droid Serif are generated from the firmware's
own TTFs at the original sizes with compatibility 2.7, including the en dash.
Bitham en dashes retain the built-in hyphen's stroke weight and vertical position.
`font-selection.json` records the selection and glyph preservation checks.

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
preserves all 20 positional font slots and verifies pack CRCs. The coverage
snapshot was extracted from the updated firmware's committed font inputs.
`pebbleos.pot` is the current universal firmware source template; its input file
list is saved alongside it. `package-sha256.txt` identifies the output.

Validated: gettext syntax and format placeholders, exact catalog/template entry
match, no fuzzy translations, all general-text character requirements, glyph
buffer limits, pack manifest and every resource CRC. These checks do not validate
on-watch text layout or appearance.
