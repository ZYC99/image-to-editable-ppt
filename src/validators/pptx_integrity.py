from __future__ import annotations

from pathlib import Path
from zipfile import BadZipFile, ZipFile


REQUIRED_FILES = {
    "[Content_Types].xml",
    "_rels/.rels",
    "ppt/presentation.xml",
    "ppt/slides/slide1.xml",
}


def check_pptx_integrity(path: str | Path) -> dict:
    pptx_path = Path(path)
    result = {
        "valid_zip": False,
        "required_files_present": False,
        "missing_files": [],
        "errors": [],
    }

    if not pptx_path.exists():
        result["errors"].append(f"file does not exist: {pptx_path}")
        return result

    try:
        with ZipFile(pptx_path) as archive:
            names = set(archive.namelist())
            archive.testzip()
    except BadZipFile as exc:
        result["errors"].append(f"invalid zip: {exc}")
        return result

    result["valid_zip"] = True
    missing = sorted(REQUIRED_FILES - names)
    result["missing_files"] = missing
    result["required_files_present"] = not missing
    if missing:
        result["errors"].append(f"missing required files: {', '.join(missing)}")
    return result
