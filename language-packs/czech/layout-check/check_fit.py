"""Measure the 37 new strings with the firmware's PBF glyph advances."""

import csv
import json
import sys
from pathlib import Path

import polib

OUTPUT = Path(__file__).resolve().parent
ROOT = OUTPUT.parents[2]
sys.path.insert(0, str(ROOT / "language-packs/font-refinement"))
from font_work import Font

# Minimum widths across the current rectangular and round screen layouts.
# The paused 144px workout screen has a 30px action bar: (144 - 30) / 2.
FIELDS = {
    "Just Once": ("GOTHIC_24_BOLD", 132, "Day-picker menu title"),
    "%d–%d BPM": ("GOTHIC_18_BOLD", 134, "Health range; 255–255 BPM"),
    "TODAY'S RANGE": ("GOTHIC_14_BOLD", 134, "Health heading"),
    "SpO2": ("GOTHIC_24_BOLD", 132, "Health settings title"),
    "SpO2 During Activity": ("GOTHIC_24_BOLD", 132, "Health settings title"),
    "Disconnect the charger to shut down.": (
        "GOTHIC_24_BOLD",
        132,
        "Shutdown dialog, maximum two lines",
    ),
    "COMPLETE": ("GOTHIC_18_BOLD", 144, "Completed workout banner"),
    "END WORKOUT?": ("GOTHIC_18_BOLD", 114, "Paused workout banner beside action bar"),
    "PAUSED": ("GOTHIC_18_BOLD", 114, "Paused workout banner beside action bar"),
    "AVG": ("GOTHIC_14_BOLD", 38, "Heart-rate badge label"),
    "Z%d": ("GOTHIC_14_BOLD", 22, "Zone row; Z4"),
    "TOTAL TIME": ("GOTHIC_14_BOLD", 62, "Gauge bottom field: 124 / 2"),
    "TIMER": ("GOTHIC_14_BOLD", 72, "Workout grid: 144 / 2"),
    "DIST MI": ("GOTHIC_14_BOLD", 57, "Paused workout column"),
    "DIST KM": ("GOTHIC_14_BOLD", 57, "Paused workout column"),
    "PACE /MI": ("GOTHIC_14_BOLD", 57, "Paused workout column"),
    "PACE /KM": ("GOTHIC_14_BOLD", 57, "Paused workout column"),
    "KCAL": ("GOTHIC_14_BOLD", 57, "Paused workout column"),
    "CADENCE": ("GOTHIC_14_BOLD", 72, "Workout grid column"),
    "SPEED MPH": ("GOTHIC_14_BOLD", 72, "Workout grid column"),
    "SPEED KM/H": ("GOTHIC_14_BOLD", 72, "Workout grid column"),
    "LOW SPO2 %": ("GOTHIC_14_BOLD", 62, "Gauge bottom field"),
    "AVG BPM": ("GOTHIC_14_BOLD", 62, "Gauge bottom field"),
    "TIME IN ZONE": ("GOTHIC_14_BOLD", 144, "Workout zones heading"),
    "LAST MINUTE": ("GOTHIC_14_BOLD", 86, "144px HR chart: 144 - 28 - 24 - 6"),
    "WAITING FOR HR": ("GOTHIC_14_BOLD", 86, "144px HR chart plot width"),
    "READING SPO2": ("GOTHIC_18_BOLD", 120, "Gauge heading, 24-byte buffer"),
    "ZONE %d": ("GOTHIC_18_BOLD", 120, "Gauge heading; zone 4, 24-byte buffer"),
    "MEASURING": ("GOTHIC_18_BOLD", 120, "Gauge heading, 24-byte buffer"),
    "SPO2 %": ("GOTHIC_14_BOLD", 62, "Gauge bottom field"),
    "WORKOUT": ("GOTHIC_18_BOLD", 144, "Workout picker/countdown heading"),
    "GO!": ("BITHAM_30_BLACK", 68, "Small countdown circle; PT2 allows 96px"),
}
UNCHANGED = {
    "%k": "Same time format; native chart measures hour labels",
    "%l%p": "Same time format; native chart omits AM/PM when labels would overlap",
    "%l": "Same time format; native chart measures hour labels",
    "m/s": "Unchanged unit in wrapped forecast text",
    "kt": "Unchanged unit in wrapped forecast text",
}


def sample(text):
    if text == "%d–%d BPM":
        return "255–255 BPM"
    return text.replace("%d", "4")


def load_font(name):
    candidates = [
        ROOT / f"resources/{group}/base/pbf/{name}.pbf"
        for group in ("common", "normal")
    ]
    font = Font(next(path for path in candidates if path.exists()).read_bytes())
    extension = ROOT / f"language-packs/czech/fonts/{name}.pbf"
    if extension.exists():
        for cp, glyph in Font(extension.read_bytes()).g.items():
            font.g.setdefault(cp, glyph)
    return font


def width(font, text):
    return sum(font.g[ord(char)]["advance"] for char in text)


def wrap(font, text, limit):
    lines = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if width(font, trial) > limit and line:
            lines.append(line)
            line = word
        else:
            line = trial
    lines.append(line)
    return lines


def main():
    catalog = polib.pofile(str(OUTPUT.parent / "tintin.po"))
    before = polib.pofile(str(OUTPUT / "before/tintin.po"))
    with (OUTPUT.parent / "new-translations.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        sources = [row["English"] for row in csv.DictReader(stream)]
    assert set(sources) == FIELDS.keys() | UNCHANGED.keys()
    fonts = {name: load_font(name) for name, _, _ in FIELDS.values()}
    results = []
    for source in sources:
        entry = catalog.find(source)
        old = before.find(source)
        record = {"source": source, "before": old.msgstr, "after": entry.msgstr}
        if source in UNCHANGED:
            assert entry.msgstr == source
            record.update(
                ok=True, method="unchanged format/unit", note=UNCHANGED[source]
            )
        else:
            name, limit, note = FIELDS[source]
            font = fonts[name]
            current, previous = sample(entry.msgstr), sample(old.msgstr)
            lines = (
                wrap(font, current, limit)
                if source.startswith("Disconnect")
                else [current]
            )
            old_lines = (
                wrap(font, previous, limit)
                if source.startswith("Disconnect")
                else [previous]
            )
            record.update(
                font=name,
                limit_px=limit,
                note=note,
                before_px=width(font, previous),
                after_px=width(font, current),
                lines=lines,
                before_lines=old_lines,
                ok=len(lines) <= 2
                and all(width(font, line) <= limit for line in lines),
            )
            if source in {"READING SPO2", "ZONE %d", "MEASURING"}:
                record["buffer_bytes_including_nul"] = len(current.encode("utf-8")) + 1
                record["ok"] &= record["buffer_bytes_including_nul"] <= 24
        results.append(record)
    report = {
        "method": "Firmware PBF advances and source-defined text boxes; separate QEMU screenshots",
        "firmware": "de23235b2",
        "strings_checked": len(results),
        "ok": all(record["ok"] for record in results),
        "results": results,
        "limitations": "No physical-watch test; larger menu text sizes can scroll selected titles.",
    }
    (OUTPUT / "fit-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    for record in results:
        if record["before"] != record["after"]:
            print(
                record["source"],
                record.get("before_px"),
                "->",
                record.get("after_px"),
                "/",
                record.get("limit_px"),
                "px",
                record.get("lines"),
            )
    print(f"{sum(r['ok'] for r in results)}/{len(results)} checks passed")
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
