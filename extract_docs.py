import zipfile
import xml.etree.ElementTree as ET
import os

def extract_text_from_docx(docx_path):
    text = ""
    try:
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = tree.findall('.//w:p', namespace)
            for paragraph in paragraphs:
                texts = paragraph.findall('.//w:t', namespace)
                text += ''.join([node.text for node in texts if node.text]) + '\n'
    except Exception as e:
        text = f"Error reading {docx_path}: {e}"
    return text

docs_dir = r"e:\New folder\prac\docs"
for filename in os.listdir(docs_dir):
    if filename.endswith(".docx"):
        print(f"--- {filename} ---")
        path = os.path.join(docs_dir, filename)
        content = extract_text_from_docx(path)
        with open(os.path.join(docs_dir, filename.replace('.docx', '.txt')), 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Extracted to {filename.replace('.docx', '.txt')}")
