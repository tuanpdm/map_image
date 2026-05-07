import os
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import pandas as pd

# ─────────────────────────────────────────────
#  Logic xử lý
# ─────────────────────────────────────────────
def run_mapping(excel_path, image_dir, output_path, log, btn_run):
    def task():
        btn_run.config(state='disabled')
        log.config(state='normal')
        log.delete('1.0', tk.END)

        def info(msg):  log.insert(tk.END, msg + '\n'); log.see(tk.END); log.update()
        def ok(msg):    log.insert(tk.END, '✅ ' + msg + '\n'); log.see(tk.END); log.update()
        def err(msg):   log.insert(tk.END, '❌ ' + msg + '\n'); log.see(tk.END); log.update()
        def warn(msg):  log.insert(tk.END, '⚠️  ' + msg + '\n'); log.see(tk.END); log.update()

        try:
            # Đọc file Excel
            info("Đang đọc file Excel...")
            df = pd.read_excel(excel_path, dtype=str)
            df.columns = df.columns.str.strip()
            ok(f"Đọc được {len(df)} dòng | Cột: {list(df.columns)}")

            # Tìm cột MHS
            mhs_col = next((c for c in df.columns if c.strip().upper() == 'MHS'), None)
            if mhs_col is None:
                err(f"Không tìm thấy cột MHS! Cột hiện có: {list(df.columns)}")
                return
            ok(f"Cột mã sinh viên: '{mhs_col}'")

            # Quét ảnh
            info("Đang quét thư mục ảnh...")
            exts = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff'}
            image_files = []
            for root, dirs, files in os.walk(image_dir):
                for f in files:
                    if os.path.splitext(f)[1].lower() in exts:
                        image_files.append(f)
            ok(f"Tìm thấy {len(image_files)} file ảnh (kể cả folder con)")

            # Mapping
            info("Đang map ảnh với mã sinh viên...")
            def find_image(mhs):
                if pd.isna(mhs) or str(mhs).strip() == '':
                    return ''
                mhs = str(mhs).strip()
                matches = [f for f in image_files if mhs in f]
                if len(matches) == 1:   return matches[0]
                elif len(matches) > 1:  return '|'.join(sorted(matches))
                return ''

            df['anh'] = df[mhs_col].apply(find_image)

            found     = (df['anh'] != '').sum()
            not_found = (df['anh'] == '').sum()
            multi     = df['anh'].str.contains(r'\|', na=False).sum()

            ok(f"Match được      : {found} sinh viên")
            if not_found: err(f"Không tìm thấy : {not_found} sinh viên")
            if multi:     warn(f"Nhiều file trùng mã : {multi} sinh viên (cột 'anh' có dấu |)")

            # In danh sách không tìm thấy
            missing_cols = [mhs_col] + (['ten'] if 'ten' in df.columns else [])
            missing = df[df['anh'] == ''][missing_cols]
            if not missing.empty:
                info("\nDanh sách không tìm thấy ảnh:")
                for _, row in missing.iterrows():
                    info(f"   {' | '.join(str(v) for v in row.values)}")

            # Lưu file
            info("\nĐang lưu file output...")
            df.to_excel(output_path, index=False)
            ok(f"Đã lưu: {output_path}")
            info("\n🎉 Hoàn tất!")

        except Exception as e:
            err(f"Lỗi: {e}")
        finally:
            btn_run.config(state='normal')
            log.config(state='disabled')

    threading.Thread(target=task, daemon=True).start()


