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
def create_custom_css():
    """Create enhanced CSS for beautiful PDFs"""
    return """
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.7;
        color: #2c3e50;
        margin: 2cm;
    }
    
    /* Headers */
    h1 {
        color: #2980b9;
        font-size: 26pt;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 20pt;
        padding-bottom: 12pt;
        border-bottom: 4px solid #3498db;
        page-break-after: avoid;
    }
    
    h2 {
        color: #16a085;
        font-size: 16pt;
        font-weight: 600;
        margin-top: 28pt;
        margin-bottom: 14pt;
        padding-left: 8pt;
        border-left: 4px solid #16a085;
        page-break-after: avoid;
    }
    
    h3 {
        color: #27ae60;
        font-size: 13pt;
        font-weight: 600;
        margin-top: 18pt;
        margin-bottom: 10pt;
        page-break-after: avoid;
    }
    
    /* Code styling */
    code {
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Liberation Mono', monospace;
        font-size: 9.5pt;
        background-color: #f7f7f7;
        padding: 3pt 5pt;
        border-radius: 3pt;
        color: #c7254e;
        border: 1px solid #e1e1e8;
    }
    
    pre {
        background-color: #f8f9fa;
        border-left: 5px solid #3498db;
        border-radius: 4pt;
        padding: 14pt 16pt;
        margin: 14pt 0;
        overflow-x: auto;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
        color: #2c3e50;
        font-size: 9pt;
        line-height: 1.5;
        border: none;
    }
    
    /* Lists */
    ul, ol {
        margin: 12pt 0;
        padding-left: 24pt;
        line-height: 1.8;
    }
    
    li {
        margin: 8pt 0;
    }
    
    ul li::marker {
        color: #3498db;
    }
    
    /* Paragraphs */
    p {
        margin: 10pt 0;
        text-align: justify;
    }
    
    /* Text formatting */
    strong {
        color: #e74c3c;
        font-weight: 600;
    }
    
    em {
        color: #8e44ad;
        font-style: italic;
    }
    
    /* Blockquotes */
    blockquote {
        border-left: 5px solid #95a5a6;
        padding: 12pt 16pt;
        margin: 14pt 0;
        background-color: #f8f9fa;
        color: #555;
        font-style: italic;
        border-radius: 0 4pt 4pt 0;
    }
    
    /* Tables */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 16pt 0;
    }
    
    th, td {
        border: 1px solid #dfe2e5;
        padding: 10pt 12pt;
        text-align: left;
    }
    
    th {
        background-color: #3498db;
        color: white;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 9pt;
        letter-spacing: 0.5pt;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    /* Links */
    a {
        color: #3498db;
        text-decoration: underline;
    }
    
    /* Horizontal rules */
    hr {
        border: none;
        border-top: 2px solid #ecf0f1;
        margin: 24pt 0;
    }
    """

def export_to_pdf(file_path):
    file_content = load_file_content(file_path)
    pdf_path = file_path.with_suffix(".pdf")
    
    pdf = MarkdownPdf(toc_level=2)
    pdf.meta["title"] = file_path.stem.replace('_', ' ').title()
    pdf.meta["author"] = "Personal Reference Library"
    
    # Add custom CSS styling
    section = Section(file_content, toc=True)
    pdf.add_section(section, user_css=create_custom_css())
    
    pdf.save(pdf_path)
    print(f"✅ Created: {pdf_path.name}")
    print(f"📂 Location: {pdf_path.parent}")

def handle():
    if len(sys.argv) < 2 :
        sys.exit(1)
    else:
        file_path = look_for_file(sys.argv[1] + ".md")
        export_to_pdf(file_path)

handle()
