# Failure Modes

## FM-001: PowerPoint repair warning

### Symptom

PowerPoint shows a repair warning when opening the generated `.pptx`.

### Impact

The output is invalid. Visual similarity and editability should not be evaluated until this is fixed.

### Suspected Causes

- Invalid OpenXML relationship
- Unsupported or malformed shape definition
- Broken media reference
- Corrupted zip package
- Renderer generated incomplete PPTX structure

### Mitigation

- Prefer stable `python-pptx` APIs in v0.1
- Validate PPTX as a zip file
- Check required PowerPoint XML files
- Avoid hand-written OpenXML unless covered by tests
- Add a LibreOffice headless open/export check when available

### Rule

Compatibility comes first. A file that opens with repair warnings is a failed output.

## FM-002: Full-page screenshot fake editability

### Symptom

The slide looks visually similar because the source image was inserted as a full-page background, but almost nothing is editable.

### Impact

This does not satisfy the project goal except in explicit `fidelity_first` mode.

### Mitigation

- Add editable object count gate
- Add full-page image area ratio check
- Require key text and major shapes to be editable

### Rule

Do not use a full-page screenshot as the main solution unless the mode is explicitly `fidelity_first`.

## FM-003: Text overflow or unexpected wrapping

### Symptom

Text boxes look correct in the generated script but overflow, wrap differently, or change line spacing in PowerPoint.

### Impact

High visual mismatch, especially for Chinese text.

### Mitigation

- Add text fit policy to IR
- Use conservative text box sizes
- Support shrink-to-fit
- Prefer common fonts
- Add rendered screenshot checks later

## FM-004: Icon mismatch

### Symptom

Icons recreated with basic shapes look visibly different from the source.

### Impact

The slide appears low-quality even when layout is correct.

### Mitigation

- Use SVG/icon library when possible
- Use crop fallback for complex icons
- Use `asset_search` or `crop` rather than hard-drawing with basic shapes

## FM-005: Visual fidelity too low in full rebuild mode

### Symptom

All objects are editable, but the slide lacks the original polish, gradients, shadows, spacing, and illustration quality.

### Impact

The slide is technically editable but not acceptable as a design reconstruction.

### Mitigation

- Default to `balanced` mixed strategy
- Rebuild key text and structure
- Crop low-edit-value decorative visuals
- Avoid over-rebuilding complex effects
