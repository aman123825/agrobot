"""Cairo-free SVG -> PNG: svglib parse -> reportlab PDF -> PyMuPDF raster."""
import os, io, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

jobs = [
    ("docs/wiring-v2.svg", "wiring.png"),
    ("docs/bts7960-drive-schematic.svg", "drive_schematic.png"),
    ("docs/chassis-layout.svg", "chassis_repo.png"),
]


def main():
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    import fitz  # PyMuPDF

    ok = []
    for src, dst in jobs:
        try:
            drawing = svg2rlg(os.path.join(REPO, src))
            if drawing is None:
                print("parse failed:", src)
                continue
            pdf_bytes = renderPDF.drawToString(drawing)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
            pix.save(os.path.join(OUT, dst))
            doc.close()
            ok.append(dst)
            print("converted", src, "->", dst, f"({pix.width}x{pix.height})")
        except Exception:
            print("FAILED", src)
            traceback.print_exc()
    print("converted", len(ok), "svgs")


if __name__ == "__main__":
    main()
