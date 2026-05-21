# Architecture

## Overview

Image-to-Editable-PPT is a local toolchain for converting a PPT visual image into a mostly editable `.pptx`.

The core design is:

```text
source image
  → visual parsing
  → layout IR / scene graph
  → strategy planning
  → asset resolving
  → PPTX rendering
  → validation
  → screenshot comparison
  → refinement loop
```

## Key Principle

Do not directly convert `image → pptx`.

Instead, use:

```text
image → layout IR → renderer → pptx
```

The Layout IR is the central artifact that enables validation, refinement, strategy switching, and future multi-format rendering.

## Module Responsibilities

### parser

Detects page structure, text blocks, cards, shapes, icons, images, and background regions.

v0.1 does not implement automatic parsing yet. It starts from manually or model-generated Layout IR.

### ir

Defines the layout schema, validates required fields, and normalizes coordinates, colors, and style values.

`src/ir/validators.py` only checks Layout IR before rendering. It does not inspect generated PPTX files.

### planner

Chooses the handling strategy for each element:

- rebuild
- crop
- background_crop
- text_on_crop
- asset_search
- native_chart

### assets

Manages cropped assets, icon replacements, image files, and asset registry metadata.

### renderers

Converts Layout IR into PowerPoint objects.

v0.1 should prefer stable `python-pptx` APIs.

### validators

Checks file compatibility and editability requirements.

The most important validator is whether the generated PPTX opens without repair warnings.

Current v0.1 validators are split by output concern:

- `src/validators/pptx_integrity.py`: checks the generated PPTX zip package and required PowerPoint parts.
- `src/validators/editable_check.py`: checks editable text boxes, editable shapes, image count, full-page image ratio, and key editable roles.

### screenshot and diff

Later-stage modules that render the generated PPTX to an image and compare it with the source image.

### refine

Adjusts Layout IR based on validation results, visual diff, and user feedback.
