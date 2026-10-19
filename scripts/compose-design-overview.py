"""Assemble the paper's three design panels into a portable full-size figure.

Uses the exported PNGs unchanged, with embedded image data so the SVG can be
opened or downloaded independently. Run after refreshing the source figures.
"""

import base64
from html import escape
from pathlib import Path

from PIL import Image


def compose():
    assets = Path(__file__).resolve().parent.parent / "assets"
    page_width, padding, gap = 2400, 64, 56
    content_width = page_width - 2 * padding - gap
    left_width = round(content_width * 0.42 / 0.98)
    right_width = content_width - left_width
    label_space, row_gap = 64, 40

    def panel(name, width):
        path = assets / f"{name}.png"
        with Image.open(path) as image:
            height = round(width * image.height / image.width)
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return width, height, data

    taxonomy = panel("capability_taxonomy", left_width)
    alignment = panel("real_sim_alignment", right_width)
    diversity = panel("scene_diversity", right_width)
    left_height = taxonomy[1] + label_space
    right_height = alignment[1] + diversity[1] + 2 * label_space + row_gap
    content_height = max(left_height, right_height)
    page_height = content_height + 2 * padding
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_width}" '
        f'height="{page_height}" viewBox="0 0 {page_width} {page_height}" '
        'style="display:block;width:100%;height:auto" '
        'role="img" aria-labelledby="title description">',
        '<title id="title">Overview of the OpenViTac design</title>',
        '<desc id="description">Capability Taxonomy on the left; '
        'Real–Sim Alignment above Scene Diversity on the right.</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
    ]

    def add_panel(image, x, y, label):
        width, height, data = image
        parts.append(
            f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
            f'href="data:image/png;base64,{data}"/>'
        )
        parts.append(
            f'<text x="{x + width / 2}" y="{y + height + 43}" '
            'text-anchor="middle" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="32" fill="#202a3b">{escape(label)}</text>'
        )

    add_panel(taxonomy, padding, padding + (content_height - left_height) / 2,
              "(a) Capability Taxonomy")
    right_x = padding + left_width + gap
    add_panel(alignment, right_x, padding, "(b) Real–Sim Alignment")
    add_panel(diversity, right_x, padding + alignment[1] + label_space + row_gap,
              "(c) Scene Diversity")
    parts.append('</svg>')
    output = assets / "design_overview.svg"
    output.write_text('\n'.join(parts), encoding="utf-8")
    print(f"{output.name}: {page_width} x {page_height}, three embedded panels")


if __name__ == "__main__":
    compose()
