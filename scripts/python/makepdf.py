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
    pdf = MarkdownPdf()
    pdf.add_section(Section(file_content))
    pdf.save(pdf_path)

def handle():
    if len(sys.argv) < 2 :
        sys.exit(1)
    else:
        file_path = look_for_file(sys.argv[1] + ".md")
        export_to_pdf(file_path)

handle()
