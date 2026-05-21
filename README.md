# Image-to-Editable-PPT

Convert a PPT design image into a high-fidelity, mostly editable `.pptx`.

The goal is not to paste a screenshot into PowerPoint.  
The goal is to reconstruct the slide into editable PowerPoint objects whenever practical.

## Pipeline

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

## MVP Scope

v0.1 focuses on:

- `layout.json` → valid `.pptx`
- Editable text boxes
- Editable basic shapes
- Local cropped image assets for complex regions
- Compatibility validation
- Editable object report

v0.1 does not focus on automatic vision parsing yet.

## Hard Rules

1. Generated PPTX must open in PowerPoint without repair warnings.
2. Do not use a full-page screenshot as the only meaningful content unless `fidelity_first` mode is explicitly selected.
3. Main title, subtitles, key numbers, and core text must be editable.
4. Complex icons, illustrations, gradients, and effects may be cropped as fallback assets.
5. Every output must include an editable report.

## Project Structure

```text
image-to-editable-ppt/
├─ README.md
├─ skill.md
├─ codex_tasks.md
├─ requirements.txt
├─ configs/
│  ├─ default.yaml
│  ├─ modes.yaml
│  └─ fonts.yaml
├─ examples/
│  ├─ input/
│  ├─ ir/
│  ├─ output/
│  └─ reports/
├─ workspace/
│  ├─ source/
│  ├─ crops/
│  ├─ assets/
│  ├─ ir/
│  ├─ pptx/
│  ├─ renders/
│  ├─ reports/
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
```

## Development Strategy

The first milestone is not automatic image understanding.  
The first milestone is a stable and testable local pipeline:

```text
layout.json → valid editable pptx → validation report
```

Only after the renderer and validation layer are stable should the project add automatic visual parsing, OCR, screenshot diff, and refinement.

## Validator Boundaries

- `src/ir/validators.py` checks whether Layout IR is valid before rendering.
- `src/validators/pptx_integrity.py` checks the generated PPTX package structure.
- `src/validators/editable_check.py` checks editable-object counts and raster fallback ratios.
