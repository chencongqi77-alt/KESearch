import {action, icon, link, node, safeUrl} from "./dom.js";

const $ = (id) => document.getElementById(id);
const rootName = (section) => section.level === 0 ? "篇首" : section.title;

function inlineText(text) {
  const body = document.createDocumentFragment();
  const pattern = /\*\*([^*\n]+)\*\*|__([^_\n]+)__|\[([^\]\n]+)\]\((https?:\/\/[^)\s]+)\)|<(sub|sup)>([^<>]+)<\/\5>/gi;
  let start = 0;
  for (const match of text.matchAll(pattern)) {
    body.append(text.slice(start, match.index));
    const href = safeUrl(match[4]);
    if (match[5]) body.append(node(match[5].toLowerCase(), "", match[6]));
    else if (href) body.append(link(match[3], href));
    else body.append(node("strong", "", match[1] || match[2] || match[0]));
    start = match.index + match[0].length;
  }
  body.append(text.slice(start));
  return body;
}

const mathNs = "http://www.w3.org/1998/Math/MathML";
const mathTags = new Set("math mrow mi mn mo mtext mspace ms mfrac msqrt mroot msub msup msubsup munder mover munderover mtable mtr mtd mfenced menclose mstyle mpadded mphantom mmultiscripts mprescripts none".split(" "));
const mathAttrs = new Set("display mathvariant mathsize displaystyle scriptlevel linethickness stretchy fence separator largeop movablelimits accent accentunder lspace rspace form symmetric width height depth minsize maxsize columnalign rowalign columnspacing rowspacing columnlines rowlines frame notation open close separators".split(" "));

function mathNode(markup) {
  const source = new DOMParser().parseFromString(markup, "application/xml").documentElement;
  if (source.localName !== "math" || source.namespaceURI !== mathNs) return null;
  function copy(elem) {
    if (elem.namespaceURI !== mathNs || !mathTags.has(elem.localName)) return null;
    const result = document.createElementNS(mathNs, elem.localName);
    for (const attr of elem.attributes) {
      if (mathAttrs.has(attr.name)) result.setAttribute(attr.name, attr.value);
    }
    for (const child of elem.childNodes) {
      if (child.nodeType === Node.TEXT_NODE) result.append(child.textContent);
      if (child.nodeType === Node.ELEMENT_NODE) {
        const converted = copy(child);
        if (!converted) return null;
        result.append(converted);
      }
    }
    return result;
  }
  return copy(source);
}

function makeFormatter(lookup = {}) {
  const cache = new Map();
  return function format(text) {
    const body = document.createDocumentFragment();
    const pattern = /\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|(?<!\\)\$(?!\$)(?:\\.|[^$])+?(?<!\\)\$/g;
    let start = 0;
    for (const match of text.matchAll(pattern)) {
      const raw = match[0];
      if (typeof lookup[raw] !== "string") continue;
      if (!cache.has(raw)) cache.set(raw, mathNode(lookup[raw]));
      const math = cache.get(raw);
      if (!math) continue;
      body.append(inlineText(text.slice(start, match.index)));
      const display = raw.startsWith("$$") || raw.startsWith("\\[");
      const box = node("span", display ? "display-math" : "inline-math");
      box.append(math.cloneNode(true));
      body.append(box);
      start = match.index + raw.length;
    }
    body.append(inlineText(text.slice(start)));
    return body;
  };
}

function makeBlock(block, formatInline) {
  const src = block.type === "figure" ? safeUrl(block.src, true) : null;
  if (src) {
    const figure = node("figure", "source-figure");
    const anchor = node("a");
    anchor.href = src;
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    const img = node("img");
    img.alt = block.caption || "综述原图";
    img.loading = "lazy";
    img.decoding = "async";
    img.src = src;
    anchor.append(img);
    figure.append(anchor);
    const caption = node("figcaption");
    if (block.caption) caption.append(formatInline(block.caption));
    if (block.page) caption.append(node("span", "source-page", "第 " + block.page + " 页"));
    if (caption.hasChildNodes()) figure.append(caption);
    return figure;
  }
  const para = node("p");
  para.dataset.kind = block.kind || "paragraph";
  para.append(formatInline(String(block.text || block.caption || "")));
  return para;
}

