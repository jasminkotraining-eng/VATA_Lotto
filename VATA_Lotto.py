import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import random
from itertools import combinations
from collections import Counter

class VATA_LottoEnhanced:
    def __init__(self, root):
        self.root = root
        self.root.title("VATA_Lotto  - LOTTERY OF THE LAST RUN")
        
        self.root.geometry("660x580") 
        self.root.resizable(False, False)
        
        self.selected_numbers = set()
        self.selected_sum_oe = set()
        self.selected_consec = set()
        self.selected_repeats = set()
        
        self.committed_numbers = set()
        self.committed_sum_oe = set()
        self.committed_consec = set()
        self.committed_repeats = set()
        
        self.history = []
        self.candidate_pool = [] 
        self.stop_requested = False 
        
        self.total_nums_var = tk.IntVar(value=39)
        self.draws_var = tk.IntVar(value=6)
        self.use_history_var = tk.BooleanVar(value=False)
        self.trend_window_var = tk.StringVar(value="20")
        self.trend_weight_var = tk.DoubleVar(value=0.3)
        self.vol_penalty_var = tk.DoubleVar(value=0.2)
        self.sensitivity_var = tk.DoubleVar(value=0.5)
        
        self.sort_states = {}
        self.setup_ui()
        self.update_ui_state()

    def setup_ui(self):
        # Top Config
        config_frame = ttk.LabelFrame(self.root, text="System Configuration")
        config_frame.pack(pady=5, padx=10, fill="x")
        ttk.Label(config_frame, text="Total Nums:").grid(row=0, column=0, padx=5)
        ttk.Entry(config_frame, textvariable=self.total_nums_var, width=5).grid(row=0, column=1)
        ttk.Label(config_frame, text="Draw Size:").grid(row=0, column=2, padx=10)
        ttk.Entry(config_frame, textvariable=self.draws_var, width=5).grid(row=0, column=3)
        ttk.Checkbutton(config_frame, text="Use History", variable=self.use_history_var, command=self.update_ui_state).grid(row=0, column=4, padx=10)

        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10)

        # Left side: History
        left_col = ttk.Frame(main_container)
        left_col.pack(side="left", fill="both", expand=True)

        hist_label_frame = ttk.LabelFrame(left_col, text="Draw History")
        hist_label_frame.pack(pady=5, fill="both", expand=True)
        
        self.history_text = tk.Text(hist_label_frame, width=40, height=12, wrap="none")
        self.history_text.pack(padx=5, pady=5, fill="both", expand=True)
        self.create_history_context_menu(self.history_text)

        hist_ctrls = ttk.Frame(hist_label_frame)
        hist_ctrls.pack(fill="x", pady=2)
        ttk.Button(hist_ctrls, text="Import", command=self.import_csv, width=8).pack(side="left", padx=2)
        ttk.Button(hist_ctrls, text="Paste", command=lambda: self.history_text.event_generate("<<Paste>>"), width=8).pack(side="left", padx=2)
        ttk.Button(hist_ctrls, text="Clear", command=self.clear_history_action, width=8).pack(side="left", padx=2)
        ttk.Button(hist_ctrls, text="Validate", command=self.validate_history, width=10).pack(side="right", padx=5)

        filter_row = ttk.Frame(left_col)
        filter_row.pack(fill="x", pady=10)
        ttk.Button(filter_row, text="Numbers", command=self.open_numbers_filter, width=10).pack(side="left", padx=2)
        ttk.Button(filter_row, text="Sums O/E", command=self.open_sums_oe_filter, width=10).pack(side="left", padx=2)
        ttk.Button(filter_row, text="Patterns", command=self.open_consec_filter, width=10).pack(side="left", padx=2)
        ttk.Button(filter_row, text="Repeats", command=self.open_repeats_filter, width=10).pack(side="left", padx=2)

        # Right side: Trend Window, Sliders and Control Buttons
        right_col = ttk.Frame(main_container)
        right_col.pack(side="left", fill="y", padx=10)

        # Trend Window Input
        tw_frame = ttk.Frame(right_col)
        tw_frame.pack(fill="x", pady=(5, 10))
        ttk.Label(tw_frame, text="Trend Window:").pack(side="left", padx=5)
        
        def validate_tw(P):
            if P == "" or (P.isdigit() and 1 <= int(P) <= 1000):
                return True
            return False
        vcmd = (self.root.register(validate_tw), '%P')
        
        self.tw_entry = ttk.Entry(tw_frame, textvariable=self.trend_window_var, width=7, validate="key", validatecommand=vcmd)
        self.tw_entry.pack(side="left")

        # Sliders
        ttk.Label(right_col, text="Trend Weight:").pack(anchor="w", padx=5)
        self.trend_slider = tk.Scale(right_col, from_=0.0, to=1.0, resolution=0.1, orient="horizontal", variable=self.trend_weight_var, length=150)
        self.trend_slider.pack(padx=5, pady=(0, 5))
        
        ttk.Label(right_col, text="Volatility Penalty:").pack(anchor="w", padx=5)
        self.vol_slider = tk.Scale(right_col, from_=0.0, to=1.0, resolution=0.1, orient="horizontal", variable=self.vol_penalty_var, length=150)
        self.vol_slider.pack(padx=5, pady=(0, 5))
        
        ttk.Label(right_col, text="Sensitivity:").pack(anchor="w", padx=5)
        self.sens_slider = tk.Scale(right_col, from_=0.1, to=0.9, resolution=0.1, orient="horizontal", variable=self.sensitivity_var, length=150)
        self.sens_slider.pack(padx=5, pady=(0, 15))

        # Control Buttons
        ttk.Button(right_col, text="Clear All Filter Selections", command=self.clear_all_filter_selections, width=22).pack(pady=2)
        ttk.Button(right_col, text="Clear Commitments", command=self.clear_all_commitments, width=22).pack(pady=2)
        ttk.Button(right_col, text="OPTIMIZE!", command=self.open_optimization_window, width=22).pack(pady=15, ipady=10)

    def open_generic_filter(self, title, items, session_set, mode):
        # 1. Window Setup
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("1150x650")
        
        top_bar = ttk.Frame(win)
        top_bar.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(top_bar, text="Copy Table", command=lambda: self.copy_tree_to_clipboard(tree)).pack(side="left", padx=5)
        ttk.Button(top_bar, text="Select All", command=lambda: self.bulk_select(tree, "all", session_set, mode, lbl)).pack(side="left", padx=2)
        ttk.Button(top_bar, text="Deselect All", command=lambda: self.bulk_select(tree, "none", session_set, mode, lbl)).pack(side="left", padx=2)
        ttk.Button(top_bar, text="Invert Selection", command=lambda: self.bulk_select(tree, "invert", session_set, mode, lbl)).pack(side="left", padx=2)
        
        lbl = ttk.Label(top_bar, text=f"Selected: {len(session_set)}", font=("Arial", 10, "bold"))
        lbl.pack(side="left", padx=20)

        # 2. Table Columns
        cols = ("Item", "Sel", "Theo%", "Exp", "Emp", "E-E", "Recent", "AvgRun", "R/A", "Vol", "Trend", "Composite", "Symbol", "Play?")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c, command=lambda _c=c: self.smart_tree_sort(tree, _c))
            tree.column(c, width=75, anchor="center")
        tree.pack(fill="both", expand=True)

        # 3. Math & Stats Gathering
        has_hist = self.use_history_var.get() and self.history
        
        # New: Get Trend Window from Entry
        try:
            w = int(self.trend_window_var.get())
        except ValueError:
            w = 20 # Fallback
            
        stats_list = []
        
        for idx, item in enumerate(items):
            theo = 0.0
            if mode == "numbers": 
                theo = 1.0 / self.total_nums_var.get()
            elif mode == "sum_oe": 
                theo = 0.5
            elif mode == "repeats": 
                theo = self.get_repeats_theo(int(item))
            elif mode == "consec": 
                theo = self.get_consec_theo(item)
            
            if has_hist:
                if mode == "numbers": 
                    seq = [1 if int(item) in d else 0 for d in self.history]
                elif mode == "sum_oe": 
                    seq = [1 if (sum(d)%2!=0 if item=="Odd Sum" else sum(d)%2==0) else 0 for d in self.history]
                elif mode == "consec": 
                    seq = [1 if self.get_pattern(d) == item else 0 for d in self.history]
                elif mode == "repeats":
                    t = int(item)
                    seq = [1 if len(set(self.history[i]).intersection(set(self.history[i-1]))) == t else 0 for i in range(1, len(self.history))]
                
                s = self.get_stats_v2(seq, w)
                stats_list.append((item, s, seq, idx, theo))
            else: 
                stats_list.append((item, [0, "", "--", "--", 0, 0, 0], [], idx, theo))

        # 4. Table Filling
        for item, s, seq, original_idx, theo in stats_list:
            if has_hist:
                ra_m = max([abs(float(x[1][3][1:])) for x in stats_list if x[1][3] != "--"]) or 1
                t_max = max([x[1][5] for x in stats_list]) or 1
                v_max = max([x[1][4] for x in stats_list]) or 1
                
                ra_norm = (ra_m - abs(float(s[3][1:]))) / ra_m if ra_m else 0
                t_norm = s[5] / t_max if t_max else 0
                v_norm = s[4] / v_max if v_max else 0
                
                comp_val = max(0, ((ra_norm * (1-self.trend_weight_var.get())) + (t_norm * self.trend_weight_var.get()) - (v_norm * self.vol_penalty_var.get())) * 100)
                comp = f"{comp_val:.2f}"
                
                sym = ("001 ↑" if s[1]=="-" else "111 →") if comp_val >= (1 - self.sensitivity_var.get()) * 100 else ("000 →" if s[1]=="-" else "110 ↑")
                play = "YES" if comp_val >= (1 - self.sensitivity_var.get()) * 100 else "NO"
                
                if mode == "numbers":
                    total_balls_in_history = len(seq) * self.draws_var.get()
                    exp_val = total_balls_in_history * theo
                else:
                    exp_val = len(seq) * theo
                
                exp = f"{exp_val:.2f}"
                ee = f"{s[6] - exp_val:.2f}"
                emp, recent, avg_run, ra_val, vol, trend = str(s[6]), f"{s[1]}{s[0]}", s[2], s[3], f"{s[4]:.2f}", f"{s[5]:.2f}"
            else: 
                exp, emp, ee, recent, avg_run, ra_val, vol, trend, comp, sym, play = ("--",)*11
            
            tree.insert("", "end", values=(item, "✓" if item in session_set else "", f"{theo*100:.2f}%", exp, emp, ee, recent, avg_run, ra_val, vol, trend, comp, sym, play))

        bot = ttk.Frame(win)
        bot.pack(fill="x", pady=10)
        ttk.Button(bot, text="Back", command=win.destroy).pack(side="left", padx=10)
        ttk.Button(bot, text="Commit", command=lambda: self.commit_filter(win, session_set, mode)).pack(side="right", padx=10)
        
        tree.bind("<Button-1>", lambda e: self.on_tree_click(e, session_set, mode, lbl))

    def smart_tree_sort(self, tree, col):
        rev = not self.sort_states.get(col, False)
        self.sort_states[col] = rev
        data = []
        for item_id in tree.get_children(''):
            val = tree.set(item_id, col)
            s_val = str(val).strip()
            if col == "Sel":
                sort_key = 1 if "✓" in s_val else 0
            elif s_val == "--" or s_val == "":
                sort_key = -999999 if not rev else 999999
            else:
                clean_val = s_val.replace('%','').replace('↑','').replace('→','').strip()
                try:
                    sort_key = float(clean_val)
                except ValueError:
                    sort_key = s_val.lower()
            data.append((sort_key, item_id))

        data.sort(key=lambda x: x[0], reverse=rev)
        for index, (_, item_id) in enumerate(data):
            tree.move(item_id, '', index)

    def open_optimization_window(self):
        self.candidate_pool = []
        self.stop_requested = False
        
        # UI COSMETICS: Optimized window dimensions
        win = tk.Toplevel(self.root); win.title("Optimization Engine"); win.geometry("700x600")
        win.resizable(False, False)
        
        pf = ttk.LabelFrame(win, text="Pool Management"); pf.pack(fill="x", padx=10, pady=5)
        self.pool_lbl = ttk.Label(pf, text="Pool Size: 0", font=("Arial", 10, "bold"))
        self.pool_lbl.pack(side="left", padx=10)
        
        ttk.Button(pf, text="From Filters", command=self.fill_pool_from_filters, width=12).pack(side="left", padx=2)
        ttk.Button(pf, text="From History", command=self.fill_pool_from_history, width=12).pack(side="left", padx=2)
        
        self.rand_size = tk.StringVar(value="2000")
        ttk.Entry(pf, textvariable=self.rand_size, width=6).pack(side="left", padx=5)
        ttk.Button(pf, text="Random", command=self.fill_pool_random, width=8).pack(side="left", padx=2)
        
        # We tell the button EXACTLY which window it belongs to for the file fix
        ttk.Button(pf, text="Fill from File", command=lambda: self.fill_pool_from_file(win), width=12).pack(side="left", padx=2)

        ctrl = ttk.Frame(win); ctrl.pack(fill="x", padx=10, pady=5)
        self.opt_then = tk.IntVar(value=3); self.opt_if = tk.IntVar(value=self.draws_var.get())
        ttk.Label(ctrl, text="Cond:").pack(side="left"); ttk.Entry(ctrl, textvariable=self.opt_then, width=3).pack(side="left")
        ttk.Label(ctrl, text=" if ").pack(side="left"); ttk.Entry(ctrl, textvariable=self.opt_if, width=3).pack(side="left")
        
        self.det_btn = ttk.Button(ctrl, text="Deterministic", state="disabled", command=lambda: self.run_engine("Det"))
        self.det_btn.pack(side="left", padx=10)
        self.heu_btn = ttk.Button(ctrl, text="Heuristic", state="disabled", command=lambda: self.run_engine("Heur"))
        self.heu_btn.pack(side="left")
        
        self.stop_btn = ttk.Button(ctrl, text="STOP", state="disabled", command=self.request_stop)
        self.stop_btn.pack(side="left", padx=20)
        
        ttk.Button(ctrl, text="Clear", command=self.clear_opt_displays).pack(side="left", padx=5)
        ttk.Button(ctrl, text="Excel", command=self.copy_all_opt_to_excel).pack(side="left")

        prog_frame = ttk.Frame(win); prog_frame.pack(fill="x", padx=10, pady=5)
        self.progress_var = tk.DoubleVar(value=0.0) 
        self.progress_bar = ttk.Progressbar(prog_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.perc_lbl = ttk.Label(prog_frame, text="0.0%", width=8); self.perc_lbl.pack(side="right")

        disp = ttk.Frame(win); disp.pack(fill="both", expand=True, padx=10, pady=5)
        self.opt_text = tk.Text(disp, width=35, height=15, font=("Courier New", 10)); self.opt_text.pack(side="left", fill="both", expand=True)
        self.freq_text = tk.Text(disp, width=15, height=15, bg="#f0f0f0", font=("Courier New", 10)); self.freq_text.pack(side="right", fill="y")
        
        bot_f = ttk.Frame(win); bot_f.pack(fill="x", pady=5)
        ttk.Button(bot_f, text="Back", command=win.destroy).pack(side="right", padx=15)

    def request_stop(self):
        self.stop_requested = True
        self.stop_btn.config(state="disabled")

    def run_engine(self, mode):
        self.clear_opt_displays()
        self.stop_requested = False
        self.stop_btn.config(state="normal")
        self.progress_var.set(0)
        self.perc_lbl.config(text="0.0%")
        
        pool = list(self.candidate_pool)
        if not pool: return
        
        if mode == "Det":
            idx = random.randint(0, len(pool)-1)
            pool = pool[idx:] + pool[:idx]
        else:
            random.shuffle(pool)
        
        covered, tickets, freq, t_then = set(), [], Counter(), self.opt_then.get()
        total_size = len(pool)

        while len(covered) < total_size:
            if self.stop_requested:
                self.opt_text.insert("end", "\n--- HALTED ---\n")
                break
            
            best_t, best_c = None, set()
            sample = pool[:2000] if mode == "Det" else random.sample(pool, min(len(pool), 1000))
            
            for t in sample:
                c = {i for i, cand in enumerate(pool) if i not in covered and len(t.intersection(cand)) >= t_then}
                if len(c) > len(best_c):
                    best_c = c
                    best_t = t
            
            if not best_t: break
            
            covered.update(best_c)
            tickets.append(sorted(list(best_t)))
            for n in best_t: freq[n] += 1
            
            prog = (len(covered) / total_size) * 100
            self.progress_var.set(prog)
            self.perc_lbl.config(text=f"{prog:.1f}%")
            
            # RESTORED: Ticket number, combinations, and cumulative coverage percentage
            ticket_line = f"T{len(tickets)}\t{', '.join(f'{x:02d}' for x in sorted(list(best_t)))}\t{prog:.1f}%\n"
            self.opt_text.insert("end", ticket_line)
            self.opt_text.see("end")
            self.update_freq_display(freq)
            self.root.update()

        self.stop_btn.config(state="disabled")

    def update_pool_state(self):
        size = len(self.candidate_pool)
        self.pool_lbl.config(text=f"Pool Size: {size:,}")
        st = "normal" if size > 0 else "disabled"
        self.det_btn.config(state=st)
        self.heu_btn.config(state=st)

    def fill_pool_from_history(self):
        if not self.history:
            messagebox.showwarning("!", "No history available to fill pool.")
            return
        self.candidate_pool = [set(d) for d in self.history]
        self.update_pool_state()

    def get_stats_v2(self, seq, window):
        # If no history is loaded, return "empty" markers
        if not seq: 
            return [0, "", "0.0", "0.00", 0, 0, 0]
        
        # Calculate 'Recent' (How many draws ago it last hit/missed)
        rv = seq[-1]
        rc = 0
        for v in reversed(seq):
            if v == rv: rc += 1
            else: break
        
        # Track 'Runs' (Streaks)
        hr, sr = [], []
        cv, ct = seq[0], 1
        for i in range(1, len(seq)):
            if seq[i] == cv: ct += 1
            else:
                if cv == 1: hr.append(ct)
                else: sr.append(ct)
                cv, ct = seq[i], 1
        if cv == 1: hr.append(ct)
        else: sr.append(ct)
        
        # Determine sign (+ for hit streak, - for miss streak)
        sign = "+" if rv == 1 else "-"
        rel = hr if rv == 1 else sr
        
        # Calculate Average Run and Relative Appearance (R/A)
        avg = sum(rel)/len(rel) if rel else 1.0
        ra = rc / avg if avg != 0 else 0
        
        emp = sum(seq) # Total hits
        
        # Volatility: How often does it switch from hit to miss?
        vol = (len(hr)+len(sr))/len(seq) if len(seq) > 0 else 0
        
        # Trend: Performance in the 'Window' vs Performance in total history
        sub = seq[-window:]
        trnd = (sum(sub)/len(sub)) - (emp/len(seq)) if (sub and len(seq) > 0) else 0
        
        return [rc, sign, f"{sign}{avg:.1f}", f"{sign}{ra:.2f}", vol, trnd, emp]

    # --- Standard Lotto Math Support ---
    def get_pattern(self, c):
        nums = sorted(list(c)); gs, ct = [], 1
        for i in range(len(nums)-1):
            if nums[i+1] == nums[i] + 1: ct += 1
            else: gs.append(ct); ct = 1
        gs.append(ct); return " ".join(map(str, sorted(gs, reverse=True)))

    def get_all_possible_patterns(self, k):
        def ps(n):
            if n == 0: yield []
            else:
                for i in range(1, n + 1):
                    for p in ps(n - i): yield sorted([i] + p, reverse=True)
        u = set(tuple(p) for p in ps(k)); return [" ".join(map(str, p)) for p in sorted(u, reverse=True, key=lambda x: (len(x), x))]

    def get_consec_theo(self, p):
        n, k = self.total_nums_var.get(), self.draws_var.get()
        try:
            parts = [int(x) for x in str(p).split()]; m = len(parts); c = Counter(parts); np = math.factorial(m)
            for v in c.values(): np //= math.factorial(v)
            return (math.comb(n - k + 1, m) * np) / math.comb(n, k)
        except: return 0.0

    def get_repeats_theo(self, k):
        n, r = self.total_nums_var.get(), self.draws_var.get()
        try: return (math.comb(r, k) * math.comb(n - r, r - k)) / math.comb(n, r)
        except: return 0.0

    def open_numbers_filter(self): self.open_generic_filter("Numbers", [str(i) for i in range(1, self.total_nums_var.get()+1)], self.selected_numbers, "numbers")
    def open_sums_oe_filter(self): self.open_generic_filter("Sums", ["Odd Sum", "Even Sum"], self.selected_sum_oe, "sum_oe")
    def open_consec_filter(self): self.open_generic_filter("Consecutives", self.get_all_possible_patterns(self.draws_var.get()), self.selected_consec, "consec")
    def open_repeats_filter(self): self.open_generic_filter("Repeats", [str(i) for i in range(self.draws_var.get()+1)], self.selected_repeats, "repeats")
    
    def commit_filter(self, win, ss, m):
        if m == "numbers": self.committed_numbers = set(ss)
        elif m == "sum_oe": self.committed_sum_oe = set(ss)
        elif m == "consec": self.committed_consec = set(ss)
        else: self.committed_repeats = set(ss)
        win.destroy()

    def update_freq_display(self, cnt):
        self.freq_text.delete("1.0", "end"); self.freq_text.insert("end", "Num|Cnt\n" + "-"*7 + "\n")
        for n, c in cnt.most_common(): self.freq_text.insert("end", f"{n:2d}|{c:3d}\n")
    
    def clear_opt_displays(self): 
        self.opt_text.delete("1.0", "end")
        self.freq_text.delete("1.0", "end")
        self.progress_var.set(0.0)
        self.perc_lbl.config(text="0.0%")

    def copy_all_opt_to_excel(self): 
        self.root.clipboard_clear()
        self.root.clipboard_append(self.opt_text.get("1.0", "end") + "\n" + self.freq_text.get("1.0", "end"))

    def fill_pool_from_filters(self):
        if not self.committed_numbers: messagebox.showwarning("!", "Commit numbers first"); return
        nums = sorted([int(n) for n in self.committed_numbers]); pool = []
        last = set(self.history[-1]) if self.history else set()
        for c in combinations(nums, self.draws_var.get()):
            if self.committed_sum_oe:
                iso = sum(c)%2!=0
                if iso and "Odd Sum" not in self.committed_sum_oe: continue
                if not iso and "Even Sum" not in self.committed_sum_oe: continue
            if self.committed_consec and self.get_pattern(c) not in self.committed_consec: continue
            if self.committed_repeats and last and str(len(set(c).intersection(last))) not in self.committed_repeats: continue
            pool.append(set(c))
            if len(pool) > 500000: break
        self.candidate_pool = pool
        self.update_pool_state()

    def fill_pool_random(self):
        try:
            n, k = self.total_nums_var.get(), self.draws_var.get()
            self.candidate_pool = [set(random.sample(range(1, n+1), k)) for _ in range(int(self.rand_size.get()))]
            self.update_pool_state()
        except: pass

    def fill_pool_from_file(self, target_win):
        p = filedialog.askopenfilename(parent=target_win, filetypes=[("Text/CSV", "*.txt *.csv")])
        if p:
            k = self.draws_var.get()
            n_max = self.total_nums_var.get()
            valid_pool = []
            try:
                with open(p, 'r') as f:
                    for line in f:
                        parts = line.replace(',', ' ').split()
                        if not parts: continue
                        try:
                            nums = sorted([int(x) for x in parts if x.strip()])
                            if len(nums) == k and all(1 <= x <= n_max for x in nums):
                                valid_pool.append(set(nums))
                        except ValueError: continue
                
                self.candidate_pool = valid_pool
                size = len(self.candidate_pool)
                
                # FORCE update the label and the buttons
                self.pool_lbl.config(text=f"Pool Size: {size:,}")
                st = "normal" if size > 0 else "disabled"
                self.det_btn.config(state=st)
                self.heu_btn.config(state=st)
                
                # FORCE the window to stay put and be visible
                target_win.lift()
                target_win.focus_force()
                
                messagebox.showinfo("Success", f"Imported {size:,} combinations.", parent=target_win)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}", parent=target_win)


    def bulk_select(self, tree, sm, ss, m, lbl):
        for i_id in tree.get_children():
            i = tree.item(i_id, 'values')[0]
            if sm == "all": ss.add(i)
            elif sm == "none": ss.discard(i)
            elif sm == "invert": ss.remove(i) if i in ss else ss.add(i)
            tree.item(i_id, values=(i, "✓" if i in ss else "") + tree.item(i_id, 'values')[2:])
        lbl.config(text=f"Selected: {len(ss)}")

    def on_tree_click(self, e, ss, m, lbl):
        t = e.widget; i_id = t.identify_row(e.y); c = t.identify_column(e.x)
        if i_id and c == '#2':
            i = t.item(i_id, 'values')[0]
            if i in ss: ss.remove(i)
            else: ss.add(i)
            t.item(i_id, values=(i, "✓" if i in ss else "") + t.item(i_id, 'values')[2:])
            lbl.config(text=f"Selected: {len(ss)}")

    def copy_tree_to_clipboard(self, t):
        o = "\t".join(t["columns"]) + "\n"
        for i in t.get_children(): o += "\t".join([str(v) for v in t.item(i)["values"]]) + "\n"
        self.root.clipboard_clear(); self.root.clipboard_append(o)

    def validate_history(self):
        r = self.history_text.get("1.0", "end").strip()
        if not r: return
        try:
            p, f = [], []
            k = self.draws_var.get()
            for l in r.split('\n'):
                n = sorted([int(x) for x in l.replace(',', ' ').split() if x.strip()])
                if len(n) == k: p.append(n); f.append(", ".join(f"{x:02d}" for x in n))
            self.history = p; self.history_text.delete("1.0", "end"); self.history_text.insert("1.0", "\n".join(f))
            if self.history: self.use_history_var.set(True); self.update_ui_state()
        except: messagebox.showerror("Err", "Validation Failed")

    def import_csv(self):
        # UPDATED: Now looks for both .csv and .txt files in the selection window
        p = filedialog.askopenfilename(filetypes=[
            ("All Supported", "*.csv *.txt"),
            ("CSV files", "*.csv"),
            ("Text files", "*.txt")
        ])
        
        if p:
            try:
                with open(p, 'r') as f:
                    content = f.read()
                    self.history_text.delete("1.0", "end")
                    self.history_text.insert("1.0", content)
                
                # Automatically clean and validate the data
                self.validate_history()
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    def validate_history(self):
        r = self.history_text.get("1.0", "end").strip()
        if not r: 
            return
            
        try:
            p, f, k = [], [], self.draws_var.get()
            n_max = self.total_nums_var.get()
            
            for l in r.split('\n'):
                line_content = l.strip()
                if not line_content: 
                    continue
                
                # THE LOGIC FIX: 
                # .replace(',', ' ') turns "01,02,03" into "01 02 03"
                # .split() then turns that into a list of numbers regardless of spacing
                nums = sorted([int(x) for x in line_content.replace(',', ' ').split() if x.strip()])
                
                if len(nums) == k and all(1 <= x <= n_max for x in nums):
                    p.append(nums)
                    f.append(", ".join(f"{x:02d}" for x in nums))
            
            if p:
                self.history = p
                self.history_text.delete("1.0", "end")
                self.history_text.insert("1.0", "\n".join(f))
                self.use_history_var.set(True)
                self.update_ui_state()
                messagebox.showinfo("Success", f"Imported {len(p)} draws successfully!")
            else:
                messagebox.showwarning("Validation", f"No draws matched your settings (Pick {k} from {n_max}).")
        except Exception as e: 
            messagebox.showerror("Err", f"Validation Failed: {e}")

    def clear_history_action(self): 
        self.history_text.delete("1.0", "end")
        self.history = []
        self.use_history_var.set(False)
        self.update_ui_state()

    def clear_all_filter_selections(self): 
        self.selected_numbers.clear(); self.selected_sum_oe.clear()
        self.selected_consec.clear(); self.selected_repeats.clear()

    def clear_all_commitments(self): 
        self.committed_numbers.clear(); self.committed_sum_oe.clear()
        self.committed_consec.clear(); self.committed_repeats.clear()

    def update_ui_state(self):
        s = "normal" if self.history and self.use_history_var.get() else "disabled"
        self.trend_slider.config(state=s); self.vol_slider.config(state=s); self.sens_slider.config(state=s)

    def create_history_context_menu(self, w):
        m = tk.Menu(w, tearoff=0)
        m.add_command(label="Paste", command=lambda: w.event_generate("<<Paste>>"))
        m.add_command(label="Validate", command=self.validate_history)
        m.add_command(label="Clear", command=self.clear_history_action)
        w.bind("<Button-3>", lambda e: m.post(e.x_root, e.y_root))

if __name__ == "__main__":
    root = tk.Tk()
    app = VATA_LottoEnhanced(root)
    root.mainloop()
