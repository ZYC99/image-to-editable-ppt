from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ElementType(str, Enum):
    TEXT = "text"
    SHAPE = "shape"
    LINE = "line"
    IMAGE = "image"
    GROUP = "group"


class Strategy(str, Enum):
    REBUILD = "rebuild"
    CROP = "crop"
    BACKGROUND_CROP = "background_crop"
    TEXT_ON_CROP = "text_on_crop"
    ASSET_SEARCH = "asset_search"
    NATIVE_CHART = "native_chart"


class Mode(str, Enum):
    BALANCED = "balanced"
    FIDELITY_FIRST = "fidelity_first"
    EDITABILITY_FIRST = "editability_first"


class Canvas(BaseModel):
    width: int = Field(default=1920, gt=0)
    height: int = Field(default=1080, gt=0)


class SlideSize(BaseModel):
    width_in: float = Field(default=13.333, gt=0)
    height_in: float = Field(default=7.5, gt=0)


class Box(BaseModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    w: float = Field(gt=0)
    h: float = Field(gt=0)


class TextRun(BaseModel):
    text: str
    bold: bool | None = None
    italic: bool | None = None
    font_size: float | None = Field(default=None, gt=0)
    color: str | None = None


class Element(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    type: ElementType
    strategy: Strategy = Strategy.REBUILD
    editable: bool = True
    fallback_strategy: Strategy | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    w: float = Field(gt=0)
    h: float = Field(gt=0)
    z_index: int = 0
    style: dict[str, Any] = Field(default_factory=dict)

    # Type-specific optional payload.
    text: str | None = None
    runs: list[TextRun] | None = None
    shape: str | None = None
    src: str | None = None
    children: list["Element"] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def id_must_not_be_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("element id cannot be empty")
        return cleaned

    @model_validator(mode="after")
    def validate_payload(self) -> "Element":
        if self.type == ElementType.TEXT and not (self.text or self.runs):
            raise ValueError(f"text element {self.id!r} requires text or runs")
        if self.type == ElementType.IMAGE and not self.src:
            raise ValueError(f"image element {self.id!r} requires src")
        if self.type == ElementType.GROUP and not self.children:
            raise ValueError(f"group element {self.id!r} requires children")
        return self

    @property
    def box(self) -> Box:
        return Box(x=self.x, y=self.y, w=self.w, h=self.h)


class Layout(BaseModel):
    version: Literal["0.1"] = "0.1"
    mode: Mode = Mode.BALANCED
    canvas: Canvas = Field(default_factory=Canvas)
    slide_size: SlideSize = Field(default_factory=SlideSize)
    background: str | None = None
    elements: list[Element]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("elements")
    @classmethod
    def elements_must_not_be_empty(cls, value: list[Element]) -> list[Element]:
        if not value:
            raise ValueError("layout requires at least one element")
        return value

    @classmethod
    def from_json_file(cls, path: str | Path) -> "Layout":
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))


Element.model_rebuild()
