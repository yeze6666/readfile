import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import subprocess

# 自动获取脚本所在目录作为基础路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = SCRIPT_DIR.replace("\\", "/") + "/"  # 统一使用正斜杠

# 配置默认值
DEFAULT_INPUT_DIR = "./svg_1"
DEFAULT_OUTPUT_JS = "fileList.js"
DEFAULT_ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'}

class FileListGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("文件列表生成工具")
        master.geometry("800x600")

        # 变量初始化
        self.input_dir = tk.StringVar(value=DEFAULT_INPUT_DIR)
        self.output_js = tk.StringVar(value=DEFAULT_OUTPUT_JS)
        self.allowed_ext = tk.StringVar(value=", ".join(DEFAULT_ALLOWED_EXT))
        self.file_list = []

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 输入目录选择
        ttk.Label(self.master, text="输入目录:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        input_frame = ttk.Frame(self.master)
        input_frame.grid(row=0, column=1, columnspan=2, sticky="ew")
        
        ttk.Entry(input_frame, textvariable=self.input_dir, width=50).pack(side="left", fill="x", expand=True)
        ttk.Button(input_frame, text="浏览...", command=self.select_input_dir).pack(side="left", padx=5)

        # 输出设置
        ttk.Label(self.master, text="输出文件:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.master, textvariable=self.output_js, width=50).grid(row=1, column=1, sticky="w")

        # 允许的扩展名
        ttk.Label(self.master, text="允许的扩展名 (逗号分隔):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.master, textvariable=self.allowed_ext).grid(row=2, column=1, sticky="w")

        # 文件列表显示
        ttk.Label(self.master, text="找到的文件:").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        self.listbox = tk.Listbox(self.master, width=60, height=15)
        self.listbox.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")

        # 日志区域
        ttk.Label(self.master, text="操作日志:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.log_text = tk.Text(self.master, height=8, state="disabled")
        self.log_text.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")

        # 操作按钮
        btn_frame = ttk.Frame(self.master)
        btn_frame.grid(row=5, column=1, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="扫描文件", command=self.scan_files).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="生成文件列表", command=self.start_generation).pack(side="left", padx=5)

        # 配置网格布局权重
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(3, weight=1)
        self.master.rowconfigure(4, weight=1)

    def select_input_dir(self):
        directory = filedialog.askdirectory(initialdir=self.input_dir.get())
        if directory:
            self.input_dir.set(directory)
            self.scan_files()

    def scan_files(self):
        self.listbox.delete(0, tk.END)
        self.file_list = []
        input_dir = self.input_dir.get()
        
        if not os.path.isdir(input_dir):
            self.log("错误：目录不存在")
            return

        allowed_ext = {ext.strip().lower() for ext in self.allowed_ext.get().split(",")}
        
        try:
            for filename in os.listdir(input_dir):
                file_path = os.path.join(input_dir, filename)
                if os.path.isfile(file_path):
                    ext = filename.split('.')[-1].lower() if '.' in filename else ''
                    if ext in allowed_ext:
                        self.file_list.append(filename)
                        self.listbox.insert(tk.END, filename)
            self.log(f"找到 {len(self.file_list)} 个符合条件的文件")
        except Exception as e:
            self.log(f"扫描文件失败: {str(e)}")

    def start_generation(self):
        Thread(target=self.generate_file_list, daemon=True).start()

    def generate_file_list(self):
        try:
            self.log("开始生成文件列表...")
            
            if not self.file_list:
                self.log("错误：没有可用的文件")
                return

            # 使用固定的基础路径
            file_list = sorted(self.file_list)
            items = [f"'{BASE_PATH}{file}'" for file in file_list]
            js_content = f"export default [\n  {',\n  '.join(items)}\n];"

            # 写入文件
            with open(self.output_js.get(), 'w', encoding='utf-8') as f:
                f.write(js_content)

            self.log(f"成功生成 {len(file_list)} 个文件到 {self.output_js.get()}")
            messagebox.showinfo("成功", "文件列表生成完成！")
            
            # 自动打开生成的JS文件
            if os.name == 'nt':
                os.startfile(self.output_js.get())
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, self.output_js.get()])
                
        except Exception as e:
            self.log(f"生成失败: {str(e)}")
            messagebox.showerror("错误", str(e))

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileListGeneratorApp(root)
    root.mainloop()