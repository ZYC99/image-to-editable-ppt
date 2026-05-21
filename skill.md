# Image-to-Editable-PPT Skill

## Role

This skill helps convert a PPT visual image into a mostly editable PowerPoint file using a local toolchain.

The skill itself does not directly generate final PPTX by hand.  
It produces or refines Layout IR, chooses element strategies, invokes the local renderer, reviews validation reports, and updates failure rules.

## Workflow

1. Receive source image.
2. Analyze page visually.
3. Produce `layout.json`.
4. Mark each element with a strategy:
   - `rebuild`
   - `crop`
   - `background_crop`
   - `text_on_crop`
   - `asset_search`
   - `native_chart`
5. Render PPTX using local renderer.
6. Validate PPTX.
7. Review editable report.
8. Compare rendered preview with source image when screenshot rendering is available.
9. Refine layout or strategy.
10. Record failure modes.

## Output Requirements

Each run should produce:

- `layout.json`
- `output.pptx`
- `validation_report.json`
- optional `rendered.png`
- optional `diff_report.json`

## Non-negotiable Rules

### Rule 001: Compatibility first

If PowerPoint opens the file with a repair warning, the output is invalid.

### Rule 002: No fake editable PPT

Do not use a full-page screenshot as the main solution unless the mode is explicitly `fidelity_first`.

### Rule 003: Key content must be editable

Main title, subtitles, key numbers, section labels, and important explanatory text should be editable whenever possible.

### Rule 004: Use crop fallback for low-edit-value visuals

Complex decorative icons, gradients, shadows, illustrations, and light effects may be cropped as local assets.

### Rule 005: Prefer mixed strategy

Default mode is `balanced`:

- text: editable
- cards/shapes: editable
- simple lines: editable
- complex icons: crop or SVG
- complex background: crop or simplified native shape

## Modes

### balanced

Default mode. Prioritizes both visual similarity and editability.

### fidelity_first

Allows more rasterized/cropped elements to preserve appearance.

### editability_first

Maximizes native PPT objects, accepting lower visual fidelity.

## Layout IR Requirements

Every element should include enough metadata for validation and refinement:

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
  "w": 680,
  "h": 64,
  "z_index": 10,
  "style": {}
}
```

The IR should use a clear coordinate system:

```json
{
  "coordinate_system": {
    "unit": "px",
    "base_width": 1920,
    "base_height": 1080,
    "ppt_width_in": 13.333,
    "ppt_height_in": 7.5
  }
}
```

## Failure Recording

Each failed run should update `docs/failure_modes.md` with:

- failure id
- symptom
- suspected cause
- fix or mitigation
- whether the fix should become a hard rule
