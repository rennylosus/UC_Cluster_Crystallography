from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

BASE_DIR = Path(__file__).resolve().parent
CONFIG_JSON = BASE_DIR / "config.json"
DEFAULTS_JSON = BASE_DIR / "config_defaults.json"
GENERATOR = BASE_DIR / "config_generator.py"
MAIN = BASE_DIR / "main.py"

OPTIONS = {
    "depth": ["0", "1", "2", "3", "Unlimited", "Custom"],
    "max_folders": ["All", "1", "5", "10", "25", "50", "100"],
    "unit_cell_source": ["ins", "cap"],
    "indexing": ["um ttt", "um twinttt"],
    "ccdc": ["csd", "local", "reduced_cell"],
    "gemmi": ["niggli", "buerger", "selling"],
    "clustering": ["simple", "reduced_cell", "hierarchical", "dbscan", "intensity"],
    "size": ["B", "KB", "MB", "GB"],
}

HELP = {
    "project": "Project name used by the application.",
    "roots": "Root directories searched for matching dataset folders. Each root is searched independently.",
    "search": "Folder names containing SEARCH_STRING are treated as datasets.",
    "case": "Controls whether SEARCH_STRING matching is case-sensitive.",
    "depth": "0 = root only; 1 = immediate subdirectories; 2/3 = deeper levels; Unlimited = no limit; Custom = any non-negative integer.",
    "max": "Maximum number of matching datasets processed. All processes every matching dataset.",
    "rod": "Controls discovery of RODHYPIX files.",
    "ins": "Controls discovery of Olex2/SHELX INS files.",
    "cell": "Controls how the SHELX CELL wavelength is handled.",
    "cluster": "Controls unit-cell tolerances and clustering workflow.",
    "cap": "Controls CrysAlisPro/CAP processing.",
    "indexing": "'um ttt' is the single-domain workflow; 'um twinttt' is the twin/multicrystal workflow.",
    "par": "Ordered CAP .par filename preference. The first matching prefix has highest priority.",
    "ccdc": "Controls CCDC search settings.",
    "gemmi": "Controls Gemmi unit-cell reduction.",
    "output": "Controls generated report location and formatting.",
    "debug": "Controls diagnostic/debug output.",
}

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    tmp = CONFIG_JSON.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
    tmp.replace(CONFIG_JSON)

def generate():
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=BASE_DIR, capture_output=True, text=True
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "config.py generation failed.")

