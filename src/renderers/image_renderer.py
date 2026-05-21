from __future__ import annotations

from pathlib import Path

from src.ir.normalize import element_to_inches
from src.ir.schema import Element, Layout


def render_image(slide, layout: Layout, element: Element, base_dir: Path):
    if not element.src:
        raise ValueError(f"image element {element.id!r} is missing src")
    image_path = Path(element.src)
    if not image_path.is_absolute():
        image_path = base_dir / image_path
    if not image_path.exists():
        raise FileNotFoundError(f"missing image asset for {element.id}: {image_path}")

    left, top, width, height = element_to_inches(layout, element)
    picture = slide.shapes.add_picture(str(image_path), left, top, width, height)
    picture.name = element.id
    return picture
