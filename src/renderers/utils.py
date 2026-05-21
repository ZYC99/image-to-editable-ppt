from __future__ import annotations

from pptx.dml.color import RGBColor


def hex_to_rgb(value: str | None, default: str = "#000000") -> RGBColor:
    color = (value or default).strip()
    if color.startswith("#"):
        color = color[1:]
    if len(color) == 3:
        color = "".join(part * 2 for part in color)
    if len(color) != 6:
        color = default.lstrip("#")
    return RGBColor(int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))


def style_value(style: dict, key: str, default=None):
    value = style.get(key, default)
    return default if value is None else value
