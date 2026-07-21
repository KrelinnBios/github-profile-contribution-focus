"""Write cache-safe SVG output and update its README reference."""

import hashlib
import os
import re
from pathlib import Path


def svg_reference(readme_path: Path, svg_path: Path) -> str:
    relative = os.path.relpath(svg_path.resolve(), readme_path.parent.resolve())
    reference = Path(relative).as_posix()
    return reference if reference.startswith(".") else f"./{reference}"


def write_text_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def write_outputs(
    svg: str,
    readme_path: Path,
    output_directory: Path,
    output_prefix: str,
) -> tuple[Path, bool]:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", output_prefix):
        raise RuntimeError(
            "output-prefix may contain only letters, numbers, dots, underscores, and hyphens."
        )

    output_directory.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(svg.encode("utf-8")).hexdigest()[:12]
    versioned_output = output_directory / f"{output_prefix}-{digest}.svg"
    changed = write_text_if_changed(versioned_output, svg)

    legacy_output = output_directory / f"{output_prefix}.svg"
    if legacy_output.exists():
        legacy_output.unlink()
        changed = True

    old_pattern = re.compile(rf"{re.escape(output_prefix)}-[0-9a-f]{{12}}\.svg")
    for candidate in output_directory.glob(f"{output_prefix}-*.svg"):
        if candidate != versioned_output and old_pattern.fullmatch(candidate.name):
            candidate.unlink()
            changed = True

    if not readme_path.exists():
        raise RuntimeError(f"README not found: {readme_path}")

    current_reference = svg_reference(readme_path, versioned_output)
    base_reference = svg_reference(readme_path, output_directory / output_prefix)
    if base_reference.startswith("./"):
        reference_pattern = rf"(?:\./)?{re.escape(base_reference[2:])}"
    else:
        reference_pattern = re.escape(base_reference)
    pattern = rf"{reference_pattern}(?:-[0-9a-f]{{12}})?\.svg(?:\?[^\"'<> ]*)?"

    readme = readme_path.read_text(encoding="utf-8")
    if not re.search(pattern, readme):
        placeholder = f"{base_reference}.svg"
        raise RuntimeError(
            "No contribution focus image reference was found in the README. Add "
            f'`<img src="{placeholder}" alt="Contribution focus" />` first.'
        )
    updated = re.sub(pattern, current_reference, readme, count=1)
    changed = write_text_if_changed(readme_path, updated) or changed
    return versioned_output, changed


def set_action_outputs(image: Path, changed: bool) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        output.write(f"image={image.as_posix()}\n")
        output.write(f"changed={'true' if changed else 'false'}\n")
