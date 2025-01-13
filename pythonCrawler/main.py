import os
import re
import matplotlib
import mplcursors
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sina_news_fetcher import SinaNewsFetcher
from github_trending_fetcher import GitHubTrendingFetcher, TRENDING_URLS
from bilibili_covers_fetcher import BilibiliCoversFetcher

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
# 用来正常显示负号
matplotlib.rcParams['axes.unicode_minus'] = False

def setup_chrome_driver():
    """设置 Chrome WebDriver 选项。"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=chrome_options)

def clean_title(title):
    """清理标题中的特殊字符"""
    # 移除表情符号和特殊字符
    cleaned = re.sub(r'[\U00010000-\U0010ffff]', '', title)
    cleaned = re.sub(r'[^\u4e00-\u9fff\u3000-\u303f\x00-\xff]', '', cleaned)
    # 如果标题太长，截取前20个字符
    if len(cleaned) > 20:
        cleaned = cleaned[:20] + '...'
    return cleaned

def format_number(num):
    """格式化数字显示"""
    if num >= 100000000:  # 亿
        return f'{num / 100000000:.1f}亿'
    elif num >= 10000:  # 万
        return f'{num / 10000:.0f}万'
    return f'{num:.0f}'

def visualize_bilibili_play_counts(video_data):
    #使用 Matplotlib 绘制播放量柱状图
    titles = []
    counts = []

    for item in video_data:
        # 清理并缩短标题
        titles.append(clean_title(item['title']))

        # 处理播放量
        play_count = item['play_count']
        if '亿' in play_count:
            count = float(play_count.replace('亿', '')) * 100000000
        elif '万' in play_count:
            count = float(play_count.replace('万', '')) * 10000
        else:
            count = float(''.join(filter(str.isdigit, play_count)))
        counts.append(count)

    if not counts:
        print("没有可视化的数据。")
        return

    plt.figure(figsize=(15, 8))
    bars = plt.bar(range(len(counts)), counts, color='#3399ff', alpha=0.7)

    # 设置x轴标签
    plt.xticks(range(len(titles)), titles, rotation=45, ha='right', fontsize=8)

    # 设置标题和轴标签
    plt.xlabel('视频标题', fontsize=10)
    plt.ylabel('播放量', fontsize=10)
    plt.title('Bilibili 视频播放量统计', fontsize=12)

    # 为每个柱子添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height,
                 format_number(height),
                 ha='center', va='bottom', rotation=0)

    # 格式化y轴刻度
    def format_func(x, p):
        return format_number(x)

    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_func))

    # 调整布局
    plt.tight_layout()
    plt.show()

def visualize_star_data(star_data):
    """使用 Matplotlib 绘制星标数柱状图"""
    project_names = [item['项目名称'] for item in star_data]
    total_stars = [item['总星标数'] for item in star_data]
    stars_recently = [item['新增星标数'] for item in star_data]

    if not total_stars:
        print("没有可视化的数据。")
        return

    plt.figure(figsize=(15, 8))
    x = range(len(total_stars))
    width = 0.35
    bars1 = plt.bar(x, total_stars, width, color='#3399ff', alpha=0.7, label='总星标数')
    bars2 = plt.bar(x, stars_recently, width, bottom=total_stars, color='#ff9999', alpha=0.7, label='新增星标数')

    # 设置x轴标签
    plt.xticks(range(len(project_names)), project_names, rotation=45, ha='right', fontsize=8)

    # 设置标题和轴标签
    plt.xlabel('项目名称', fontsize=10)
    plt.ylabel('星标数', fontsize=10)
    plt.title('GitHub 项目星标统计', fontsize=12)

    # 为每个柱子添加总星标数的数值标签
    for bar1 in bars1:
        height1 = bar1.get_height()
        plt.text(bar1.get_x() + bar1.get_width() / 2., height1,
                 format_number(height1),
                 ha='center', va='bottom', rotation=0)

    # 添加图例
    plt.legend(loc='upper left')

    # 调整y轴刻度
    def format_func(x, p):
        return format_number(x)

    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_func))

    # 调整布局
    plt.tight_layout()

    # 使用 mplcursors 添加交互式数据显示
    cursor = mplcursors.cursor(bars1, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        f"总星标数: {format_number(total_stars[sel.index])}\n"
        f"新增星标数: {format_number(stars_recently[sel.index])}"))

    plt.show()



def fetch_sina_news(driver, parent_directory, choice):
    """根据用户选择抓取新浪新闻。"""
    try:
        folder_name = os.path.join(parent_directory, 'News')
        os.makedirs(folder_name, exist_ok=True)
        sina_fetcher = SinaNewsFetcher(driver, folder_name)  # 确保只传递两个参数

        if choice == '1':
            pages = int(input("请输入要抓取的实时新闻页数（默认5页）：") or 5)
            print("开始抓取实时新闻，请稍候...")
            results = sina_fetcher.fetch_realtime_news(max_pages=pages)
            if results:
                print("\n抓取结果：")
                for result in results:
                    print(result)
            else:
                print("未获取到新闻数据")
        elif choice == '2':
            print("开始抓取热门新闻，请稍候...")
            results = sina_fetcher.fetch_trending_news()
            if results:
                print("\n抓取结果：")
                for result in results:
                    print(result)
            else:
                print("未获取到新闻数据")
    except Exception as e:
        print(f"抓取新闻时发生错误: {e}")

def fetch_github_trending(github_fetcher):
    """根据用户选择抓取 GitHub 热门项目并可视化星标数据。"""
    print("请选择爬取的时间范围：")
    print("1. 今日热门")
    print("2. 周热门")
    print("3. 月热门")
    sub_choice = input("请输入选项（1/2/3）：").strip()
    if sub_choice == "1":
        star_data = github_fetcher.get_github_trending(TRENDING_URLS["daily"])
        visualize_star_data(star_data)
    elif sub_choice == "2":
        star_data = github_fetcher.get_github_trending(TRENDING_URLS["weekly"])
        visualize_star_data(star_data)
    elif sub_choice == "3":
        star_data = github_fetcher.get_github_trending(TRENDING_URLS["monthly"])
        visualize_star_data(star_data)
    else:
        print("输入无效，请输入 1、2 或 3。")

def fetch_bilibili_covers(driver):
    """根据用户选择抓取 Bilibili 封面。"""
    bilibili_fetcher = BilibiliCoversFetcher(driver, 'BilibiliCovers')
    print("请输入爬取页面的选项（1 - 入站必刷视频，2 - 每周必看视频，3 - 两种都获取）：")
    sub_choice = input().strip()

    video_data = []
    if sub_choice == '1':
        video_data = bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/history")
    elif sub_choice == '2':
        video_data = bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/weekly")
    elif sub_choice == '3':
        data1 = bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/history")
        data2 = bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/weekly")
        video_data = data1 + data2
    else:
        print("无效选项，程序结束。")
        return

    # 将下载到的视频信息打印
    for idx, item in enumerate(video_data):
        print(f"{idx+1}. {item['title']} | UP主：{item['up_name']} | 播放量：{item['play_count']}| BV ID：{item['bv_id']}")

    # 通过 Matplotlib 可视化
    visualize_bilibili_play_counts(video_data)

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
            print("3. GitHub 热门项目（包含星标数据可视化）")
            print("4. Bilibili 热播视频封面（可视化）")
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
