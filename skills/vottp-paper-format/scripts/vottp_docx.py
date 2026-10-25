# /// script
# requires-python = ">=3.10"
# dependencies = ["lxml>=5"]
# ///
"""Inventory, format and check VOTTP DOCX layout while preserving author content."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

from lxml import etree as ET

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
}
PART = "word/document.xml"
ROLES = set("body udc author affiliation contact title abstract-uk abstract-en keywords-uk keywords-en heading subheading figure figure-caption table-label table-title table reference-heading reference equation keep".split())
ORDERS = {
    "pPr": "pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd tabs suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection textAlignment textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange".split(),
    "rPr": "rStyle rFonts b bCs i iCs caps smallCaps strike dstrike outline shadow emboss imprint noProof snapToGrid vanish webHidden color spacing w kern position sz szCs highlight u effect bdr shd fitText vertAlign rtl cs em lang eastAsianLayout specVanish oMath rPrChange".split(),
    "sectPr": "headerReference footerReference footnotePr endnotePr type pgSz pgMar paperSrc pgBorders lnNumType pgNumType cols formProt vAlign noEndnote titlePg textDirection bidi rtlGutter docGrid printerSettings sectPrChange".split(),
}


def q(local: str) -> str:
    return f"{{{NS['w']}}}{local}"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_docx(path: Path):
    with zipfile.ZipFile(path) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError("Duplicate DOCX ZIP members are unsupported")
        members = {i.filename: (i, z.read(i.filename)) for i in z.infolist()}
    if PART not in members:
        raise ValueError("Not a Word DOCX: missing word/document.xml")
    if any("vbaproject" in n.lower() for n in members):
        raise ValueError("Macro-enabled input is not a supported submission")
    parser = ET.XMLParser(resolve_entities=False, no_network=True)
    root = ET.fromstring(members[PART][1], parser)
    if root.xpath(".//w:ins | .//w:del | .//w:moveFrom | .//w:moveTo | .//w:pPrChange | .//w:rPrChange | .//w:sectPrChange", namespaces=NS):
        raise ValueError("Resolve tracked revisions in an author-reviewed copy first")
    return members, root


def paragraphs(root):
    return root.xpath("./w:body//w:p", namespaces=NS)


def text(p):
    return "".join(p.xpath(".//w:t/text() | .//m:t/text()", namespaces=NS))


def own_runs(p):
    return [r for r in p.xpath(".//w:r", namespaces=NS)
            if r.xpath("ancestor::w:p[1]", namespaces=NS)[0] is p
            and not r.xpath("ancestor::m:oMath", namespaces=NS)]


def special_font_styles(members):
    """Protect scientific fonts inherited through paragraph/character styles."""
    if "word/styles.xml" not in members:
        return set()
    styles = ET.fromstring(members["word/styles.xml"][1], ET.XMLParser(resolve_entities=False, no_network=True))
    nodes = {s.get(q("styleId")): s for s in styles.findall(q("style"))}
    protected = set()
    for style_id in nodes:
        current, visited = style_id, set()
        while current in nodes and current not in visited:
            visited.add(current)
            node = nodes[current]
            fonts = " ".join(node.xpath("./w:rPr/w:rFonts/@*", namespaces=NS)).lower()
            if any(name in fonts for name in ("symbol", "wingdings", "webdings", "cambria math")):
                protected.add(style_id)
                break
            base = node.find(q("basedOn"))
            current = base.get(q("val")) if base is not None else None
    return protected


def ordinary(r, protected_styles=()):
    fonts = " ".join(r.xpath("./w:rPr/w:rFonts/@*", namespaces=NS)).lower()
    styles = r.xpath("./w:rPr/w:rStyle/@w:val | ancestor::w:p[1]/w:pPr/w:pStyle/@w:val", namespaces=NS)
    return bool(r.xpath("./w:t", namespaces=NS)) and not any(
        name in fonts for name in ("symbol", "wingdings", "webdings", "cambria math")) and not any(s in protected_styles for s in styles)


def prop(parent, name, attrs=None, replace=False):
    el = parent.find(q(name))
    if el is None:
        el = ET.Element(q(name))
        order = ORDERS.get(ET.QName(parent).localname, [])
        rank = order.index(name) if name in order else len(order)
        pos = next((i for i, c in enumerate(parent)
                    if ET.QName(c).localname in order and
                    order.index(ET.QName(c).localname) > rank), len(parent))
        parent.insert(pos, el)
    if replace:
        el.attrib.clear()
    for k, v in (attrs or {}).items():
        el.set(q(k), str(v))
    return el


def child_properties(parent, name):
    found = parent.find(q(name))
    if found is None:
        found = ET.Element(q(name))
        parent.insert(0, found)
    return found


def spec(role, profile):
    alignment = "both" if role in {"body", "abstract-uk", "abstract-en", "keywords-uk", "keywords-en"} else "left"
    if role in {"author", "affiliation", "contact", "table-label"}:
        alignment = "right"
    if role in {"title", "heading", "reference-heading", "figure", "figure-caption", "table-title", "equation"}:
        alignment = "center"
    result = dict(font="Times New Roman", size=20, line=312, align=alignment,
                  indent=709 if alignment == "both" else 0)
    if role in {"title", "heading", "subheading", "reference-heading", "table-title"}:
        result["bold"] = True
    if profile == "published":
        if role in {"title", "author"}:
            result["size"] = 24
        if role in {"affiliation", "contact", "reference", "table"}:
            result.update(size=16, line=240)
        if role.startswith(("abstract-", "keywords-")):
            result.update(font="Tahoma", size=16, line=240, italic=True)
    return result


def normalized_content(root):
    """Ignore only properties this helper is permitted to change."""
    r = copy.deepcopy(root)
    allowed = {
        "pPr": {"jc", "spacing", "ind", "keepNext", "keepLines", "widowControl"},
        "rPr": {"rFonts", "sz", "szCs", "b", "bCs", "i", "iCs"},
        "sectPr": {"pgSz", "pgMar"},
    }
    for parent_name, children in allowed.items():
        for p in r.iter(q(parent_name)):
            for c in list(p):
                if c.tag in {q(n) for n in children}:
                    p.remove(c)
    # Empty property elements can be introduced by formatting.
    for name in ("pPr", "rPr"):
        for p in list(r.iter(q(name))):
            if not len(p) and not p.attrib and not p.text:
                p.getparent().remove(p)
    return ET.tostring(r, method="c14n")


def preservation(before, after, original_root, formatted_root):
    unchanged = set(before) == set(after) and all(
        before[n][1] == after[n][1] for n in before if n != PART)
    # Explicit native-math comparison also protects math-internal run properties.
    math = lambda r: [ET.tostring(e, method="c14n") for e in r.xpath(".//m:oMath", namespaces=NS)]
    return {
        "other_package_parts_unchanged": unchanged,
        "content_and_structure_preserved": normalized_content(original_root) == normalized_content(formatted_root),
        "native_equations_preserved": math(original_root) == math(formatted_root),
    }


def inventory(path, root):
    entries = []
    for i, p in enumerate(paragraphs(root)):
        table = bool(p.xpath("ancestor::w:tc", namespaces=NS))
        math = bool(p.xpath(".//m:oMath", namespaces=NS))
        entries.append(dict(index=i, text=text(p), in_table=table,
                            role="equation" if math else "table" if table else "body"))
    return {"source_sha256": sha(path.read_bytes()), "paragraphs": entries}


def load_roles(path, root, original):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("source_sha256") != sha(original.read_bytes()):
        raise ValueError("Stale role inventory: source SHA-256 differs")
    entries = data.get("paragraphs", [])
    ps = paragraphs(root)
    if len(entries) != len(ps):
        raise ValueError("Paragraph count differs from role inventory")
    for i, (e, p) in enumerate(zip(entries, ps)):
        if e.get("index") != i or e.get("text") != text(p):
            raise ValueError(f"Stale/misordered paragraph {i}")
        if e.get("role") not in ROLES:
            raise ValueError(f"Unknown role in paragraph {i}: {e.get('role')}")
    return entries


def apply(root, entries, profile, protected_styles=()):
    for section in root.xpath(".//w:sectPr", namespaces=NS):
        prop(section, "pgSz", dict(w=11906, h=16838, orient="portrait"), replace=True)
        # Preserve header/footer positioning, clear gutter and exotic side settings.
        old = section.find(q("pgMar"))
        hf = {k: old.get(q(k), "0") if old is not None else "0" for k in ("header", "footer")}
        prop(section, "pgMar", dict(top=1417, right=850, bottom=1417, left=1417, gutter=0, **hf), replace=True)
    for p, e in zip(paragraphs(root), entries):
        role = e["role"]
        if role == "keep":
            continue
        s = spec(role, profile)
        pp = child_properties(p, "pPr")
        prop(pp, "jc", {"val": s["align"]}, replace=True)
        prop(pp, "spacing", dict(before=0, after=0, line=s["line"], lineRule="auto"), replace=True)
        prop(pp, "ind", dict(left=0, right=0, firstLine=s["indent"]), replace=True)
        prop(pp, "keepLines", {"val": 1})
        prop(pp, "widowControl", {"val": 1})
        keep = role in {"title", "heading", "subheading", "reference-heading", "table-label", "table-title", "figure"}
        prop(pp, "keepNext", {"val": int(keep)})
        for r in own_runs(p):
            if not ordinary(r, protected_styles):
                continue
            rp = child_properties(r, "rPr")
            prop(rp, "rFonts", dict(ascii=s["font"], hAnsi=s["font"], eastAsia=s["font"], cs=s["font"]), replace=True)
            prop(rp, "sz", {"val": s["size"]}, replace=True)
            prop(rp, "szCs", {"val": s["size"]}, replace=True)
            for key, tags in (("bold", ("b", "bCs")), ("italic", ("i", "iCs"))):
                if s.get(key):
                    for tag in tags:
                        prop(rp, tag, {"val": 1})


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check(root, entries, profile, protected_styles=()):
    findings = []
    def add(level, rule, where, message):
        findings.append(dict(status=level, rule=rule, location=where, message=message))
    sections = root.xpath(".//w:sectPr", namespaces=NS)
    if not sections:
        add("ERROR", "F02", "document", "No section properties")
    for i, section in enumerate(sections):
        for tag, attrs in (("pgSz", dict(w="11906", h="16838", orient="portrait")),
                           ("pgMar", dict(top="1417", right="850", bottom="1417", left="1417", gutter="0"))):
            el = section.find(q(tag))
            if el is None or any(el.get(q(k)) != v for k, v in attrs.items()):
                add("ERROR", "F02", f"section {i}", f"Unexpected {tag}; expected {attrs}")
        cols = section.find(q("cols"))
        if cols is not None and cols.get(q("num"), "1") != "1":
            add("NOT VERIFIED", "layout-convention", f"section {i}", "Multiple columns differ from reviewed papers")
    abstracts = {"uk": [], "en": []}
    for i, (p, e) in enumerate(zip(paragraphs(root), entries)):
        role = e["role"]
        where = f"paragraph {i}"
        if role == "keep":
            add("NOT VERIFIED", "F03", where, "Role keep: layout intentionally unchecked")
            continue
        if role.startswith("abstract-"):
            abstracts[role[-2:]].append(text(p))
        s = spec(role, profile)
        pp = p.find(q("pPr"))
        expected = {"jc": {"val": s["align"]}, "spacing": {"line": str(s["line"]), "lineRule": "auto", "before": "0", "after": "0"}, "ind": {"left": "0", "right": "0", "firstLine": str(s["indent"])}}
        for tag, attrs in expected.items():
            el = pp.find(q(tag)) if pp is not None else None
            if el is None or any(el.get(q(k)) != v for k, v in attrs.items()):
                add("ERROR", "F03/layout", where, f"Unexpected {tag} for role {role}")
        for r in own_runs(p):
            if not ordinary(r, protected_styles):
                continue
            rp = r.find(q("rPr"))
            fonts = rp.find(q("rFonts")) if rp is not None else None
            size = rp.find(q("sz")) if rp is not None else None
            if fonts is None or any(fonts.get(q(k)) != s["font"] for k in ("ascii", "hAnsi", "eastAsia", "cs")) or any(k.endswith("Theme") for k in (ET.QName(a).localname for a in fonts.attrib)) or size is None or size.get(q("val")) != str(s["size"]):
                add("ERROR", "F03", where, "Run font/size differs from chosen profile")
                break
            for key, tag in (("bold", "b"), ("italic", "i")):
                el = rp.find(q(tag))
                if s.get(key) and (el is None or el.get(q("val"), "1") not in {"1", "true", "on"}):
                    add("ERROR", "layout-convention", where, f"Expected {key} role treatment")
    anchors = root.xpath(".//wp:anchor", namespaces=NS)
    if anchors:
        add("ERROR", "F05", "document", f"{len(anchors)} floating DrawingML object(s); convert to inline and review")
    legacy = root.xpath(".//w:pict | .//o:OLEObject", namespaces=NS)
    if legacy:
        add("NOT VERIFIED", "F05/F06", "document", f"{len(legacy)} legacy image/OLE nodes; inspect inline placement and editability")
    if root.xpath(".//w:headerReference | .//w:footerReference", namespaces=NS):
        add("NOT VERIFIED", "production-furniture", "document", "Existing header/footer parts preserved; inspect contents")
    counts = {lang: len(" ".join(" ".join(parts).split())) for lang, parts in abstracts.items()}
    for lang, count in counts.items():
        if not count:
            add("NOT VERIFIED", "M03/M04", "document", f"No {lang} abstract role assigned")
    if 0 < counts["en"] < 1800:
        add("WARN", "M04", "English abstract", f"{counts['en']} characters including spaces; below provisional ~1800 target")
    add("NOT VERIFIED", "F04", "document", "Actual page count requires rendering")
    return dict(profile=profile, findings=findings, abstract_characters_including_spaces=counts,
                errors=sum(f["status"] == "ERROR" for f in findings),
                scope="Automated layout subset only; manual content, policy and visual review required")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("inspect", "format", "check"))
    ap.add_argument("docx", type=Path)
    ap.add_argument("--roles", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--original", type=Path)
    ap.add_argument("--profile", choices=("guide", "published"), default="guide")
    args = ap.parse_args(argv)
    if args.out.resolve() in {p.resolve() for p in (args.docx, args.roles, args.original) if p}:
        ap.error("Output must differ from all input paths")
    try:
        members, root = read_docx(args.docx)
        if args.command == "inspect":
            write_json(args.out, inventory(args.docx, root))
            return 0
        if not args.roles:
            raise ValueError("--roles is required")
        if args.command == "check" and not args.original:
            raise ValueError("check requires --original for preservation verification")
        original_path = args.original if args.command == "check" else args.docx
        before, original_root = read_docx(original_path)
        entries = load_roles(args.roles, root, original_path)
        if args.command == "check":
            report = check(root, entries, args.profile, special_font_styles(members))
            report["preservation"] = preservation(before, members, original_root, root)
            report["errors"] += sum(not v for v in report["preservation"].values())
            write_json(args.out, report)
            print(json.dumps({"errors": report["errors"], "report": str(args.out)}, ensure_ascii=False))
            return int(report["errors"] > 0)
        apply(root, entries, args.profile, special_font_styles(members))
        updated = dict(members)
        updated[PART] = (members[PART][0], ET.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))
        invariant = preservation(before, updated, original_root, root)
        if not all(invariant.values()):
            raise ValueError(f"Preservation check failed: {invariant}")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(suffix=".docx", dir=args.out.parent)
        os.close(handle)
        try:
            with zipfile.ZipFile(temporary, "w") as z:
                for info, data in updated.values():
                    z.writestr(info, data)
            os.replace(temporary, args.out)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        print(json.dumps({"output": str(args.out), "profile": args.profile, "preservation": invariant}))
        return 0
    except (ValueError, OSError, zipfile.BadZipFile, ET.XMLSyntaxError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
