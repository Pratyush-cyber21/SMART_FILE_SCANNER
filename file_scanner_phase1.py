import os
import pdfplumber
import docx

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def detect_and_extract(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.txt':
            return extract_text_from_txt(file_path)
        elif ext == '.pdf':
            return extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return extract_text_from_docx(file_path)
        else:
            return None  # Unsupported for now
    except Exception as e:
        print(f"[ERROR] Failed to extract from {file_path}: {e}")
        return None

def main():
    folder_path = input("📁 Enter the path to the folder containing files: ").strip()

    if not os.path.isdir(folder_path):
        print("❌ Invalid folder path.")
        return

    print("\n🔍 Scanning files...\n")
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"📄 File: {file}")
            content = detect_and_extract(file_path)
            if content:
                print("📝 Preview:")
                print(content[:300] + ('...' if len(content) > 300 else ''))
            else:
                print("⚠️ Unsupported or unreadable file type.\n")
            print("-" * 50)

if __name__ == "__main__":
    main()