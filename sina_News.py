import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random


def fetch_realtime_news(driver, max_pages=5, folder_name=None):
    """
    抓取实时新闻
    :param driver: Selenium WebDriver
    :param max_pages: 最大抓取页数
    :param folder_name: 保存文件的文件夹
    :return: 是否成功
    """
    realtime_csv_path = os.path.join(folder_name, "sina_realTimeNews.csv")
    with open(realtime_csv_path, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["标题", "链接", "时间"])

        print("开始抓取实时新闻：")
        try:
            for page in range(1, max_pages + 1):
                url = f"https://news.sina.com.cn/roll/#pageid=153&lid=2509&k=&num=50&page={page}"
                print(f"抓取第 {page} 页: {url}")
                driver.get(url)
                driver.refresh()

                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#d_list ul li"))
                )

                news_items = driver.find_elements(By.CSS_SELECTOR, "#d_list ul li")

                for item in news_items:
                    try:
                        title_element = item.find_element(By.CSS_SELECTOR, ".c_tit a")
                        title = title_element.text.strip()
                        link = title_element.get_attribute("href")
                        time_text = item.find_element(By.CSS_SELECTOR, ".c_time").text.strip()

                        if title and link:
                            print(f"实时新闻 - 标题: {title}, 时间: {time_text}, 链接: {link}")
                            writer.writerow([title, link, time_text])
                    except Exception as e:
                        print(f"解析实时新闻条目失败: {e}")
                        continue

                time.sleep(random.uniform(2, 5))

            print(f"\n实时新闻抓取完成，结果已保存至 {realtime_csv_path}")
            return True
        except Exception as e:
            print("抓取实时新闻失败:", e)
            return False


def fetch_trending_news(driver, folder_name=None):
    """
    抓取热门排行新闻
    :param driver: Selenium WebDriver
    :param folder_name: 保存文件的文件夹
    :return: 是否成功
    """
    trending_csv_path = os.path.join(folder_name, "sina_trendingNews.csv")
    with open(trending_csv_path, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["类别", "标题", "链接"])

        print("开始抓取热门排行新闻：")
        try:
            url = "https://news.sina.com.cn/hotnews/#1"
            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".loopblk"))
            )

            news_blocks = driver.find_elements(By.CSS_SELECTOR, ".loopblk")

            for block in news_blocks:
                try:
                    category_name = block.find_element(By.CSS_SELECTOR, ".lbti h2").text.strip()
                    if not category_name:
                        continue

                    print(f"\n类别: {category_name}")
                    rows = block.find_elements(By.CSS_SELECTOR, "table tbody tr")

                    for row in rows:
                        try:
                            if row.find_elements(By.CSS_SELECTOR, "th"):
                                continue

                            title_element = row.find_element(By.CSS_SELECTOR, "td.ConsTi a")
                            title = title_element.text.strip()
                            url = title_element.get_attribute("href")

                            if title and url:
                                print(f"热门新闻 - 类别: {category_name}, 标题: {title}, 链接: {url}")
                                writer.writerow([category_name, title, url])
                        except Exception as e:
                            print(f"解析热门新闻条目失败: {e}")
                            continue
                except Exception as e:
                    print(f"解析类别失败: {e}")

            print(f"\n热门新闻抓取完成，结果已保存至 {trending_csv_path}")
            return True
        except Exception as e:
            print("抓取热门新闻失败:", e)
            return False


def main():
    """
    主函数：用户交互式选择新闻抓取类型
    """
    # 配置无头浏览器
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # 创建浏览器实例
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 获取当前脚本的绝对路径，然后向上一级目录
        current_script_path = os.path.abspath(__file__)
        parent_directory = os.path.dirname(os.path.dirname(current_script_path))

        # 在父目录中创建 News 文件夹
        folder_name = os.path.join(parent_directory, 'News')
        os.makedirs(folder_name, exist_ok=True)
        print(f"文件夹 '{folder_name}' 已创建。")

        # 用户选择
        while True:
            print("\n请选择要抓取的新闻类型：")
            print("1. 实时新闻")
            print("2. 热门排行新闻")
            print("3. 全部新闻")
            print("0. 退出")

            choice = input("请输入数字选择：").strip()

            if choice == '1':
                pages = int(input("请输入要抓取的实时新闻页数（默认5页）：") or 5)
                fetch_realtime_news(driver, max_pages=pages, folder_name=folder_name)
            elif choice == '2':
                fetch_trending_news(driver, folder_name=folder_name)
            elif choice == '3':
                pages = int(input("请输入要抓取的实时新闻页数（默认5页）：") or 5)
                fetch_realtime_news(driver, max_pages=pages, folder_name=folder_name)
                fetch_trending_news(driver, folder_name=folder_name)
            elif choice == '0':
                print("程序已退出。")
                break
            else:
                print("无效的选择，请重新输入。")

    except Exception as e:
        print(f"新闻抓取过程中发生错误: {e}")
    finally:
        # 关闭浏览器
        driver.quit()


if __name__ == "__main__":
    main()