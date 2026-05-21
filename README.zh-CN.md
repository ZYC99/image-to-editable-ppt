# Image-to-Editable-PPT 中文说明

把一张 PPT 视觉稿图片转换成一个尽量高保真、主要元素可编辑、可自动迭代修正的 `.pptx` 文件。

这个项目的目标不是把整张截图塞进 PowerPoint，而是尽可能把页面重建为真正可编辑的 PPT 对象，例如文本框、形状、线条、图片、局部裁剪素材和 SVG 图标。

## 项目目标

当前阶段的目标是先打通一条稳定的本地工具链：

```text
layout.json → valid editable pptx → validation report
```

第一阶段不急着做自动视觉识别，而是先确保：

1. 能根据结构化的 `layout.json` 稳定生成 `.pptx`。
2. 生成的文件在 PowerPoint 中打开时不提示修复。
3. 主要文本、卡片、线条和基础形状是可编辑对象。
4. 不用整页截图冒充可编辑 PPT。
5. 每次生成都输出验证报告，方便持续改进。

## 为什么需要这个项目

GPT 或其他 AI 工具生成 PPT 图片时，效果经常很好，因为它是在生成一张完整视觉稿。

但 `.pptx` 文件不同。PPTX 需要被 PowerPoint 解释为可编辑对象：

- 文本框
- 形状
- 线条
- 图片
- SVG
- 表格
- 图表
- 阴影
- 渐变
- 图层关系

这些对象在不同系统、不同字体和不同 PowerPoint 版本中可能渲染不一致。尤其中文文本框容易出现换行、溢出、行距不一致等问题。

因此，本项目的核心价值在于：建立一个可验证、可迭代的 image-to-editable-PPT 工程流水线。

## 基本流程

```text
source image
  → visual parsing
  → layout IR
  → strategy planning
  → asset resolving
  → PPTX rendering
  → validation
  → screenshot comparison
  → refinement loop
```

第一阶段主要实现：

```text
layout IR
  → PPTX rendering
  → validation report
```

后续再逐步加入自动视觉解析、截图对比和自动修正。

## 三种模式

### balanced：混合模式，默认推荐

适合大多数正式 PPT 场景。

策略：

- 文字尽量可编辑
- 卡片、圆角矩形、线条尽量可编辑
- 简单图标可用形状或 SVG 重建
- 复杂图标、插画、光效、纹理可以局部裁剪
- 不允许把整页截图作为唯一内容

### fidelity_first：保真优先

适合用户更在意视觉一致性，而不是全部可编辑的场景。

策略：

- 允许更多复杂区域图片化
- 文字仍尽量可编辑
- 背景、装饰、插画可以裁剪
- 可以使用整页背景图，但必须明确标记为保真兜底

### editability_first：可编辑优先

适合用户希望后续大量修改内容的场景。

策略：

- 尽量使用 PPT 原生对象
- 尽量少使用裁剪图片
- 接受视觉效果下降
- 复杂阴影、渐变、光效可以简化

## MVP 验收标准

一份合格的 v0.1 输出至少应该满足：

1. PowerPoint 打开不提示修复。
2. 至少包含 8 个可编辑文本框。
3. 至少包含 8 个可编辑形状。
4. 不依赖整页截图作为主要内容。
5. 标题、副标题、关键数字、核心说明文字可编辑。
6. 输出 `validation_report.json`。
7. 能清楚标注哪些元素是重建的，哪些元素是裁剪兜底。

## 推荐目录结构

```text
image-to-editable-ppt/
├─ README.md
├─ README.zh-CN.md
├─ skill.md
├─ codex_tasks.md
├─ configs/
├─ examples/
├─ workspace/
├─ src/
│  ├─ pipeline/
│  ├─ parser/
│  ├─ ir/
│  ├─ planner/
│  ├─ assets/
│  ├─ renderers/
│  ├─ validators/
│  ├─ screenshot/
│  ├─ diff/
│  └─ refine/
├─ tests/
└─ docs/
```

## 第一阶段开发建议

先不要让 Codex 实现完整的 image parser。

第一阶段只做：

```text
layout.json → output.pptx → validation_report.json
```

这样可以先把最关键的渲染链路和兼容性链路打稳。

## 给 Codex 的建议指令

```text
请阅读 README.md、README.zh-CN.md、skill.md、codex_tasks.md 和 docs 目录。

先实现 v0.1：
layout.json → valid editable pptx → validation report。

不要实现自动视觉识别。
不要做 image parsing。
不要用整页截图作为主要内容。

重点是：
1. 稳定的 PPTX renderer；
2. PPTX 结构完整性检查；
3. 可编辑对象数量检查；
4. 生成 validation_report.json；
5. PowerPoint 打开不提示修复。
```

## 非目标

v0.1 暂时不追求：

- 任意图片 100% 复刻
- 所有元素完全可编辑
- 自动识别复杂图表原始数据
- 完美中文排版
- 完美还原所有阴影、滤镜、渐变和混合模式
- 自动在线搜索素材库

## 当前最重要的原则

先保证生成的 PPT 文件稳定、可打开、可验证。

然后再逐步提高视觉相似度和自动化程度。
