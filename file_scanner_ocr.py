import os
import re
import shutil
import pdfplumber
import docx
import pandas as pd
import pytesseract
from PIL import Image
from datetime import datetime

# Optional: Set tesseract path if not auto-detected
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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

def extract_text_from_image(file_path):
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"[OCR ERROR] {file_path}: {e}")
        return None

def detect_and_extract(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.txt':
            return extract_text_from_txt(file_path)
        elif ext == '.pdf':
            return extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return extract_text_from_docx(file_path)
        elif ext in ['.png', '.jpg', '.jpeg']:
            return extract_text_from_image(file_path)
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
    return new_path

def main():
    folder_path = input("📁 Enter the path to the folder containing files: ").strip()

    if not os.path.isdir(folder_path):
        print("❌ Invalid folder path.")
        return

    report = []

    print("\n📸 Scanning all files (including images)...\n")
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if any(skip in file_path for skip in ['Sensitive', 'Documents', 'Others']):
                continue

            ext = os.path.splitext(file)[1].lower()
            print(f"📄 File: {file}")
            content = detect_and_extract(file_path)

            sensitive_found = "No"
            sensitive_types = []
            new_path = ""

            if content:
                found = find_sensitive_info(content)
                if found:
                    sensitive_found = "Yes"
                    sensitive_types = list(found.keys())
                    new_path = move_file(file_path, os.path.join(folder_path, 'Sensitive'))
                    action = "Moved to Sensitive"
                    print("🚨 Sensitive Info Found.")
                else:
                    new_path = move_file(file_path, os.path.join(folder_path, 'Documents'))
                    action = "Moved to Documents"
                    print("✅ No sensitive data found.")
            else:
                new_path = move_file(file_path, os.path.join(folder_path, 'Others'))
                action = "Moved to Others"
                print("⚠️ Unreadable or unsupported file.")

            report.append({
                "File Name": file,
                "Original Path": file_path,
                "New Path": new_path,
                "File Type": ext,
                "Sensitive Found": sensitive_found,
                "Sensitive Types": ', '.join(sensitive_types),
                "Action Taken": action
            })
            print("-" * 60)

    # Save report
    df = pd.DataFrame(report)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(folder_path, f"scan_report_{timestamp}.csv")
    df.to_csv(report_file, index=False)

    print(f"\n📁 Report saved to: {report_file}")
    print("✅ All done including OCR support!")

if __name__ == "__main__":
    main()