class Tip:
    def __init__(self, widget, text):
        self.widget, self.text, self.tip, self.after_id = widget, text, None, None
        widget.bind("<Enter>", self.start, add="+")
        widget.bind("<Leave>", self.stop, add="+")
    def start(self, _=None):
        self.after_id = self.widget.after(400, self.show)
    def show(self):
        if self.tip: return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
        y = self.widget.winfo_rooty()
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, justify="left", wraplength=430,
                 relief="solid", borderwidth=1, padx=8, pady=6).pack()
    def stop(self, _=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip:
            self.tip.destroy()
            self.tip = None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RA3 Crystallography - Configuration")
        self.geometry("950x780")
        self.minsize(820, 650)
        self.defaults = load(DEFAULTS_JSON)
        self.saved = load(CONFIG_JSON)
        self.data = copy.deepcopy(self.saved)
        self.vars = {}
        self.custom_depth = tk.StringVar()
        self.par_prefixes = []
        self.build()
        self.load_widgets()

    def row(self, parent, r, label, key, widget):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", pady=5, padx=(0,10))
        widget.grid(row=r, column=1, sticky="ew", pady=5)
        b = ttk.Button(parent, text="?", width=3, command=lambda: self.help(key))
        b.grid(row=r, column=2, sticky="e", pady=5)
        Tip(b, HELP.get(key, "No help available."))

    def entry(self, parent, r, label, path, key, width=55):
        v = tk.StringVar()
        self.vars[path] = v
        self.row(parent, r, label, key, ttk.Entry(parent, textvariable=v, width=width))

    def boolean(self, parent, r, label, path, key):
        v = tk.BooleanVar()
        self.vars[path] = v
        self.row(parent, r, label, key, ttk.Checkbutton(parent, variable=v))

    def combo(self, parent, r, label, path, key, values):
        v = tk.StringVar()
        self.vars[path] = v
        w = ttk.Combobox(parent, textvariable=v, values=values, state="readonly", width=28)
        self.row(parent, r, label, key, w)
        return w

    def build(self):
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="RA3 Crystallography Configuration",
                  font=("Segoe UI",16,"bold")).pack(anchor="w", pady=(0,10))
        nb = ttk.Notebook(outer); nb.pack(fill="both", expand=True)

        tabs = {}
        for name in ["Project","Search","RODHYPIX","INS","Unit Cell","CAP",
                     "CCDC","Gemmi","Clustering","Output","Debug"]:
            f = ttk.Frame(nb, padding=14); nb.add(f, text=name); tabs[name] = f

        self.project(tabs["Project"]); self.search(tabs["Search"])
        self.rod(tabs["RODHYPIX"]); self.ins(tabs["INS"])
        self.cell(tabs["Unit Cell"]); self.cap(tabs["CAP"])
        self.ccdc(tabs["CCDC"]); self.gemmi(tabs["Gemmi"])
        self.cluster(tabs["Clustering"]); self.output(tabs["Output"])
        self.debug(tabs["Debug"])

        bottom = ttk.Frame(outer); bottom.pack(fill="x", pady=(10,0))
        ttk.Button(bottom,text="Restore Defaults",command=self.restore).pack(side="left")
        ttk.Button(bottom,text="Revert Changes",command=self.revert).pack(side="left",padx=8)
        ttk.Button(bottom,text="Open HTML",command=lambda:self.open_latest(".html")).pack(side="left",padx=(12,0))
        ttk.Button(bottom,text="Open Excel",command=lambda:self.open_latest(".xlsx")).pack(side="left",padx=8)
        ttk.Button(bottom,text="Cancel",command=self.destroy).pack(side="right")
        ttk.Button(bottom,text="Save",command=self.save).pack(side="right",padx=8)
        ttk.Button(bottom,text="Save & Run",command=self.save_run).pack(side="right")

    def project(self,f):
        f.columnconfigure(1,weight=1)
        self.entry(f,0,"Project name","project.name","project")
        ttk.Label(f,text="Root directories").grid(row=1,column=0,sticky="nw",pady=5)
        box=ttk.Frame(f); box.grid(row=1,column=1,sticky="ew")
        self.root_list=tk.Listbox(box,height=10); self.root_list.pack(side="left",fill="both",expand=True)
        c=ttk.Frame(box); c.pack(side="left",padx=8,anchor="n")
        ttk.Button(c,text="Add",command=self.add_root).pack(fill="x")
        ttk.Button(c,text="Remove",command=self.remove_root).pack(fill="x",pady=5)
        b=ttk.Button(f,text="?",width=3,command=lambda:self.help("roots")); b.grid(row=1,column=2,sticky="ne"); Tip(b,HELP["roots"])

    def search(self,f):
        f.columnconfigure(1,weight=1)
        self.entry(f,0,"Search string","search.search_string","search")
        self.boolean(f,1,"Case sensitive","search.case_sensitive","case")
        w=self.combo(f,2,"Search recursion depth","search.recursion_depth","depth",OPTIONS["depth"])
        w.bind("<<ComboboxSelected>>",lambda _:self.depth_state())
        self.custom_entry=ttk.Entry(f,textvariable=self.custom_depth,width=12)
        self.row(f,3,"Custom depth","depth",self.custom_entry)
        self.combo(f,4,"Maximum datasets","search.max_folders","max",OPTIONS["max_folders"])

    def rod(self,f):
        f.columnconfigure(1,weight=1)
        self.entry(f,0,"Folder name","rodhypix.folder_name","rod")
        self.entry(f,1,"File extension","rodhypix.extension","rod")
        self.boolean(f,2,"Recursive search","rodhypix.recursive","rod")
        self.boolean(f,3,"First matching file only","rodhypix.first_only","rod")

    def ins(self,f):
        f.columnconfigure(1,weight=1)
        self.entry(f,0,"Structure folder","ins.struct_folder","ins")
        self.entry(f,1,"Olex2 prefix","ins.olex_prefix","ins")
        self.entry(f,2,"Auto suffix","ins.auto_suffix","ins")
        self.entry(f,3,"File extension","ins.extension","ins")
        self.boolean(f,4,"Recursive search","ins.recursive","ins")
        self.boolean(f,5,"First matching file only","ins.first_only","ins")

    def cell(self,f):
        self.boolean(f,0,"Ignore CELL wavelength","unit_cell.ignore_wavelength","cell")

    def cap(self,f):
        f.columnconfigure(1,weight=1)
        self.boolean(f,0,"CAP enabled","cap.enabled","cap")
        self.boolean(f,1,"Peak finding","cap.peak_finding","cap")
        self.boolean(f,2,"Multicrystal indexing","cap.multicrystal_indexing","cap")
        self.boolean(f,3,"Unit-cell refinement","cap.unit_cell_refinement","cap")
        self.combo(f,4,"Indexing command","cap.indexing_command","indexing",OPTIONS["indexing"])
        self.entry(f,5,"Peak-hunting command","cap.smart_peak_hunting_command","cap",75)
        ttk.Label(f,text=".par prefix preference").grid(row=6,column=0,sticky="nw",pady=5)
        box=ttk.Frame(f); box.grid(row=6,column=1,sticky="ew")
        self.par_list=tk.Listbox(box,height=5); self.par_list.pack(side="left",fill="x",expand=True)
        c=ttk.Frame(box); c.pack(side="left",padx=8)
        ttk.Button(c,text="↑",width=3,command=self.par_up).pack()
        ttk.Button(c,text="↓",width=3,command=self.par_down).pack(pady=5)
        b=ttk.Button(f,text="?",width=3,command=lambda:self.help("par")); b.grid(row=6,column=2,sticky="ne"); Tip(b,HELP["par"])

    def ccdc(self,f):
        f.columnconfigure(1,weight=1)
        self.boolean(f,0,"CCDC enabled","ccdc.enabled","ccdc")
        self.combo(f,1,"Search mode","ccdc.search_mode","ccdc",OPTIONS["ccdc"])

    def gemmi(self,f):
        f.columnconfigure(1,weight=1)
        self.boolean(f,0,"Gemmi enabled","gemmi.enabled","gemmi")
        self.combo(f,1,"Reduction method","gemmi.reduction_method","gemmi",OPTIONS["gemmi"])

    def cluster(self,f):
        f.columnconfigure(1,weight=1)
        self.entry(f,0,"Length tolerance (Å)","clustering.length_tolerance","cluster",15)
        self.entry(f,1,"Angle tolerance (°)","clustering.angle_tolerance","cluster",15)
        self.combo(f,2,"Unit-cell source","clustering.unit_cell_source","cluster",OPTIONS["unit_cell_source"])
        self.combo(f,3,"Clustering method","clustering.method","cluster",OPTIONS["clustering"])

    def output(self,f):
        f.columnconfigure(1,weight=1)
        self.entry(f,0,"Output directory","output.output_dir","output")
        self.entry(f,1,"Output prefix","output.output_prefix","output")
        self.boolean(f,2,"Add timestamp","output.add_timestamp_to_filename","output")
        self.entry(f,3,"Timestamp format","output.timestamp_format","output")
        self.combo(f,4,"Size unit","size.unit","output",OPTIONS["size"])
        ttk.Separator(f).grid(row=5,column=0,columnspan=3,sticky="ew",pady=12)
        self.entry(f,6,"Excel sheet name","excel.sheet_name","output")
        self.entry(f,7,"Excel date format","excel.date_format","output")
        self.entry(f,8,"Excel size format","excel.size_format","output")
        self.entry(f,9,"Excel cell format","excel.cell_format","output")
        self.entry(f,10,"Excel freeze panes","excel.freeze_panes","output")

    def debug(self,f):
        names=["enabled","search","rodhypix","ins","cell","size","cap","ccdc","gemmi","phase"]
        for r,n in enumerate(names):
            self.boolean(f,r,"Debug "+n.title(),"debug."+n,"debug")

    def get(self,data,path):
        for p in path.split("."): data=data[p]
        return data
    def put(self,data,path,value):
        parts=path.split(".")
        for p in parts[:-1]: data=data[p]
        data[parts[-1]]=value

    def load_widgets(self):
        for path,var in self.vars.items():
            value=self.get(self.data,path)
            var.set(bool(value) if isinstance(var,tk.BooleanVar) else str(value))
        depth=self.data["search"]["recursion_depth"]
        self.vars["search.recursion_depth"].set("Unlimited" if depth is None else str(depth) if depth in (0,1,2,3) else "Custom")
        self.custom_depth.set("" if depth is None else str(depth))
        m=self.data["search"]["max_folders"]
        self.vars["search.max_folders"].set("All" if m is None else str(m))
        self.root_list.delete(0,tk.END)
        for p in self.data["search"]["root_dirs"]: self.root_list.insert(tk.END,p)
        self.par_prefixes=list(self.data["cap"]["par_prefix_preference"])
        self.refresh_par(); self.depth_state()

    def read_widgets(self):
        d=copy.deepcopy(self.data)
        for path,var in self.vars.items():
            value=var.get()
            if isinstance(var,tk.BooleanVar): value=bool(value)
            self.put(d,path,value)
        depth=self.vars["search.recursion_depth"].get()
        if depth=="Unlimited": d["search"]["recursion_depth"]=None
        elif depth=="Custom":
            try: n=int(self.custom_depth.get())
            except ValueError: raise ValueError("Custom search depth must be a non-negative integer.")
            if n<0: raise ValueError("Custom search depth must be a non-negative integer.")
            d["search"]["recursion_depth"]=n
        else: d["search"]["recursion_depth"]=int(depth)
        m=self.vars["search.max_folders"].get()
        d["search"]["max_folders"]=None if m=="All" else int(m)
        try:
            d["clustering"]["length_tolerance"]=float(self.vars["clustering.length_tolerance"].get())
            d["clustering"]["angle_tolerance"]=float(self.vars["clustering.angle_tolerance"].get())
        except ValueError: raise ValueError("Clustering tolerances must be numbers.")
        d["search"]["root_dirs"]=list(self.root_list.get(0,tk.END))
        d["cap"]["par_prefix_preference"]=list(self.par_prefixes)
        return d

    def depth_state(self):
        self.custom_entry.configure(state="normal" if self.vars["search.recursion_depth"].get()=="Custom" else "disabled")
    def refresh_par(self):
        self.par_list.delete(0,tk.END)
        for p in self.par_prefixes: self.par_list.insert(tk.END,p if p else "(original)")
    def par_up(self):
        q=self.par_list.curselection()
        if not q or q[0]==0:return
        i=q[0]; self.par_prefixes[i-1],self.par_prefixes[i]=self.par_prefixes[i],self.par_prefixes[i-1]
        self.refresh_par(); self.par_list.selection_set(i-1)
    def par_down(self):
        q=self.par_list.curselection()
        if not q or q[0]>=len(self.par_prefixes)-1:return
        i=q[0]; self.par_prefixes[i+1],self.par_prefixes[i]=self.par_prefixes[i],self.par_prefixes[i+1]
        self.refresh_par(); self.par_list.selection_set(i+1)

    def add_root(self):
        d=tk.Toplevel(self); d.title("Add root directory"); d.transient(self); d.grab_set()
        v=tk.StringVar()
        ttk.Label(d,text="Directory").pack(padx=12,pady=(12,4),anchor="w")
        ttk.Entry(d,textvariable=v,width=65).pack(padx=12,pady=4)
        b=ttk.Frame(d); b.pack(fill="x",padx=12,pady=12)
        ttk.Button(b,text="Cancel",command=d.destroy).pack(side="right")
        def add():
            if v.get().strip(): self.root_list.insert(tk.END,v.get().strip())
            d.destroy()
        ttk.Button(b,text="Add",command=add).pack(side="right",padx=8)
    def remove_root(self):
        q=self.root_list.curselection()
        if q:self.root_list.delete(q[0])

    def help(self,key): messagebox.showinfo(key,HELP.get(key,"No help available."),parent=self)
    def restore(self):
        if messagebox.askyesno("Restore Defaults","Restore defaults? Changes are not saved until Save.",parent=self):
            self.data=copy.deepcopy(self.defaults); self.load_widgets()
    def revert(self):
        self.data=copy.deepcopy(self.saved); self.load_widgets()

    def open_latest(self,ext):
        folder=Path(self.vars["output.output_dir"].get()).expanduser()
        if not folder.exists():
            messagebox.showerror("Directory not found",str(folder),parent=self); return
        files=[p for p in folder.iterdir() if p.is_file() and p.suffix.lower()==ext]
        if not files:
            messagebox.showinfo("Not found",f"No {ext} files found in:\n{folder}",parent=self); return
        os.startfile(str(max(files,key=lambda p:p.stat().st_mtime)))

    def save(self):
        try:
            self.data=self.read_widgets(); save(self.data); generate()
            self.saved=copy.deepcopy(self.data)
            messagebox.showinfo("Saved","config.json saved and config.py regenerated.",parent=self)
        except Exception as e:
            messagebox.showerror("Save failed",str(e),parent=self)

    def save_run(self):
        try:
            self.data=self.read_widgets(); save(self.data); generate()
        except Exception as e:
            messagebox.showerror("Save failed",str(e),parent=self); return
        if not MAIN.exists():
            messagebox.showerror("main.py not found",str(MAIN),parent=self); return
        subprocess.Popen([sys.executable,str(MAIN)],cwd=str(BASE_DIR))

if __name__=="__main__":
    App().mainloop()
