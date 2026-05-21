# Layout IR

## Purpose

Layout IR is the intermediate representation between visual parsing and PPTX rendering.

It should describe what elements exist on a slide, where they are, how they should look, and how they should be reconstructed.

## Coordinate System

Use pixel coordinates based on the source image canvas.

Recommended default:

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

Renderer should map pixels to PowerPoint inches:

```text
ppt_x = x / base_width * ppt_width_in
ppt_y = y / base_height * ppt_height_in
ppt_w = w / base_width * ppt_width_in
ppt_h = h / base_height * ppt_height_in
```

## Element Types

v0.1 supports these element types.

### text

Editable text box.

### shape

Editable PowerPoint shape such as rectangle, rounded rectangle, oval, triangle, or freeform placeholder.

### line

Editable line, connector, arrow, or separator.

### image

Inserted image asset, usually cropped from source or resolved from asset library.

### group

Semantic grouping of child elements.

Future versions may add `chart` and `table` once the renderer and validation gates are stable.

## Strategies

### rebuild

Recreate as native PowerPoint object.

### crop

Crop from source image and place as image asset.

### background_crop

Crop a low-edit-value visual region and use it as a background layer.

### text_on_crop

Use cropped image as visual base, then overlay editable text.

### asset_search

Use an icon or SVG replacement from an asset library.

### native_chart

Rebuild as editable native PowerPoint chart when data can be inferred or provided.

## Example

```json
{
  "version": "0.1",
  "mode": "balanced",
  "page": {
    "width": 1920,
    "height": 1080,
    "background": {
      "type": "solid",
      "color": "#F7F8FA"
    },
    "coordinate_system": {
      "unit": "px",
      "base_width": 1920,
      "base_height": 1080,
      "ppt_width_in": 13.333,
      "ppt_height_in": 7.5
    }
  },
  "elements": [
    {
      "id": "title_1",
      "type": "text",
      "strategy": "rebuild",
      "editable": true,
      "fallback_strategy": "crop",
      "confidence": 0.92,
      "text": "年度经营分析",
      "x": 120,
      "y": 80,
      "w": 680,
      "h": 64,
      "z_index": 10,
      "style": {
        "font_family": "Microsoft YaHei",
        "font_size": 42,
        "font_weight": 700,
        "color": "#111827",
        "align": "left",
        "vertical_align": "top",
        "line_height": 1.15,
        "fit": {
          "autofit": "shrink_text",
          "max_font_size": 42,
          "min_font_size": 28,
          "wrap": true
        }
      }
    }
  ]
}
```
