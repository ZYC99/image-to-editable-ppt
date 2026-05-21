# Image-to-Editable-PPT 项目总体规划

## 1. 项目定位

Image-to-Editable-PPT 是一个将 PPT 视觉稿图片转换为尽量高保真、主要元素可编辑、可验证、可迭代修正的 `.pptx` 文件的工程化工具链。

它不是一个简单的“图片转 PPT”工具，也不是把整张截图贴进 PowerPoint。它的核心目标是：

> 将视觉稿拆解为结构化页面元素，并尽可能重建为 PowerPoint 原生可编辑对象。

项目应长期演进为：

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

## 2. 项目价值

当前 AI 可以生成很好看的 PPT 图片，但生成真正可编辑的 PPT 文件时效果明显下降。根本原因是两者的生成目标不同：

- 图片是像素级整体绘制。
- PPTX 必须落到 PowerPoint 对象模型。
- PowerPoint 会重新解释字体、换行、阴影、渐变、缩放和图层。
- 中文文本框尤其容易出现溢出、换行、行距变化。
- 仅靠一次生成无法知道 PowerPoint 打开后的真实效果。

因此，本项目的价值不在于“让模型直接生成 PPTX”，而在于建立一条可验证、可修正、可复用的工程流水线。

## 3. 核心原则

### 3.1 不直接 image → pptx

不要让模型直接生成最终 PPTX。  
必须先生成中间结构：

```text
image → layout IR → renderer → pptx
```

Layout IR 是整个系统的核心资产。它让系统可以：

- 做结构校验；
- 做局部修正；
- 切换保真/可编辑策略；
- 记录元素语义；
- 输出 PPTX、PNG、SVG、HTML 等不同格式；
- 支持后续自动 diff/refine。

### 3.2 模型负责理解，代码负责渲染

模型负责：

- 视觉分析；
- 版式拆解；
- 元素识别；
- 语义分组；
- 策略判断；
- 生成或修正 Layout IR。

代码负责：

- 坐标转换；
- 稳定生成 PPTX；
- 管理素材；
- 文件兼容性检查；
- 可编辑性检查；
- 截图导出；
- 差异对比；
- 自动修正。

### 3.3 默认采用混合策略

不要追求所有元素都可编辑，也不要为了保真把整页做成图片。

默认策略应为 `balanced`：

- 文字可编辑；
- 卡片、线条、基础形状可编辑；
- 复杂图标、插画、光效、纹理允许局部裁剪；
- 背景可以简化重建或局部裁剪；
- 关键内容优先可编辑，低价值装饰优先保真。

## 4. 产品目标

### 4.1 MVP 目标

v0.1 先实现：

```text
layout.json → valid editable pptx → validation_report.json
```

不急着实现自动视觉识别。

MVP 目标：

- 输入手写或半自动生成的 `layout.json`。
- 输出结构合法的 `.pptx`。
- PowerPoint 打开不提示修复。
- 标题、副标题、关键数字、正文等文本可编辑。
- 卡片、线条、圆角矩形等基础形状可编辑。
- 可局部使用裁剪 PNG 作为复杂视觉兜底。
- 输出验证报告。
- 禁止整页截图冒充可编辑 PPT。

### 4.2 v0.2 目标

在稳定 renderer 基础上加入：

- 图片输入管理；
- 手动或半自动裁剪复杂区域；
- 更完善的 Layout IR schema；
- 常见商业页面 demo；
- 更严格的 editable gate；
- LibreOffice headless 导出 PNG/PDF；
- 初步 rendered preview。

### 4.3 v0.3 目标

加入视觉回归能力：

- PPTX → PNG；
- 原图与渲染图尺寸对齐；
- 输出 diff report；
- 检测主要区域偏移；
- 检测文本溢出；
- 根据 diff 给出修正建议。

### 4.4 v0.4 目标

加入半自动视觉解析：

