import os
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SinaNewsFetcher:
    def __init__(self, driver, folder_name):
        self.driver = driver
        self.folder_name = folder_name

    def fetch_realtime_news(self, max_pages=5):
        # 设置保存实时新闻的 CSV 文件路径
        realtime_csv_path = os.path.join(self.folder_name, "sina_realTimeNews.csv")
        with open(realtime_csv_path, mode="w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["标题", "链接", "时间"])

            print("开始抓取实时新闻：")
            all_news = []
            try:
                for page in range(1, max_pages + 1):
                    url = f"https://news.sina.com.cn/roll/#pageid=153&lid=2509&k=&num=50&page={page}"
                    print(f"抓取第 {page} 页: {url}")
                    self.driver.get(url)
                    self.driver.refresh()

                    # 等待页面加载完成
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#d_list ul li"))
                    )

                    news_items = self.driver.find_elements(By.CSS_SELECTOR, "#d_list ul li")

                    for item in news_items:
                        try:
                            # 获取新闻标题、链接和时间
                            title_element = item.find_element(By.CSS_SELECTOR, ".c_tit a")
                            title = title_element.text.strip()
                            link = title_element.get_attribute("href")
                            time_text = item.find_element(By.CSS_SELECTOR, ".c_time").text.strip()

                            if title and link:
                                news_str = f"实时新闻 - 标题: {title}, 时间: {time_text}, 链接: {link}"
                                print(news_str)
                                writer.writerow([title, link, time_text])
                                all_news.append(news_str)
                        except Exception as e:
                            print(f"解析实时新闻条目失败: {e}")
                            continue

                    # 随机等待一段时间以避免被反爬虫机制检测
                    time.sleep(random.uniform(2, 5))

                print(f"\n实时新闻抓取完成，结果已保存至 {realtime_csv_path}")
                return all_news
            except Exception as e:
                print("抓取实时新闻失败:", e)
                return []

    def fetch_trending_news(self):
        # 设置保存热门新闻的 CSV 文件路径
        trending_csv_path = os.path.join(self.folder_name, "sina_trendingNews.csv")
        with open(trending_csv_path, mode="w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["类别", "标题", "链接"])

            print("开始抓取热门排行新闻：")
            all_news = []
            try:
                url = "https://news.sina.com.cn/hotnews/"
                self.driver.get(url)

                # 等待页面加载完成
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".loopblk"))
                )

                news_blocks = self.driver.find_elements(By.CSS_SELECTOR, ".loopblk")

                for block in news_blocks:
                    try:
                        # 获取新闻类别
                        category_name = block.find_element(By.CSS_SELECTOR, ".lbti h2").text.strip()
                        if not category_name:
                            continue

                        print(f"\n类别: {category_name}")
                        rows = block.find_elements(By.CSS_SELECTOR, "table tbody tr")

                        for row in rows:
                            try:
                                if row.find_elements(By.CSS_SELECTOR, "th"):
                                    continue

                                # 获取新闻标题和链接
                                title_element = row.find_element(By.CSS_SELECTOR, "td.ConsTi a")
                                title = title_element.text.strip()
                                url = title_element.get_attribute("href")

                                if title and url:
                                    news_str = f"热门新闻 - 类别: {category_name}, 标题: {title}, 链接: {url}"
                                    print(news_str)
                                    writer.writerow([category_name, title, url])
                                    all_news.append(news_str)
                            except Exception as e:
                                print(f"解析热门新闻条目失败: {e}")
                                continue
                    except Exception as e:
                        print(f"解析类别失败: {e}")

                print(f"\n热门新闻抓取完成，结果已保存至 {trending_csv_path}")
                return all_news
            except Exception as e:
                print("抓取热门新闻失败:", e)
                return []