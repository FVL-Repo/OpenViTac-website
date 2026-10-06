"""Export source PDFs without their large white vector background panels.

Usage: python scripts/export-figures.py /path/to/Tactilebench/figs
Dependencies: pip install pillow pymupdf pikepdf
Source PDFs are never changed. Photos and small white details remain intact.
"""

import io
import re
import sys
from pathlib import Path

import fitz
import pikepdf
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(sys.argv[1])
FIGURES = {
    "teaser": ("main_teaser.pdf", 2000),
    "capability_taxonomy": ("compability_taxonomy.pdf", 1600),
    "real_sim_alignment": ("real_sim_alignment.pdf", 2000),
    "scene_diversity": ("diverse_scene.pdf", 2000),
    "tactile_design": ("tactile_injection.pdf", 2200),
    "tactile_radar": ("tactile_radar.pdf", 1000),
}
TASKS = {
    "weight_classify": "weight_classify_combined_figure.pdf",
    "hardness_classify": "hardness_classify_combined_figure.pdf",
    "roughness_classify": "roughness_classify_combined_figure.pdf",
    "roughness_regrasp": "roughness_regrasp_combined_figure.pdf",
    "empty_can_select": "can_empty_select_combined_figure.pdf",
    "grasp_chips": "grasp_chips_0_figure.pdf",
    "gear_assembly": "turn_gear_pair_0_figure.pdf",
    "pull_drawer": "pull_drawer_0_figure.pdf",
    "insert_usb": "insert_USB_0_figure.pdf",
    "insert_usb_sensors": "insert_USB_three_sensors_figure.pdf",
    "insert_block_v1": "insert_block_v1_combined_figure.pdf",
    "insert_block_v2_p1": "insert_block_v2_part1_figure.pdf",
    "insert_block_v2_p2": "insert_block_v2_part2_figure.pdf",
}
OPAQUE_FIGURES = {"tactile_radar", "tactile_design"}


def transparent_pdf(path):
    pdf = pikepdf.open(path)
    page = pdf.pages[0]
    original = fitz.open(path)
    source_page = original[0]
    # Some task PDFs contain a single flattened diagram rather than vectors.
    # Add a PDF soft mask only to large diagram images, preserving photos.
    page_background_only = path.name == "real_sim_alignment.pdf"
    for entry in ([] if page_background_only else source_page.get_images()):
        xref = entry[0]
        rects = source_page.get_image_rects(xref)
        if not any(rect.width * rect.height >= source_page.rect.width * source_page.rect.height * 0.5 for rect in rects):
            continue
        obj = pdf.get_object(xref, 0)
        if '/SMask' in obj:
            continue
        embedded = Image.open(io.BytesIO(original.extract_image(xref)['image'])).convert('RGB')
        channels = embedded.split()
        minimum = ImageChops.darker(ImageChops.darker(channels[0], channels[1]), channels[2])
        candidates = minimum.point(lambda value: 255 if value >= 250 else 0)
        w, h = embedded.size
        for x, y in ([(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]):
            if candidates.getpixel((x, y)) == 255:
                ImageDraw.floodfill(candidates, (x, y), 128)
        alpha = candidates.point(lambda value: 0 if value == 128 else 255)
        if alpha.getextrema()[0] == 0:
            mask = pdf.make_stream(alpha.tobytes())
            mask.Type = pikepdf.Name('/XObject')
            mask.Subtype = pikepdf.Name('/Image')
            mask.Width, mask.Height = w, h
            mask.ColorSpace = pikepdf.Name('/DeviceGray')
            mask.BitsPerComponent = 8
            obj.SMask = mask
    box = [float(x) for x in page.MediaBox]
    # Alignment labels have white fills that must remain opaque. Its only
    # removable white shape is the background covering the entire page.
    threshold = (box[2] - box[0]) * (box[3] - box[1]) * (0.99 if page_background_only else 0.01)
    color, stack, points, output = (0,), [], [], []
    removed = 0
    for instruction in pikepdf.parse_content_stream(page):
        args, operator = instruction
        op = str(operator)
        if op == "q":
            stack.append(color)
        elif op == "Q" and stack:
            color = stack.pop()
        elif op in {"g", "rg", "k", "sc", "scn"}:
            try:
                color = tuple(float(x) for x in args)
                if op == "k":
                    color = (1,) if color == (0, 0, 0, 0) else (0,)
            except (TypeError, ValueError):
                color = (0,)
        elif op in {"m", "l", "c", "v", "y"}:
            values = [float(x) for x in args]
            points.extend(zip(values[::2], values[1::2]))
        elif op == "re":
            x, y, w, h = map(float, args)
            points.extend([(x, y), (x + w, y + h)])
        if op in {"f", "f*", "F", "B", "B*", "b", "b*", "S", "s", "n"}:
            area = 0
            if points:
                xs, ys = zip(*points)
                area = (max(xs) - min(xs)) * (max(ys) - min(ys))
            if op in {"f", "f*", "F", "B", "B*", "b", "b*"} and color in {(1,), (1, 1, 1)} and area >= threshold:
                replacement = "s" if op.startswith("b") else "S" if op.startswith("B") else "n"
                instruction = pikepdf.ContentStreamInstruction([], pikepdf.Operator(replacement))
                removed += 1
            points = []
        output.append(instruction)
    page.Contents = pdf.make_stream(pikepdf.unparse_content_stream(output))
    data = io.BytesIO()
    pdf.save(data)
    return data.getvalue(), removed


def export(name, source, width, directory, responsive=False):
    opaque = name in OPAQUE_FIGURES
    data, removed = (source.read_bytes(), 0) if opaque else transparent_pdf(source)
    document = fitz.open(stream=data, filetype="pdf")
    page = document[0]
    pixmap = page.get_pixmap(matrix=fitz.Matrix(width / page.rect.width, width / page.rect.width), alpha=not opaque)
    # MuPDF returns premultiplied alpha; PNG encoding restores straight alpha.
    image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("RGBA")
    image.save(directory / f"{name}.png", optimize=True)
    image.save(directory / f"{name}.webp", quality=88, method=6, exact=True)
    if responsive:
        small = image.resize((800, round(image.height * 800 / image.width)), Image.Resampling.LANCZOS)
        small.save(directory / f"{name}-800.webp", quality=85, method=6, exact=True)
    expected_minimum = 255 if opaque else 0
    assert image.getchannel("A").getextrema()[0] == expected_minimum, f"Unexpected background: {source}"
    print(f"{name}: {image.width}x{image.height}, removed {removed} background panels")
    return image.size


html_path = ROOT / "index.html"
html = html_path.read_text()
for name, (filename, width) in FIGURES.items():
    w, h = export(name, SOURCE / filename, width, ROOT / "assets", True)
    # Keep image dimensions consistent with the newly rendered PDFs.
    pattern = rf'(src="assets/{name}\.webp"[\s\S]*?width=")\d+("\s+height=")\d+(")'
    html, count = re.subn(pattern, lambda m: f'{m[1]}{w}{m[2]}{h}{m[3]}', html)
    assert count == 1, name
html_path.write_text(html)
for name, filename in TASKS.items():
    export(name, SOURCE / "Task_visualization" / filename, 1200, ROOT / "assets/tasks")