- OCR 文本识别；
- 文本 bbox 提取；
- 基础形状检测；
- 图片/图标区域检测；
- 语义区域初步分组；
- 生成初始 Layout IR。

### 4.5 v1.0 目标

形成可用工具链：

- 单页商业 PPT 图片转可编辑 PPTX；
- 支持 balanced / fidelity_first / editability_first；
- 支持区域级策略；
- 支持多轮人工反馈修正；
- 支持 demo 样例和测试；
- 支持稳定 CLI；
- 支持 GitHub 开源协作。

## 5. 技术路线

### 5.1 Layout IR

Layout IR 是系统核心。

每个元素至少包含：

```json
{
  "id": "title_1",
  "type": "text",
  "strategy": "rebuild",
  "editable": true,
  "fallback_strategy": "crop",
  "confidence": 0.9,
  "x": 120,
  "y": 80,
  "w": 600,
  "h": 64,
  "z_index": 10,
  "style": {}
}
```

v0.1 需要支持的元素类型：

- `text`
- `shape`
- `line`
- `image`
- `group`

后续阶段再扩展：

- `chart`
- `table`

需要支持的策略：

- `rebuild`
- `crop`
- `background_crop`
- `text_on_crop`
- `asset_search`
- `native_chart`

### 5.2 Renderer

Renderer 只接受 Layout IR，不直接分析图片。

职责：

- 读取 `layout.json`；
- 校验 schema；
- 将 px 坐标映射到 PPT inch/EMU；
- 生成文本框；
- 生成形状；
- 插入图片；
- 管理图层顺序；
- 输出 `.pptx`。

第一阶段优先使用 Python 技术栈：

- `python-pptx`
- `pydantic`
- `Pillow`
- `typer`
- `rich`

### 5.3 Validator

Validator 是项目早期必须重视的模块。

至少检查：

- `.pptx` 是否为合法 zip；
- 必要 XML 文件是否存在；
- 文本框数量；
- 形状数量；
- 图片数量；
- 是否存在疑似整页截图；
- 关键元素是否可编辑；
- 是否通过 MVP editable gate。

LibreOffice headless 打开/导出属于 v0.2 preview 能力，不作为 v0.1 的阻塞 gate。

### 5.4 Screenshot / Diff

第二阶段再做，不阻塞 MVP。

功能：

- 将 PPTX 导出为 PNG；
- 与原始图片对齐尺寸；
- 计算整体差异；
- 计算区域差异；
- 输出 `diff_report.json`；
- 给 refiner 提供依据。

### 5.5 Refiner

Refiner 用于根据反馈修正 Layout IR。

初期可基于人工反馈：

```text
标题偏左 10px
数字字号太大
底部卡片整体下移
图标建议裁剪
```

后期可基于 diff 自动修正：

- 位置偏移；
- 尺寸偏移；
- 字号偏差；
- 颜色偏差；
- 文本溢出；
- 图层错误。

## 6. 推荐目录结构

```text
image-to-editable-ppt/
├─ README.md
├─ README.zh-CN.md
├─ skill.md
├─ codex_tasks.md
├─ requirements.txt
├─ configs/
│  ├─ default.yaml
│  ├─ modes.yaml
│  └─ fonts.yaml
├─ examples/
│  ├─ input/
│  ├─ output/
│  └─ reports/
├─ workspace/
│  ├─ source/
│  ├─ crops/
│  ├─ assets/
│  ├─ ir/
│  ├─ pptx/
│  ├─ renders/
│  └─ diff/
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
   ├─ architecture.md
   ├─ layout_ir.md
   ├─ skill_rules.md
   ├─ skill_rules.zh-CN.md
   ├─ failure_modes.md
   ├─ failure_modes.zh-CN.md
   └─ project_plan.zh-CN.md
```

## 7. 阶段规划

### Phase 0：项目初始化

目标：建立仓库和基础文档。

交付物：

