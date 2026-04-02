#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, webbrowser, sys
from datetime import datetime, date
from pathlib import Path

DATA_FILE = Path(__file__).parent / "tasks.json"

_DEF = {
    "tasks": [], "next_id": 1,
    "custom_columns": [], "finish_time": "17:00", "last_reset_date": "",
}

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        for k, v in _DEF.items():
            d.setdefault(k, v)
        return d
    return dict(_DEF)

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def _create_startup_bat():
    bat = Path(__file__).parent / "起動_タスク管理.bat"
    py  = Path(sys.executable).resolve()
    app = Path(__file__).resolve()
    bat.write_text(
        f'@echo off\nstart "" "{py}" "{app}"\n',
        encoding="utf-8",
    )
    return bat

def _center(win):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"+{(sw-win.winfo_width())//2}+{(sh-win.winfo_height())//2}")


class FinishTimeDialog(tk.Toplevel):
    def __init__(self, parent, current="17:00"):
        super().__init__(parent)
        self.title("おはようございます")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        BG = "#f8f9fa"
        self.configure(bg=BG)
        tk.Label(self, text="おはようございます！\U0001f305",
                 font=("Meiryo", 14, "bold"), bg=BG).pack(pady=(22, 4))
        tk.Label(self, text="今日の退勤時間を入力してください",
                 font=("Meiryo", 10), bg=BG, fg="#6c757d").pack()
        row = tk.Frame(self, bg=BG)
        row.pack(pady=14)
        self._v = tk.StringVar(value=current)
        self._e = tk.Entry(row, textvariable=self._v,
                           font=("Meiryo", 14), width=7, justify="center")
        self._e.pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(row, text="HH:MM", font=("Meiryo", 9),
                 bg=BG, fg="#adb5bd").pack(side=tk.LEFT)
        tk.Button(self, text="開始 \u2192", command=self._ok,
                  bg="#0d6efd", fg="white", relief=tk.FLAT,
                  font=("Meiryo", 11, "bold"), padx=24, pady=8,
                  cursor="hand2").pack(pady=(4, 22))
        self.bind("<Return>", lambda _e: self._ok())
        self.protocol("WM_DELETE_WINDOW", self._ok)
        self._e.focus_set()
        self._e.select_range(0, tk.END)
        _center(self)

    def _ok(self):
        t = self._v.get().strip()
        try:
            datetime.strptime(t, "%H:%M")
        except ValueError:
            messagebox.showerror("入力エラー",
                "HH:MM形式で入力してください（例：17:30）", parent=self)
            return
        self.result = t
        self.destroy()


class TaskDialog(tk.Toplevel):
    def __init__(self, parent, custom_cols, task=None):
        super().__init__(parent)
        self.title("タスク編集" if task else "タスク追加")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self._cc = custom_cols
        BG = "#f8f9fa"
        self.configure(bg=BG, padx=22, pady=18)
        self._f = {}
        r = 0

        tk.Label(self, text="優先順位：", bg=BG,
                 font=("Meiryo", 10)).grid(row=r, column=0, sticky="w", pady=5)
        pv = tk.IntVar(value=task["priority"] if task else 1)
        tk.Spinbox(self, from_=1, to=99, textvariable=pv,
                   width=5, font=("Meiryo", 10)).grid(
            row=r, column=1, sticky="w", padx=10, pady=5)
        self._f["p"] = pv; r += 1

        tk.Label(self, text="タスク名 *：", bg=BG,
                 font=("Meiryo", 10)).grid(row=r, column=0, sticky="w", pady=5)
        nv = tk.StringVar(value=task["name"] if task else "")
        ne = tk.Entry(self, textvariable=nv, font=("Meiryo", 10), width=36)
        ne.grid(row=r, column=1, sticky="ew", padx=10, pady=5)
        self._f["n"] = nv; r += 1

        tk.Label(self, text="リンク（任意）：", bg=BG,
                 font=("Meiryo", 10)).grid(row=r, column=0, sticky="w", pady=5)
        lv = tk.StringVar(value=(task.get("link") or "") if task else "")
        tk.Entry(self, textvariable=lv, font=("Meiryo", 10), width=36).grid(
            row=r, column=1, sticky="ew", padx=10, pady=5)
        self._f["l"] = lv; r += 1

        for col in custom_cols:
            tk.Label(self, text=f"{col}：", bg=BG,
                     font=("Meiryo", 10)).grid(row=r, column=0, sticky="w", pady=5)
            val = ((task.get("custom") or {}).get(col, "")) if task else ""
            cv = tk.StringVar(value=val)
            tk.Entry(self, textvariable=cv, font=("Meiryo", 10), width=36).grid(
                row=r, column=1, sticky="ew", padx=10, pady=5)
            self._f[f"c_{col}"] = cv; r += 1

        btns = tk.Frame(self, bg=BG)
        btns.grid(row=r, column=0, columnspan=2, pady=(14, 4))
        tk.Button(btns, text="保存", command=self._save,
                  bg="#0d6efd", fg="white", relief=tk.FLAT,
                  font=("Meiryo", 10, "bold"), padx=18, pady=5).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="キャンセル", command=self.destroy,
                  bg="#dee2e6", fg="#495057", relief=tk.FLAT,
                  font=("Meiryo", 10), padx=18, pady=5).pack(side=tk.LEFT, padx=6)

        ne.focus_set()
        self.bind("<Return>", lambda _e: self._save())
        self.bind("<Escape>", lambda _e: self.destroy())
        _center(self)

    def _save(self):
        name = self._f["n"].get().strip()
        if not name:
            messagebox.showerror("入力エラー", "タスク名は必須です。", parent=self)
            return
        try:
            pri = int(self._f["p"].get())
        except (ValueError, tk.TclError):
            pri = 1
        self.result = {
            "priority": pri, "name": name,
            "link": self._f["l"].get().strip(),
            "custom": {c: self._f[f"c_{c}"].get() for c in self._cc},
        }
        self.destroy()


