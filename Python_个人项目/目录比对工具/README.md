# 目录比对工具

一个用于比较两个目录并生成类似GitHub风格diff报告的Python工具。

## 功能特点

- 比较两个目录的所有文件（包含子目录）
- 生成Markdown格式的差异报告
- 显示文件统计摘要（新增、删除、修改的文件）
- 支持多种文本编码（UTF-8, GBK, GB2312等）
- 高亮显示文件差异（新增行以`+`开头，删除行以`-`开头）
- 识别二进制文件或不支持的编码格式

## 使用方法

```bash
python app.py <input1_path> <input2_path> [output_file.md]
```

### 参数说明

- `input1_path`: 第一个目录路径
- `input2_path`: 第二个目录路径
- `output_file.md`: 输出报告文件名（可选，默认为`diff_report.md`）

### 示例

```bash
# 比较两个目录，生成默认报告文件 diff_report.md
python app.py ./input1 ./input2

# 比较两个目录，生成自定义报告文件
python app.py ./input1 ./input2 custom_report.md
```

## 输出报告内容

生成的Markdown报告包含以下部分：

1. **统计摘要**：显示仅存在于Input1、Input2的文件数量以及共同文件数量
2. **仅存在于Input1的文件**：标记为已删除的文件（在Input2中已删除）
3. **仅存在于Input2的文件**：标记为新增的文件（新增）
4. **已修改的文件**：内容发生变化的文件列表
5. **详细差异内容**：显示具体文件的行级差异
6. **内容完全相同的文件**：未发生变化的文件列表

## 报告格式

- 新增行：以`+`标识
- 删除行：以`-`标识
- 二进制文件：显示`[Binary file or unsupported encoding]`

## 适用场景

- 代码版本对比
- 项目文件变更分析
- 文档差异比较
- 配置文件对比
- 任意文本文件目录的差异分析

## 技术特点

- 使用Python标准库`difflib`生成统一差异格式
- 自动检测文件编码（UTF-8、GBK、GB2312、latin-1）
- 递归遍历子目录
- 支持大文件内容截断显示（前50行）
- 生成结构化的Markdown报告

## 依赖

- Python 3.x
- 标准库：`os`, `difflib`, `pathlib`, `datetime`