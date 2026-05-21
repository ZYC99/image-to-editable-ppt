from pathlib import Path

from src.ir.schema import Layout
from src.renderers.pptx_renderer import PptxRenderer
from src.validators.editable_check import check_editability
from src.validators.pptx_integrity import check_pptx_integrity


def test_demo_render_passes_validation(tmp_path: Path):
    layout = Layout.from_json_file("workspace/ir/layout_v01.json")
    output = tmp_path / "demo.pptx"

    PptxRenderer(layout, base_dir="workspace/ir").render(output)

    integrity = check_pptx_integrity(output)
    editability = check_editability(output, layout=layout)

    assert integrity["valid_zip"]
    assert integrity["required_files_present"]
    assert editability["passes_thresholds"]
    assert editability["editable_text_boxes"] >= 8
    assert editability["editable_shapes"] >= 8
    assert editability["editable_object_ratio"] > 0
    assert editability["key_elements_editable"]["passed"]
    assert "text_overflow_warnings" in editability
