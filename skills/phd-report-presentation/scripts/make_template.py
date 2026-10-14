# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["lxml>=5.0"]
# ///
"""make_template.py -- derive assets/template.pptx from the analysed source deck.

Strips every slide (and slide-only media/notes) from a KPI-branded reference
.pptx while keeping the slide master, ALL slide layouts, the theme and the
layout-owned brand chrome (footer bar, logo, university wordmark, slide-number
field). Also scrubs personal metadata (docProps/core.xml author fields,
docProps/app.xml per-part title list, any thumbnail/comments/customXml parts).

Works purely at the OPC/zip + XML level with lxml -- does NOT use python-pptx,
so it has no run-time dependency on python-pptx and is safe to run with only
lxml installed.

Usage:
    python make_template.py --source SOURCE.pptx --out template.pptx

Re-run this script any time the reference deck (analysis/source.pptx) changes;
its output is the file shipped as assets/template.pptx.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

from lxml import etree

NS = {
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "r": "http://schemas.openxmlformats.org/package/2006/relationships",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "ep": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
    "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
}


def qn(tag: str) -> str:
    prefix, local = tag.split(":")
    return f"{{{NS[prefix]}}}{local}"


def parse_xml(data: bytes) -> etree._Element:
    return etree.fromstring(data)


def dump_xml(el: etree._Element) -> bytes:
    return etree.tostring(el, xml_declaration=True, encoding="UTF-8", standalone=True)


def load_rels(zin: zipfile.ZipFile, part_name: str) -> etree._Element | None:
    rels_name = _rels_path(part_name)
    try:
        data = zin.read(rels_name)
    except KeyError:
        return None
    return parse_xml(data)


def _rels_path(part_name: str) -> str:
    d = part_name.rsplit("/", 1)
    if len(d) == 1:
        return f"_rels/{d[0]}.rels"
    return f"{d[0]}/_rels/{d[1]}.rels"


def build_template(source: Path, out: Path, verbose: bool = True) -> None:
    with zipfile.ZipFile(source, "r") as zin:
        names = zin.namelist()
        parts: dict[str, bytes] = {n: zin.read(n) for n in names}

    def log(msg: str) -> None:
        if verbose:
            print(f"[make_template] {msg}", file=sys.stderr)

    # ---- 1. presentation.xml: drop the slide list -----------------------
    pres = parse_xml(parts["ppt/presentation.xml"])
    pres_rels = parse_xml(parts["ppt/_rels/presentation.xml.rels"])

    sld_id_lst = pres.find(qn("p:sldIdLst"))
    removed_slide_rids: set[str] = set()
    if sld_id_lst is not None:
        for sld_id in list(sld_id_lst):
            rid = sld_id.get(qn("rel:id"))
            if rid:
                removed_slide_rids.add(rid)
            sld_id_lst.remove(sld_id)
        # Keep the (now empty) <p:sldIdLst/> element -- required by the schema.

    # ---- 2. figure out which slide parts + their notesSlide parts to drop
    slide_parts = sorted(
        n for n in parts if n.startswith("ppt/slides/slide") and n.endswith(".xml")
    )
    notes_slide_parts: set[str] = set()
    for sp in slide_parts:
        srels = load_rels_from_parts(parts, sp)
        if srels is None:
            continue
        for rel in srels.findall(qn("r:Relationship")):
            if rel.get("Type", "").endswith("/notesSlide"):
                target = _resolve_target(sp, rel.get("Target"))
                notes_slide_parts.add(target)

    log(f"removing {len(slide_parts)} slide parts and {len(notes_slide_parts)} notes-slide parts")

    parts_to_delete: set[str] = set()
    for sp in slide_parts:
        parts_to_delete.add(sp)
        parts_to_delete.add(_rels_path(sp))
    for nsl in notes_slide_parts:
        parts_to_delete.add(nsl)
        parts_to_delete.add(_rels_path(nsl))

    # ---- 3. presentation.xml.rels: drop slide relationships --------------
    for rel in list(pres_rels.findall(qn("r:Relationship"))):
        if rel.get("Type", "").endswith("/slide") and rel.get("Id") in removed_slide_rids:
            pres_rels.remove(rel)

    parts["ppt/presentation.xml"] = dump_xml(pres)
    parts["ppt/_rels/presentation.xml.rels"] = dump_xml(pres_rels)

    for name in parts_to_delete:
        parts.pop(name, None)

    # ---- 4. [Content_Types].xml: drop Overrides for removed parts --------
    ct = parse_xml(parts["[Content_Types].xml"])
    for override in list(ct.findall(qn("ct:Override"))):
        part_name = override.get("PartName", "").lstrip("/")
        if part_name in parts_to_delete:
            ct.remove(override)

    # ---- 5. docProps: scrub personal data --------------------------------
    if "docProps/core.xml" in parts:
        core = parse_xml(parts["docProps/core.xml"])
        _clear_text(core, qn("dc:title"))
        _clear_text(core, qn("dc:subject"))
        _clear_text(core, qn("dc:creator"), replacement="")
        _clear_text(core, qn("cp:lastModifiedBy"), replacement="")
        parts["docProps/core.xml"] = dump_xml(core)

    if "docProps/app.xml" in parts:
        app = parse_xml(parts["docProps/app.xml"])
        _scrub_app_xml(app)
        parts["docProps/app.xml"] = dump_xml(app)

    # ---- 6. drop thumbnail / comments / customXml if present -------------
    # "comment" (not just "/comments") also matches ppt/commentAuthors.xml --
    # a part that is NOT inside a ppt/comments/ directory and has no "/comments"
    # substring, but still carries personal data (commenters' display names)
    # that must not leak into the shipped template. It has no .rels of its
    # own, so the generic dangling-relationship sweep in step 7b below can't
    # catch it by itself -- it must be removed here, by name.
    for name in list(parts):
        lname = name.lower()
        if "thumbnail" in lname or "comment" in lname or lname.startswith("customxml/"):
            parts.pop(name, None)
    for override in list(ct.findall(qn("ct:Override"))):
        part_name = override.get("PartName", "").lstrip("/")
        if part_name not in parts:
            ct.remove(override)
    # Root .rels: drop the thumbnail relationship if it existed.
    if "_rels/.rels" in parts:
        root_rels = parse_xml(parts["_rels/.rels"])
        for rel in list(root_rels.findall(qn("r:Relationship"))):
            if rel.get("Type", "").endswith("/thumbnail"):
                target = _resolve_target("", rel.get("Target"))
                parts.pop(target, None)
                root_rels.remove(rel)
        parts["_rels/.rels"] = dump_xml(root_rels)

    parts["[Content_Types].xml"] = dump_xml(ct)

    # ---- 7. drop now-orphaned media (images only referenced by removed
    #         slides, e.g. per-slide formulas/charts/decorative pics) ------
    referenced_targets: set[str] = set()
    for name in list(parts):
        if not name.endswith(".rels"):
            continue
        rels_el = parse_xml(parts[name])
        base_part = _part_for_rels(name)
        for rel in rels_el.findall(qn("r:Relationship")):
            target = rel.get("Target", "")
            if target.startswith("http") or rel.get("TargetMode") == "External":
                continue
            referenced_targets.add(_resolve_target(base_part, target))

    removed_media = []
    for name in list(parts):
        if name.startswith("ppt/media/") and name not in referenced_targets:
            parts.pop(name)
            removed_media.append(name)
    log(f"removed {len(removed_media)} orphaned media file(s): {sorted(removed_media)}")

    # ---- 7b. drop any relationship left pointing at a part we removed -----
    # Belt-and-braces pass covering every removal above (slides, notes,
    # thumbnail, comments/commentAuthors, customXml, orphaned media): a
    # <Relationship> whose Target no longer resolves to a surviving part
    # would make PowerPoint show its "needs repair" dialog and would fail
    # the zip-level "no rels point to missing parts" check. Internal rels
    # only -- External (hyperlink) targets are never part names and must be
    # left alone.
    dangling = 0
    for rels_name in [n for n in parts if n.endswith(".rels")]:
        rels_el = parse_xml(parts[rels_name])
        base_part = _part_for_rels(rels_name)
        changed = False
        for rel in list(rels_el.findall(qn("r:Relationship"))):
            if rel.get("TargetMode") == "External":
                continue
            target = rel.get("Target", "")
            if target.startswith("http"):
                continue
            if _resolve_target(base_part, target) not in parts:
                rels_el.remove(rel)
                changed = True
                dangling += 1
        if changed:
            parts[rels_name] = dump_xml(rels_el)
    if dangling:
        log(f"dropped {dangling} dangling relationship(s) pointing at removed parts")

    # ---- 8. write the output zip -----------------------------------------
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        # [Content_Types].xml must be first for maximum compatibility.
        zout.writestr("[Content_Types].xml", parts.pop("[Content_Types].xml"))
        for name in sorted(parts):
            zout.writestr(name, parts[name])

    log(f"wrote {out} ({out.stat().st_size} bytes)")


def load_rels_from_parts(parts: dict[str, bytes], part_name: str) -> etree._Element | None:
    rels_name = _rels_path(part_name)
    data = parts.get(rels_name)
    if data is None:
        return None
    return parse_xml(data)


def _part_for_rels(rels_name: str) -> str:
    # "ppt/slides/_rels/slide1.xml.rels" -> "ppt/slides/slide1.xml"
    # "_rels/.rels" -> ""
    d = rels_name.rsplit("/_rels/", 1)
    if len(d) == 1:
        return ""
    base_dir, fname = d
    return f"{base_dir}/{fname[:-5]}" if base_dir else fname[:-5]


def _resolve_target(base_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base_dir = base_part.rsplit("/", 1)[0] if "/" in base_part else ""
    combined = f"{base_dir}/{target}" if base_dir else target
    parts_out: list[str] = []
    for seg in combined.split("/"):
        if seg == "..":
            if parts_out:
                parts_out.pop()
        elif seg == "." or seg == "":
            continue
        else:
            parts_out.append(seg)
    return "/".join(parts_out)


def _clear_text(root: etree._Element, tag: str, replacement: str = "") -> None:
    el = root.find(tag)
    if el is not None:
        el.text = replacement


def _scrub_app_xml(app: etree._Element) -> None:
    # Drop the whole TitlesOfParts / HeadingPairs vectors that enumerate
    # per-slide titles (person/topic specific) and reset slide-count fields.
    for tag in ("Slides", "Notes", "HiddenSlides", "Paragraphs", "Words", "TotalTime"):
        el = app.find(qn(f"ep:{tag}"))
        if el is not None:
            el.text = "0"

    heading_pairs = app.find(qn("ep:HeadingPairs"))
    titles_of_parts = app.find(qn("ep:TitlesOfParts"))
    if heading_pairs is not None and titles_of_parts is not None:
        vector = heading_pairs.find(qn("vt:vector"))
        title_vector = titles_of_parts.find(qn("vt:vector"))
        if vector is not None and title_vector is not None:
            # Keep only the "fonts" and "theme" heading-pair entries (safe,
            # non-personal); drop the "slide titles" pair and its strings.
            variants = list(vector)
            new_variants = []
            keep_title_count = 0
            i = 0
            while i < len(variants):
                label_variant = variants[i]
                count_variant = variants[i + 1] if i + 1 < len(variants) else None
                label = label_variant.find(qn("vt:lpstr"))
                label_text = label.text or "" if label is not None else ""
                count_val = 0
                if count_variant is not None:
                    i4 = count_variant.find(qn("vt:i4"))
                    if i4 is not None and i4.text:
                        count_val = int(i4.text)
                is_slide_titles = "заголов" in label_text.lower() or "slide titles" in label_text.lower()
                if not is_slide_titles:
                    new_variants.append(label_variant)
                    if count_variant is not None:
                        new_variants.append(count_variant)
                    if "шрифт" in label_text.lower() or "font" in label_text.lower():
                        keep_title_count = count_val
                i += 2
            for child in list(vector):
                vector.remove(child)
            for v in new_variants:
                vector.append(v)
            vector.set("size", str(len(new_variants)))

            # Trim TitlesOfParts down to just the first `keep_title_count`
            # strings (the font-name list), dropping the per-slide titles.
            lpstrs = list(title_vector)
            trimmed = lpstrs[:keep_title_count] if keep_title_count else lpstrs
            for child in list(title_vector):
                title_vector.remove(child)
            for s in trimmed:
                title_vector.append(s)
            title_vector.set("size", str(len(trimmed)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, type=Path, help="path to the reference .pptx")
    ap.add_argument("--out", required=True, type=Path, help="path to write the stripped template .pptx")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if not args.source.exists():
        print(f"error: source file not found: {args.source}", file=sys.stderr)
        raise SystemExit(2)

    build_template(args.source, args.out, verbose=not args.quiet)


if __name__ == "__main__":
    main()
