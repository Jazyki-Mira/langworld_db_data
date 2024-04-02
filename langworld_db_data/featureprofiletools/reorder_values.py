from pathlib import Path


def _lines(file: Path, line_number_to_cut: int, line_number_to_insert_before: int) -> None:
    """Cut one line and insert it before the other."""

    with file.open(encoding="utf8") as fh:
        lines = fh.readlines()
        new_lines = (
            lines[:67] + lines[68: 98] + [lines[67]] + lines[98:]
        )

    with file.open(mode="w", encoding="utf8") as fh:
        fh.writelines(new_lines)