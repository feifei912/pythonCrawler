import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sina_news_fetcher import SinaNewsFetcher
from github_trending_fetcher import GitHubTrendingFetcher, TRENDING_URLS
from bilibili_covers_fetcher import BilibiliCoversFetcher

def setup_chrome_driver():
    """设置 Chrome WebDriver 选项。"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=chrome_options)

def fetch_sina_news(driver, parent_directory, choice):
    """根据用户选择抓取新浪新闻。"""
    folder_name = os.path.join(parent_directory, 'News')
    os.makedirs(folder_name, exist_ok=True)
    sina_fetcher = SinaNewsFetcher(driver, folder_name)

    if choice == '1':
        pages = int(input("请输入要抓取的实时新闻页数（默认5页）：") or 5)
        sina_fetcher.fetch_realtime_news(max_pages=pages)
    elif choice == '2':
        sina_fetcher.fetch_trending_news()

def fetch_github_trending(github_fetcher):
    """根据用户选择抓取 GitHub 热门项目。"""
    print("请选择爬取的时间范围：")
    print("1. 周热门")
    print("2. 月热门")
    print("3. 全年热门")
    sub_choice = input("请输入选项（1/2/3）：").strip()
    if sub_choice == "1":
        github_fetcher.get_github_trending(TRENDING_URLS["weekly"])
    elif sub_choice == "2":
        github_fetcher.get_github_trending(TRENDING_URLS["monthly"])
    elif sub_choice == "3":
        github_fetcher.get_github_trending(TRENDING_URLS["yearly"])
    else:
        print("输入无效，请输入 1、2 或 3。")

def fetch_bilibili_covers(driver):
    """根据用户选择抓取 Bilibili 封面。"""
    bilibili_fetcher = BilibiliCoversFetcher(driver, 'BilibiliCovers')
    print("请输入爬取页面的选项（1 - 入站必刷视频，2 - 每周必看视频，3 - 入站必刷视频以及每周必看视频）：")
    sub_choice = input().strip()

    if sub_choice == '1':
        bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/history")
    elif sub_choice == '2':
        bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/weekly")
    elif sub_choice == '3':
        bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/history")
        bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/weekly")
    else:
        print("无效选项，程序结束。")

def main():
    driver = setup_chrome_driver()
    try:
        current_script_path = os.path.abspath(__file__)
        parent_directory = os.path.dirname(os.path.dirname(current_script_path))
        github_fetcher = GitHubTrendingFetcher()

        while True:
            print("\n请选择要抓取的功能：")
            print("1. 新浪实时新闻")
            print("2. 新浪热门排行新闻")
            print("3. GitHub 热门项目")
            print("4. Bilibili 视频封面")
            print("0. 退出")

            choice = input("请输入数字选择：").strip()

            if choice == '1' or choice == '2':
                fetch_sina_news(driver, parent_directory, choice)
            elif choice == '3':
                fetch_github_trending(github_fetcher)
            elif choice == '4':
                fetch_bilibili_covers(driver)
            elif choice == '0':
                print("程序已退出。")
                break
            else:
                print("无效的选择，请重新输入。")

    except Exception as e:
        print(f"新闻抓取过程中发生错误: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()