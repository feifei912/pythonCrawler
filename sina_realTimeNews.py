from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import random

def fetch_news_with_categories(max_pages=5):
    # 配置无头浏览器
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # 替换为实际 ChromeDriver 路径
    service = Service('C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 创建 CSV 文件存储结果
    with open("sina_realTimeNews.csv", mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["类别", "标题", "链接", "时间"])

        print("开始抓取新闻：")
        try:
            for page in range(1, max_pages + 1):
                url = f"https://news.sina.com.cn/roll/#pageid=153&lid=2509&k=&num=50&page={page}"
                print(f"抓取第 {page} 页: {url}")
                driver.get(url)

                # 强制刷新页面以避免缓存问题
                driver.refresh()

                # 等待主要内容加载完成
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#d_list ul li"))
                )

                # 找到所有新闻条目
                news_items = driver.find_elements(By.CSS_SELECTOR, "#d_list ul li")

                for item in news_items:
                    try:
                        # 提取新闻标题
                        title_element = item.find_element(By.CSS_SELECTOR, ".c_tit a")
                        title = title_element.text.strip()
                        # 提取链接
                        link = title_element.get_attribute("href")
                        # 提取时间
                        time_text = item.find_element(By.CSS_SELECTOR, ".c_time").text.strip()

                        if title and link:
                            print(f"标题: {title},\n时间: {time_text},\n链接: {link}\n")
                            writer.writerow([title, link, time_text])
                    except Exception as e:
                        print(f"解析新闻条目失败: {e}")
                        continue  # 忽略异常行

                # 等待一段时间，避免过于频繁的请求
                time.sleep(random.uniform(2, 5))

        except Exception as e:
            print("解析页面失败:", e)
        finally:
            # 关闭浏览器
            driver.quit()

if __name__ == "__main__":
    fetch_news_with_categories(max_pages=5)  # 抓取前 5 页
