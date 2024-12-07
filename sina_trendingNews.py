from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import csv

def fetch_news_with_categories():
    # 配置无头浏览器
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    # 从系统 PATH 中查找 ChromeDriver
    driver = webdriver.Chrome(options=chrome_options)

    # 打开页面
    url = "https://news.sina.com.cn/hotnews/#1"
    driver.get(url)

    folder_name = 'News'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"文件夹 '{folder_name}' 已创建。")

    csv_file_path = os.path.join(folder_name, "sina_trendingNews.csv")
    # 创建 CSV 文件存储结果
    with open(csv_file_path, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["类别", "标题", "链接"])  # CSV 文件的表头

        print("每日排行新闻：")
        try:
            # 等待主要内容加载完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".loopblk"))
            )

            # 找到所有新闻类别块
            news_blocks = driver.find_elements(By.CSS_SELECTOR, ".loopblk")

            for block in news_blocks:
                try:
                    # 提取类别名称
                    category_name = block.find_element(By.CSS_SELECTOR, ".lbti h2").text.strip()
                    if not category_name:
                        continue  # 跳过没有类别的块
                    print(f"\n类别: {category_name}")

                    # 提取该类别下的新闻表格行
                    rows = block.find_elements(By.CSS_SELECTOR, "table tbody tr")
                    for row in rows:
                        try:
                            # 忽略表头行
                            if row.find_elements(By.CSS_SELECTOR, "th"):
                                continue

                            # 获取新闻标题和链接
                            title_element = row.find_element(By.CSS_SELECTOR, "td.ConsTi a")
                            title = title_element.text.strip()
                            url = title_element.get_attribute("href")

                            if title and url:  # 确保标题和链接都存在
                                print(f"标题: {title}, \n链接: {url}")
                                writer.writerow([category_name, title, url])  # 格式化写入
                        except Exception as e:
                            print(f"解析新闻条目失败: {e}")
                            continue  # 忽略异常行
                except Exception as e:
                    print(f"解析类别失败: {e}")
        except Exception as e:
            print("解析页面失败:", e)
        finally:
            # 关闭浏览器
            driver.quit()

if __name__ == "__main__":
    fetch_news_with_categories()
