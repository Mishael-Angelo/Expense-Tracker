# Expense-Tracker
This is a simple Expense Tracker built with Python, EastOCR + TogetherAI for categorization
# 🧾 Expense Tracker with EasyOCR + Together AI

This is a Python desktop application that allows users to:
- Upload receipts (PDF or image),
- Automatically extract key expense data using OCR (EasyOCR),
- Categorize expenses using AI (Together AI),
- Save and manage expenses locally,
- Export a categorized summary report as a PDF.

Built with **Tkinter**, **EasyOCR**, **Together AI**, and **FPDF**.

---

## 🔧 Features

- 🧠 **AI Categorization** of receipts (Food, Bills, Transport, etc.)
- 🖼️ **OCR Support** for both image and PDF receipts
- 🗂️ **Editable Preview** before saving an expense
- 📊 **Dashboard Summary** with per-category totals
- 📄 **PDF Export** with detailed and summarized views

---

## 🛠️ Technologies Used

- `Tkinter` — GUI Framework
- `EasyOCR` — OCR engine to read receipt content
- `Together AI` — Natural language model for expense categorization
- `FPDF` — Generate PDF reports
- `pdf2image`, `PIL` — Convert PDFs to images for OCR

---

## 📦 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/expense-tracker-ocr-ai.git
cd expense-tracker-ocr-ai
```

2. **Install the dependencies:**

```bash
pip install -r requirements.txt
```

> ⚠️ Note: You also need **Poppler** installed on your system for `pdf2image` to work.
- Windows: https://github.com/Belval/pdf2image#windows
- macOS: `brew install poppler`
- Ubuntu: `sudo apt install poppler-utils`

3. **Add your Together AI API key:**

In the code, replace:
```python
TOGETHER_API_KEY = "6d465442f538fa048b243353e5267782e4b8bf647f28b2eecdd77cb18972c4d2"
```
with your actual key from [Together AI](https://www.together.ai/).

---

## 🚀 Usage

```bash
run the main.py
```

- Click **"Select Receipt"** and choose a PDF or image file.
- Review and edit the auto-extracted values (vendor, date, total, category).
- Click **"Save"** to add it to the dashboard.
- Click **"Export PDF Report"** to save the results as a PDF.

---

## 📌 Future Enhancements

- Save/load expense data to/from local file (CSV/JSON)
- Monthly/yearly filters and graphs (via Matplotlib)
- Email report feature
- Multi-receipt batch processing


---

## 🧑‍💻 Author

Made by [
Usman-wamba Mishael
NDIBE MICHAEL CHUKWUNONSO
Adeiyi Abdulsamad
Ayantunde Joshua Opeyemi]

---
