import { closeDetails, showDetails } from "./detail.js";

const tree = document.querySelector("#tree");
const viewport = document.querySelector("#viewport");
let selected;
let scrollAnchor;

async function readJSON(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(path);
  return response.json();
}

function buildTree(taxonomy, papers) {
  const rootName = "大语言模型综述";
  const uniquePapers = new Map(papers.map(paper => [paper.id, paper]));
  const byTopic = new Map();
  for (const paper of uniquePapers.values()) {
    for (const topic of new Set(paper.topics)) {
      if (!byTopic.has(topic)) byTopic.set(topic, []);
      byTopic.get(topic).push(paper);
    }
  }

  function buildTopic(topic, depth) {
    const children = (topic.children ?? []).map(child => buildTopic(child, depth + 1));
    const directPapers = byTopic.get(topic.id) ?? [];
    const all = new Map(directPapers.map(paper => [paper.id, paper]));
    for (const child of children) {
      for (const paper of child.allPapers) all.set(paper.id, paper);
    }
    return { ...topic, depth, children, directPapers, allPapers: [...all.values()] };
  }

  return {
    id: "root", depth: 0, name_zh: rootName, name: "Large Language Model Surveys",
    children: taxonomy.map(topic => buildTopic(topic, 1)),
    directPapers: [], allPapers: [...uniquePapers.values()],
  };
}

function clearSelection() {
  if (!selected) return;
  selected.classList.remove("is-selected");
  // On a leaf aria-expanded describes the paper panel. On a parent it describes its branch.
  if (!selected.nextElementSibling) selected.setAttribute("aria-expanded", "false");
  selected = null;
}

function selectTopic(node, button) {
  clearSelection();
  selected = button;
  button.classList.add("is-selected");
  button.setAttribute("aria-expanded", "true");
  document.querySelector("#details").style.setProperty("--topic-bg", getComputedStyle(button).getPropertyValue("--topic-bg"));
  showDetails(node, () => {
    clearSelection();
    if (!button.closest("[hidden], [inert]")) button.focus({ preventScroll: true });
  });
}

function anchorDuringReveal(button) {
  const reveal = button.nextElementSibling;
  const motion = reveal.getAnimations().find(animation => animation.transitionProperty === "grid-template-rows");
  if (!motion) return;

  // Compensate only for layout changes, so the reader can still scroll during the transition.
  const layoutTop = () => button.getBoundingClientRect().top + viewport.scrollTop;
  let previous = layoutTop();
  const observer = new ResizeObserver(() => {
    const current = layoutTop();
    viewport.scrollTop += current - previous;
    previous = current;
  });
  observer.observe(reveal);
  scrollAnchor = observer;
  const stop = () => observer.disconnect();
  motion.finished.then(stop, stop);
}

function renderNode(node, expanded = false) {
  const row = document.createElement("li");
  const button = document.createElement("button");
  button.type = "button";
  button.className = "node " + ["root", "primary", "leaf"][node.depth];
  button.dataset.topic = node.id;
  const label = document.createElement("span");
  label.textContent = node.name_zh;
  button.append(label);
  row.append(button);

  let children;
  if (node.children.length) {
    children = document.createElement("ul");
    children.id = "children-" + node.id;
    node.children.forEach((child, index) => {
      children.append(renderNode(child, node.depth === 0 && index === 0));
    });
    if (node.depth === 1) {
      const reveal = document.createElement("div");
      reveal.className = "branch-reveal";
      children.inert = !expanded;
      reveal.append(children);
      row.append(reveal);
    } else {
      children.hidden = !expanded;
      row.append(children);
    }
  }

  button.setAttribute("aria-controls", children ? children.id + " details" : "details");
  button.setAttribute("aria-expanded", String(expanded));
  button.addEventListener("click", () => {
    scrollAnchor?.disconnect();
    if (!children) {
      if (selected === button) closeDetails();
      else selectTopic(node, button);
      return;
    }

    const before = button.getBoundingClientRect().top;
    const opening = button.getAttribute("aria-expanded") === "false";
    button.setAttribute("aria-expanded", String(opening));
    if (node.depth === 1) children.inert = !opening;
    else children.hidden = !opening;
    if (opening) {
      selectTopic(node, button);
    } else if (selected && row.contains(selected)) {
      closeDetails();
      button.focus({ preventScroll: true });
    }
    viewport.scrollTop += button.getBoundingClientRect().top - before;
    button.scrollIntoView({ block: "nearest", inline: "nearest" });
    if (node.depth === 1) anchorDuringReveal(button);
  });
  return row;
}

async function start() {
  const status = document.querySelector("#status");
  try {
    const [taxonomy, papers] = await Promise.all([readJSON("../taxonomy.json"), readJSON("../index.json")]);
    tree.append(renderNode(buildTree(taxonomy, papers), true));
    tree.hidden = false;
    status.hidden = true;
  } catch {
    status.textContent = "无法读取分类或论文索引，请从 SurveyLibrary 目录启动静态服务后刷新。";
  }
}

start();
