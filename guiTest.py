import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import io
import sys

# 强制设置标准输出和错误输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("爬虫脚本运行工具")
        self.root.geometry("600x400")

        # 标题
        self.label = tk.Label(root, text="爬虫脚本运行工具", font=("Arial", 16))
        self.label.pack(pady=10)

        # 文件选择框
        self.file_frame = tk.Frame(root)
        self.file_frame.pack(pady=10)

        self.file_label = tk.Label(self.file_frame, text="选择爬虫脚本:")
        self.file_label.pack(side=tk.LEFT, padx=5)

        self.file_entry = tk.Entry(self.file_frame, width=40)
        self.file_entry.pack(side=tk.LEFT, padx=5)

        self.browse_button = tk.Button(
            self.file_frame, text="浏览", command=self.browse_file
        )
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # 运行按钮
        self.run_button = tk.Button(root, text="运行脚本", command=self.run_script)
        self.run_button.pack(pady=10)

        # 输出框
        self.output_label = tk.Label(root, text="爬虫输出结果:")
        self.output_label.pack(pady=5)

        self.output_box = scrolledtext.ScrolledText(root, width=70, height=15)
        self.output_box.pack(pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py")], title="选择爬虫脚本"
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def run_script(self):
        script_path = self.file_entry.get()
        if not os.path.isfile(script_path):
            messagebox.showerror("错误", "请选择有效的 Python 脚本文件")
            return

        try:
            # 清空输出框
            self.output_box.delete(1.0, tk.END)

            # 使用 subprocess 运行脚本，显式指定编码为 UTF-8
            result = subprocess.run(
                ["python", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",  # 确保输出为 UTF-8 编码
            )

            # 显示结果
            if result.stdout:
                self.output_box.insert(tk.END, f"输出:\n{result.stdout}\n")
            if result.stderr:
                self.output_box.insert(tk.END, f"错误:\n{result.stderr}\n")
        except UnicodeDecodeError as e:
            messagebox.showerror("解码错误", f"解码失败: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"运行脚本时出错:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()
