with file.open(encoding="utf8") as fh:
    lines = fh.readlines()
    new_lines = (
        lines[:67] + lines[68: 98] + [lines[67]] + lines[98:]
    )

with file.open(mode="w", encoding="utf8") as fh:
    fh.writelines(new_lines)