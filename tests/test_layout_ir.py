from src.ir.schema import Layout
from src.ir.validators import validate_layout


def test_demo_layout_is_valid():
    layout = Layout.from_json_file("workspace/ir/layout_v01.json")
    assert validate_layout(layout, base_dir="workspace/ir") == []
    assert len(layout.elements) >= 20
