"""Optional presentation MathML for the reader; citation text and offsets stay verbatim."""
from __future__ import annotations

from html import unescape
import re
from xml.etree import ElementTree

from .citations import MATH_OR_CODE


NAMESPACE = "http://www.w3.org/1998/Math/MathML"
TAGS = frozenset("math mrow mi mn mo ms mtext mspace mfrac msqrt mroot mstyle merror mpadded mphantom "
                 "mfenced menclose msub msup msubsup munder mover munderover mmultiscripts mprescripts "
                 "none mtable mtr mlabeledtr mtd".split())
TOKEN_ATTRIBUTES = frozenset("mathvariant stretchy fence separator accent accentunder movablelimits "
                             "largeop symmetric form columnalign rowalign displaystyle "
                             "notation columnlines rowlines align".split())
LENGTH_ATTRIBUTES = frozenset("width height depth lspace rspace minsize maxsize linethickness".split())
UNSAFE_TEX = re.compile(r"\\(?:def|gdef|edef|xdef|let|futurelet|newcommand|renewcommand|providecommand|global|"
                        r"catcode|input|include|includegraphics|href|url|html\w*|write|openout|read|csname|"
                        r"expandafter|require|usepackage|documentclass|newenvironment|renewenvironment)\b", re.I)


def _supported(tex):
    if not tex.strip() or len(tex) > 4096 or UNSAFE_TEX.search(tex):
        return False
    depth = 0
    for part in re.finditer(r"\\.|[{}]", tex):
        if part[0] == "{":
            depth += 1
        elif part[0] == "}":
            depth -= 1
        if not 0 <= depth <= 32:
            return False
    return depth == 0


def _render(convert, source):
    display = source.startswith(("$$", r"\["))
    delimiter_size = 1 if source.startswith("$") and not display else 2
    tex = source[delimiter_size:-delimiter_size].strip()
    if not _supported(tex):
        return None
    # Work with the converter's tree, decoding math entities only as text.
    # Serializing the cleaned tree escapes angle brackets in typeset user input.
    root = convert(tex, display="block" if display else "inline")
    for element in root.iter():
        if element.tag not in TAGS:
            return None
        attrs = element.attrib.copy()
        element.attrib.clear()
        for name, value in attrs.items():
            if name in TOKEN_ATTRIBUTES and re.fullmatch(r"[a-zA-Z -]{1,96}", value):
                element.set(name, value)
            elif name in LENGTH_ATTRIBUTES and re.fullmatch(r"-?(?:\d{1,2}(?:\.\d{1,4})?|\.\d{1,4})(?:em|ex|px|pt|%)?", value):
                element.set(name, value)
        if element.text:
            element.text = unescape(element.text)
        if element.tail:
            element.tail = unescape(element.tail)
    root.set("xmlns", NAMESPACE)
    root.set("display", "block" if display else "inline")
    return ElementTree.tostring(root, encoding="unicode")


def formula_dictionary(sections):
    try:
        from latex2mathml.converter import convert_to_element
    except ImportError:
        return {}
    result, seen = {}, set()
    total_chars = 0
    for section in sections:
        texts = [block["text"] for block in section["blocks"] if block.get("kind") != "code"]
        # Table cells may be present only as image pixels in the body, yet their
        # quoted text in the citation panel is available from the content list.
        texts.extend(q["text"] for ref in section["references"] for q in ref["quotes"])
        for text in texts:
            for token in MATH_OR_CODE.finditer(text):
                if token.group("ticks"):
                    continue
                source = token[0]
                if source in seen or len(source) > 4100:
                    continue
                if len(seen) >= 1024 or total_chars > 4 * 1024 * 1024:
                    return result
                seen.add(source)
                try:
                    rendered = _render(convert_to_element, source)
                except Exception:
                    # Parser exceptions vary by version. Keep the exact original formula.
                    continue
                if rendered:
                    result[source] = rendered
                    total_chars += len(rendered)
    return result
