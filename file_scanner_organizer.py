import os
import re
import shutil
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
            return None
    except Exception as e:
        print(f"[ERROR] Failed to extract from {file_path}: {e}")
        return None

def find_sensitive_info(text):
    patterns = {
        "Password": r"(?i)password\s*[:=]\s*\S+",
        "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "Account Number": r"\b\d{9,18}\b",
        "API Key / Secret": r"(?i)(api[_-]?key|secret)[\s:=]+[\w-]{8,}"
    }

    found = {}
    for label, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            found[label] = matches
    return found

def move_file(file_path, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    filename = os.path.basename(file_path)
    new_path = os.path.join(destination_folder, filename)
    shutil.move(file_path, new_path)

def main():
    folder_path = input("📁 Enter the path to the folder containing files: ").strip()

    if not os.path.isdir(folder_path):
        print("❌ Invalid folder path.")
        return

    print("\n🔍 Scanning and organizing files...\n")
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Skip already moved files
            if any(skip in file_path for skip in ['Sensitive', 'Documents', 'Others']):
                continue

            print(f"📄 File: {file}")
            content = detect_and_extract(file_path)

            if content:
                found = find_sensitive_info(content)
                if found:
                    print("🚨 Sensitive Info Found. Moving to 'Sensitive/' folder.")
                    move_file(file_path, os.path.join(folder_path, 'Sensitive'))
                else:
                    print("✅ No sensitive data. Moving to 'Documents/' folder.")
                    move_file(file_path, os.path.join(folder_path, 'Documents'))
            else:
                print("⚠️ Unreadable or unsupported. Moving to 'Others/' folder.")
                move_file(file_path, os.path.join(folder_path, 'Others'))

            print("-" * 60)

if __name__ == "__main__":
    main()