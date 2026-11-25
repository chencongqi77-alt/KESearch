import {action, icon, node} from "./dom.js";
import {mobilePanel, mountReader} from "./reader-view.js";

const $ = (id) => document.getElementById(id);
const statusNames = {queued: "等待解析", running: "解析中", ready: "可阅读", failed: "解析失败"};
const stages = {queued: "等待解析", mineru: "MinerU 解析 PDF", structure: "整理章节与引用", summary: "DeepSeek 生成总结"};
let requestVersion = 0;
let poll;
let readerView;
let readerKey;
let activeJob;
let file;

for (const element of document.querySelectorAll("[data-icon]")) element.replaceChildren(icon(element.dataset.icon));
for (const button of document.querySelectorAll(".mobile-panels button")) {
  button.addEventListener("click", () => mobilePanel(button.dataset.panel));
}
for (const close of document.querySelectorAll("[data-close]")) {
  close.addEventListener("click", () => close.closest("dialog").close());
}

async function api(path, options) {
  let response;
  try { response = await fetch(path, {cache: "no-store", ...options}); }
  catch { throw new Error("无法连接工作台，请检查本地服务后重试。"); }
  let result;
  try { result = await response.json(); }
  catch { throw new Error("服务响应异常，请重新连接。"); }
  if (!response.ok) throw new Error(result.error || "请求未完成，请重试。");
  return result;
}

function notice(text, button) {
  const bar = $("notice");
  bar.replaceChildren();
  if (text) bar.append(node("span", "", text));
  if (button) bar.append(button);
  bar.hidden = !text;
}

function landing(title, message, control, mark = "document", filename = "") {
  readerKey = null;
  readerView?.dispose();
  readerView = null;
  $("workspace").hidden = true;
  const host = $("landing");
  host.hidden = false;
  const contents = node("div", "landing-content");
  const symbol = node("div", "landing-symbol");
  symbol.append(icon(mark));
  contents.append(symbol, node("h1", "", title));
  if (filename) contents.append(node("p", "status-filename", filename));
  if (message) contents.append(node("p", "landing-message", message));
  if (control) contents.append(control);
  host.replaceChildren(contents);
}

function emptyLibrary() {
  activeJob = null;
  const upload = action("选择 PDF", openUpload, "primary-button");
  upload.prepend(icon("upload"));
  landing("从一篇综述开始", "上传 PDF，按目录阅读综述和原图，查看每节引用的论文与介绍原文。", upload, "references");
}

function selectFile(next) {
  file = null;
  $("upload-error").hidden = true;
  if (next) {
    if (!next.name.toLowerCase().endsWith(".pdf") && next.type !== "application/pdf") setUploadError("请选择 PDF 文件。");
    else if (!next.size || next.size > 200 * 1024 * 1024) setUploadError("请选择大于 0 字节且不超过 200 MiB 的 PDF。");
    else file = next;
  }
  $("file-name").textContent = file ? file.name : "选择或拖入 PDF";
  $("file-detail").textContent = file ? (file.size / 1024 / 1024).toFixed(2) + " MiB · 点击更换文件" : "最多 200 页，单个文件不超过 200 MiB";
  $("upload-submit").disabled = !file;
}

function setUploadError(message) {
  $("upload-error").textContent = message;
  $("upload-error").hidden = false;
}

function openUpload() {
  $("file-input").value = "";
  selectFile(null);
  $("upload-dialog").showModal();
}
$("upload-button").addEventListener("click", openUpload);
$("file-drop").addEventListener("click", () => $("file-input").click());
$("file-input").addEventListener("change", (event) => selectFile(event.target.files[0]));
for (const name of ["dragenter", "dragover", "dragleave", "drop"]) {
  $("file-drop").addEventListener(name, (event) => {
    event.preventDefault();
    $("file-drop").classList.toggle("dragging", name === "dragenter" || name === "dragover");
    if (name === "drop" && !$("file-drop").disabled) {
      if (event.dataTransfer.files.length > 1) {
        selectFile(null);
        setUploadError("一次请选择一篇综述。");
      } else selectFile(event.dataTransfer.files[0]);
    }
  });
}
$("upload-submit").addEventListener("click", async () => {
  if (!file || $("upload-submit").disabled) return;
  const dialog = $("upload-dialog");
  const closers = dialog.querySelectorAll("[data-close]");
  const preventClose = (event) => event.preventDefault();
  dialog.addEventListener("cancel", preventClose);
  for (const close of closers) close.disabled = true;
  $("upload-submit").disabled = true;
  $("file-drop").disabled = true;
  $("upload-submit").textContent = "正在上传…";
  $("upload-error").hidden = true;
  try {
    const result = await api("/api/jobs?filename=" + encodeURIComponent(file.name), {
      method: "POST", headers: {"Content-Type": "application/pdf"}, body: file,
    });
    dialog.close();
    openJob(result.id, true, result);
  } catch (error) { setUploadError(error.message); }
  finally {
    dialog.removeEventListener("cancel", preventClose);
    for (const close of closers) close.disabled = false;
    $("file-drop").disabled = false;
    $("upload-submit").disabled = !file;
    $("upload-submit").replaceChildren("上传并解析", icon("arrow-right"));
  }
});

