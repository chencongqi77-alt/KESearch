# 综述精读工作台

上传一篇综述 PDF，MinerU 提取 Markdown、正文和原图。工作台恢复章节目录，定位被引论文和讨论它们的原句，再用 DeepSeek 生成中文总结。点击目录或正文段落，右侧会显示该节引用的论文、原句、页码和论文链接。

## 接手并启动

源码可单独复制到其他工作区。交接实现时带上 `src/`、`test/`、`pyproject.toml`、`.gitignore`、`README.md`、`start.cmd` 和根目录的 Python 入口脚本。接收方在自己的机器上配置凭据。`.env.local` 属于本机私有配置，`workspace/` 含上传原件和阅读历史，`runs/` 保存命令行生成的精读包。需要交接阅读结果时，可另选对应的任务或批次目录。

1. 准备 Python 3.12。从 `Deal_survey/` 目录执行以下命令安装项目和完整依赖。已有依赖时，也可直接使用下一步的源码入口。

   ```powershell
   py -3.12 -m pip install -e ".[full]"
   ```

   基础安装可用 `py -3.12 -m pip install -e .`。核心依赖为 `pypdf`，`full` 另含用于核对 PDF 数字引文跳转的 `PyMuPDF` 和用于排版公式的 `latex2mathml`。前端由 Python 服务直接提供静态文件。

2. 使用在线解析和总结时，配置 `KET_MINERU_API_TOKEN` 和 `DEEPSEEK_API_KEY`。工作台先用进程环境，再查本项目的 `.env.local`，Windows 还可读取当前用户的环境变量。在已有凭据的 KESearch 开发机上，首次可用以下命令从已有环境和服务端配置新建私有配置。已有配置会被保留。

   ```powershell
   py -3.12 -B -X utf8 settings.py --copy-existing
   ```

3. 双击 [start.cmd](start.cmd) 或在 `Deal_survey/` 目录运行以下命令，浏览器会打开本机工作台。启动脚本优先使用项目的 `.venv`，其次使用已激活的虚拟环境，最后使用 `py -3.12`。默认地址为 <http://127.0.0.1:8765>。`--port` 可指定端口，`--data-dir` 可指定其他任务目录。

   ```powershell
   py -3.12 -B -X utf8 server.py --open-browser
   ```

也可以从 KESearch 仓库根执行 `py -3.12 -B -X utf8 Deal_survey/server.py`。如需交付可安装的 wheel，可在 `Deal_survey/` 运行 `py -3.12 -m pip wheel --no-deps . -w dist`。安装为 Python 包后，命令 `deal-survey`、`deal-survey-prepare` 和 `deal-survey-settings` 分别对应工作台、命令行精读包和配置导入，可加 `--help` 查看参数。源码运行或可编辑安装默认使用 `Deal_survey/` 下的 `.env.local` 和 `workspace/`。从 wheel 安装后，默认在启动命令的当前目录读取配置、保存任务。

## 目录和处理流程

| 路径 | 维护内容 |
| --- | --- |
| [src/deal_survey/](src/deal_survey/) | 可复用的 Python 包。业务改动在此完成。 |
| [src/deal_survey/web/](src/deal_survey/web/) | 三栏阅读界面的 HTML、CSS 和 JavaScript。随包分发。 |
| [test/](test/) | 按模块组织的离线回归测试，使用临时工作目录和模拟服务。 |
| [pyproject.toml](pyproject.toml) | Python 依赖、可选依赖、包内资源和命令入口。 |
| [server.py](server.py) · [prepare.py](prepare.py) · [settings.py](settings.py) | 源码目录的启动脚本，转交给包内对应模块。 |
| `workspace/<任务 ID>/` | 工作台记录。`job.json` 为状态，`source.pdf` 为上传原件，`cloud/` 存 MinerU ZIP、回执和可用的 `full.md`。`reading/` 为精读包，`assets/` 和 `reader.json` 为界面使用的图片和读本。 |
| `runs/<批次>/` | 命令行批次，`reading/` 中保存成对生成的 Markdown 和 JSON。在线批次的 `cloud/` 保留恢复状态、ZIP 和回执。 |

1. **PDF → MinerU 结果。** 上传、查询、恢复及离线 ZIP 校验由 [mineru_api.py](src/deal_survey/mineru_api.py) 和 [mineru_pdf.py](src/deal_survey/mineru_pdf.py) 处理。PDF 检查和 v4 协议沿用 KESearch 的 Test01 客户端和产品 MinerU 适配。
2. **正文 → 章节与引文。** [structure.py](src/deal_survey/structure.py) 按同页同名的 PDF 书签、印刷节号、MinerU 标题级别依次恢复目录。[citations.py](src/deal_survey/citations.py) 识别编号、组引、区间和可匹配的作者年份引文，沿用 Test01 的数字引文规则。[pdf_check.py](src/deal_survey/pdf_check.py) 对有可识别 `cite.*` 跳转和印刷编号的 PDF 核对引文次数。
3. **章节与引文 → 精读包。** [prepare.py](src/deal_survey/prepare.py) 编排上述步骤，生成 `reading/reading.md` 和 `reading/survey.json`。Markdown 可沿章节阅读或按被引论文反查，JSON 供程序处理。
4. **精读包 → 浏览器读本。** [reader.py](src/deal_survey/reader.py) 组装正文、原图、引句与书目，生成 DeepSeek 总结。[paper_links.py](src/deal_survey/paper_links.py)、[proceedings_links.py](src/deal_survey/proceedings_links.py) 和 [openalex_links.py](src/deal_survey/openalex_links.py) 在 arXiv 匹配之外核对 DOI、会议论文和其他出版来源。[server.py](src/deal_survey/server.py) 管理阅读任务、API 和静态页面。

