from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from crawler_utils import chrome_options
from selenium import webdriver
from sina_news_fetcher import SinaNewsFetcher
from github_trending_fetcher import GitHubTrendingFetcher, TRENDING_URLS
from bilibili_covers_fetcher import BilibiliCoversFetcher
from bilidownload import BiliVideoDownloader

app = Flask(__name__, template_folder='templates')

def run_sina_news_fetcher(option, pages=5):

    driver = webdriver.Chrome(options=chrome_options())

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

    driver = webdriver.Chrome(options=chrome_options())

    bilibili_fetcher = BilibiliCoversFetcher(driver, 'BilibiliCovers')

    if video_type == 'history':
        video_data = bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/history")
    elif video_type == 'weekly':
        video_data = bilibili_fetcher.download_bilibili_covers("https://www.bilibili.com/v/popular/weekly")
    else:
        video_data = []

    driver.quit()
    return video_data

@app.route('/run_bili_download', methods=['POST'])
def run_bili_download():
    data = request.json
    bvid = data.get('bvid', '').strip()
    quality = data.get('quality', '80')
    sess_data = data.get('sessData', '')
    is_collection = data.get('isCollection', False)
    start_page = data.get('startPage', 1)
    end_page = data.get('endPage', 1)

    if not bvid:
        return jsonify({'message': 'BVID 为空，请检查输入'}), 400
    if not sess_data:
        return jsonify({'message': 'SESSDATA 为空，无法下载'}), 400

    downloader = BiliVideoDownloader()
    # 通过 Video 类或者直接设置 downloader 的 cookie
    # downloader.set_cookie(sess_data)  # 如果你在类里有类似的方法，请相应修改

    # 这里仅作示例，具体调用方式与你的 bilidownload.py 结构相关
    try:
        if is_collection:
            # 批量下载：从 start_page 到 end_page
            for page_idx in range(start_page, end_page + 1):
                downloader.download_video(bvid, directory='DownloadedVideos', quality=quality, pages=page_idx)
            message = f"合集下载完成：从第 {start_page} 集到第 {end_page} 集"
        else:
            # 单个下载
            downloader.download_video(bvid, directory='DownloadedVideos', quality=quality, pages=1)
            message = "单视频下载完成"
    except Exception as e:
        return jsonify({'message': f'下载出现错误: {e}'}), 500

    return jsonify({'message': message})

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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)