async function loadLibrary() {
  const list = $("library-list");
  list.replaceChildren(node("p", "library-empty", "正在读取记录…"));
  try {
    const {jobs} = await api("/api/jobs");
    list.replaceChildren();
    if (!jobs.length) list.append(node("p", "library-empty", "尚未上传综述。"));
    for (const job of jobs) {
      const item = action("", () => {
        $("library-dialog").close();
        openJob(job.id, true);
      }, "library-item");
      item.append(icon("document"));
      const info = node("span", "library-info");
      info.append(node("strong", "", job.title || job.filename));
      info.append(node("small", "", [job.title ? job.filename : "", statusNames[job.status]].filter(Boolean).join(" · ")));
      item.append(info);
      if (job.id === activeJob?.id) {
        item.setAttribute("aria-current", "true");
        item.append(icon("check"));
      }
      list.append(item);
    }
  } catch (error) {
    list.replaceChildren(node("p", "library-empty", error.message), action("重新读取", loadLibrary));
  }
}
$("library-button").addEventListener("click", () => {
  $("library-dialog").showModal();
  loadLibrary();
});

function requestJobOperation(job, button, operation = "retry") {
  if (button) button.disabled = true;
  const version = requestVersion;
  api("/api/jobs/" + encodeURIComponent(job.id) + "/" + operation, {method: "POST"})
    .then((result) => { if (version === requestVersion) openJob(job.id, false, result); })
    .catch((error) => {
      if (version === requestVersion) notice(error.message);
      if (button) button.disabled = false;
    });
}

function loadingState(job) {
  const items = node("ol", "progress-stages");
  const steps = ["mineru", "structure", "summary"];
  const current = steps.indexOf(job.stage);
  for (const [index, step] of steps.entries()) {
    const item = node("li", "", stages[step]);
    const dot = node("span", "stage-dot");
    if (index < current) dot.append(icon("check"));
    item.prepend(dot);
    item.dataset.state = index === current ? "active" : index < current ? "done" : "pending";
    items.append(item);
  }
  items.setAttribute("aria-label", "解析阶段");
  landing(stages[job.stage] || "正在解析", job.message, items, "document", job.filename);
}

async function updateJob(id, version, initial) {
  const prefix = "/api/jobs/" + encodeURIComponent(id);
  try {
    const job = initial || await api(prefix);
    if (version !== requestVersion) return;
    const previous = activeJob;
    activeJob = job;
    document.title = (job.title || job.filename || "综述精读") + " · KESearch";
    const pending = job.status === "queued" || job.status === "running";
    const checking = ["queued", "running"].includes(job.link_check?.status);
    if (job.status === "ready" || job.has_reader) {
      if (readerKey !== job.id || (!pending && !checking)) {
        const data = await api(prefix + "/reader");
        if (version !== requestVersion) return;
        $("landing").hidden = true;
        $("workspace").hidden = false;
        if (readerKey === job.id && ["queued", "running"].includes(previous?.link_check?.status)) {
          readerView.applyLinks(data);
        } else {
          readerView?.dispose();
          readerView = mountReader(job, data,
            pending ? null : (event) => requestJobOperation(job, event.currentTarget),
            (event) => requestJobOperation(job, event.currentTarget, "recheck-links"));
        }
        readerKey = job.id;
      }
      readerView.showLinkCheck(job);
      if (pending) notice(job.message || "正在重新生成综述总结…");
      else if (job.status === "failed") notice(job.message || "总结更新失败。", checking ? null : action("重试", (event) => requestJobOperation(job, event.currentTarget)));
      else notice("");
    } else if (pending) {
      notice("");
      loadingState(job);
    } else {
      const retry = action("重试解析", (event) => requestJobOperation(job, event.currentTarget), "primary-button");
      notice("");
      landing("解析未完成", job.message || "服务未能完成这篇综述的解析。", retry, "alert", job.filename);
    }
    if (pending || checking) poll = setTimeout(() => updateJob(id, version), 1800);
  } catch (error) {
    if (version !== requestVersion) return;
    const reconnect = action("重新连接", () => openJob(id, false), "secondary-button");
    if (readerKey === id) notice(error.message, reconnect);
    else landing("暂时无法打开综述", error.message, reconnect, "alert");
  }
}

function openJob(id, push = false, initial) {
  const version = ++requestVersion;
  clearTimeout(poll);
  notice("");
  if (readerKey !== id) landing("正在打开综述", "", null, "document");
  const url = new URL(location.href);
  if (url.searchParams.get("job") !== id) {
    url.searchParams.set("job", id);
    history[push ? "pushState" : "replaceState"]({}, "", url);
  }
  updateJob(id, version, initial);
}

async function initialize() {
  const id = new URL(location.href).searchParams.get("job");
  if (id) { openJob(id); return; }
  const version = ++requestVersion;
  clearTimeout(poll);
  notice("");
  try {
    const {jobs} = await api("/api/jobs");
    if (version !== requestVersion) return;
    if (jobs.length) openJob(jobs[0].id, false, jobs[0]);
    else emptyLibrary();
  } catch (error) {
    if (version === requestVersion) landing("暂时无法打开工作台", error.message, action("重新连接", initialize, "secondary-button"), "alert");
  }
}

window.addEventListener("popstate", initialize);
initialize();
