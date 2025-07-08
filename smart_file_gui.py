import os
import re
import shutil
import pdfplumber
import docx
import pytesseract
import pandas as pd
from PIL import Image
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Optional: set Tesseract path if needed
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
        return ""

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
    except:
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

def run_scan(folder_path, log_box):
    report = []
    scanned_count = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Skip previously sorted folders
            if any(skip in file_path for skip in ['Sensitive', 'Documents', 'Others']):
                continue

            ext = os.path.splitext(file)[1].lower()
            log_box.insert(tk.END, f"📄 Scanning: {file_path}\n")
            log_box.update()

            content = detect_and_extract(file_path)
            sensitive_found = "No"
            sensitive_types = []
            new_path = ""
            action = ""

            if content and len(content.strip()) > 10:  # avoid empty files
                found = find_sensitive_info(content)
                if found:
                    sensitive_found = "Yes"
                    sensitive_types = list(found.keys())
                    new_path = move_file(file_path, os.path.join(folder_path, 'Sensitive'))
                    action = "Moved to Sensitive"
                    log_box.insert(tk.END, "🚨 Sensitive Info Found!\n")
                else:
                    new_path = move_file(file_path, os.path.join(folder_path, 'Documents'))
                    action = "Moved to Documents"
                    log_box.insert(tk.END, "✅ Clean file.\n")
            else:
                new_path = move_file(file_path, os.path.join(folder_path, 'Others'))
                action = "Unsupported/Unreadable"
                log_box.insert(tk.END, "⚠️ File skipped (empty or unsupported).\n")

            log_box.insert(tk.END, "-" * 50 + "\n")

            report.append({
                "File Name": file,
                "Original Path": file_path,
                "New Path": new_path,
                "File Type": ext,
                "Sensitive Found": sensitive_found,
                "Sensitive Types": ', '.join(sensitive_types),
                "Action Taken": action
            })

            scanned_count += 1

    if scanned_count == 0:
        messagebox.showwarning("Nothing Scanned", "No valid files found in this folder.")
        return

    df = pd.DataFrame(report)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(folder_path, f"scan_report_{timestamp}.csv")
    df.to_csv(report_path, index=False)
    log_box.insert(tk.END, f"\n📁 Report saved: {report_path}\n")
    messagebox.showinfo("Scan Complete", f"Report saved:\n{report_path}")

def browse_folder(entry, log_box):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry.delete(0, tk.END)
        entry.insert(0, folder_path)
        log_box.delete('1.0', tk.END)

def start_scan(entry, log_box):
    folder = entry.get().strip()
    if not os.path.isdir(folder):
        messagebox.showerror("Error", "Invalid folder path.")
        return
    run_scan(folder, log_box)

# GUI Layout
def main():
    window = tk.Tk()
    window.title("Smart File Scanner")
    window.geometry("700x500")
    window.resizable(False, False)

    tk.Label(window, text="Select Folder to Scan:", font=('Arial', 12)).pack(pady=5)

    frame = tk.Frame(window)
    frame.pack()

    entry = tk.Entry(frame, width=60)
    entry.pack(side=tk.LEFT, padx=10)

    browse_btn = tk.Button(frame, text="Browse", command=lambda: browse_folder(entry, log_box))
    browse_btn.pack(side=tk.LEFT)

    scan_btn = tk.Button(window, text="Start Scan", font=('Arial', 11), bg='green', fg='white',
                         command=lambda: start_scan(entry, log_box))
    scan_btn.pack(pady=10)

    log_box = scrolledtext.ScrolledText(window, width=80, height=20)
    log_box.pack(padx=10, pady=10)

    window.mainloop()

if __name__ == "__main__":
    main()