"""Select font extensions that preserve the firmware's existing glyph style."""

import json
import struct
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
WORK = ROOT.parent / "font-refinement"
sys.path.insert(0, str(WORK))
sys.path.insert(0, str(REPO / "tools"))
from font.fontgen import Font as TtfFont, MAX_GLYPHS_EXTENDED
from font_work import Font, bitlist_to_bytes, compress_rle4
from refine_try import write

ALPHABET = "ÁáČčĎďÉéĚěÍíŇňÓóŘřŠšŤťÚúŮůÝýŽž"


def record(font, points, advance):
    left = min(x for x, _ in points)
    top = min(y for _, y in points)
    width = max(x for x, _ in points) - left + 1
    height = max(y for _, y in points) - top + 1
    bits = [int((left + x, top + y) in points)
            for y in range(height) for x in range(width)]
    encoded_height, bitmap = (compress_rle4(bits) if font.flags & 2
                              else (height, bitlist_to_bytes(bits)))
    raw = struct.pack("<BBbbb", width, encoded_height, left, top, advance)
    raw += bitmap + b"\0" * (-len(bitmap) % 4)
    return {"raw": raw}


def transplant(font, target, donor, donor_base):
    body = font.g[ord(unicodedata.normalize("NFD", target)[0])]["points"]
    source_body = font.g[ord(donor_base)]["points"]
    source_top = min(y for _, y in source_body)
    accent = {p for p in font.g[ord(donor)]["points"] if p[1] < source_top}
    body_top = min(y for _, y in body)
    dx = round((min(x for x, _ in body) + max(x for x, _ in body)
                - min(x for x, _ in source_body) - max(x for x, _ in source_body)) / 2)
    # Preserve the donor's exact bitmap and clearance above the original body.
    dy = body_top - source_top
    points = body | {(x + dx, y + dy) for x, y in accent}
    base = unicodedata.normalize("NFD", target)[0]
    return record(font, points, font.g[ord(base)]["advance"])


def save(font, path):
    header = bytearray(font.data)
    struct.pack_into("<H", header, 2, len(font.g))
    font.data = bytes(header)
    write(font, {}, path)


def main():
    report = {}
    for name in ("GOTHIC_36", "BITHAM_30_BLACK", "BITHAM_42_BOLD", "BITHAM_42_LIGHT"):
        base = Font((REPO / "resources/normal/base/pbf" / f"{name}.pbf").read_bytes())
        selected = Font((WORK / "before" / f"{name}.pbf").read_bytes())
        missing = [c for c in ALPHABET if ord(c) not in base.g]
        for c in missing:
            # Reuse original matching carons and side carons with unchanged letter bodies.
            glyph = selected.g[ord(c)]
            body = unicodedata.normalize("NFD", c)[0]
            assert base.g[ord(body)]["points"] <= glyph["points"], (name, c)
            if c == "Ý":
                glyph = transplant(base, c, "Á", "A")
            elif c in "Ůů":
                donor = "Å" if c == "Ů" and ord("Å") in base.g else "å"
                glyph = transplant(base, c, donor, "A" if donor == "Å" else "a")
            elif name == "GOTHIC_36" and c not in "ďť":
                donor = "Š" if c.isupper() else "š"
                glyph = transplant(base, c, donor, "S" if c.isupper() else "s")
            base.g[ord(c)] = glyph
        path = ROOT / "fonts" / f"{name}.pbf"
        save(base, path)
        original = Font((REPO / "resources/normal/base/pbf" / f"{name}.pbf").read_bytes())
        result = Font(path.read_bytes())
        assert all(result.g[cp]["raw"] == g["raw"] for cp, g in original.g.items())
        report[name] = {"selection": "original matching bitmap variant; system acute and ring donors",
                        "added": "".join(missing), "existing_glyphs_unchanged": True}
    for name, filename, height in (("ROBOTO_CONDENSED_21", "Roboto-Condensed.ttf", 21),
                                   ("DROID_SERIF_28_BOLD", "DroidSerif-Bold.ttf", 28)):
        source = REPO / "resources/normal/base/ttf" / filename
        original = TtfFont(str(source), height, MAX_GLYPHS_EXTENDED, 256, True)
        original.set_codepoint_list(str(REPO / "resources/normal/base/ttf/basic_latin_codepoints.json"))
        original.build_tables()
        generated = TtfFont(str(source), height, MAX_GLYPHS_EXTENDED, 256, True)
        generated.codepoints = set(original.codepoints) | set(map(ord, ALPHABET + "–"))
        generated.build_tables()
        path = ROOT / "fonts" / f"{name}.pbf"
        path.write_bytes(generated.bitstring())
        base = Font(original.bitstring())
        result = Font(path.read_bytes())
        assert all(result.g[cp]["raw"] == g["raw"] for cp, g in base.g.items())
        report[name] = {"selection": "firmware TTF, size and compatibility 2.7",
                        "existing_glyphs_unchanged": True}
    (ROOT / "font-selection.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
