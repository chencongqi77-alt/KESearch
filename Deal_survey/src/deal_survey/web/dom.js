const paths = {
  library: ["M4 5v14", "M8 5v14", "M12 5v14", "m16 5 4 13"],
  upload: ["M12 15V3", "m7 8 5-5 5 5", "M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"],
  document: ["M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z", "M14 2v6h6", "M8 13h8", "M8 17h6"],
  outline: ["M8 6h12M8 12h12M8 18h12", "M4 6h.01M4 12h.01M4 18h.01"],
  references: ["M3 5a3 3 0 0 1 3-2h3a4 4 0 0 1 3 2 4 4 0 0 1 3-2h3a3 3 0 0 1 3 2v14h-5a5 5 0 0 0-4 2 5 5 0 0 0-4-2H3z", "M12 5v16"],
  external: ["M14 4h6v6", "m20 4-9 9", "M10 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-4"],
  download: ["M12 3v12", "m7 10 5 5 5-5", "M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"],
  close: ["m6 6 12 12M18 6 6 18"],
  "arrow-right": ["M4 12h15", "m13 6 6 6-6 6"],
  check: ["m4 12 5 5L20 6"],
  alert: ["M12 7v6", "M12 17h.01", "M10 3a2.4 2.4 0 0 1 4 0l8 15a2 2 0 0 1-2 3H4a2 2 0 0 1-2-3z"],
};

export function icon(name) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  for (const [key, value] of Object.entries({
    viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", "stroke-width": "1.65",
    "stroke-linecap": "round", "stroke-linejoin": "round", "aria-hidden": "true",
  })) svg.setAttribute(key, value);
  for (const d of paths[name] || []) {
    const path = document.createElementNS(ns, "path");
    path.setAttribute("d", d);
    svg.append(path);
  }
  return svg;
}

export function node(tag, className, content) {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (content != null) result.textContent = content;
  return result;
}

export function action(label, callback, className = "plain-button") {
  const button = node("button", className, label);
  button.type = "button";
  button.addEventListener("click", callback);
  return button;
}

export function safeUrl(raw, local = false) {
  if (typeof raw !== "string" || !raw.trim()) return null;
  try {
    const url = local ? new URL(raw, location.origin) : new URL(raw);
    if (url.protocol !== "https:" && url.protocol !== "http:") return null;
    if (local && url.origin !== location.origin) return null;
    return url.href;
  } catch { return null; }
}

export function link(label, href, iconName = "external") {
  const item = node("a", "text-link", label);
  item.href = href;
  item.target = "_blank";
  item.rel = "noopener noreferrer";
  item.append(icon(iconName));
  return item;
}
