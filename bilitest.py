import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from PIL import Image
from io import BytesIO


def sanitize_filename(filename):
    """替换或移除不允许在文件名中的字符。"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename.replace('\u3000', ' ').strip()  # 替换全角空格为半角空格，移除头尾空格


def clean_image_url(url):
    """确保图像URL使用https协议并清除URL中的无关参数。"""
    if url.startswith("//"):
        url = "https:" + url  # 添加https前缀
    if '@' in url:
        url = url.split('@')[0]  # 清除 '@' 及其后面的部分
    return url


def download_bilibili_covers(save_folder):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无界面模式
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    url = "https://www.bilibili.com/v/popular/weekly?num=298"
    driver.get(url)
    time.sleep(5)  # 等待页面加载

    videos = driver.find_elements(By.CSS_SELECTOR, '.video-card')
    print("Bilibili 每周必看视频：\n")

    for video in videos[:10]:
        try:
            title_element = video.find_element(By.CSS_SELECTOR, '.video-name')
            cover_element = video.find_element(By.CSS_SELECTOR, '.cover-picture__image')

            title = title_element.get_attribute('title')
            cover_url = cover_element.get_attribute('data-src') or cover_element.get_attribute('src')
            cover_url = clean_image_url(cover_url)  # 清理图片URL
            safe_title = sanitize_filename(title)
            print(f"标题: {title}, 封面图片 URL: {cover_url}")

            response = requests.get(cover_url, stream=True)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image_path = os.path.join(save_folder, f"{safe_title}.jpg")
                image.save(image_path)
            else:
                print(f"下载失败，状态码: {response.status_code}, URL: {cover_url}")

        except Exception as e:
            print(f"处理视频错误: {e}")

    driver.quit()


if __name__ == '__main__':
    save_folder = 'BilibiliCovers'
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        print(f"创建文件夹: {save_folder}")

    download_bilibili_covers(save_folder)
