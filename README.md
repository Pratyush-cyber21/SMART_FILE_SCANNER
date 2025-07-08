# 🔐 Smart File Scanner & Organizer

A desktop tool that scans uploaded folders, detects sensitive information (like passwords, emails, account numbers), and automatically organizes files into folders like `Sensitive`, `Documents`, or `Others`.

### ✅ Features
- Supports `.txt`, `.pdf`, `.docx`, `.png`, `.jpg`
- Detects:
  - Passwords
  - Emails
  - Account numbers
  - API keys
- OCR support for images
- GUI using Tkinter
- Generates a CSV report
- Fully offline – privacy preserved

### 📦 How to Run

```bash
pip install -r requirements.txt
python smart_file_gui.py