# ─────────────────────────────────────────────
#  Giao diện
# ─────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.title("Map Ảnh Sinh Viên")
    root.resizable(False, False)

    BG      = "#1e1e2e"
    CARD    = "#2a2a3e"
    ACCENT  = "#7c6af7"
    TEXT    = "#cdd6f4"
    MUTED   = "#6c7086"
    SUCCESS = "#a6e3a1"
    BTN_FG  = "#ffffff"

    root.configure(bg=BG)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TEntry', fieldbackground=CARD, foreground=TEXT,
                    insertcolor=TEXT, bordercolor=MUTED, relief='flat')

    # ── Header ──────────────────────────────
    header = tk.Frame(root, bg=ACCENT, pady=14)
    header.pack(fill='x')
    tk.Label(header, text="🖼  Map Ảnh Sinh Viên",
             font=('Segoe UI', 16, 'bold'), bg=ACCENT, fg=BTN_FG).pack()
    tk.Label(header, text="Tự động ghép tên file ảnh vào danh sách sinh viên",
             font=('Segoe UI', 9), bg=ACCENT, fg="#ddd").pack()

    # ── Body ────────────────────────────────
    body = tk.Frame(root, bg=BG, padx=24, pady=20)
    body.pack(fill='both')

    def file_row(parent, label, is_folder=False, is_save=False):
        tk.Label(parent, text=label, font=('Segoe UI', 9, 'bold'),
                 bg=BG, fg=MUTED).pack(anchor='w', pady=(10, 2))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill='x')
        var = tk.StringVar()
        entry = tk.Entry(row, textvariable=var, font=('Segoe UI', 10),
                         bg=CARD, fg=TEXT, insertbackground=TEXT,
                         relief='flat', bd=0, highlightthickness=1,
                         highlightbackground=MUTED, highlightcolor=ACCENT)
        entry.pack(side='left', fill='x', expand=True, ipady=6, padx=(0, 8))

        def browse():
            if is_folder:
                path = filedialog.askdirectory()
            elif is_save:
                path = filedialog.asksaveasfilename(
                    defaultextension='.xlsx',
                    filetypes=[('Excel files', '*.xlsx')])
            else:
                path = filedialog.askopenfilename(
                    filetypes=[('Excel files', '*.xlsx *.xls')])
            if path:
                var.set(path)

        btn = tk.Button(row, text="Browse", command=browse,
                        font=('Segoe UI', 9), bg=ACCENT, fg=BTN_FG,
                        relief='flat', padx=12, pady=4, cursor='hand2',
                        activebackground="#6a5ae0", activeforeground=BTN_FG)
        btn.pack(side='left')
        return var

    var_excel  = file_row(body, "📄  File Excel đầu vào (.xlsx)")
    var_folder = file_row(body, "📁  Thư mục chứa ảnh", is_folder=True)
    var_output = file_row(body, "💾  File Excel đầu ra (.xlsx)", is_save=True)

    # ── Divider ─────────────────────────────
    tk.Frame(body, bg=MUTED, height=1).pack(fill='x', pady=(20, 0))

    # ── Log area ────────────────────────────
    tk.Label(body, text="📋  Kết quả", font=('Segoe UI', 9, 'bold'),
             bg=BG, fg=MUTED).pack(anchor='w', pady=(12, 4))

    log = scrolledtext.ScrolledText(
        body, height=12, font=('Consolas', 9),
        bg=CARD, fg=SUCCESS, insertbackground=TEXT,
        relief='flat', bd=0, state='disabled',
        highlightthickness=1, highlightbackground=MUTED)
    log.pack(fill='x')

    # ── Run button ──────────────────────────
    def on_run():
        excel  = var_excel.get().strip()
        folder = var_folder.get().strip()
        output = var_output.get().strip()
        if not excel or not folder or not output:
            log.config(state='normal')
            log.delete('1.0', tk.END)
            log.insert(tk.END, "❌ Vui lòng chọn đủ 3 đường dẫn!\n")
            log.config(state='disabled')
            return
        run_mapping(excel, folder, output, log, btn_run)

    btn_run = tk.Button(body, text="▶   Chạy", command=on_run,
                        font=('Segoe UI', 11, 'bold'), bg=ACCENT, fg=BTN_FG,
                        relief='flat', padx=20, pady=10, cursor='hand2',
                        activebackground="#6a5ae0", activeforeground=BTN_FG)
    btn_run.pack(pady=(16, 4), ipadx=30)

    # ── Footer ──────────────────────────────
    tk.Label(root, text="Tìm ảnh theo cột MHS  •  Hỗ trợ folder con",
             font=('Segoe UI', 8), bg=BG, fg=MUTED).pack(pady=(0, 10))

    root.update_idletasks()
    w, h = root.winfo_width(), root.winfo_height()
    x = (root.winfo_screenwidth()  - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == '__main__':
    main()
