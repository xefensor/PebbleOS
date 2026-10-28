"""Build the Czech sideload pack using the current translation tools."""

import json
import struct
import sys
from pathlib import Path

import polib

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT.parent / "pebbleos-translations" / "tools"
sys.path.insert(0, str(TOOLS))
from extract_builtin_coverage import pbf_codepoints
from generate_codepoint_requirements import generate_codepoint_requirements
from lang_commands import compile_catalog, firmware_catalog
from pack_format import FONT_SLOTS, MAX_GLYPH_SIZE, crc32, serialize


def subset(data, required):
    version, _, count, wildcard, buckets, cp_bytes = struct.unpack_from("<BBHHBB", data)
    header_size = 10 if version == 3 else 8
    flags = data[9] if version == 3 else 0
    offset_bytes = 2 if flags & 1 else 4
    entry_size = cp_bytes + offset_bytes
    table_start = header_size + buckets * 4
    glyph_start = table_start + count * entry_size
    mappings = {}
    for bucket in range(buckets):
        _, size, offset = struct.unpack_from("<BBH", data, header_size + bucket * 4)
        for index in range(size):
            start = table_start + offset + index * entry_size
            cp = int.from_bytes(data[start : start + cp_bytes], "little")
            glyph = int.from_bytes(data[start + cp_bytes : start + entry_size], "little")
            mappings[cp] = glyph
    selected = required | {wildcard}
    records = {}
    for cp in sorted(selected & mappings.keys()):
        start = glyph_start + mappings[cp]
        width, height = struct.unpack_from("<BB", data, start)
        size = (height + 1) // 2 if flags & 2 else (width * height + 7) // 8
        if 5 + size > MAX_GLYPH_SIZE:
            raise ValueError(f"U+{cp:04X} exceeds the universal glyph buffer")
        records[cp] = data[start : start + 5 + ((size + 3) // 4) * 4]
    header = bytearray(data[:header_size])
    struct.pack_into("<H", header, 2, len(records))
    glyphs = bytearray(b"\0" * 4)
    offsets = {}
    for cp, record in records.items():
        offsets[cp] = len(glyphs)
        glyphs.extend(record)
    hashes = bytearray()
    table = bytearray()
    for bucket in range(buckets):
        codes = [cp for cp in records if cp % buckets == bucket]
        hashes.extend(struct.pack("<BBH", bucket, len(codes), len(table)))
        for cp in codes:
            table.extend(cp.to_bytes(cp_bytes, "little"))
            table.extend(offsets[cp].to_bytes(offset_bytes, "little"))
    result = bytes(header + hashes + table + glyphs)
    assert set(pbf_codepoints(result)) == required
    return result


def main():
    catalog = firmware_catalog(polib.pofile(str(ROOT / "tintin.po")), locale="cs_CZ", version=40)
    catalog.save(str(ROOT / "firmware.po"))
    compile_catalog(ROOT / "firmware.po", ROOT / "strings.mo")
    resources = [(ROOT / "strings.mo").read_bytes()]
    coverage = json.loads((ROOT / "builtin_font_coverage.json").read_text())["fonts"]
    requirements = set(generate_codepoint_requirements(ROOT / "tintin.po", language="cs_CZ")["codepoints"])
    alphabet = set(map(ord, "ÁáČčĎďÉéĚěÍíŇňÓóŘřŠšŤťÚúŮůÝýŽž"))
    report = {}
    for name in FONT_SLOTS:
        base = set(coverage[name]["codepoints"])
        source = ROOT / "fonts" / (name.removesuffix("_EXTENDED") + ".pbf")
        available = set(pbf_codepoints(source.read_bytes())) if source.exists() else set()
        needed = requirements - base
        included = needed & available
        data = subset(source.read_bytes(), included) if included else b""
        resources.append(data)
        if not any(part in name for part in ("SUBSET", "NUMBERS")):
            assert not alphabet - base - included, name
        report[name] = {"added": "".join(map(chr, sorted(included))), "bytes": len(data),
                        "uncovered": "".join(map(chr, sorted(needed - included)))}
    packed = serialize(resources)
    output = ROOT.parent / "cs_CZ-with-fonts.pbl"
    output.write_bytes(packed)
    # Verify the manifest and every positional resource independently.
    count, checksum, _ = struct.unpack_from("<III", packed)
    assert count == 21 and crc32(packed[4108:]) == checksum
    for index, expected in enumerate(resources):
        resource_id, offset, size, checksum = struct.unpack_from("<IIII", packed, 12 + index * 16)
        content = packed[4108 + offset : 4108 + offset + size]
        assert resource_id == index + 1 and content == expected and crc32(content) == checksum
    (ROOT / "coverage.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Created {output}: {len(packed)} bytes; all Czech letters covered in 15 text styles")


if __name__ == "__main__":
    main()
