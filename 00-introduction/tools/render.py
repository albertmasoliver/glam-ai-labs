#!/usr/bin/env python3
"""
render.py — render study-guide.md and study-guide-solutions.md to PDF.

Self-contained (its own CSS), so this repo rebuilds its PDFs without any
external dependency. Dev deps:  pip install markdown weasyprint pygments
Full rebuild:  python tools/gen.py && python tools/build_md.py && python tools/render.py
"""
import pathlib
import markdown
from weasyprint import HTML

ROOT = pathlib.Path(__file__).resolve().parent.parent

CSS = """
@page { size: A4; margin: 22mm 20mm;
  @bottom-center { content: counter(page) " / " counter(pages);
                   font-size: 9pt; color: #888; } }
body { font-family: "DejaVu Sans","Liberation Sans",sans-serif;
       font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; }
h1 { font-size: 21pt; color: #0b3d5c; border-bottom: 3px solid #0b3d5c;
     padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 15pt; color: #0b3d5c; margin-top: 1.4em;
     border-bottom: 1px solid #cdd9e0; padding-bottom: 3px; }
h3 { font-size: 12.5pt; color: #14506e; margin-top: 1.1em; }
h4 { font-size: 11pt; color: #333; }
h1,h2,h3,h4 { page-break-after: avoid; }
p,li { orphans: 2; widows: 2; }
a { color: #1565a8; text-decoration: none; }
blockquote { border-left: 4px solid #9bb8c9; background: #f3f7fa;
             margin: 1em 0; padding: 0.4em 1em; color: #3d4d57; font-style: italic; }
code { font-family: "DejaVu Sans Mono",monospace; font-size: 9pt;
       background: #eef1f3; padding: 1px 4px; border-radius: 3px; }
pre { background: #1e2733; color: #e6edf3; padding: 12px 14px; border-radius: 6px;
      font-size: 8.6pt; line-height: 1.4; overflow-x: auto; page-break-inside: avoid; }
pre code { background: transparent; color: inherit; padding: 0; font-size: 8.6pt; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 9.5pt; }
th,td { border: 1px solid #c5d0d8; padding: 6px 9px; text-align: left; vertical-align: top; }
th { background: #0b3d5c; color: #fff; }
tr:nth-child(even) td { background: #f3f7fa; }
hr { border: none; border-top: 1px solid #d3dde3; margin: 1.6em 0; }
img { max-width: 100%; }
"""
MD_EXTS = ["fenced_code", "tables", "codehilite", "sane_lists", "toc", "attr_list"]


def main():
    for name in ("study-guide", "study-guide-solutions"):
        src = ROOT / f"{name}.md"
        dst = ROOT / f"{name}.pdf"
        body = markdown.markdown(
            src.read_text(encoding="utf-8"), extensions=MD_EXTS,
            extension_configs={"codehilite": {"noclasses": True, "pygments_style": "default"}})
        html = (f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
                f"<style>{CSS}</style></head><body>{body}</body></html>")
        HTML(string=html, base_url=str(ROOT)).write_pdf(str(dst))
        print("wrote", dst.name)


if __name__ == "__main__":
    main()
