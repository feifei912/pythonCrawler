from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from PIL import Image
import matplotlib.pyplot as plt

# 配置 Matplotlib 后端（在无GUI的环境下使用）
import matplotlib
try:
    matplotlib.use('TkAgg')  # 优先使用交互式后端（适合本地运行）
except Exception:
    matplotlib.use('Agg')  # 切换到无交互式后端（适合无GUI环境）

# 配置 Selenium 驱动
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无界面模式
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# Bilibili 每周必看网址
url = "https://www.bilibili.com/v/popular/weekly?num=297"
driver.get(url)
time.sleep(5)  # 等待页面加载

# 定位视频信息
videos = driver.find_elements(By.CSS_SELECTOR, '.video-card')

data = []

print("Bilibili 每周必看视频：\n")
for video in videos[:10]:  # 只提取前10个视频
    try:
        # 定位标题、作者和封面图片
        title_element = video.find_element(By.CSS_SELECTOR, '.video-name')
        author_element = video.find_element(By.CSS_SELECTOR, '.up-name__text')
        cover_element = video.find_element(By.CSS_SELECTOR, '.cover-picture__image')

        title = title_element.get_attribute('title')  # 获取视频标题
        author = author_element.text  # 获取作者名称
        cover_url = cover_element.get_attribute('data-src') or cover_element.get_attribute('src')  # 优先使用 data-src

        # 如果封面图片 URL 是相对路径，添加前缀
        if cover_url.startswith("//"):
            cover_url = "https:" + cover_url

        print(f"标题: {title}, 作者: {author}")
        print(f"封面图片 URL: {cover_url}")

        # 下载封面图片
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Referer": "https://www.bilibili.com/"
        }
        response = requests.get(cover_url, headers=headers, stream=True)

        # 检查图片下载是否成功
        if response.status_code == 200:
            try:
                cover_image = Image.open(response.raw).convert('RGB')  # 转换为RGB格式
                print(f"成功下载图片: {cover_url}")
                data.append({"title": title, "author": author, "cover_image": cover_image})
            except Exception as e:
                print(f"图片处理错误: {e}, URL: {cover_url}")
        else:
            print(f"图片下载失败，状态码: {response.status_code}, URL: {cover_url}")
    except Exception as e:
        print(f"错误: {e}")

driver.quit()

# 使用 Matplotlib 绘制封面图片
plt.figure(figsize=(15, 10))
for i, item in enumerate(data):
    try:
        if not isinstance(item["cover_image"], Image.Image):
            print(f"无效的图片对象: {item['title']}")
            continue
        plt.subplot(2, 5, i + 1)
        plt.imshow(item["cover_image"])
        plt.axis('off')
        plt.title(f"{item['title']}\n{item['author']}", fontsize=8)
    except Exception as e:
        print(f"绘图错误: {e}, 视频: {item['title']}")

if __name__ == '__main__':
    # 保存最终的展示图片
    output_file = "output.png"
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"封面图展示已保存为: {output_file}")

    # 显示图片（仅在支持GUI的环境中可用）
    try:
        plt.show()
    except Exception as e:
        print(f"非交互环境，无法显示图片: {e}")