function overviewFigure(data) {
  const topic = (data.title || "").toLowerCase().match(/[a-z]{4,}/g) || [];
  const filler = new Set("general survey comprehensive review overview methods deep learning applications challenges recent advances from into based".split(" "));
  let best;
  for (const section of data.sections || []) {
    for (const block of section.blocks || []) {
      if (block.type !== "figure" || block.kind === "table" || !block.src || !block.caption) continue;
      // Some MinerU captions contain a separate table label before the figure caption.
      const lines = block.caption.split(/\r?\n/);
      const figureLine = lines.findIndex((line) => /^(?:Fig(?:ure)?\.?\s*\d+|图\s*\d+)/i.test(line));
      const caption = (figureLine > 0 && /^(?:table|表)\s*\d+/i.test(lines[0]) ? lines.slice(figureLine).join("\n") : block.caption);
      const lead = caption.toLowerCase().slice(0, 280);
      if (!/taxonomy|overview|organization|organisation|framework|general structure|概览|总览|分类体系|分类框架|总体框架|全文结构/.test(lead)) continue;
      const surveyWide = /(?:this|our|the present)\s+(?:survey|review|article|paper)|(?:本综述|本文|全文)(?:的|所)?(?:结构|组织|分类|框架)|综述(?:总览|概览)/.test(lead);
      const mainTheme = topic.some((word) => !filler.has(word) && lead.includes(word));
      const taxonomy = /taxonomy|分类体系|分类框架/.test(lead) && /taxonomy|分类|概览|框架/i.test(section.title);
      const opening = /introduction|overview|引言|绪论|概述/i.test(section.title);
      const general = /general\s+(?:structure|framework)|unified\s+framework|总体框架/.test(lead);
      const score = surveyWide ? 3 : section.level <= 1 && taxonomy ? 2 : section.level <= 1 && opening && general && mainTheme ? 1 : 0;
      if (score && (!best || score > best.score)) best = {block: {...block, caption}, section, score};
    }
  }
  return best;
}

function summaryBody(text, formatInline) {
  const element = node("div", "summary-body");
  const paragraphs = text.split(/\n\s*\n/);
  let first = text, remainder = "";
  if (text.length > 460 && paragraphs.length > 1) {
    first = paragraphs.shift();
    remainder = paragraphs.join("\n\n");
  }
  const lead = node("p");
  lead.append(formatInline(first));
  element.append(lead);
  if (remainder) {
    const more = node("details", "summary-more");
    const toggle = node("summary", "", "展开完整总结");
    const para = node("p");
    para.append(formatInline(remainder));
    more.append(toggle, para);
    more.addEventListener("toggle", () => { toggle.textContent = more.open ? "收起总结" : "展开完整总结"; });
    element.append(more);
  }
  return element;
}

function docHeader(job, data, retry, formatInline, revealFigure) {
  const header = node("header", "doc-header");
  const metadata = [];
  if (data.pages) metadata.push(data.pages + " 页");
  if (Number.isFinite(data.reference_count)) metadata.push(data.reference_count + " 篇参考文献");
  if (data.figure_count) metadata.push(data.figure_count + " 幅图");
  header.append(node("h1", "", data.title || job.title || job.filename));
  const meta = node("div", "doc-meta");
  if (metadata.length) meta.append(node("span", "", metadata.join(" · ")));
  const base = "/api/jobs/" + encodeURIComponent(job.id);
  const tools = node("div", "doc-tools");
  if (job.has_pdf) tools.append(link("原始 PDF", base + "/pdf"));
  if (job.has_markdown) tools.append(link("Markdown", base + "/markdown", "download"));
  if (tools.hasChildNodes()) meta.append(tools);
  header.append(meta);
  const summary = data.summary;
  if (summary?.text || summary?.warning) {
    const box = node("div", "summary");
    const labels = {deepseek: "综述总结", abstract: "原文摘要", extract: "正文摘录"};
    if (summary.text) {
      box.append(node("h2", "summary-title", labels[summary.source] || "综述总结"));
      box.append(summaryBody(summary.text, formatInline));
    }
    if (summary.warning || (retry && summary.source !== "deepseek")) {
      const warning = node("p", "summary-warning", summary.warning);
      if (retry && summary.source !== "deepseek") {
        warning.append(action(summary.warning ? "重试摘要" : "生成 DeepSeek 总结", retry, "inline-button"));
      }
      box.append(warning);
    }
    header.append(box);
  }
  const overview = overviewFigure(data);
  if (overview) {
    const figure = makeBlock(overview.block, formatInline);
    figure.classList.add("overview-figure");
    const jump = action("定位原图", () => revealFigure(overview.section, overview.block.block_index), "page-link");
    figure.querySelector("figcaption")?.append(jump);
    header.append(figure);
  }
  return header;
}

