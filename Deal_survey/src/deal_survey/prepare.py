"""Build a section-by-section reading pack from one downloaded survey PDF."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
from html import unescape
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from .citations import bibliography_indices, build_citations
from .mineru_pdf import load_parse, parse_pdf
from .pdf_check import check_pdf_citations
from .settings import load_service_env
from .structure import locate_passages, pdf_outline


def build_pack(pdf_path, archive_path, receipt_path=None):
    blocks, source = load_parse(pdf_path, archive_path, receipt_path=receipt_path)
    title, bookmarks, diagnostics = pdf_outline(pdf_path)
    sections, units, issues = locate_passages(blocks, bibliography_indices(blocks), bookmarks, title)
    evidence = build_citations(blocks, units)
    references, mentions = evidence["references"], evidence["mentions"]
    by_section = {section["id"]: section for section in sections}
    by_work = {ref["id"]: ref for ref in references}
    for section in sections:
        section.update(reference_ids=[], mention_ids=[])
    for ref in references:
        ref.update(section_ids=[], mention_ids=[])
    for mention in mentions:
        section = by_section[mention["section_id"]]
        section["mention_ids"].append(mention["id"])
        for ref_id in mention["reference_ids"]:
            ref = by_work[ref_id]
            if ref_id not in section["reference_ids"]:
                section["reference_ids"].append(ref_id)
            if section["id"] not in ref["section_ids"]:
                ref["section_ids"].append(section["id"])
            ref["mention_ids"].append(mention["id"])
    subtree = {s["id"]: set(s["reference_ids"]) for s in sections}
    for section in reversed(sections):
        ids = subtree[section["id"]]
        section["subtree_reference_ids"] = sorted(ids)
        if section["parent_id"]:
            subtree[section["parent_id"]].update(ids)
    status_counts = Counter(item["status"] for item in mentions)
    original_check = check_pdf_citations(pdf_path, references, mentions)
    # Both the bookmark reader and the PDF-link checker reopen the user's file.
    with open(pdf_path, "rb") as source_file:
        if hashlib.file_digest(source_file, "sha256").hexdigest() != source["source_sha256"]:
            raise ValueError("准备精读材料期间原 PDF 已改变，请用完整原件重新运行")
    return {"schema_version": 1, "title": sections[0]["title"] or Path(pdf_path).stem,
            "source": {**source, "pdf_name": Path(pdf_path).name},
            "counts": {"sections": len(sections) - 1, "bibliography_entries": len(references),
                       "cited_entries": sum(bool(ref["mention_ids"]) for ref in references),
                       "markers": len(mentions), "marker_status": dict(status_counts)},
            "sections": sections, "references": references, "mentions": mentions,
            "pdf_check": original_check,
            "diagnostics": [*diagnostics, *issues, *evidence["diagnostics"]]}


def _display(text):
    return " ".join(text.split())


def _ref_label(ref):
    return f'[{ref["number"]}]' if ref["number"] is not None else ref["id"]


def render_reading(pack):
    refs = {ref["id"]: ref for ref in pack["references"]}
    mentions = {mention["id"]: mention for mention in pack["mentions"]}
    counts = pack["counts"]
    lines = ["# " + _display(pack["title"]), "", "## 精读范围", "",
             f"从 {pack['source']['pdf_pages']} 页 PDF 的解析中识别出 {counts['sections']} 个章节标题、"
             f"{counts['bibliography_entries']} 条书目。正文、图表等位置有 {counts['markers']} 处引文标记，"
             f"其中能唯一关联到的书目有 {counts['cited_entries']} 条。",
             "", "下文摘录综述作者讨论这些论文的原文。页码指 MinerU 结构块的起始物理页，跨页段落可回查原 PDF。"]
    if pack["source"]["page_scope"] == "unverified":
        lines += ["", "本包缺少完整页范围回执，全文覆盖情况待核。"]
    check = pack["pdf_check"]
    by_number = {ref["number"]: ref for ref in refs.values() if ref["number"] is not None}
    missing = {d["label"]: d for d in check["differences"] if d["parsed_count"] == 0 and d["pdf_count"]}
    if check["status"] == "unverified":
        lines += ["", f"PDF 原始引文跳转核验未完成（{check.get('reason', 'unknown')}）。"]
    else:
        lines += ["", "已根据原 PDF 的印刷编号和书目跳转目标逐编号核对出现次数。", ""]
        for diff in check["differences"]:
            ref = by_number.get(diff["label"])
            title = _display(ref["title"] or ref["entry"]) if ref else ""
            lines.append(f"- [{diff['label']}] {title}。原 PDF 有 {diff['pdf_count']} 次跳转，解析有 {diff['parsed_count']} 次标记。")
            for item in diff.get("pdf_excerpts", []):
                lines += [f"  - 原 PDF 第 {item['page']} 页摘录：{_display(item['quote'])}"]
    lines += ["", "## 章节索引", "",
              "| 章节 | 本节直接引用的论文 | 含子节的论文（去重） |", "| --- | ---: | ---: |"]
    for section in pack["sections"][1:]:
        label = " › ".join(section["path"]).replace("|", "\\|")
        if section["mention_ids"]:
            label = f"[{label}](#{section['id']})"
        lines.append(f"| {label} | {len(section['reference_ids'])} | {len(section['subtree_reference_ids'])} |")
    lines += ["", "## 按章节精读", ""]
    for section in pack["sections"]:
        if not section["mention_ids"]:
            continue
        lines += [f'<a id="{section["id"]}"></a>', "", "### " + " › ".join(section["path"] or ["篇首"]), ""]
        contexts = defaultdict(list)
        for mention_id in section["mention_ids"]:
            m = mentions[mention_id]
            contexts[(m["block_index"], m["field"], m["field_offset"], m["context_start"], m["context_end"])].append(m)
        for group in contexts.values():
            first = group[0]
            used = dict.fromkeys(rid for m in group for rid in m["reference_ids"])
            titles = [f"{_ref_label(refs[rid])} {_display(refs[rid]['title'] or refs[rid]['entry'])}" for rid in used]
            titles.extend(f"{m['marker']}（有待核对的引文）" for m in group if m["status"] != "matched")
            page = f"第 {first['page']} 页" if first["page"] else "页码待核"
            lines += [f"**{page}** · " + "；".join(titles), ""]
            quote = first["context"]
            if first["field"] == "table_body":
                quote = unescape(re.sub(r"</?[^>]+>", " ", quote))
            lines += ["> " + _display(quote), ""]
    lines += ["## 按被引论文回查", ""]
    paths = {s["id"]: f"[{' › '.join(s['path'] or ['篇首'])}](#{s['id']})" for s in pack["sections"]}
    for ref in pack["references"]:
        locations = "；".join(paths[s] for s in ref["section_ids"])
        if not locations and ref["number"] in missing:
            pages = "、".join(str(p) for p in missing[ref["number"]]["pdf_pages"])
            locations = f"原 PDF 第 {pages} 页有引文跳转，详见篇首原页核验。"
        lines += ["- " + _display(ref["entry"]), "  - " + (locations or "当前解析未匹配到正文引文。")]
    return "\n".join(lines) + "\n"


def prepare(pdf, out, *, archive=None, receipt=None, model="vlm", max_wait_seconds=900):
    pdf, out = Path(pdf).resolve(strict=True), Path(out).resolve()
    if receipt and not archive:
        raise ValueError("--receipt 适用于 --mineru-zip 回放")
    final = out / "reading"
    if final.exists():
        raise FileExistsError(f"精读结果已存在，请指定新的 --out：{final}")
    if archive is None:
        archive = parse_pdf(pdf, out / "cloud", model=model, max_wait_seconds=max_wait_seconds)["result_zip"]
    pack = build_pack(pdf, archive, receipt)
    out.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=out, prefix=".prepare-") as staging:
        ready = Path(staging) / "reading"
        ready.mkdir()
        (ready / "survey.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8", newline="\n")
        (ready / "reading.md").write_text(render_reading(pack), encoding="utf-8", newline="\n")
        ready.rename(final)
    return final, pack["counts"]


def main(argv=None):
    cli = argparse.ArgumentParser(description="从本地综述 PDF 生成逐章节精读材料；有 MinerU ZIP 时可离线回放。")
    cli.add_argument("--pdf", type=Path, required=True, help="已下载的综述 PDF")
    cli.add_argument("--out", type=Path, required=True, help="本次结果目录")
    cli.add_argument("--mineru-zip", type=Path, help="已有的 MinerU v1 结果 ZIP；省略时上传 PDF 到 MinerU")
    cli.add_argument("--receipt", type=Path, help="已有云回执；默认检查 ZIP 旁的 result.json")
    cli.add_argument("--model", choices=["vlm", "pipeline"], help="默认读取 KET_MINERU_MODEL，缺省为 vlm")
    cli.add_argument("--max-wait-seconds", type=int, default=900, help="新云任务等待预算")
    args = cli.parse_args(argv)
    try:
        if args.mineru_zip is None:
            load_service_env()
        path, counts = prepare(args.pdf, args.out, archive=args.mineru_zip, receipt=args.receipt,
                               model=args.model or os.environ.get("KET_MINERU_MODEL") or "vlm",
                               max_wait_seconds=args.max_wait_seconds)
    except (OSError, ValueError, RuntimeError) as exc:
        cli.exit(1, f"精读准备失败：{exc}\n")
    print(json.dumps({"reading": str(path), **counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