## 使用工作台

点「上传 PDF」，选取或拖入综述后点「上传并解析」。整篇上限为 200 页、200 MiB。服务重启后，可从「综述记录」打开已有读本或尝试恢复已知 MinerU 批次。

中栏可读总结、原文、图表和图注，也可打开原 PDF、下载 MinerU Markdown。综述有合适的分类图或概览图时，总结会配上原图、图注和所属章节入口。总结生成失败时，页面标明替代摘录的来源，可单独重试 DeepSeek。窄屏可在目录、正文和引用之间切换。

点击右栏的页码可定位到引用段落。标为「原 PDF 摘录」的引句可打开原页。「arXiv 论文页」「DOI 论文页」「论文来源页」对应已确认的链接，「arXiv 检索 · 待确认」提供题名搜索。「核对全篇链接」使用公开书目来源补查已有读本，完成后同步更新当前章节和完整书目，保留前次 PDF 解析与总结。

## 命令行和 Python 复用

从 `Deal_survey/` 目录运行以下命令即可为任意本地 PDF 生成精读包。输出示例可直接查看 Attention 综述的[逐章摘录](runs/attention-2203.14263v1/reading/reading.md)和[结构化引文](runs/attention-2203.14263v1/reading/survey.json)。

```powershell
py -3.12 -B -X utf8 prepare.py --pdf "D:/papers/survey.pdf" --out "runs/my-survey-v1"
```

默认 MinerU 模型为 `vlm`。等待超时时，使用同一 PDF、模型和输出目录可继续查询已知批次。提交结果不明时会停止。重新生成已完成的精读包时，请选择新的输出目录。

已有原 PDF 和同篇综述的 MinerU ZIP 时，可在 `Deal_survey/` 目录离线回放。将下面两个输入路径换成本机保存的文件。

```powershell
py -3.12 -B -X utf8 prepare.py --pdf "D:/papers/survey.pdf" --mineru-zip "D:/papers/mineru/result.zip" --out "runs/replay-v1"
```

在其他 Python 项目安装本包后，可直接调用同一处理函数。以下离线示例返回新建的 `reading/` 路径和章节、书目、引文计数。

```python
from pathlib import Path
from deal_survey.prepare import prepare

reading_dir, counts = prepare(
    Path("inputs/survey.pdf"),
    Path("runs/replay-v1"),
    archive=Path("inputs/result.zip"),
)
```

ZIP 中应有唯一的 MinerU v1 `*_content_list.json` 或 `content_list.json`。程序会核对 PDF 与 ZIP 的身份。提供方重编码 PDF 时，需要同时绑定输入 SHA-256、ZIP SHA-256 和整篇请求页数的完成回执。默认读取 ZIP 旁的 `result.json`，也可通过命令行 `--receipt` 或 Python 参数 `receipt=` 指定。仅凭 ZIP 内同字节 PDF 确认身份时，输出会标记页范围待核。

## 数据字段和验证

`survey.json` 中的 `sections` 记录章节层级、路径、本节直接引用及含子节的去重引用。`references` 记录书目原文、原始位置和关联小节。`mentions` 记录引文标记、综述的讨论原句、匹配到的书目及缺项、重号或多候选等状态。ID 在本篇综述内有效。

每处引文保留 MinerU 的 `block_index`、`field` 和 Unicode 字符半开区间 `[start,end)`。表身按原始 HTML 行取上下文，回查整字段时加上 `field_offset`，`context_start/context_end` 同理。图注、脚注和列表项保留字段名。原 PDF 有跳转而解析正文缺失引文时，`pdf_check.differences[].pdf_excerpts` 可另附原页文本片段和坐标，保留解析所得的出现次数。书目中没有匹配讨论的论文仍可回查。

读本按题名和作者寻找论文，处理 OCR 遗漏的空格或连字符，并用年份、期刊、卷期和页码核对版本。同一期刊论文有多条可确认 DOI 时可保存备用 DOI，已有的备用全文 PDF 也会显示。读本分别记录查无匹配、候选冲突、限流和本轮尚未查询的状态，以便后续补查。

独立交接后，可在 `Deal_survey/` 目录运行 `py -3.12 -B -X utf8 -m unittest -q`。逐项查看测试结果可用以下命令。

```powershell
py -3.12 -B -X utf8 -m unittest discover -s test -t . -v
```

从 GitHub 克隆仓库后，也可在仓库根运行相同测试。

```powershell
py -3.12 -B -X utf8 -m unittest discover -s Deal_survey/test -t Deal_survey -v
```

在包含 `work_tool/` 的 KESearch 完整开发工作区中，另运行 `python -X utf8 work_tool/audit_project.py` 做全仓审计。Attention 样本当时的独立核对记录保存在该工作区的 `Test01/work_tool/reports/survey-smoke-2203-14263-20261118-v1.md`。
