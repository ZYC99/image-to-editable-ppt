from __future__ import annotations

from pathlib import Path

from src.ir.normalize import flatten_elements
from src.ir.schema import ElementType, Layout, Mode, Strategy


def validate_layout(layout: Layout, base_dir: str | Path | None = None) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    canvas_area = layout.canvas.width * layout.canvas.height

    for element in flatten_elements(layout.elements):
        if element.id in ids:
            errors.append(f"duplicate element id: {element.id}")
        ids.add(element.id)

        if element.x + element.w > layout.canvas.width:
            errors.append(f"element {element.id} exceeds canvas width")
        if element.y + element.h > layout.canvas.height:
            errors.append(f"element {element.id} exceeds canvas height")

        if element.type == ElementType.IMAGE and element.src and base_dir:
            image_path = Path(base_dir, element.src).resolve()
            if not image_path.exists():
                errors.append(f"image element {element.id} missing asset: {element.src}")

        image_like = element.type == ElementType.IMAGE or element.strategy in {
            Strategy.CROP,
            Strategy.BACKGROUND_CROP,
            Strategy.TEXT_ON_CROP,
        }
        if layout.mode != Mode.FIDELITY_FIRST and image_like:
            area_ratio = (element.w * element.h) / canvas_area
            if area_ratio >= 0.9:
                errors.append(
                    f"element {element.id} looks like a full-page raster fallback "
                    f"({area_ratio:.2%}) outside fidelity_first mode"
                )

    return errors
