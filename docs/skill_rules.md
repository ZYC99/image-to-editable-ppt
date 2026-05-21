# Skill Rules

## Rule 001: Compatibility first

Generated PPTX must open in PowerPoint without repair warnings.

If the file requires repair, the run is failed. Do not evaluate visual similarity until compatibility is fixed.

## Rule 002: No fake editable PPT

Do not use a full-page screenshot as the main solution unless the user explicitly chooses `fidelity_first` mode.

## Rule 003: Key content must be editable

Main title, subtitles, key numbers, section labels, and important explanatory text should be editable whenever possible.

## Rule 004: Use crop fallback for low-edit-value visuals

Complex decorative icons, gradients, shadows, illustrations, textures, and light effects may be cropped as local assets.

## Rule 005: Prefer mixed strategy by default

Default mode is `balanced`.

Recommended handling:

- text: editable
- cards and basic shapes: editable
- simple lines: editable
- complex icons: crop or SVG
- complex background: crop or simplified native shape

## Rule 006: Use Layout IR as the source of truth

Do not directly generate final PPTX without a Layout IR.

Every output should be reproducible from `layout.json`.

## Rule 007: Validate editability

Each generated PPTX should produce an editable report.

Recommended MVP gate:

```text
text_boxes >= 8
editable_shapes >= 8
full_page_image_area_ratio <= 0.4 unless mode == fidelity_first
```

## Rule 008: Record failures

Every major failure should be recorded in `docs/failure_modes.md`.

A useful failure record includes:

- symptom
- suspected cause
- mitigation
- whether the mitigation becomes a hard rule
