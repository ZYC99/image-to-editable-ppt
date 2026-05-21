from __future__ import annotations

from pathlib import Path
from math import ceil
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from src.ir.normalize import flatten_elements
from src.ir.schema import Element, ElementType, Layout, Mode, Strategy


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def check_editability(
    pptx_path: str | Path,
    layout: Layout | None = None,
    min_text_boxes: int = 8,
    min_shapes: int = 8,
    max_full_page_image_ratio: float = 0.9,
) -> dict:
    counts = {
        "editable_text_boxes": 0,
        "editable_shapes": 0,
        "images": 0,
        "editable_object_ratio": 0.0,
        "full_page_image_area_ratio": 0.0,
        "key_elements_editable": {
            "required_roles": [],
            "found_roles": [],
            "missing_roles": [],
            "passed": True,
        },
        "text_overflow_warnings": [],
        "passes_thresholds": False,
        "errors": [],
    }

    with ZipFile(pptx_path) as archive:
        slide_names = sorted(name for name in archive.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
        for slide_name in slide_names:
            root = ET.fromstring(archive.read(slide_name))
            counts["images"] += len(root.findall(".//p:pic", NS))
            shape_nodes = root.findall(".//p:sp", NS)
            for node in shape_nodes:
                c_nv_sp_pr = node.find("./p:nvSpPr/p:cNvSpPr", NS)
                is_textbox = c_nv_sp_pr is not None and c_nv_sp_pr.attrib.get("txBox") == "1"
                if is_textbox:
                    counts["editable_text_boxes"] += 1
                else:
                    counts["editable_shapes"] += 1

    total_objects = counts["editable_text_boxes"] + counts["editable_shapes"] + counts["images"]
    if total_objects:
        editable_objects = counts["editable_text_boxes"] + counts["editable_shapes"]
        counts["editable_object_ratio"] = round(editable_objects / total_objects, 4)

    mode = layout.mode if layout else Mode.BALANCED
    if layout:
        counts["full_page_image_area_ratio"] = largest_image_like_area_ratio(layout)
        counts["key_elements_editable"] = check_key_elements_editable(layout)
        counts["text_overflow_warnings"] = estimate_text_overflow_warnings(layout)

    if counts["editable_text_boxes"] < min_text_boxes:
        counts["errors"].append(
            f"editable text boxes too low: {counts['editable_text_boxes']} < {min_text_boxes}"
        )
    if counts["editable_shapes"] < min_shapes:
        counts["errors"].append(f"editable shapes too low: {counts['editable_shapes']} < {min_shapes}")
    if mode != Mode.FIDELITY_FIRST and counts["full_page_image_area_ratio"] >= max_full_page_image_ratio:
        counts["errors"].append(
            "full-page image fallback ratio too high: "
            f"{counts['full_page_image_area_ratio']:.2%} >= {max_full_page_image_ratio:.2%}"
        )
    if not counts["key_elements_editable"]["passed"]:
        missing = ", ".join(counts["key_elements_editable"]["missing_roles"])
        counts["errors"].append(f"required key elements are not editable: {missing}")

    counts["passes_thresholds"] = not counts["errors"]
    return counts


def largest_image_like_area_ratio(layout: Layout) -> float:
    canvas_area = layout.canvas.width * layout.canvas.height
    largest = 0.0
    for element in flatten_elements(layout.elements):
        image_like = element.type == ElementType.IMAGE or element.strategy in {
            Strategy.CROP,
            Strategy.BACKGROUND_CROP,
            Strategy.TEXT_ON_CROP,
        }
        if image_like:
            largest = max(largest, (element.w * element.h) / canvas_area)
    return largest


def check_key_elements_editable(layout: Layout) -> dict:
    required_roles = {
        "title",
        "subtitle",
        "key_metric",
        "conclusion",
    }
    found_roles: set[str] = set()

    for element in flatten_elements(layout.elements):
        role = element.style.get("semantic_role") or element.style.get("role")
        if role in required_roles and element.editable and element.type == ElementType.TEXT:
            found_roles.add(role)

    missing_roles = sorted(required_roles - found_roles)
    return {
        "required_roles": sorted(required_roles),
        "found_roles": sorted(found_roles),
        "missing_roles": missing_roles,
        "passed": not missing_roles,
    }


def estimate_text_overflow_warnings(layout: Layout) -> list[dict]:
    warnings = []
    for element in flatten_elements(layout.elements):
        if element.type != ElementType.TEXT:
            continue
        text = element_text(element)
        font_size = float(element.style.get("font_size", 18))
        line_spacing = float(element.style.get("line_spacing", 1.2))
        estimated_lines = estimate_line_count(text, font_size, element.w)
        estimated_height = estimated_lines * font_size * max(line_spacing, 1.0)
        if estimated_height > element.h:
            warnings.append(
                {
                    "element_id": element.id,
                    "text_length": len(text),
                    "font_size": font_size,
                    "textbox": {
                        "w": element.w,
                        "h": element.h,
                    },
                    "estimated_lines": estimated_lines,
                    "estimated_height": round(estimated_height, 2),
                    "available_height": element.h,
                    "message": "estimated text height exceeds textbox height",
                }
            )
    return warnings


def element_text(element: Element) -> str:
    if element.runs:
        return "".join(run.text for run in element.runs)
    return element.text or ""


def estimate_line_count(text: str, font_size: float, width: float) -> int:
    if not text:
        return 1
    explicit_lines = text.splitlines() or [text]
    chars_per_line = max(1, int(width / max(font_size * 0.6, 1)))
    return sum(max(1, ceil(len(line) / chars_per_line)) for line in explicit_lines)
