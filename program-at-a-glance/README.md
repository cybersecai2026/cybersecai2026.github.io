# Program At A Glance source code

- `build_from_pdf.py` is the current image builder. It reads `../artifacts/program-at-a-glance.pdf` and writes `../assets/images/program-at-a-glance.png` with the requested visual adjustments.
- `build_compact_legacy.py` is the earlier standalone image design. It also writes to the website image path, so running it will replace the current PDF-based image.
- `build_pptx_legacy.mjs` created the earlier editable PowerPoint file. Its layout predates the supplied PDF and the later image revisions.

The PDF, PPTX, and exported images remain in `artifacts/` and `assets/images/`; this directory holds their generation code.
