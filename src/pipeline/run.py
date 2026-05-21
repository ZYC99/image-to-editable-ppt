from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from src.ir.schema import Layout
from src.ir.validators import validate_layout
from src.renderers.pptx_renderer import PptxRenderer
from src.validators.editable_check import check_editability
from src.validators.pptx_integrity import check_pptx_integrity


app = typer.Typer(add_completion=False)
console = Console()

DEFAULT_LAYOUT = Path("workspace/ir/layout_v01.json")
DEFAULT_OUTPUT = Path("workspace/pptx/output_v01.pptx")
DEFAULT_REPORT = Path("workspace/reports/validation_report_v01.json")


@app.command()
def main(
    layout: Annotated[Path, typer.Option("--layout", help="Path to layout JSON.")] = DEFAULT_LAYOUT,
    output: Annotated[Path, typer.Option("--output", help="Path for generated PPTX.")] = DEFAULT_OUTPUT,
    report: Annotated[Path, typer.Option("--report", help="Path for validation JSON report.")] = DEFAULT_REPORT,
    min_text_boxes: Annotated[int, typer.Option(help="Minimum editable text boxes.")] = 8,
    min_shapes: Annotated[int, typer.Option(help="Minimum editable shapes.")] = 8,
) -> None:
    run_v01_pipeline(layout, output, report, min_text_boxes, min_shapes)


def run_v01_pipeline(
    layout: Path = DEFAULT_LAYOUT,
    output: Path = DEFAULT_OUTPUT,
    report: Path = DEFAULT_REPORT,
    min_text_boxes: int = 8,
    min_shapes: int = 8,
) -> dict:
    parsed_layout = Layout.from_json_file(layout)
    base_dir = layout.parent

    layout_errors = validate_layout(parsed_layout, base_dir=base_dir)
    if layout_errors:
        raise typer.BadParameter("; ".join(layout_errors))

    renderer = PptxRenderer(parsed_layout, base_dir=base_dir)
    renderer.render(output)

    integrity = check_pptx_integrity(output)
    editability = check_editability(
        output,
        layout=parsed_layout,
        min_text_boxes=min_text_boxes,
        min_shapes=min_shapes,
    )
    passed = not integrity["errors"] and not editability["errors"]
    report_data = {
        "passed": passed,
        "layout": str(layout),
        "output": str(output),
        "mode": parsed_layout.mode,
        "layout_validation": {
            "passed": True,
            "errors": [],
        },
        "integrity": integrity,
        "editability": editability,
    }

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")

    if passed:
        console.print(f"[green]PPTX generated and validated:[/green] {output}")
    else:
        console.print(f"[red]Validation failed.[/red] See {report}")
        raise typer.Exit(code=1)
    return report_data


if __name__ == "__main__":
    app()