- README.md
- README.zh-CN.md
- skill.md
- codex_tasks.md
- requirements.txt
- docs/architecture.md
- docs/layout_ir.md
- docs/skill_rules.zh-CN.md
- docs/failure_modes.zh-CN.md
- docs/project_plan.zh-CN.md

完成标准：

- 仓库结构清晰；
- Codex 能读懂下一步任务；
- 项目目标、非目标和验收标准明确。

### Phase 1：Renderer MVP

目标：实现 `layout.json → pptx`。

交付物：

- `src/ir/schema.py`
- `src/ir/validators.py`
- `src/renderers/pptx_renderer.py`
- `src/renderers/text_renderer.py`
- `src/renderers/shape_renderer.py`
- `src/renderers/image_renderer.py`
- `src/pipeline/run.py`
- demo layout
- demo output pptx

完成标准：

- 可以通过 CLI 生成 PPTX；
- PowerPoint 打开不提示修复；
- 文本和基础形状可编辑；
- 不使用整页截图兜底。

### Phase 2：Validation MVP

目标：建立输出质量门槛。

交付物：

- `src/validators/pptx_integrity.py`
- `src/validators/editable_check.py`
- `validation_report.json`

完成标准：

- 检查 PPTX 结构；
- 统计可编辑对象；
- 检查疑似整页截图；
- 输出 pass/fail；
- 失败时给出原因。

### Phase 3：Asset / Crop 支持

目标：支持复杂元素局部裁剪。

交付物：

- `src/assets/cropper.py`
- `src/assets/asset_registry.py`
- `workspace/crops/`
- image element rendering
- crop metadata

完成标准：

- 可以在 IR 中引用局部裁剪图片；
- 支持 `background_crop` 和 `text_on_crop`；
- 不影响 PPTX 兼容性。

### Phase 4：Preview / Screenshot

目标：生成 PPT 渲染预览。

交付物：

- `src/screenshot/pptx_to_png.py`
- rendered preview image
- preview report

完成标准：

- 可以将 PPTX 导出为 PNG 或 PDF；
- 能用于人工对比；
- 不要求自动 diff 精确。

### Phase 5：Visual Diff

目标：开始自动对比。

交付物：

- `src/diff/visual_diff.py`
- `src/diff/report.py`
- `diff_report.json`

完成标准：

- 输出整体差异指标；
- 输出主要区域差异；
- 能标记明显偏移区域；
- 可作为 refiner 输入。

### Phase 6：Vision Parser Prototype

目标：从图片自动生成初始 IR。

交付物：

- `src/parser/vision_parser.py`
- `src/parser/ocr_parser.py`
- `src/parser/shape_detector.py`
- 初始 parser demo

完成标准：

- 能识别主要文本区域；
- 能识别主要卡片/模块；
- 能生成初始 IR；
- 允许人工继续修正。

### Phase 7：Refinement Loop

目标：支持多轮修正。

交付物：

- `src/refine/layout_refiner.py`
- `src/refine/text_overflow_refiner.py`
- feedback format
- refine history

完成标准：

- 能根据人工反馈修改 IR；
- 能根据 diff report 给出修正建议；
- 能保存每轮版本。

## 8. 里程碑

### Milestone A：可生成稳定 PPTX

预期成果：

- 本地 CLI 可运行；
- demo layout 可生成 PPTX；
- PowerPoint 打开不提示修复；
- validation report 可生成。

这是项目的第一个关键里程碑。

### Milestone B：可编辑性达标

预期成果：

- 至少 8 个文本框；
- 至少 8 个可编辑形状；
- 主标题、关键数字、核心说明文字可编辑；
- 不依赖整页截图。

### Milestone C：单页样例可交付

预期成果：

- 对 1 张商业汇报页实现 70%–85% 相似度；
- 主要内容可编辑；
- 复杂图标允许局部裁剪；
- 有失败报告和修正记录。

### Milestone D：支持视觉预览

预期成果：

