from markdown_pdf import MarkdownPdf, Section
import sys
from pathlib import Path

## take .md file , load and convert it to pdf

def load_file_content(path_to_file):
    with open(path_to_file, "r", encoding="utf-8") as f:
        file_content = f.read()
    return (file_content)

def look_for_file(file_name):
    base_dir = (Path(__file__).resolve().parent / "../../references").resolve()
    match = list(base_dir.rglob(file_name))
    if not match:
        print(f"❌ File '{file_name}' not found under {base_dir}")
        sys.exit(1)

    else:
        md_path = match[0]
        print(f"md Path {md_path}")
        print(f"📄 Found: {md_path.relative_to(base_dir)}")
        return (md_path)

def export_to_pdf(file_path):
    file_content = load_file_content(file_path)
    pdf_path = file_path.with_suffix(".pdf")
    
    # Create custom CSS file
    css_path = Path(__file__).parent / "pdf_style.css"
    if not css_path.exists():
        css_content = """
body { font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #2c3e50; }
h1 { color: #2980b9; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
h2 { color: #16a085; margin-top: 24px; }
h3 { color: #27ae60; }
code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; color: #c7254e; }
pre { background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 12px; }
pre code { background-color: transparent; color: #2c3e50; }
strong { color: #e74c3c; }
"""
        css_path.write_text(css_content)
    
    pdf = MarkdownPdf(toc_level=2)
    pdf.meta["title"] = file_path.stem
    pdf.meta["author"] = "Personal Reference"
    
    pdf.add_section(Section(file_content, toc=True))
    pdf.save(pdf_path)
    print(f"✅ Created: {pdf_path}")

def handle():
    if len(sys.argv) < 2 :
        sys.exit(1)
    else:
        file_path = look_for_file(sys.argv[1] + ".md")
        export_to_pdf(file_path)

handle()
