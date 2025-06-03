import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pdf2image import convert_from_path
from PIL import Image
import easyocr
import re
from collections import defaultdict
from fpdf import FPDF
import requests  # for Together AI API

class ExpenseTracker:
    # === Together AI Config ===
    TOGETHER_API_KEY = "6d465442f538fa048b243353e5267782e4b8bf647f28b2eecdd77cb18972c4d2"
    TOGETHER_API_URL = "https://api.together.ai/api/v1/generate"  # Hypothetical endpoint

    # Initialize EasyOCR reader once
    reader = easyocr.Reader(['en'])
    CATEGORIES = ['Food & Beverage', 'Transport', 'Groceries', 'Bills', 'Entertainment', 'Other']

    def __init__(self):
        # In-memory storage of expenses (list of dicts)
        self.expenses = []
        # Main GUI Setup
        self.root = tk.Tk()
        self.root.title("Expense Tracker with EasyOCR + Together AI")
        self.root.geometry("700x550")
        # File label
        self.file_label = tk.Label(self.root, text="No file selected.")
        # Treeview for dashboard
        self.cols = ('Vendor', 'Date', 'Total', 'Category')
        self.tree = ttk.Treeview(self.root, columns=self.cols, show='headings')
        # Totals label
        self.totals_label = tk.Label(self.root, text="Totals will be shown here.")
        self.setup_gui()

    def setup_gui(self):
        tk.Label(self.root, text="Upload a Receipt").pack(pady=10)
        tk.Button(self.root, text="Select Receipt", command=self.process_receipt).pack()
        self.file_label.pack(pady=5)
        for col in self.cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(expand=True, fill='both', pady=10)
        self.totals_label.pack(pady=5)
        tk.Button(self.root, text="Export PDF Report", command=self.export_pdf).pack(pady=10)
        self.refresh_dashboard()

    # --- OCR & Data Extraction ---
    def extract_text_from_file(self, file_path):
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path)
            image = images[0]
            image_path = "temp_image.png"
            image.save(image_path)
        else:
            image_path = file_path

        results = self.reader.readtext(image_path)
        text = "\n".join([text for (_, text, _) in results])
        return text

    # --- Together AI categorization ---
    def categorize_with_together_ai(self, text):
        prompt = f"""
You are an assistant that categorizes expense receipts into one of these categories:
Food & Beverage, Transport, Groceries, Bills, Entertainment, Other.

Categorize this text:
\"\"\"{text}\"\"\"
Just return the category name only.
"""
        headers = {
            "Authorization": f"Bearer {self.TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        json_data = {
            "model": "together/open-chat-7b",
            "prompt": prompt,
            "max_tokens": 10,
            "temperature": 0.0,
            "stop": ["\n"]
        }

        try:
            response = requests.post(self.TOGETHER_API_URL, headers=headers, json=json_data)
            response.raise_for_status()
            result = response.json()
            category = result.get("choices", [{}])[0].get("text", "").strip()

            if category not in self.CATEGORIES:
                category = 'Other'
            return category
        except Exception as e:
            print(f"Together AI API error: {e}")
            return 'Other'

    def extract_fields(self, text):
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        total_match = re.search(r'(Total|Amount Due|Grand Total|Balance)[^\d]*(\d+\.\d{2})', text, re.IGNORECASE)

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        vendor = lines[0] if lines else 'Unknown'

        category = self.categorize_with_together_ai(text)

        return {
            'vendor': vendor,
            'date': date_match.group(1) if date_match else '',
            'total': total_match.group(2) if total_match else '',
            'category': category
        }

    # --- PDF report generation ---
    def generate_pdf_report(self, expenses_list):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Expense Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Vendor", 1)
        pdf.cell(30, 10, "Date", 1)
        pdf.cell(30, 10, "Total", 1)
        pdf.cell(50, 10, "Category", 1)
        pdf.ln()

        pdf.set_font("Arial", "", 12)
        for exp in expenses_list:
            pdf.cell(50, 10, exp['vendor'][:20], 1)
            pdf.cell(30, 10, exp['date'], 1)
            pdf.cell(30, 10, exp['total'], 1)
            pdf.cell(50, 10, exp['category'], 1)
            pdf.ln()

        totals = defaultdict(float)
        for exp in expenses_list:
            try:
                totals[exp['category']] += float(exp['total'])
            except:
                pass

        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Summary Totals:", ln=True)

        pdf.set_font("Arial", "", 12)
        for cat in self.CATEGORIES:
            pdf.cell(0, 10, f"{cat}: ${totals[cat]:.2f}", ln=True)

        file_path = "expense_report.pdf"
        pdf.output(file_path)
        return file_path

    # --- GUI Functions ---
    def show_preview(self, data):
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Review and Save")
        preview_win.geometry("350x350")

        entries = {}
        for field in ['vendor', 'date', 'total', 'category']:
            tk.Label(preview_win, text=field.capitalize()).pack()
            if field == 'category':
                category_var = tk.StringVar(value=data['category'])
                option_menu = tk.OptionMenu(preview_win, category_var, *self.CATEGORIES)
                option_menu.pack()
                entries[field] = category_var
            else:
                entry = tk.Entry(preview_win)
                entry.insert(0, data[field])
                entry.pack()
                entries[field] = entry

        def confirm_save():
            saved_data = {
                'vendor': entries['vendor'].get(),
                'date': entries['date'].get(),
                'total': entries['total'].get(),
                'category': entries['category'].get()
            }
            if not saved_data['total']:
                messagebox.showwarning("Warning", "Total amount is empty. Please fill it in.")
                return
            self.expenses.append(saved_data)
            messagebox.showinfo("Saved", "Expense saved successfully!")
            preview_win.destroy()
            self.refresh_dashboard()

        tk.Button(preview_win, text="Save", command=confirm_save).pack(pady=10)

    def process_receipt(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF or Image files", "*.pdf *.png *.jpg *.jpeg")]
        )
        if not file_path:
            return

        self.file_label.config(text=f"File: {file_path}")
        try:
            text = self.extract_text_from_file(file_path)
            data = self.extract_fields(text)
            self.show_preview(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process receipt:\n{str(e)}")

    def refresh_dashboard(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        category_totals = defaultdict(float)
        overall_total = 0.0

        for expense in self.expenses:
            self.tree.insert('', 'end', values=(expense['vendor'], expense['date'], expense['total'], expense['category']))
            try:
                amount = float(expense['total'])
                category_totals[expense['category']] += amount
                overall_total += amount
            except:
                pass

        totals_text = " | ".join([f"{cat}: ${category_totals[cat]:.2f}" for cat in self.CATEGORIES])
        self.totals_label.config(text=f"Totals - {totals_text} | Overall: ${overall_total:.2f}")

    def export_pdf(self):
        if not self.expenses:
            messagebox.showinfo("No Data", "No expenses to export.")
            return
        pdf_file = self.generate_pdf_report(self.expenses)
        messagebox.showinfo("PDF Created", f"PDF report saved to {pdf_file}")

    def run(self):
        self.root.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = ExpenseTracker()
    app.run()
