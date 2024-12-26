from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sina_news_fetcher import SinaNewsFetcher
from github_trending_fetcher import GitHubTrendingFetcher, TRENDING_URLS
from bilibili_covers_fetcher import BilibiliCoversFetcher

app = Flask(__name__, template_folder='templates')

def run_sina_news_fetcher(option, pages=5):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    parent_directory = os.path.dirname(os.path.abspath(__file__))
    folder_name = os.path.join(parent_directory, 'News')
    os.makedirs(folder_name, exist_ok=True)

    sina_fetcher = SinaNewsFetcher(driver, folder_name)
    if option == 'realtime':
        result = sina_fetcher.fetch_realtime_news(max_pages=pages)
    elif option == 'trending':
        result = sina_fetcher.fetch_trending_news()
    else:
        result = []
    driver.quit()
    return result

def run_github_trending_fetcher(time_range):
    github_fetcher = GitHubTrendingFetcher()
    return github_fetcher.get_github_trending(TRENDING_URLS[time_range])

def run_bilibili_covers_fetcher(video_type):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    bilibili_fetcher = BilibiliCoversFetcher(driver, 'BilibiliCovers')

    if video_type == 'history':
        video_data = bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/history")
    elif video_type == 'weekly':
        video_data = bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/weekly")
    else:
        video_data = []

    driver.quit()
    return video_data

@app.route('/run_crawler', methods=['POST'])
def run_crawler():
    data = request.json
    crawler_type = data.get('crawler_type')
    option = data.get('option')
    pages = data.get('pages', 5)

    if crawler_type == 'sina':
        result = run_sina_news_fetcher(option, pages)
    elif crawler_type == 'github':
        result = run_github_trending_fetcher(option)
    elif crawler_type == 'bilibili':
        result = run_bilibili_covers_fetcher(option)
    else:
        return jsonify({'error': 'Invalid crawler type'})

    return jsonify(result)

# 提供 favicon 路由，避免 404 错误
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)