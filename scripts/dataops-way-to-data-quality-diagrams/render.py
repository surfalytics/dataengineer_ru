"""Отрисовка схем книги с помощью общего формата спецификаций портала."""
from pathlib import Path
import importlib.util

DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "book_canvas", DIRECTORY.parent / "data-quality-fundamentals-diagrams" / "excb.py"
)
canvas = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(canvas)
canvas.OUT = DIRECTORY.parents[1] / "public" / "assets" / "dataops-way-to-data-quality"
E, N, T, Z = canvas.E, canvas.N, canvas.T, canvas.Z


def render(diagrams):
    for name, diagram in diagrams.items():
        # The shared helper uses its input name for both the scene and the PNG.
        # Give each scene a book-specific name without changing the public URL.
        unique_name = f"dataops-way-{name}"
        canvas.run(unique_name, diagram)
        (canvas.OUT / f"{unique_name}.png").replace(canvas.OUT / f"{name}.png")
