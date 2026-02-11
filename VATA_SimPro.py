import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random

def generate_combinations():
    try:
        output_text.delete("1.0", "end")
        n_total = int(nums_var.get())
        k_draw = int(draws_var.get())
        count = int(count_var.get())
        
        if k_draw > n_total:
            messagebox.showerror("Error", "Draw size cannot be larger than total numbers!")
            return
        
        results = []
        for _ in range(count):
            # Realistic random draw order
            combo = random.sample(range(1, n_total + 1), k_draw)
            line = ", ".join(f"{x:02d}" for x in combo)
            results.append(line)
        
        output_text.insert("end", "\n".join(results))
        status_lbl.config(text=f"Generated: {len(results)}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers!")

def save_to_file():
    content = output_text.get("1.0", "end").strip()
    if not content:
        messagebox.showwarning("Warning", "Nothing to save!")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")])
    if file_path:
        try:
            with open(file_path, "w") as f:
                f.write(content)
            messagebox.showinfo("Success", "File saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

def sort_results():
    content = output_text.get("1.0", "end").strip()
    if not content: return
    sorted_lines = []
    for line in content.split('\n'):
        try:
            nums = sorted([int(x.strip()) for x in line.replace(',', ' ').split() if x.strip()])
            sorted_lines.append(", ".join(f"{x:02d}" for x in nums))
        except: continue
    output_text.delete("1.0", "end")
    output_text.insert("end", "\n".join(sorted_lines))

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(output_text.get("1.0", "end").strip())

def clear_all():
    output_text.delete("1.0", "end")
    status_lbl.config(text="Generated: 0")

# UI Setup
root = tk.Tk()
root.title("VATA_SimPro")
root.geometry("340x550")
root.resizable(False, False)

input_frame = ttk.Frame(root, padding=10)
input_frame.pack(fill="x")

ttk.Label(input_frame, text="Nums:").grid(row=0, column=0)
nums_var = tk.StringVar(value="39")
ttk.Entry(input_frame, textvariable=nums_var, width=5).grid(row=0, column=1, padx=5)

ttk.Label(input_frame, text="Draws:").grid(row=0, column=2)
draws_var = tk.StringVar(value="6")
ttk.Entry(input_frame, textvariable=draws_var, width=5).grid(row=0, column=3, padx=5)

ttk.Label(input_frame, text="Qty:").grid(row=1, column=0, pady=10)
count_var = tk.StringVar(value="50")
ttk.Entry(input_frame, textvariable=count_var, width=10).grid(row=1, column=1, pady=10)
ttk.Button(input_frame, text="GO!", command=generate_combinations, width=10).grid(row=1, column=2, columnspan=2, padx=5)

output_text = tk.Text(root, width=35, height=18, font=("Courier New", 10))
output_text.pack(padx=10, pady=5, fill="both", expand=True)

status_lbl = ttk.Label(root, text="Generated: 0", font=("Arial", 9, "italic"))
status_lbl.pack()

btn_frame = ttk.Frame(root, padding=10)
btn_frame.pack(fill="x")

# Row 1 of buttons
ttk.Button(btn_frame, text="Sort", command=sort_results).pack(side="left", expand=True, padx=2)
ttk.Button(btn_frame, text="Copy", command=copy_to_clipboard).pack(side="left", expand=True, padx=2)

# Row 2 of buttons
btn_frame2 = ttk.Frame(root, padding=10)
btn_frame2.pack(fill="x")
ttk.Button(btn_frame2, text="Save to File", command=save_to_file).pack(side="left", expand=True, padx=2)
ttk.Button(btn_frame2, text="Clear All", command=clear_all).pack(side="right", expand=True, padx=2)

root.mainloop()