const paperLabels = {arxiv: "arXiv 论文页", doi: "DOI 论文页", source: "论文来源页", arxiv_search: "arXiv 检索 · 待确认"};

function paperLinks(ref, prefix = "", group = node("span", "paper-links")) {
  if (!ref) return group;
  group.dataset.paperId = ref.id;
  group.dataset.labelPrefix = prefix;
  const urls = [ref.url, ...(Array.isArray(ref.alternate_urls) ? ref.alternate_urls : [])];
  const seen = new Set();
  let count = 0;
  urls.forEach((raw, index) => {
    const href = safeUrl(raw);
    if (!href) return;
    const url = new URL(href);
    if (url.username || url.password) return;
    const doi = /^(?:dx\.)?doi\.org$/i.test(url.hostname) && /^\/10\.\d{4,9}\//i.test(url.pathname);
    const identity = doi ? "doi:" + url.pathname.toLowerCase() : href.split("#")[0];
    if (seen.has(identity)) return;
    seen.add(identity);
    let label = paperLabels[ref.link_kind] || "论文来源页";
    if (index > 0) {
      const pdf = /\.pdf$/i.test(url.pathname) || (url.hostname === "arxiv.org" && url.pathname.startsWith("/pdf/"));
      label = "备用链接";
      if (doi) label = "备用 DOI";
      else if (pdf) label = "备用 PDF";
    }
    const text = prefix + label;
    let anchor = group.children[count++];
    if (!anchor) {
      anchor = link(text, href);
      group.append(anchor);
    } else {
      anchor.href = href;
      if (anchor.textContent !== text) anchor.replaceChildren(text, icon("external"));
    }
    anchor.classList.toggle("lookup-link", index === 0 && ref.link_kind === "arxiv_search");
  });
  while (group.children.length > count) group.lastElementChild.remove();
  return group;
}

function referenceRow(ref, showBlock, bibliography, formatInline, pdfUrl, linkRef) {
  const row = node("li", "reference");
  const head = node("div", "reference-head");
  if (ref.number != null) head.append(node("span", "ref-num", "[" + ref.number + "]"));
  head.append(node("h3", "", ref.title || ref.entry || "未识别题名"));
  row.append(head);
  row.append(paperLinks(linkRef || ref), node("p", "ref-hint missing-link", "暂无可用论文链接"));
  function excerpt(quote) {
    const figure = node("figure", "quote");
    const original = quote.source === "pdf";
    const caption = node("figcaption", "", original ? "原 PDF 摘录" : "综述原文");
    if (quote.page) {
      const page = "第 " + quote.page + " 页";
      if (original && pdfUrl && Number.isInteger(quote.page) && quote.page > 0) {
        const anchor = link(page, pdfUrl + "#page=" + quote.page);
        anchor.classList.add("pdf-page-link");
        caption.append(anchor);
      } else {
        const source = !original && showBlock(quote.block_index);
        caption.append(source ? action(page, source, "page-link") : node("span", "", page));
      }
    }
    const excerptText = node("blockquote");
    excerptText.append(formatInline(quote.text));
    figure.append(caption, excerptText);
    return figure;
  }
  const quotes = bibliography ? ref.pdf_excerpts || [] : ref.quotes || [];
  if (quotes.length) row.append(excerpt(quotes[0]));
  else if (!bibliography) row.append(node("p", "ref-hint", "本节未定位到可展示的介绍原文。"));
  if (quotes.length > 1) {
    const details = node("details", "more-quotes");
    details.append(node("summary", "", "其余 " + (quotes.length - 1) + " 处原文"));
    details.addEventListener("toggle", () => {
      if (details.open && details.childElementCount === 1) {
        for (const quote of quotes.slice(1)) details.append(excerpt(quote));
      }
    });
    row.append(details);
  }
  return row;
}

export function mobilePanel(name) {
  $("workspace").dataset.panel = name;
  for (const button of document.querySelectorAll(".mobile-panels button")) {
    if (button.dataset.panel === name) button.setAttribute("aria-current", "true");
    else button.removeAttribute("aria-current");
  }
}