class BlinkingReminder(tk.Toplevel):
    _C = ("#ff6b6b", "#ffd93d")

    def __init__(self, parent, on_close):
        super().__init__(parent)
        self.title("退勤時刻です！")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.grab_set()
        self._cb = on_close
        self._t = 0
        self.geometry("420x220")
        self._tl = tk.Label(self, text="\u23f0  退勤時刻です！",
                            font=("Meiryo", 18, "bold"))
        self._tl.pack(pady=(38, 10))
        self._sl = tk.Label(self, text="今日のタスクリストを確認しましょう。",
                            font=("Meiryo", 11))
        self._sl.pack()
        tk.Button(self, text="タスクを確認 \u2192", command=self._close,
                  bg="#198754", fg="white", relief=tk.FLAT,
                  font=("Meiryo", 12, "bold"), padx=22, pady=8,
                  cursor="hand2").pack(pady=26)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._blink()
        _center(self)

    def _blink(self):
        if not self.winfo_exists():
            return
        bg = self._C[self._t % 2]
        self._t += 1
        self.configure(bg=bg)
        self._tl.configure(bg=bg)
        self._sl.configure(bg=bg)
        self.after(500, self._blink)

    def _close(self):
        self.destroy()
        self._cb()


class App(tk.Tk):
    _FIXED  = ["done", "priority", "name", "link"]
    _HEADS  = {"done": "\u2713", "priority": "\u512a\u5148\u9806\u4f4d",
               "name": "タスク名", "link": "リンク"}
    _WIDTHS = {"done": 44, "priority": 90, "name": 300, "link": 220}

    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("日次タスク管理")
        self.geometry("960x560")
        self.configure(bg="#f0f4f8")
        self.minsize(680, 420)

        self._d = load_data()
        self._auto_reset()

        dlg = FinishTimeDialog(self, self._d.get("finish_time", "17:00"))
        self.wait_window(dlg)
        if dlg.result:
            self._d["finish_time"] = dlg.result
            save_data(self._d)

        self._alerted = False
        self._build_ui()
        self._refresh()
        self.after(30_000, self._tick)
        self.deiconify()
        _center(self)

    def _auto_reset(self):
        today = str(date.today())
        if self._d.get("last_reset_date") != today:
            for t in self._d["tasks"]:
                t["done"] = False
            self._d["last_reset_date"] = today
            save_data(self._d)

    def _build_ui(self):
        hdr = tk.Frame(self, bg="#212529")
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="日次タスク管理",
                 font=("Meiryo", 14, "bold"),
                 bg="#212529", fg="white").pack(side=tk.LEFT, padx=18, pady=10)
        self._lf = tk.Label(hdr, text=self._fs(),
                            font=("Meiryo", 9), bg="#212529", fg="#adb5bd")
        self._lf.pack(side=tk.RIGHT, padx=18)

        bar = tk.Frame(self, bg="#e9ecef")
        bar.pack(fill=tk.X)
        bk = dict(relief=tk.FLAT, font=("Meiryo", 9), padx=10, pady=5, cursor="hand2")

        def btn(txt, cmd, bg, fg="white"):
            return tk.Button(bar, text=txt, command=cmd, bg=bg, fg=fg, **bk)

        btn("＋ タスク追加", self._add,    "#0d6efd").pack(side=tk.LEFT, padx=(8,3), pady=5)
        btn("✎ 編集",       self._edit,   "#6c757d").pack(side=tk.LEFT, padx=3,     pady=5)
        btn("✕ 削除",       self._delete, "#dc3545").pack(side=tk.LEFT, padx=3,     pady=5)
        btn("＋ 列追加",    self._col,    "#198754").pack(side=tk.LEFT, padx=3,     pady=5)
        btn("↺ リセット",   self._reset,  "#e67e22").pack(side=tk.LEFT, padx=3,     pady=5)
        btn("⚙ 自動起動",   self._auto,   "#6c757d").pack(side=tk.RIGHT, padx=(3,8),pady=5)

        self._tf = tk.Frame(self, bg="#f0f4f8")
        self._tf.pack(fill=tk.BOTH, expand=True, padx=10, pady=(8, 0))
        self._build_tree()

        self._sv = tk.StringVar()
        tk.Label(self, textvariable=self._sv, font=("Meiryo", 9),
                 bg="#dee2e6", fg="#495057", anchor="w",
                 padx=10, pady=3).pack(fill=tk.X, side=tk.BOTTOM)

        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def _build_tree(self):
        for w in self._tf.winfo_children():
            w.destroy()
        cols = self._FIXED + self._d["custom_columns"]
        st = ttk.Style()
        st.configure("T.Treeview", font=("Meiryo", 10), rowheight=29)
        st.configure("T.Treeview.Heading", font=("Meiryo", 10, "bold"))
        st.map("T.Treeview",
               background=[("selected", "#0d6efd")],
               foreground=[("selected", "white")])
        self.tv = ttk.Treeview(self._tf, columns=cols,
                               show="headings", selectmode="browse",
                               style="T.Treeview")
        for c in cols:
            self.tv.heading(c, text=self._HEADS.get(c, c),
                            command=lambda x=c: self._sort(x))
            self.tv.column(c, width=self._WIDTHS.get(c, 120),
                           minwidth=36, stretch=True)
        self.tv.tag_configure("done", foreground="#adb5bd")
        self.tv.tag_configure("todo", foreground="#212529")
        vsb = ttk.Scrollbar(self._tf, orient="vertical",   command=self.tv.yview)
        hsb = ttk.Scrollbar(self._tf, orient="horizontal", command=self.tv.xview)
        self.tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT,  fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tv.pack(fill=tk.BOTH, expand=True)
        self.tv.bind("<Double-1>", self._dbl)
        self.tv.bind("<space>",    lambda _e: self._toggle())
        self.tv.bind("<Return>",   lambda _e: self._link())

    def _refresh(self):
        tasks = sorted(self._d["tasks"],
                       key=lambda t: (t["priority"], t["name"].lower()))
        self.tv.delete(*self.tv.get_children())
        for t in tasks:
            mark = "\u2611" if t.get("done") else "\u2610"
            vals = ([mark, t["priority"], t["name"], t.get("link") or "\u2014"]
                    + [(t.get("custom") or {}).get(c, "")
                       for c in self._d["custom_columns"]])
            self.tv.insert("", tk.END, iid=str(t["id"]),
                           values=vals, tags=("done" if t.get("done") else "todo",))
        done = sum(1 for t in self._d["tasks"] if t.get("done"))
        total = len(self._d["tasks"])
        self._sv.set(f"  {done} / {total} 件完了  │  "
                     f"退勤時刻：{self._d.get('finish_time','--:--')}")
        self._lf.configure(text=self._fs())

    def _fs(self):
        return f"退勤：{self._d.get('finish_time','--:--')}"

    def _sel(self):
        s = self.tv.selection()
        return int(s[0]) if s else None

    def _task(self, tid):
        return next((t for t in self._d["tasks"] if t["id"] == tid), None)

    def _toggle(self):
        tid = self._sel()
        if tid is None: return
        t = self._task(tid)
        if t:
            t["done"] = not t.get("done", False)
            save_data(self._d)
            self._refresh()
            try: self.tv.selection_set(str(tid))
            except tk.TclError: pass

    def _dbl(self, ev):
        col = self.tv.identify_column(ev.x)
        idx = int(col.lstrip("#")) - 1 if col else -1
        cols = self._FIXED + self._d["custom_columns"]
        if 0 <= idx < len(cols):
            n = cols[idx]
            if n == "done": self._toggle()
            elif n == "link": self._link()
            else: self._edit()

    def _link(self):
        tid = self._sel()
        if tid is None: return
        t = self._task(tid)
        if t and t.get("link"): webbrowser.open(t["link"])

    def _add(self):
        dlg = TaskDialog(self, self._d["custom_columns"])
        self.wait_window(dlg)
        if dlg.result:
            self._d["tasks"].append({"id": self._d["next_id"], "done": False, **dlg.result})
            self._d["next_id"] += 1
            save_data(self._d)
            self._refresh()

    def _edit(self):
        tid = self._sel()
        if tid is None:
            messagebox.showinfo("未選択", "タスクを選択してください。", parent=self); return
        t = self._task(tid)
        if not t: return
        dlg = TaskDialog(self, self._d["custom_columns"], task=t)
        self.wait_window(dlg)
        if dlg.result:
            t.update(dlg.result)
            save_data(self._d)
            self._refresh()

    def _delete(self):
        tid = self._sel()
        if tid is None:
            messagebox.showinfo("未選択", "タスクを選択してください。", parent=self); return
        t = self._task(tid)
        if not t: return
        if messagebox.askyesno("削除確認", f'「{t["name"]}」を削除しますか？', parent=self):
            self._d["tasks"] = [x for x in self._d["tasks"] if x["id"] != tid]
            save_data(self._d)
            self._refresh()

    def _col(self):
        name = simpledialog.askstring("列追加", "新しい列名：", parent=self)
        if not name: return
        name = name.strip()
        if not name or name in self._FIXED or name in self._d["custom_columns"]:
            messagebox.showerror("エラー", "列名が無効または既に存在します。", parent=self); return
        self._d["custom_columns"].append(name)
        for t in self._d["tasks"]:
            t.setdefault("custom", {})[name] = ""
        save_data(self._d)
        self._build_tree()
        self._refresh()

    def _reset(self):
        if messagebox.askyesno("リセット確認", "全タスクのチェックを外しますか？", parent=self):
            for t in self._d["tasks"]: t["done"] = False
            save_data(self._d)
            self._refresh()

    def _sort(self, col):
        rev = getattr(self, "_ls", None) == col
        self._ls = None if rev else col
        km = {"priority": lambda t: t["priority"],
              "name":     lambda t: t["name"].lower(),
              "done":     lambda t: t.get("done", False)}
        if col in km:
            self._d["tasks"].sort(key=km[col], reverse=rev)
        self._refresh()

    def _auto(self):
        try:
            bat = _create_startup_bat()
        except Exception as e:
            messagebox.showerror("エラー", f"BATファイルの作成に失敗しました。\n{e}", parent=self)
            return
        startup = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        messagebox.showinfo(
            "自動起動の設定方法",
            f"BATファイルを作成しました：\n{bat}\n\n"
            "以下のフォルダにそのファイルをコピー（またはショートカット）してください：\n\n"
            f"{startup}\n\n"
            "※ セキュリティのため、手動での配置をお願いしています。",
            parent=self,
        )
        webbrowser.open(str(bat.parent))

    def _tick(self):
        try:
            finish = self._d.get("finish_time", "")
            if finish and not self._alerted:
                if datetime.now().strftime("%H:%M") == finish:
                    self._alerted = True
                    self._remind()
        except Exception:
            pass
        self.after(30_000, self._tick)

    def _remind(self):
        self.deiconify(); self.lift()
        self.attributes("-topmost", True)
        self.after(300, lambda: self.attributes("-topmost", False))
        BlinkingReminder(self, on_close=self.lift)


if __name__ == "__main__":
    App().mainloop()
