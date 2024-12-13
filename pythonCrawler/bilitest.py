import os
import time
import random
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


def download_bilibili_covers(save_folder, url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无界面模式
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(5)  # 等待页面加载

    # 判断要抓取哪个页面的标题
    if 'weekly' in url:
        update_info = '每周必看视频'
    else:
        update_info = '入站必刷视频'

    print(f"\nBilibili {update_info}：\n")

    # 获取视频封面并下载
    videos = driver.find_elements(By.CSS_SELECTOR, '.video-card')

    for video in videos[:30]:  # 只处理前30个视频
        try:
            title_element = video.find_element(By.CSS_SELECTOR, '.video-name')
            up_name_element = video.find_element(By.CSS_SELECTOR, '.up-name__text')
            cover_element = video.find_element(By.CSS_SELECTOR, '.cover-picture__image')

            name = up_name_element.get_attribute('title')  # 获取UP主名字
            title = title_element.get_attribute('title')  # 获取视频标题
            cover_url = cover_element.get_attribute('data-src') or cover_element.get_attribute('src')
            cover_url = clean_image_url(cover_url)  # 清理图片URL
            safe_title = sanitize_filename(title)

            print(f"视频标题：{title} - UP名称：{name}")  # 输出视频标题和UP主名字

            # 下载图片
            response = requests.get(cover_url, stream=True)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))

                # 检查并转换图片模式
                if image.mode == 'RGBA':
                    image = image.convert('RGB')

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

    # 提示用户选择要爬取的页面
    choice = input("请输入爬取页面的选项（1 - 入站必刷视频，2 - 每周必看视频，3 - 入站必刷视频以及每周必看视频）：")

    if choice == '1':
        download_bilibili_covers(save_folder, "https://www.bilibili.com/v/popular/history")
    elif choice == '2':
        download_bilibili_covers(save_folder, "https://www.bilibili.com/v/popular/weekly")
    elif choice == '3':
        download_bilibili_covers(save_folder, "https://www.bilibili.com/v/popular/history")
        download_bilibili_covers(save_folder, "https://www.bilibili.com/v/popular/weekly")
    else:
        print("无效选项，程序结束。")

'''
if __name__ == '__main__':
    save_folder = 'BilibiliCovers'
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        print(f"创建文件夹: {save_folder}")

    # 随机选择要爬取的网址
    url_list = [
        "https://www.bilibili.com/v/popular/weekly",
        "https://www.bilibili.com/v/popular/history"
    ]

    # 随机选择一个网址来爬取
    selected_url = random.choice(url_list)
    print(f"正在爬取网址：{selected_url}")
    download_bilibili_covers(save_folder, selected_url)
'''
