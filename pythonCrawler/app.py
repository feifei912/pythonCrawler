# app.py
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bilibili_covers_fetcher import BilibiliCoversFetcher
from github_trending_fetcher import GitHubTrendingFetcher, TRENDING_URLS
from sina_news_fetcher import SinaNewsFetcher

app = Flask(__name__)

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

@app.route('/scrape/github', methods=['GET'])
def scrape_github():
    time_range = request.args.get('time_range', 'weekly')
    github_fetcher = GitHubTrendingFetcher()
    projects = github_fetcher.get_github_trending(TRENDING_URLS[time_range])
    return jsonify(projects)

@app.route('/scrape/bilibili', methods=['GET'])
def scrape_bilibili():
    video_type = request.args.get('video_type', 'history')
    driver = create_driver()
    bilibili_fetcher = BilibiliCoversFetcher(driver, 'BilibiliCovers')
    url = f"https://www.bilibili.com/v/popular/{video_type}"
    covers = bilibili_fetcher.download_bilibili_covers(url)
    driver.quit()
    return jsonify(covers)

@app.route('/scrape/sina', methods=['GET'])
def scrape_sina():
    news_type = request.args.get('news_type', 'realtime')
    pages = int(request.args.get('pages', 5))
    driver = create_driver()
    folder_name = 'News'
    sina_fetcher = SinaNewsFetcher(driver, folder_name)
    if news_type == 'realtime':
        news = sina_fetcher.fetch_realtime_news(max_pages=pages)
    else:
        news = sina_fetcher.fetch_trending_news()
    driver.quit()
    return jsonify(news)

if __name__ == '__main__':
    app.run(debug=True)