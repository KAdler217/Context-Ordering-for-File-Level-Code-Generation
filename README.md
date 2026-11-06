# 文件级代码生成中的上下文排序优化

> 本科毕业设计 · 实验代码
>
> Context Ordering for File-Level Code Generation

在文件级代码生成任务里，模型通常需要把**目标函数所在文件中的其他函数**一并作为上下文。这些函数以什么顺序出现，会直接影响模型能否正确复用它们。本项目把「顺序」当作唯一变量，实现并对比了几种上下文排序策略。

## 方法概览

整体流水线：

1. **解析**：用 `tree-sitter-java` 从样本中抽取目标函数、同文件的其余方法、类声明与注释块；
2. **排序**：按不同策略重排上下文中的函数顺序；
3. **生成**：把重排后的上下文拼进 prompt，调用代码大模型补全目标函数；
4. **评测**：用行级命中率与文本相似度指标衡量生成质量。

### 排序策略

| 策略 | 脚本 | 做法 |
|---|---|---|
| 原始顺序 | `Tree-sitter.py`、`test.py` | 保持源文件中函数的原始先后 |
| 字母序 | `ABC_order.py` | 按函数名排序 |
| 全排列 | `All_permutations.py` | 枚举所有可能顺序，用于小规模分析顺序的敏感度 |
| 嵌入相似度 | `Embedding_order.py` | 按与目标函数的向量相似度降序排列，并按区间分组插入 |
| 贪心 | `Greedy.py` | 结合嵌入相似度与困惑度逐位选择下一个函数 |

### 支撑模块

| 模块 | 作用 |
|---|---|
| `Get_function.py` | 解析文件、提取函数与其调用关系 |
| `Perplexity.py` | 调用模型计算困惑度 |
| `Text_embedding.py` | 调用嵌入接口取向量 |
| `chutes.py` | 封装对话模型调用（含重试） |
| `para_perm.py` | 并行打分，加速排列评估 |
| `New_dataset.py` | 按 token 数过滤样本 |
| `ToJsonl.py`、`extract.py` | 文本与 JSONL 之间的格式转换 |
| `Read_PPL.py` | 汇总困惑度结果 |

## 目录结构

```
src/
├── demo/                     上下文排序与生成的主实验脚本
├── line_metric/              评测：行命中率、ROUGE / BLEU / CodeBLEU / SBERT
└── huawei/                   图像批处理辅助脚本
```

`src/line_metric/` 中：

- `lines_hit_ratio.py`：生成代码与参考代码的行级匹配率，可选择以参考行数或生成行数为分母；
- `metric.py`：ROUGE、BLEU、CodeBLEU、Sentence-BERT 相似度；
- `run_local_eval.py`：批量跑评测并汇总。

## 环境

Python 3.9 及以上。

```bash
pip install -r requirements.txt
```

`tree-sitter-java` 需要能编译出对应的语言包；若安装失败，请先升级 `tree-sitter` 到与 `tree-sitter-java` 匹配的版本。

## 数据准备

实验使用 **CoderEval4Java** 数据集（Java 方法级代码生成），以及 RepoBench 的评测结果文件做横向对比。**数据集不随本仓库分发**，请从各自官方渠道获取后按原实验目录放置。

脚本中的输入路径（如 `CoderEval4Java.jsonl`、`../../Demo/...`）保留了原始实验环境的相对布局，迁移后需要按实际路径调整。

样本字段大致为：

```json
{"func_name": "...", "file_content": "...", "func_code": "..."}
```

其中 `file_content` 是目标函数所在文件的完整内容，脚本据此重建上下文。

## 配置

代码中不再包含任何密钥。运行前设置环境变量：

```bash
export CHUTES_API_TOKEN="..."     # 对话模型网关令牌
export LLM_API_KEY="..."          # OpenAI 兼容接口的 key（如 SiliconFlow）
export EMBEDDING_API_KEY="..."    # 嵌入接口的 key
```

Windows PowerShell：

```powershell
$env:CHUTES_API_TOKEN = "..."
```

## 运行示例

以字母序策略为例：

```bash
cd src/demo
python ABC_order.py
```

其余策略把脚本名替换为 `Embedding_order.py` / `Greedy.py` / `All_permutations.py` 即可。各脚本顶部通常有 `file_path` 与样本下标 `num` 需要按需修改。

## 评测

```bash
cd src/line_metric
python run_local_eval.py
```

行命中率的口径：对生成代码与参考代码逐行做「去空白后精确匹配」，再按选定的分母归一化。它衡量的是**逐行复现**能力，对语义等价但写法不同的代码不友好，因此与 ROUGE / CodeBLEU / SBERT 一起看。

## 说明与限制

- 本仓库是**整理后的实验代码**，不含数据集、模型输出与论文正文；
- 部分脚本是探索过程的产物，存在功能重叠与硬编码路径，保持原样以便复现当时的实验；
- `src/demo/123.py`、`Less_function.py` 是零散的小工具，保留作为过程记录；
- 未附开源许可证。

## 参考

- Hierarchical Context Pruning — <https://arxiv.org/abs/2406.18294>
- 面向依赖利用的仓库级代码生成评测（DIR 指标） — <https://arxiv.org/abs/2406.11927>
- Enhancing RAG-based Repository-Level Method Body Completion — <https://arxiv.org/abs/2409.15204>
