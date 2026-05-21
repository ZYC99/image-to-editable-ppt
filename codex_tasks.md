# Codex Tasks v0.1

## Goal

Implement the first stable local toolchain:

```text
layout.json → valid editable pptx → validation report
```

Do not implement automatic image parsing yet.

## Task 1: Project setup

Create a Python project with the existing directory structure.

Use these dependencies first:

- `python-pptx`
- `pillow`
- `pydantic`
- `typer`
- `rich`

Create or update `requirements.txt`.

## Task 2: Define Layout IR schema

Create:

```text
src/ir/schema.py
src/ir/validators.py
src/ir/normalize.py
```

Support these element types:

- `text`
- `shape`
- `line`
- `image`
- `group`

Support these strategies:

- `rebuild`
- `crop`
- `background_crop`
- `text_on_crop`
- `asset_search`
- `native_chart`

Each element should support:

- `id`
- `type`
- `strategy`
- `editable`
- `fallback_strategy`
- `confidence`
- `x`, `y`, `w`, `h`
- `z_index`
- `style`

The page object should support:

- width
- height
- background
- coordinate system
- slide size in inches

## Task 3: Implement PPTX renderer

Create:

```text
src/renderers/pptx_renderer.py
src/renderers/text_renderer.py
src/renderers/shape_renderer.py
src/renderers/image_renderer.py
```

The renderer should convert `layout.json` into a `.pptx`.

Use a 16:9 slide size by default:

```text
13.333 x 7.5 inches
```

Coordinates in IR are based on a 1920x1080 pixel canvas and must be mapped to PPT inches.

Renderer requirements:

- text elements become editable text boxes
- shape elements become editable PowerPoint shapes
- line elements become editable PowerPoint lines
- image elements are inserted from local assets
- elements are ordered by `z_index`
- unsupported element types should fail clearly, not silently

## Task 4: Add validation

Create:

```text
src/validators/pptx_integrity.py
src/validators/editable_check.py
```

Validation should check:

- PPTX is a valid zip
- required PowerPoint files exist
- number of editable text boxes
- number of editable shapes
- number of images
- full-page image area ratio

Fail if:

- the PPTX is structurally invalid
- text boxes count is too low
- editable shapes count is too low
- full-page screenshot area ratio is too high in `balanced` or `editability_first` mode

Recommended MVP gate:

```text
text_boxes >= 8
editable_shapes >= 8
full_page_image_area_ratio <= 0.4 unless mode == fidelity_first
```

## Task 5: CLI

Create:

```text
src/pipeline/run.py
```

CLI example:

```bash
python -m src.pipeline.run \
  --layout workspace/ir/layout_v01.json \
  --output workspace/pptx/output_v01.pptx \
  --report workspace/reports/report_v01.json
```

The CLI should:

1. load layout JSON
2. validate IR
3. render PPTX
4. validate PPTX structure
5. run editable check
6. write validation report

## Task 6: Demo layout

Create a demo layout file based on a business report slide.

Output should contain:

- title
- subtitle
- top-right page tag
- conclusion banner
- two metric cards
- one scenario card
- three bottom cards

Do not use full-page screenshot as background.

Suggested path:

```text
workspace/ir/layout_v01_demo.json
```

## Acceptance Criteria

The generated PPTX must:

1. Open without repair warning.
2. Have at least 8 editable text boxes.
3. Have at least 8 editable shapes.
4. Not rely on a full-page screenshot.
5. Produce a JSON validation report.

## Important Constraints

- Do not hand-write risky OpenXML unless absolutely necessary.
- Prefer stable `python-pptx` APIs for v0.1.
- Do not optimize visual fidelity before compatibility and editability gates pass.
- Do not implement image recognition in v0.1.
- Keep the renderer deterministic and testable.
