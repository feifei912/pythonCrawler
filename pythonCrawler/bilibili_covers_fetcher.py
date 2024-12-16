import os
import time
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
        # 清理文件名中的无效字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename.replace('\u3000', ' ').strip()

    @staticmethod
    def clean_image_url(url):
        # 清理图片 URL
        if url.startswith("//"):
            url = "https:" + url
        if '@' in url:
            url = url.split('@')[0]
        return url

    def download_bilibili_covers(self, url):
        # 打开指定的 URL
        self.driver.get(url)
        time.sleep(5)

        # 尝试获取日期信息
        try:
            date_info_element = self.driver.find_element(By.CSS_SELECTOR, '.date-info .current-tiem')
            date_info = date_info_element.text.strip()
        except:
            date_info = '未知日期'

        # 根据 URL 判断更新信息
        update_info = f'每周必看视频 --{date_info}' if 'weekly' in url else f'入站必刷视频'
        print(f"\nBilibili {update_info}：\n")

        # 获取所有视频元素
        videos = self.driver.find_elements(By.CSS_SELECTOR, '.video-card')
        all_videos = []

        for video in videos[:30]:
            try:
                # 获取视频标题、UP 名称和封面图片 URL
                title = video.find_element(By.CSS_SELECTOR, '.video-name').get_attribute('title')
                up_name = video.find_element(By.CSS_SELECTOR, '.up-name__text').get_attribute('title')
                cover_url = video.find_element(By.CSS_SELECTOR, '.cover-picture__image').get_attribute('data-src') or video.find_element(By.CSS_SELECTOR, '.cover-picture__image').get_attribute('src')
                cover_url = self.clean_image_url(cover_url)
                safe_title = self.sanitize_filename(title)

                video_str = f"视频标题：{title} - UP名称：{up_name}"
                print(video_str)
                all_videos.append(video_str)

                # 下载封面图片
                response = requests.get(cover_url, stream=True)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    if image.mode == 'RGBA':
                        image = image.convert('RGB')

                    # 将图片保存到父文件夹的 BilibiliCovers 文件夹中
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