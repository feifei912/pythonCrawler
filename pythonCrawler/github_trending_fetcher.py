import requests
from bs4 import BeautifulSoup
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"
]

TRENDING_URLS = {
    "daily": "https://github.com/trending",
    "weekly": "https://github.com/trending?since=weekly",
    "monthly": "https://github.com/trending?since=monthly"
}

class GitHubTrendingFetcher:
    def __init__(self):
        self.user_agents = USER_AGENTS

    def get_github_trending(self, url):
        try:
            # 设置请求头，随机选择一个 User-Agent
            headers = {
                "User-Agent": random.choice(self.user_agents)
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取热门项目列表，限制为前 10 个
            projects = soup.find_all('article', class_='Box-row', limit=10)
            all_projects = []

            if not projects:
                print("未能找到项目列表，请检查页面结构或反爬措施。")
                return []

            print("GitHub 热门前十项目：")
            for index, project in enumerate(projects, start=1):
                # 获取项目名称和链接
                name_tag = project.find('h2', class_='h3 lh-condensed')
                project_name = name_tag.text.strip().replace("\n", " ").replace(" ", "") if name_tag else "未知"
                link = "https://github.com" + name_tag.a['href'] if name_tag and name_tag.a else "无链接"

                # 获取项目星标数和最近增加的星标数
                stars_tag = project.find('a', class_='Link Link--muted d-inline-block mr-3')
                total_stars = int(stars_tag.text.strip().replace(',', '')) if stars_tag else 0
                stars_recently = project.find('span', class_='d-inline-block float-sm-right').text.strip()

                # 处理不同时间范围的星标数据
                if "stars today" in stars_recently:
                    stars_recently = int(stars_recently.replace(' stars today', '').replace(',', ''))
                    stars_description = "今日新增星标数"
                elif "stars this week" in stars_recently:
                    stars_recently = int(stars_recently.replace(' stars this week', '').replace(',', ''))
                    stars_description = "本周新增星标数"
                elif "stars this month" in stars_recently:
                    stars_recently = int(stars_recently.replace(' stars this month', '').replace(',', ''))
                    stars_description = "本月新增星标数"
                else:
                    stars_recently = 0
                    stars_description = "新增星标数"

                project_str = f"{index}. 项目：{project_name}；\n总星标数：{total_stars}；\n{stars_description}：{stars_recently}\n跳转：{link}\n"
                print(project_str)
                all_projects.append({
                    "项目名称": project_name,
                    "总星标数": total_stars,
                    "新增星标数": stars_recently,
                    "项目链接": link
                })

            # 随机等待一段时间以避免被反爬虫机制检测
            time.sleep(random.uniform(1, 3))
            return all_projects

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return []
        except Exception as e:
            print(f"发生错误: {e}")
            return []

