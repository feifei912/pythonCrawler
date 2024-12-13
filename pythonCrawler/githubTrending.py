import requests
from bs4 import BeautifulSoup
import random
import time

# 定义多个 User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"
]

# GitHub热门项目URL
TRENDING_URLS = {
    "weekly": "https://github.com/trending?since=weekly",
    "monthly": "https://github.com/trending?since=monthly",
    "yearly": "https://github.com/trending"
}

# 爬取 GitHub 热门前十项目
def get_github_trending(url):
    try:
        # 随机选择一个 User-Agent
        headers = {
            "User-Agent": random.choice(USER_AGENTS)
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到包含项目列表的区域
        projects = soup.find_all('article', class_='Box-row', limit=10)

        if not projects:
            print("未能找到项目列表，请检查页面结构或反爬措施。")
            return

        print("GitHub 热门前十项目：")
        for index, project in enumerate(projects, start=1):
            # 提取程序名称
            name_tag = project.find('h2', class_='h3 lh-condensed')
            project_name = name_tag.text.strip().replace("\n", " ").replace(" ", "") if name_tag else "未知"

            # 提取链接
            link = "https://github.com" + name_tag.a['href'] if name_tag and name_tag.a else "无链接"

            print(f"{index}. 程序：{project_name}；\n跳转：{link}\n")

        # 添加延迟，避免频繁爬取触发反爬
        time.sleep(random.uniform(1, 3))

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    print("请选择爬取的时间范围：")
    print("1. 周热门")
    print("2. 月热门")
    print("3. 全年热门")
    choice = input("请输入选项（1/2/3）：").strip()

    if choice == "1":
        get_github_trending(TRENDING_URLS["weekly"])
    elif choice == "2":
        get_github_trending(TRENDING_URLS["monthly"])
    elif choice == "3":
        get_github_trending(TRENDING_URLS["yearly"])
    else:
        print("输入无效，请输入 1、2 或 3。")
