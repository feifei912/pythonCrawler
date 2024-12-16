import tkinter as tk
from tkinter import scrolledtext
import os
import threading
import queue
import io
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sina_news_fetcher import SinaNewsFetcher
from github_trending_fetcher import GitHubTrendingFetcher, TRENDING_URLS
from bilibili_covers_fetcher import BilibiliCoversFetcher

# 强制设置标准输出和错误输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

class ScraperGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("pythonCrawler")
        self.root.geometry("800x600")

        # 标题
        self.label = tk.Label(root, text="爬虫脚本运行工具", font=("SimHei", 18, "bold"))
        self.label.pack(pady=10)

        # 功能选择框
        self.option_frame = tk.Frame(root)
        self.option_frame.pack(pady=10)

        self.option_label = tk.Label(self.option_frame, text="选择爬虫功能:")
        self.option_label.pack(side=tk.LEFT, padx=5)

        self.option_var = tk.StringVar(value="1")
        self.option_menu = tk.OptionMenu(self.option_frame, self.option_var, "1. 新浪实时新闻", "2. 新浪热门排行新闻", "3. GitHub 热门项目", "4. Bilibili 视频封面", command=self.update_options)
        self.option_menu.pack(side=tk.LEFT, padx=5)

        # GitHub 热门项目时间范围选择框
        self.github_option_frame = tk.Frame(root)
        self.github_option_label = tk.Label(self.github_option_frame, text="选择 GitHub 热门项目时间范围:")
        self.github_option_label.pack(side=tk.LEFT, padx=5)
        self.github_option_var = tk.StringVar(value="weekly")
        self.github_option_menu = tk.OptionMenu(self.github_option_frame, self.github_option_var, "weekly", "monthly", "yearly")
        self.github_option_menu.pack(side=tk.LEFT, padx=5)

        # Bilibili 视频类型选择框
        self.bilibili_option_frame = tk.Frame(root)
        self.bilibili_option_label = tk.Label(self.bilibili_option_frame, text="选择 Bilibili 视频类型:")
        self.bilibili_option_label.pack(side=tk.LEFT, padx=5)
        self.bilibili_option_var = tk.StringVar(value="history")
        self.bilibili_option_menu = tk.OptionMenu(self.bilibili_option_frame, self.bilibili_option_var, "history", "weekly")
        self.bilibili_option_menu.pack(side=tk.LEFT, padx=5)

        # 运行按钮
        self.run_button = tk.Button(root, text="运行爬虫", command=self.run_scraper, font=("seihei", 12, "bold"))
        self.run_button.pack(pady=10)

        # 输出框
        self.output_label = tk.Label(root, text="爬虫输出结果:")
        self.output_label.pack(pady=5)

        self.output_box = scrolledtext.ScrolledText(root, width=100, height=25, wrap=tk.WORD, font=("Consolas", 11))
        self.output_box.pack(pady=5)

        # 创建队列用于线程间通信
        self.queue = queue.Queue()

    def update_options(self, choice):
        if choice.startswith("3"):
            self.github_option_frame.pack(pady=10)
            self.bilibili_option_frame.pack_forget()
        elif choice.startswith("4"):
            self.bilibili_option_frame.pack(pady=10)
            self.github_option_frame.pack_forget()
        else:
            self.github_option_frame.pack_forget()
            self.bilibili_option_frame.pack_forget()

    def run_scraper(self):
        self.output_box.delete(1.0, tk.END)
        threading.Thread(target=self.execute_scraper).start()
        self.root.after(100, self.process_queue)

    def execute_scraper(self):
        option = self.option_var.get().split(".")[0]

        # 设置 Chrome 浏览器选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        # 初始化 Chrome 浏览器驱动
        driver = webdriver.Chrome(options=chrome_options)

        try:
            # 获取当前脚本路径和父目录路径
            current_script_path = os.path.abspath(__file__)
            parent_directory = os.path.dirname(os.path.dirname(current_script_path))

            if option == '1' or option == '2':
                # 创建保存新闻的文件夹
                folder_name = os.path.join(parent_directory, 'News')
                os.makedirs(folder_name, exist_ok=True)

                # 初始化 SinaNewsFetcher
                sina_fetcher = SinaNewsFetcher(driver, folder_name)

                if option == '1':
                    # 抓取新浪实时新闻
                    pages = 5  # 默认抓取5页
                    news = sina_fetcher.fetch_realtime_news(max_pages=pages)
                elif option == '2':
                    # 抓取新浪热门排行新闻
                    news = sina_fetcher.fetch_trending_news()

                for item in news:
                    self.queue.put(item)

            elif option == '3':
                # 抓取 GitHub 热门项目
                github_fetcher = GitHubTrendingFetcher()
                trending_url = TRENDING_URLS[self.github_option_var.get()]  # 根据选择的时间范围抓取
                projects = github_fetcher.get_github_trending(trending_url)

                for project in projects:
                    self.queue.put(project)

            elif option == '4':
                # 抓取 Bilibili 视频封面
                bilibili_fetcher = BilibiliCoversFetcher(driver, 'BilibiliCovers')
                bilibili_url = "https://www.bilibili.com/v/popular/" + self.bilibili_option_var.get()
                covers = bilibili_fetcher.download_bilibili_covers(bilibili_url)

                for cover in covers:
                    self.queue.put(cover)

        except Exception as e:
            self.queue.put(f"爬虫运行过程中发生错误: {e}")
        finally:
            if driver:
                driver.quit()

    def process_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                self.append_output(item)
        except queue.Empty:
            self.root.after(100, self.process_queue)

    def append_output(self, text):
        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()