import os
import time
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import asyncio
import aiohttp
from aiohttp.client_exceptions import ClientPayloadError

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

    async def fetch_image(self, session, url, image_path, retries=3):
        for attempt in range(retries):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        content = await response.read()
                        image = Image.open(BytesIO(content))
                        if image.mode == 'RGBA':
                            image = image.convert('RGB')
                        image.save(image_path)
                        return
                    else:
                        print(f"下载失败，状态码: {response.status}, URL: {url}")
            except (ClientPayloadError, aiohttp.ClientError) as e:
                print(f"下载封面时出现错误: {e}, 尝试次数: {attempt + 1}/{retries}")
                if attempt + 1 == retries:
                    print(f"下载失败，URL: {url}")

    async def download_images(self, image_urls):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url, image_path in image_urls:
                tasks.append(self.fetch_image(session, url, image_path))
            await asyncio.gather(*tasks)

    def download_bilibili_covers(self, url):
        """
        下载B站视频封面并获取视频信息，包括BV号
        :param url: 目标页面URL
        :return: 包含视频信息的列表
        """
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
        image_urls = []

        for video in videos[:30]:
            try:
                # 获取视频标题
                title_element = video.find_element(By.CSS_SELECTOR, '.video-name')
                title = title_element.get_attribute('title')

                # 获取UP主名称
                up_name_element = video.find_element(By.CSS_SELECTOR, '.up-name__text')
                up_name = up_name_element.get_attribute('title')

                # 获取播放量
                play_count_element = video.find_element(By.CSS_SELECTOR, '.play-text')
                play_count = play_count_element.text.strip()

                # 获取BV号
                video_link = video.find_element(By.CSS_SELECTOR, '.video-card__content a')
                video_url = video_link.get_attribute('href')
                bv_id = video_url.split('/')[-1] if video_url else None

                # 获取封面URL
                cover_url_element = video.find_element(By.CSS_SELECTOR, '.cover-picture__image')
                cover_url = cover_url_element.get_attribute('data-src') or cover_url_element.get_attribute('src')
                cover_url = self.clean_image_url(cover_url)

                safe_title = self.sanitize_filename(title)

                # 存储完整的视频信息
                single_video_data = {
                    'title': title,
                    'up_name': up_name,
                    'play_count': play_count,
                    'bv_id': bv_id,
                    'video_url': f'https://www.bilibili.com/video/{bv_id}' if bv_id else None,
                    'cover_url': cover_url
                }

                print(f"视频标题：{title}")
                print(f"UP主：{up_name}")
                print(f"播放量：{play_count}")
                print(f"BV号：{bv_id}")
                print(f"视频链接：https://www.bilibili.com/video/{bv_id}")
                print("-" * 50)

                all_videos.append(single_video_data)

                # 下载封面图片
                if cover_url:
                    parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    save_path = os.path.join(parent_folder, 'BilibiliCovers')
                    os.makedirs(save_path, exist_ok=True)
                    # 在文件名中加入BV号
                    image_path = os.path.join(save_path, f"{safe_title}_BV{bv_id}.jpg")
                    image_urls.append((cover_url, image_path))

            except Exception as e:
                print(f"处理视频错误: {e}")
                continue

        # 使用多线程异步IO下载图片
        if image_urls:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.download_images(image_urls))
            loop.close()

        return all_videos