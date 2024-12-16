from flask import Flask, render_template, jsonify
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sina_news_fetcher import SinaNewsFetcher
from github_trending_fetcher import GitHubTrendingFetcher, TRENDING_URLS
from bilibili_covers_fetcher import BilibiliCoversFetcher

app = Flask(__name__)

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_sina_news')
def fetch_sina_news():
    driver = initialize_driver()
    folder_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'News')
    os.makedirs(folder_name, exist_ok=True)
    sina_fetcher = SinaNewsFetcher(driver, folder_name)
    news = sina_fetcher.fetch_realtime_news(max_pages=5)
    driver.quit()
    return jsonify(news)

@app.route('/fetch_github_trending/<period>')
def fetch_github_trending(period):
    github_fetcher = GitHubTrendingFetcher()
    trending_url = TRENDING_URLS.get(period, TRENDING_URLS["weekly"])
    projects = github_fetcher.get_github_trending(trending_url)
    return jsonify(projects)

@app.route('/fetch_bilibili_covers/<video_type>')
def fetch_bilibili_covers(video_type):
    driver = initialize_driver()
    bilibili_fetcher = BilibiliCoversFetcher(driver, 'BilibiliCovers')
    bilibili_url = f"https://www.bilibili.com/v/popular/{video_type}"
    covers = bilibili_fetcher.download_bilibili_covers(bilibili_url)
    driver.quit()
    return jsonify(covers)

if __name__ == '__main__':
    app.run(debug=True)