import os
import time
import random
from typing import Optional

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def sanitize_filename(filename: str) -> str:
    """
    清理文件名中的非法字符。
    
    Args:
        filename (str): 原始文件名
    
    Returns:
        str: 处理后的安全文件名
    """
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename.replace('\u3000', ' ').strip()


def clean_image_url(url: str) -> str:
    """
    规范化和清理图像URL。
    
    Args:
        url (str): 原始图像URL
    
    Returns:
        str: 处理后的URL
    """
    if url.startswith("//"):
        url = "https:" + url
    return url.split('@')[0] if '@' in url else url


def get_webdriver() -> webdriver.Chrome:
    """
    创建并配置 Chrome WebDriver。
    
    Returns:
        webdriver.Chrome: 配置好的 WebDriver 实例
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def download_image(cover_url: str, save_path: str) -> bool:
    """
    下载并保存图像。
    
    Args:
        cover_url (str): 图像URL
        save_path (str): 保存路径
    
    Returns:
        bool: 是否成功下载
    """
    try:
        response = requests.get(cover_url, timeout=10)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        image = image.convert('RGB')
        image.save(save_path)
        return True
    except Exception as e:
        print(f"下载图像失败: {e}")
        return False


def extract_video_info(video_element) -> Optional[dict]:
    """
    从网页元素中提取视频信息。
    
    Args:
        video_element: Selenium WebElement
    
    Returns:
        Optional[dict]: 视频信息字典，提取失败返回 None
    """
    try:
        title_element = video_element.find_element(By.CSS_SELECTOR, '.video-name')
        up_name_element = video_element.find_element(By.CSS_SELECTOR, '.up-name__text')
        cover_element = video_element.find_element(By.CSS_SELECTOR, '.cover-picture__image')

        return {
            'name': up_name_element.get_attribute('title'),
            'title': title_element.get_attribute('title'),
            'cover_url': clean_image_url(
                cover_element.get_attribute('data-src') or 
                cover_element.get_attribute('src')
            )
        }
    except Exception as e:
        print(f"提取视频信息错误: {e}")
        return None


def download_bilibili_covers(save_folder: str, url: str) -> None:
    """
    下载 Bilibili 视频封面。
    
    Args:
        save_folder (str): 保存文件夹路径
        url (str): 目标网页 URL
    """
    with get_webdriver() as driver:
        driver.get(url)
        
        # 使用显式等待确保页面元素加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.video-card'))
        )
        
        # 判断页面类型
        update_info = '每周必看视频' if 'weekly' in url else '入站必刷视频'
        print(f"\nBilibili {update_info}：\n")

        videos = driver.find_elements(By.CSS_SELECTOR, '.video-card')[:30]
        
        for video in videos:
            video_info = extract_video_info(video)
            if not video_info:
                continue

            safe_title = sanitize_filename(video_info['title'])
            image_path = os.path.join(save_folder, f"{safe_title}.jpg")
            
            print(f"视频标题：{video_info['title']} - UP名称：{video_info['name']}")
            
            download_image(video_info['cover_url'], image_path)


def main():
    """主程序入口"""
    save_folder = 'BilibiliCovers'
    os.makedirs(save_folder, exist_ok=True)
    print(f"创建文件夹: {save_folder}")

    url_dict = {
        '1': "https://www.bilibili.com/v/popular/history",
        '2': "https://www.bilibili.com/v/popular/weekly",
        '3': None
    }

    choice = input("请输入爬取页面的选项（1 - 入站必刷视频，2 - 每周必看视频，3 - 全部）：")
    
    if choice == '3':
        download_bilibili_covers(save_folder, url_dict['1'])
        download_bilibili_covers(save_folder, url_dict['2'])
    elif choice in ['1', '2']:
        download_bilibili_covers(save_folder, url_dict[choice])
    else:
        print("无效选项，程序结束。")


if __name__ == '__main__':
    main()
