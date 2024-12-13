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
    �����ļ����еķǷ��ַ���
    
    Args:
        filename (str): ԭʼ�ļ���
    
    Returns:
        str: �����İ�ȫ�ļ���
    """
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename.replace('\u3000', ' ').strip()


def clean_image_url(url: str) -> str:
    """
    �淶��������ͼ��URL��
    
    Args:
        url (str): ԭʼͼ��URL
    
    Returns:
        str: ������URL
    """
    if url.startswith("//"):
        url = "https:" + url
    return url.split('@')[0] if '@' in url else url


def get_webdriver() -> webdriver.Chrome:
    """
    ���������� Chrome WebDriver��
    
    Returns:
        webdriver.Chrome: ���úõ� WebDriver ʵ��
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
    ���ز�����ͼ��
    
    Args:
        cover_url (str): ͼ��URL
        save_path (str): ����·��
    
    Returns:
        bool: �Ƿ�ɹ�����
    """
    try:
        response = requests.get(cover_url, timeout=10)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        image = image.convert('RGB')
        image.save(save_path)
        return True
    except Exception as e:
        print(f"����ͼ��ʧ��: {e}")
        return False


def extract_video_info(video_element) -> Optional[dict]:
    """
    ����ҳԪ������ȡ��Ƶ��Ϣ��
    
    Args:
        video_element: Selenium WebElement
    
    Returns:
        Optional[dict]: ��Ƶ��Ϣ�ֵ䣬��ȡʧ�ܷ��� None
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
        print(f"��ȡ��Ƶ��Ϣ����: {e}")
        return None


def download_bilibili_covers(save_folder: str, url: str) -> None:
    """
    ���� Bilibili ��Ƶ���档
    
    Args:
        save_folder (str): �����ļ���·��
        url (str): Ŀ����ҳ URL
    """
    with get_webdriver() as driver:
        driver.get(url)
        
        # ʹ����ʽ�ȴ�ȷ��ҳ��Ԫ�ؼ���
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.video-card'))
        )
        
        # �ж�ҳ������
        update_info = 'ÿ�ܱؿ���Ƶ' if 'weekly' in url else '��վ��ˢ��Ƶ'
        print(f"\nBilibili {update_info}��\n")

        videos = driver.find_elements(By.CSS_SELECTOR, '.video-card')[:30]
        
        for video in videos:
            video_info = extract_video_info(video)
            if not video_info:
                continue

            safe_title = sanitize_filename(video_info['title'])
            image_path = os.path.join(save_folder, f"{safe_title}.jpg")
            
            print(f"��Ƶ���⣺{video_info['title']} - UP���ƣ�{video_info['name']}")
            
            download_image(video_info['cover_url'], image_path)


def main():
    """���������"""
    save_folder = 'BilibiliCovers'
    os.makedirs(save_folder, exist_ok=True)
    print(f"�����ļ���: {save_folder}")

    url_dict = {
        '1': "https://www.bilibili.com/v/popular/history",
        '2': "https://www.bilibili.com/v/popular/weekly",
        '3': None
    }

    choice = input("��������ȡҳ���ѡ�1 - ��վ��ˢ��Ƶ��2 - ÿ�ܱؿ���Ƶ��3 - ȫ������")
    
    if choice == '3':
        download_bilibili_covers(save_folder, url_dict['1'])
        download_bilibili_covers(save_folder, url_dict['2'])
    elif choice in ['1', '2']:
        download_bilibili_covers(save_folder, url_dict[choice])
    else:
        print("��Чѡ����������")


if __name__ == '__main__':
    main()
