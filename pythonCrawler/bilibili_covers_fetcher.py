# b i l i b i l i_covers_fetcher.py

import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from PIL import Image
from io import BytesIO

class BilibiliCoversFetcher:
    def __init__(self, driver, save_folder):
        self.driver = driver
        self.save_folder = save_folder

    @staticmethod
    def sanitize_filename(filename):
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename.replace('\u3000', ' ').strip()

    @staticmethod
    def clean_image_url(url):
        if url.startswith("//"):
            url = "https:" + url
        if '@' in url:
            url = url.split('@')[0]
        return url

    def download_bilibili_covers(self, url):
        # 打开指定的 URL
        self.driver.get(url)
        time.sleep(5)

        # 提取日期信息
        try:
            date_info_element = self.driver.find_element(By.CSS_SELECTOR, '.date-info .current-tiem')
            date_info = date_info_element.text.strip()
        except:
            date_info = '未知日期'

        update_info = f'每周必看视频 --{date_info}' if 'weekly' in url else '入站必刷视频'
        print(f"\nBilibili {update_info}：\n")

        videos = self.driver.find_elements(By.CSS_SELECTOR, '.video-card')
        all_videos = []

        for video in videos[:30]:
            try:
                title_element = video.find_element(By.CSS_SELECTOR, '.video-name')
                title = title_element.get_attribute('title')

                up_name_element = video.find_element(By.CSS_SELECTOR, '.up-name__text')
                up_name = up_name_element.get_attribute('title')

                # 新增：获取播放量
                play_count_element = video.find_element(By.CSS_SELECTOR, '.play-text')
                play_count = play_count_element.text.strip()

                cover_url_element = video.find_element(By.CSS_SELECTOR, '.cover-picture__image')
                cover_url = cover_url_element.get_attribute('data-src') or cover_url_element.get_attribute('src')
                cover_url = self.clean_image_url(cover_url)

                safe_title = self.sanitize_filename(title)
                video_str = f"视频标题：{title} - UP名称：{up_name} - 播放量：{play_count}"
                print(video_str)
                all_videos.append(video_str)

                # 下载封面图片
                response = requests.get(cover_url, stream=True)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    if image.mode == 'RGBA':
                        image = image.convert('RGB')

                    parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    save_path = os.path.join(parent_folder, 'BilibiliCovers')
                    os.makedirs(save_path, exist_ok=True)
                    image_path = os.path.join(save_path, f"{safe_title}.jpg")
                    image.save(image_path)
                else:
                    print(f"下载失败，状态码: {response.status_code}, URL: {cover_url}")

            except Exception as e:
                print(f"处理视频错误: {e}")

        return all_videos