# 🔐 SMART FILE SCANNER

A Python GUI-based tool that scans folders, detects **sensitive content** like passwords, emails, and account numbers, and **auto-sorts files** into folders like `Sensitive/`, `Documents/`, and `Others/`.

---

## 🚀 Features

- ✅ Supports `.txt`, `.pdf`, `.docx`, `.png`, `.jpg`
- 🧠 Detects:  
  - Passwords, API keys, emails, account numbers, and more
- 🗃️ Automatically moves files into:
  - `Sensitive/`, `Documents/`, or `Others/`
- 📋 Generates a CSV scan report
- 🖼 OCR support for image-based text (using Tesseract)
- 🪟 User-friendly GUI with file logs

---

## 🛠 Requirements

- Python 3.9+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and added to PATH
- Tkinter GUI support (macOS has it by default)

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python3 smart_file_gui.py