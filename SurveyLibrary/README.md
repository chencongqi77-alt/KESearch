# SurveyLibrary 大模型综述库

SurveyLibrary 为研究者提供可离线阅读、可按主题查找的大语言模型综述。每篇正式收录的论文都有公开标识、来源链接和一份经过验收的本地 PDF。

## 收录规模

下表按本次交付的索引、主题树、PDF 和文末清单统计。年份取 arXiv 首次提交年或出版记录的年份。

| 项目 | 数量或年份 |
| --- | ---: |
| 正式论文 | 974 |
| 本地 PDF | 974 |
| arXiv 编号 | 861 |
| 出版 DOI | 113 |
| 最早收录年份 | 2020 |
| 最近收录年份 | 2026 |
| 一级主题 | 12 |
| 二级主题 | 76 |
| 清单条目 | 117 |
| 缺少 PDF | 57 |
| 此前待核 | 12 |
| 本轮验收异常 | 17 |
| 采集阶段排除 | 31 |

## 来源与使用

一期采用 KalyanKS-NLP、AiHubCN 和 NiuTrans 的综述清单，二期采用 Max Hort、Fernando Vallecillos-Ruiz 和 Leon Moonen 整理的 DataSED 书目。各链接指向本库采用的固定提交。[KalyanKS-NLP](https://github.com/KalyanKS-NLP/LLM-Survey-Papers-Collection/tree/ac2a7fe847c199afcf4382b143e87e9f0b32812c) · [AiHubCN](https://github.com/AiHubCN/Awesome-LLM-Survey/tree/4ef976f8d1a8e67a3080b51348eb7133d17b35e6) · [NiuTrans](https://github.com/NiuTrans/ABigSurveyOfLLMs/tree/2c4092a2959cc1d35b3885b07ca5e9f32ac20412) · [DataSED](https://github.com/dataSED-condenSE/LLM-Survey-Survey/tree/7df227c67db78b653ac0de472232e6ebb45725c9)

DataSED 清单采用 CC BY 4.0，本库对其条目进行了筛选、去重和分类。单篇 PDF 的使用与转交条件以原文的许可为准。[DataSED 许可](https://github.com/dataSED-condenSE/LLM-Survey-Survey/blob/7df227c67db78b653ac0de472232e6ebb45725c9/LICENSE)

| 文件 | 用法 |
| --- | --- |
| [index.json](index.json) | 按 `id`、`title` 或 `year` 查找论文。`url` 指向公开记录，`pdf` 是相对本目录的文件路径，`topics` 列出关联主题 ID。 |
| [taxonomy.json](taxonomy.json) | 从主题的 `children` 浏览子主题，按 `recommended` 的顺序用论文 ID 到索引定位精选。 |
| [papers/](papers/) | 直接打开索引指向的 PDF。文件保留来源给出的名称，arXiv 文件名可能带版本后缀。 |
| [README.md](README.md) | 查阅收录标准、主题范围和文末异常题录。 |

复制或交付时保持上述相对位置。arXiv 论文的索引 ID 使用不含版本后缀的公开编号，其他论文使用 `doi:` 加出版 DOI。

## 主题与精选

一级主题按目录顺序为综合综述、基础与架构、数据、训练与适应、提示与上下文、大模型推理、知识与检索增强、大模型智能体、评测与基准、模型理解与可信性、推理执行、效率与系统、多模态与多语言、大模型应用。每篇论文可以关联多个主题。浏览一级主题时，合并该节点及其子节点的论文并按 ID 去重。精选只引用该主题或其子主题内通过验收的论文。[主题目录](taxonomy.json)

## 质量控制

按公开标识、题名、作者和版本线索合并重复论文，核对 arXiv 或 Crossref 的题名与年份，并比对交付版本的实际封面。对带有出版商扉页的 PDF，同时核对正文首页。逐份核对来源回执中的原文件名、页数与 SHA-256，逐页解析和渲染，并复查异常页、撤回提示和文章类型。

最终检查覆盖索引与文件的一一对应、主题归属、精选引用以及下表的完整性。同一论文的大小写、标点或排版差异按等价处理。未取得全文、论文版本题名有实质差异或身份仍有疑点的记录保留在下表。两阶段的完整施工题录、来源快照和下载回执另行归档。