function catalogue(data) {
  const works = new Map();
  // Older saved readers may keep the bibliography under its old key or only inside chapters.
  for (const list of [data.references || [], data.bibliography || [], ...(data.sections || []).map((s) => s.references || [])]) {
    for (const ref of list) if (!works.has(ref.id)) works.set(ref.id, ref);
  }
  return [...works.values()];
}

export function mountReader(job, data, retry, recheck) {
  const sections = data.sections || [];
  let bibliography = catalogue(data);
  const bibIndex = new Map(bibliography.map((ref) => [ref.id, ref]));
  const formatInline = makeFormatter(data.mathml);
  const pdfUrl = job.has_pdf ? "/api/jobs/" + encodeURIComponent(job.id) + "/pdf" : null;
  const outline = $("outline");
  const article = $("article");
  const body = $("body-pane");
  const buttons = new Map();
  const anchors = new Map();
  const blockNodes = new Map();
  let current;
  let frame;
  let highlighted;
  let highlightTimer;
  let lastTop = 0;
  const events = new AbortController();
  let lastCheck;

  function showLinkCheck(status) {
    const check = status.link_check;
    const pending = check?.status === "queued" || check?.status === "running";
    const busy = pending || status.status === "queued" || status.status === "running";
    const remaining = bibliography.filter((ref) => ref.link_kind === "arxiv_search").length;
    const key = JSON.stringify([check, busy, remaining]);
    if (lastCheck === key) return;
    lastCheck = key;
    const bar = $("link-check");
    bar.replaceChildren();
    bar.hidden = !remaining && !check;
    if (bar.hidden) return;
    const message = check?.message || ("全篇有 " + remaining + " 篇仅有检索入口。");
    bar.append(node("p", "", message));
    if (remaining && !busy) bar.append(action("核对全篇链接", recheck, "inline-button"));
    const summaryButton = article.querySelector(".summary-warning button");
    if (summaryButton) summaryButton.disabled = busy;
  }

  function applyLinks(updated) {
    bibliography = catalogue(updated);
    bibIndex.clear();
    for (const ref of bibliography) bibIndex.set(ref.id, ref);
    const bySection = new Map((updated.sections || []).map((section) => [section.id, section]));
    for (const section of sections) {
      const fresh = bySection.get(section.id);
      if (fresh) section.references = fresh.references || [];
    }
    // Keep the current paragraph, open quotation details and mobile panel in place.
    for (const group of $("workspace").querySelectorAll(".paper-links[data-paper-id]")) {
      paperLinks(bibIndex.get(group.dataset.paperId), group.dataset.labelPrefix, group);
    }
  }

  function reveal(section, target) {
    mobilePanel("body");
    const nearest = target || anchors.get(section.id);
    if (!nearest) return;
    body.scrollTop += nearest.getBoundingClientRect().top - body.getBoundingClientRect().top - 20;
    lastTop = body.scrollTop;
    select(section);
    nearest.focus({preventScroll: true});
  }
  function showBlock(index) {
    const elem = blockNodes.get(current.id)?.get(index);
    if (!elem) return null;
    return () => {
      reveal(current, elem);
      highlighted?.classList.remove("located");
      clearTimeout(highlightTimer);
      highlighted = elem;
      elem.classList.add("located");
      highlightTimer = setTimeout(() => elem.classList.remove("located"), 2400);
    };
  }
  function select(section) {
    if (current?.id === section.id) return;
    if (current) buttons.get(current.id)?.removeAttribute("aria-current");
    current = section;
    const button = buttons.get(section.id);
    button?.setAttribute("aria-current", "location");
    if (button && outline.clientHeight) {
      const box = button.getBoundingClientRect();
      const pane = outline.getBoundingClientRect();
      if (box.top < pane.top || box.bottom > pane.bottom) outline.scrollTop += box.top - pane.top - 16;
    }
    const isBibliography = bibliography.length > 0 && (
      (section.blocks?.length && section.blocks.every((block) => block.bibliography_ids?.length)) ||
      /^(?:[\d.\s]+)?(?:references|bibliography|参考文献|引用文献)[\s.:：]*$/i.test(section.title.trim())
    );
    const refs = isBibliography ? bibliography : section.references || [];
    $("references-heading").replaceChildren(icon("references"), isBibliography ? "全部书目" : "本节引用");
    $("reference-total").textContent = refs.length + " 篇";
    $("mobile-ref-count").textContent = String(refs.length);
    $("reference-section").textContent = rootName(section);
    const container = $("references");
    container.replaceChildren();
    if (refs.length) {
      const list = node("ol", "reference-list");
      for (const ref of refs) list.append(referenceRow(ref, showBlock, isBibliography, formatInline, pdfUrl, bibIndex.get(ref.id)));
      container.append(list);
    } else {
      container.append(node("p", "ref-empty", "这一节没有已匹配的参考论文。"));
      const index = sections.indexOf(section);
      const nearby = sections.slice(index + 1).find((item) => item.references?.length);
      if (nearby) {
        const jump = action("前往 " + rootName(nearby), () => reveal(nearby), "next-ref");
        jump.append(icon("arrow-right"));
        container.append(jump);
      }
    }
    $("reference-scroll").scrollTop = 0;
  }

  article.replaceChildren(docHeader(job, data, retry, formatInline, (section, index) => reveal(section, blockNodes.get(section.id)?.get(index))));
  outline.replaceChildren();
  $("section-total").textContent = sections.filter((s) => s.level !== 0).length + " 节";
  const outlineItems = document.createDocumentFragment();
  const content = document.createDocumentFragment();
  for (const section of sections) {
    const name = rootName(section);
    const overview = section.level === 0;
    const item = action(overview ? "综述总览" : name, () => {
      if (overview) {
        mobilePanel("body");
        body.scrollTop = lastTop = 0;
        select(section);
        const heading = article.querySelector("h1");
        heading.tabIndex = -1;
        heading.focus({preventScroll: true});
      } else reveal(section);
    }, "toc-item");
    item.dataset.depth = String(Math.max(0, Math.min(4, (section.level || 1) - 1)));
    buttons.set(section.id, item);
    outlineItems.append(item);
    const part = node("section", section.level === 0 ? "doc-section front-matter" : "doc-section");
    part.tabIndex = 0;
    part.setAttribute("aria-label", name);
    anchors.set(section.id, part);
    if (section.level !== 0) part.append(node(section.level > 1 ? "h3" : "h2", "", name));
    const nodes = new Map();
    blockNodes.set(section.id, nodes);
    for (const block of section.blocks || []) {
      const element = makeBlock(block, formatInline);
      if (block.bibliography_ids?.length) {
        const links = node("span", "bibliography-links");
        for (const id of block.bibliography_ids) {
          const ref = bibIndex.get(id);
          if (ref) links.append(paperLinks(ref, block.bibliography_ids.length > 1 && ref.number != null ? "[" + ref.number + "] " : ""));
        }
        if (links.hasChildNodes()) element.append(links);
      }
      if (block.block_index != null) {
        element.tabIndex = -1;
        if (!nodes.has(block.block_index)) nodes.set(block.block_index, element);
      }
      part.append(element);
    }
    const choose = () => {
      cancelAnimationFrame(frame);
      lastTop = body.scrollTop;
      select(section);
    };
    part.addEventListener("click", choose);
    part.addEventListener("focusin", choose);
    content.append(part);
  }
  outline.append(outlineItems);
  article.append(content);
  body.scrollTop = 0;
  mobilePanel("body");
  const first = sections.find((s) => s.level !== 0 || s.blocks?.length || s.references?.length);
  if (first) select(first);
  else {
    $("reference-total").textContent = "0 篇";
    $("mobile-ref-count").textContent = "0";
    $("reference-section").textContent = "";
    $("references").replaceChildren(node("p", "ref-empty", "这篇综述尚无可展示的章节引用。"));
  }

  // Read the section at the top of the body without stealing a user's explicit selection.
  lastTop = body.scrollTop;
  body.addEventListener("scroll", () => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      if (body.scrollTop === lastTop || !body.clientHeight) return;
      lastTop = body.scrollTop;
      const threshold = body.getBoundingClientRect().top + 26;
      let visible = first;
      for (const section of sections) {
        const part = anchors.get(section.id);
        if (part.getBoundingClientRect().top > threshold) break;
        if (part.offsetHeight) visible = section;
      }
      // At the end, a short final section can never reach the top of the viewport.
      if (body.scrollTop > 0 && Math.ceil(body.scrollTop + body.clientHeight) >= body.scrollHeight) {
        visible = sections.at(-1);
      }
      if (visible) select(visible);
    });
  }, {signal: events.signal, passive: true});
  return {
    showLinkCheck, applyLinks,
    dispose() {
      events.abort();
      clearTimeout(highlightTimer);
      cancelAnimationFrame(frame);
    },
  };
}
