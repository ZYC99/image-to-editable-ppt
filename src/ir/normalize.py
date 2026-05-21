from __future__ import annotations

from pptx.util import Inches

from src.ir.schema import Element, Layout


def px_to_inches(value: float, source_px: float, target_in: float) -> float:
    return value / source_px * target_in


def element_to_inches(layout: Layout, element: Element) -> tuple[int, int, int, int]:
    left = Inches(px_to_inches(element.x, layout.canvas.width, layout.slide_size.width_in))
    top = Inches(px_to_inches(element.y, layout.canvas.height, layout.slide_size.height_in))
    width = Inches(px_to_inches(element.w, layout.canvas.width, layout.slide_size.width_in))
    height = Inches(px_to_inches(element.h, layout.canvas.height, layout.slide_size.height_in))
    return left, top, width, height


def sorted_elements(elements: list[Element]) -> list[Element]:
    return sorted(elements, key=lambda item: item.z_index)


def flatten_elements(elements: list[Element]) -> list[Element]:
    flattened: list[Element] = []
    for element in sorted_elements(elements):
        flattened.append(element)
        if element.children:
            flattened.extend(flatten_elements(element.children))
    return flattened
