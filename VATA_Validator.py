import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import random

class VATA_ValidatorUltimateV3:
    def __init__(self, root):
        self.root = root
        self.root.title("VATA_Validator")
        self.root.geometry("1000x750")
        
        # Parametri težina
        self.w_ra = tk.DoubleVar(value=0.09)
        self.w_vol = tk.DoubleVar(value=0.55)
        self.w_trend = tk.DoubleVar(value=0.35)
        
        # Parametri analize
        self.depth = tk.IntVar(value=41)
        self.test_count = tk.IntVar(value=30)
        
        # Pravila igre
        self.draw_size = tk.IntVar(value=6)
        self.max_num = tk.IntVar(value=39)
        self.predict_n = tk.IntVar(value=18)
        
        self.setup_ui()

    def setup_ui(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=15, pady=10)
        
        config = ttk.LabelFrame(top_frame, text="Lottery Setup")
        config.pack(side="left", padx=5)
        ttk.Label(config, text="Draw:").grid(row=0, column=0, padx=2)
        ttk.Combobox(config, textvariable=self.draw_size, values=[5, 6, 7], width=3).grid(row=0, column=1, padx=2)
        ttk.Label(config, text="From:").grid(row=0, column=2, padx=2)
        ttk.Spinbox(config, from_=12, to=54, textvariable=self.max_num, width=4).grid(row=0, column=3, padx=2)

        params = ttk.LabelFrame(top_frame, text="Weighting Factors")
        params.pack(side="left", fill="x", expand=True, padx=5)
        for i, (l, v) in enumerate([("R/A", self.w_ra), ("Volatility", self.w_vol), ("Trend", self.w_trend)]):
            tk.Scale(params, from_=0, to=1, resolution=0.01, label=l, orient="horizontal", variable=v, length=100).grid(row=0, column=i, padx=5)

        cmd_frame = ttk.Frame(self.root)
        cmd_frame.pack(fill="x", padx=15, pady=5)
        
        ttk.Button(cmd_frame, text="START TEST", command=self.run_backtest).pack(side="left", padx=2)
        
        ttk.Label(cmd_frame, text="Depth:").pack(side="left", padx=(5,0))
        ttk.Entry(cmd_frame, textvariable=self.depth, width=4).pack(side="left", padx=2)
        
        ttk.Label(cmd_frame, text="Test Count:").pack(side="left", padx=(5,0))
        ttk.Entry(cmd_frame, textvariable=self.test_count, width=4).pack(side="left", padx=2)
        
        ttk.Button(cmd_frame, text="DEEP OPTIMIZE", command=self.optimize_all).pack(side="left", padx=10)
        ttk.Button(cmd_frame, text="VALIDATE", command=self.validate_history).pack(side="left", padx=2)
        
        ttk.Separator(cmd_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        
        ttk.Entry(cmd_frame, textvariable=self.predict_n, width=4).pack(side="left", padx=2)
        ttk.Button(cmd_frame, text="Predict_Numbers", command=self.predict_next).pack(side="left", padx=2)

        data_ctrl = ttk.Frame(self.root)
        data_ctrl.pack(fill="x", padx=15, pady=5)
        
        ttk.Button(data_ctrl, text="Import Hist.", command=self.import_file).pack(side="left", padx=2)
        ttk.Button(data_ctrl, text="Paste Hist.", command=self.paste_history).pack(side="left", padx=2)
        ttk.Button(data_ctrl, text="Clear Hist.", command=lambda: self.hist_text.delete("1.0", "end")).pack(side="left", padx=2)
        
        ttk.Button(data_ctrl, text="Copy Table", command=self.copy_to_clip).pack(side="left", padx=(150, 2))
        ttk.Button(data_ctrl, text="Clear Table", command=lambda: self.log.delete("1.0", "end")).pack(side="left", padx=2)

        ttk.Label(self.root, text="Draw history").pack(anchor="w", padx=15)
        self.hist_text = scrolledtext.ScrolledText(self.root, height=8, font=("Courier New", 10))
        self.hist_text.pack(fill="x", padx=15, pady=5)
        
        self.hist_menu = tk.Menu(self.root, tearoff=0)
        self.hist_menu.add_command(label="Import", command=self.import_file)
        self.hist_menu.add_command(label="Paste", command=self.paste_history)
        self.hist_menu.add_command(label="Clear History", command=lambda: self.hist_text.delete("1.0", "end"))
        self.hist_text.bind("<Button-3>", lambda e: self.hist_menu.tk_popup(e.x_root, e.y_root))

        self.prog = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.prog.pack(fill="x", padx=15, pady=5)

        self.log = scrolledtext.ScrolledText(self.root, height=15, bg="#1a1a1a", fg="#00ff00", font=("Courier New", 10))
        self.log.pack(fill="both", expand=True, padx=15, pady=5)

    def validate_history(self):
        self.log.delete("1.0", "end")
        raw = self.hist_text.get("1.0", "end").strip().split('\n')
        if not raw or raw == ['']: return
        max_n, draw_s = self.max_num.get(), self.draw_size.get()
        errors = []
        for i, line in enumerate(raw):
            if not line.strip(): continue
            try:
                nums = [int(x) for x in line.replace(',', ' ').split() if x.isdigit()]
                if len(nums) != draw_s: errors.append(f"Kolo {i+1}: Ima {len(nums)} br, traži se {draw_s}")
                if any(n > max_n or n < 1 for n in nums): errors.append(f"Kolo {i+1}: Broj van ranga (1-{max_n})")
                if len(set(nums)) != len(nums): errors.append(f"Kolo {i+1}: Duplikat u redu")
            except: errors.append(f"Kolo {i+1}: Nevalidan format")
        
        if errors: self.log.insert("end", "ERRORS DETECTED:\n" + "\n".join(errors))
        else: self.log.insert("end", f"VALIDATION OK: {len(raw)} correct {draw_s}/{max_n}")

    def get_stats(self, seq, window):
        if not seq: return 1.0, 0, 0
        emp = sum(seq)
        vol = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i-1]) / len(seq)
        avg_dist = len(seq) / emp if emp > 0 else len(seq)
        last_h = -1
        for i in range(len(seq)-1, -1, -1):
            if seq[i] == 1: last_h = i; break
        ra = (len(seq) - 1 - last_h) / avg_dist if avg_dist > 0 else 1.0
        tr = (sum(seq[-window:])/len(seq[-window:])) - (emp/len(seq)) if len(seq) >= window else 0
        return ra, vol, tr

    def run_backtest(self, silent=False):
        if not silent: self.log.delete("1.0", "end")
        raw = self.hist_text.get("1.0", "end").strip().split('\n')
        try:
            data = [[int(x) for x in l.replace(',', ' ').split() if x.isdigit()] for l in raw if l]
        except: return 0
        
        n, d = int(self.test_count.get()), int(self.depth.get())
        pred_count = int(self.predict_n.get()) # Eksplicitno uzimamo broj brojeva za predikciju
        
        if len(data) < (n + d): 
            if not silent: messagebox.showwarning("!", f"Not enough data. Needed at least {n+d} draws.")
            return 0

        if not silent:
            self.log.insert("end", f"{'DRAW':<10} | {'PLAY':<8} | {'AVOID':<8} | STATUS\n" + "-"*45 + "\n")

        res_p, res_a, res_r = [], [], []
        for i in range(len(data)-n, len(data)):
            target, train = set(data[i]), data[i-d:i]
            scores = []
            for num in range(1, self.max_num.get() + 1):
                seq = [1 if num in draw else 0 for draw in train]
                ra, vol, tr = self.get_stats(seq, 10)
                # Formula
                s = ((1-ra)*self.w_ra.get()) - (vol*self.w_vol.get()) + (tr*self.w_trend.get())
                scores.append((num, s))
            
            sn = [x[0] for x in sorted(scores, key=lambda x: x[1], reverse=True)]
            h_p = len(set(sn[:pred_count]) & target)
            h_a = len(set(sn[-pred_count:]) & target)
            h_r = len(set(random.sample(range(1, self.max_num.get() + 1), pred_count)) & target)
            
            res_p.append(h_p); res_a.append(h_a); res_r.append(h_r)
            if not silent: self.log.insert("end", f"Kolo #{i+1:<4}  | {h_p:<8} | {h_a:<8} | {'!!!' if h_p>=4 else ''}\n")
        
        avg_p, avg_a, avg_r = sum(res_p)/n, sum(res_a)/n, sum(res_r)/n
        if not silent:
            self.log.insert("end", "="*45 + "\n")
            self.log.insert("end", f"HITS AVERAGE(for {pred_count} numbers): PLAY: {avg_p:.2f} | AVOID: {avg_a:.2f} | RANDOM: {avg_r:.2f}\n")
            self.log.insert("end", f"SETUP: R/A={self.w_ra.get():.2f}, V={self.w_vol.get():.2f}, T={self.w_trend.get():.2f}, D={d}\n")
        return avg_p

    def predict_next(self):
        self.log.delete("1.0", "end")
        raw = self.hist_text.get("1.0", "end").strip().split('\n')
        data = [[int(x) for x in l.replace(',', ' ').split() if x.isdigit()] for l in raw if l]
        d = int(self.depth.get())
        pred_count = int(self.predict_n.get())
        if len(data) < d: return
        
        train = data[-d:]
        scores = []
        for num in range(1, self.max_num.get() + 1):
            seq = [1 if num in draw else 0 for draw in train]
            ra, vol, tr = self.get_stats(seq, 10)
            s = ((1-ra)*self.w_ra.get()) - (vol*self.w_vol.get()) + (tr*self.w_trend.get())
            scores.append((num, s))
            
        sn = sorted(scores, key=lambda x: x[1], reverse=True)
        top_n = sorted([x[0] for x in sn[:pred_count]])
        
        self.log.insert("end", f"PREDICTION FOR DRAW #{len(data)+1}\n" + "="*45 + "\n")
        self.log.insert("end", f"TOP {pred_count} NUMBERS:\n\n" + " ".join(f"[{n:02d}]" for n in top_n) + "\n\n")

    def optimize_all(self):
        self.log.delete("1.0", "end")
        self.log.insert("end", "DEEP OPTIMIZATION IN PROGRESS (500 iterations)...\n")
        best_avg, best_cfg = -1, (0.09, 0.55, 0.35, 41)
        
        for i in range(500):
            w = [random.random() for _ in range(3)]; s = sum(w); w = [x/s for x in w]
            dt = random.randint(30, 60)
            self.w_ra.set(round(w[0], 2)); self.w_vol.set(round(w[1], 2)); self.w_trend.set(round(w[2], 2)); self.depth.set(dt)
            curr = self.run_backtest(silent=True)
            if curr > best_avg:
                best_avg = curr; best_cfg = (w[0], w[1], w[2], dt)
                self.log.insert("end", f"New record: {best_avg:.2f} (D:{dt}, R/A:{w[0]:.2f})\n")
            self.prog['value'] = (i/500)*100
            if i % 10 == 0: self.root.update()
            
        self.w_ra.set(best_cfg[0]); self.w_vol.set(best_cfg[1]); self.w_trend.set(best_cfg[2]); self.depth.set(best_cfg[3])
        self.run_backtest()

    def paste_history(self):
        try: 
            self.hist_text.insert(tk.INSERT, self.root.clipboard_get())
            self.validate_history()
        except: pass

    def import_file(self):
        f = filedialog.askopenfilename()
        if f:
            with open(f, 'r') as file:
                self.hist_text.delete("1.0", "end")
                self.hist_text.insert("1.0", file.read())
            self.validate_history()

    def copy_to_clip(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log.get("1.0", "end"))

if __name__ == "__main__":
    root = tk.Tk()
    app = VATA_ValidatorUltimateV3(root)
    root.mainloop()