- 自动导出 rendered preview；
- 用户可以对比原图；
- 系统保存预览和报告。

### Milestone E：支持半自动解析

预期成果：

- 输入图片后能生成初始 IR；
- 人工只需要修正关键错误；
- 初步进入 image-to-PPT 阶段。

## 9. MVP 验收标准

v0.1 必须满足：

1. 能从 `layout.json` 生成 `.pptx`。
2. PowerPoint 打开不提示修复。
3. 输出 `validation_report.json`。
4. 至少 8 个可编辑文本框。
5. 至少 8 个可编辑形状。
6. 不使用整页截图作为主要内容。
7. 支持文本、形状、线条、图片四类基础元素。
8. 坐标系统明确，支持 1920×1080 到 16:9 PPT 的映射。
9. 失败时能说明原因。
10. 代码结构清晰，方便后续扩展。

## 10. 非目标

v0.1 不做：

- 自动 image parser；
- 任意复杂页面 95% 复刻；
- 所有元素完全可编辑；
- 自动识别图表原始数据；
- 完美中文排版；
- 完美还原复杂阴影、渐变、光效；
- 自动在线搜索图标；
- 多页批量处理；
- 商业化 UI。

## 11. 风险与应对

### 风险 1：PPTX 兼容性问题

应对：

- 只用稳定 API；
- 加结构检查；
- 加 LibreOffice 打开检查；
- 不手写复杂 XML。

### 风险 2：中文排版不稳定

应对：

- 预留文本框宽度；
- 加字体 fallback；
- 支持 shrink text；
- 建立中文文本失败样例。

### 风险 3：过度图片化

应对：

- 加 editable gate；
- 检查 full-page image ratio；
- 强制关键文本可编辑。

### 风险 4：过度重建导致不像

应对：

- 使用 mixed strategy；
- 复杂元素局部裁剪；
- 引入 SVG/icon library；
- 后续做 visual diff。

### 风险 5：项目范围膨胀

应对：

- v0.1 只做 renderer 和 validator；
- image parser 延后；
- diff/refine 延后；
- 每个阶段有明确验收标准。

## 12. 推荐开发顺序

```text
1. 建仓库和文档
2. 定义 Layout IR schema
3. 实现基础 PPTX renderer
4. 实现 validation report
5. 做 demo layout
6. 本机 PowerPoint 验证
7. 加 crop/image 支持
8. 加 preview 导出
9. 加 diff
10. 加 vision parser
11. 加 refine loop
```

## 13. Codex 协作方式

Codex 适合在本地仓库中执行工程实现。

推荐让 Codex 分阶段工作，不要一次性让它做完整系统。

### Codex 第一条任务

```text
请阅读 README.md、README.zh-CN.md、skill.md、codex_tasks.md 和 docs 目录。

先实现 v0.1：
layout.json → valid editable pptx → validation_report.json。

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

### Codex 工作要求

- 每次只完成一个阶段；
- 每次修改后运行测试；
- 每次输出变更说明；
- 不要绕过 validation；
- 不要为了相似度使用整页截图；
- 遇到失败要更新 failure_modes 文档。

## 14. 成功标准

短期成功：

- 可以稳定从 layout.json 生成可打开、可编辑的 PPTX。

中期成功：

- 可以基于一张商业 PPT 图片，半自动生成 70%–85% 相似度的可编辑 PPTX。

长期成功：

- 可以通过视觉解析、策略规划、渲染验证和多轮修正，将典型商业 PPT 图片转换为 90%+ 相似度、关键内容可编辑的 PPTX。

## 15. 当前下一步

当前最应该做的是：

1. 将本文档放入 `docs/project_plan.zh-CN.md`。
2. 让 Codex 初始化 v0.1 代码结构。
3. 优先实现 Layout IR schema。
4. 优先实现 PPTX renderer。
5. 优先实现 validation report。
6. 用一张手写 demo layout 生成第一份稳定 PPTX。
