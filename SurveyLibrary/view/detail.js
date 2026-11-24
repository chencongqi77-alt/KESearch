import { introductions } from "./introductions.js";

const panel = document.querySelector("#details");
let afterClose;

function element(tag, className, text) {
  const el = document.createElement(tag);
  el.className = className;
  if (text !== undefined) el.textContent = text;
  return el;
}

function link(text, href, className) {
  const el = element("a", className, text);
  el.href = href;
  el.target = "_blank";
  el.rel = "noopener noreferrer";
  return el;
}

function paperRow(paper) {
  const row = element("li", "detail-paper");
  const hasSource = /^https?:\/\//i.test(paper.url);
  const title = hasSource
    ? link(paper.title, paper.url, "detail-paper-title")
    : element("span", "detail-paper-title", paper.title);
  const metadata = element("div", "detail-paper-meta");
  metadata.append(element("span", "detail-year", paper.year));
  // 每篇 PDF 保留索引中的原始文件名，包括空格、百分号等字符。
  const segments = paper.pdf?.split("/") ?? [];
  if (segments.length === 2 && segments[0] === "papers" && /\.pdf$/i.test(segments[1])) {
    const pdf = link("本地 PDF", "../papers/" + encodeURIComponent(segments[1]), "detail-pdf");
    pdf.setAttribute("aria-label", `${paper.title}（本地 PDF）`);
    metadata.append("·", pdf);
  }
  if (hasSource) {
    const source = link("原文", paper.url, "detail-source");
    source.setAttribute("aria-label", `${paper.title}（原文）`);
    metadata.append("·", source);
  }
  row.append(title, metadata);
  return row;
}

export function closeDetails() {
  if (panel.hidden) return;
  panel.hidden = true;
  panel.replaceChildren();
  const callback = afterClose;
  afterClose = undefined;
  callback?.();
}

document.addEventListener("keydown", event => {
  if (event.key === "Escape" && !panel.hidden) {
    event.preventDefault();
    closeDetails();
  }
});

export function showDetails(node, onClose) {
  afterClose = onClose;
  panel.innerHTML = `
    <header class="detail-heading">
      <h2 id="detail-name"></h2>
      <button type="button" class="detail-close" aria-label="关闭详情" title="关闭详情（Esc）">×</button>
    </header>
    <div class="detail-scroll" tabindex="0" aria-label="主题论文">
      <p class="detail-en" lang="en"></p>
      <div class="detail-range"></div>
      <p class="detail-intro"></p>
      <ul class="detail-list" id="detail-papers"></ul>
      <p class="detail-empty" hidden></p>
    </div>`;
  panel.querySelector("#detail-name").textContent = node.name_zh;
  panel.querySelector(".detail-en").textContent = node.name;
  const intro = panel.querySelector(".detail-intro");
  intro.textContent = introductions[node.id] ?? "";
  intro.hidden = !intro.textContent;
  const range = panel.querySelector(".detail-range");
  const list = panel.querySelector(".detail-list");
  const empty = panel.querySelector(".detail-empty");
  const scopes = { all: node.allPapers, direct: node.directPapers };

  function showPapers(scope) {
    const papers = [...scopes[scope]].sort((a, b) => b.year - a.year || a.title.localeCompare(b.title, "en"));
    for (const button of range.querySelectorAll("button")) {
      button.setAttribute("aria-pressed", String(button.dataset.scope === scope));
    }
    list.replaceChildren(...papers.map(paperRow));
    empty.hidden = papers.length > 0;
    empty.textContent = scope === "direct" ? "此节点没有直接收录的综述。" : "此主题暂无收录综述。";
  }

  if (node.children?.length) {
    range.setAttribute("role", "group");
    range.setAttribute("aria-label", "论文收录范围，按论文 ID 去重");
    for (const [scope, label] of [["all", "含下级"], ["direct", "直接"]]) {
      const button = element("button", "detail-scope", `${label} ${scopes[scope].length}`);
      button.type = "button";
      button.dataset.scope = scope;
      button.title = scope === "all" ? "本主题及其下级去重后的综述" : "直接标注本主题的综述";
      button.setAttribute("aria-controls", list.id);
      button.addEventListener("click", () => showPapers(scope));
      if (range.childElementCount) range.append("·");
      range.append(button);
    }
  } else {
    range.textContent = `${node.allPapers.length} 篇综述`;
  }
  panel.querySelector(".detail-close").addEventListener("click", closeDetails);
  showPapers("all");
  panel.hidden = false;
}
