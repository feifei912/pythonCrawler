import requests
from PIL import Image
from io import BytesIO

# 封面图片链接列表
cover_urls = [
    "https://i1.hdslb.com/bfs/archive/2e2964859b5e28d3d9cc34a564657f9ea81d4bed.jpg",
    "https://i0.hdslb.com/bfs/archive/5af30279e7ae9c4eadfd0269cdbad62a6a5a1138.jpg",
    "https://i2.hdslb.com/bfs/archive/106cbae1eca86867fdb3ff69feec5361e5f07e05.jpg",
    "https://i0.hdslb.com/bfs/archive/1645a9c209014d10e22d9fbddb0cd980c4dcfa91.jpg",
    "https://i0.hdslb.com/bfs/archive/02c38fe5ca429deababee7ff94a9d543dda395bd.jpg"
]

# 下载并保存图片
for index, url in enumerate(cover_urls, start=1):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            file_name = f"cover_image_{index}.jpg"
            img.save(file_name)
            print(f"图片 {index} 已保存为 {file_name}")
        else:
            print(f"图片下载失败，状态码: {response.status_code}, URL: {url}")
    except Exception as e:
        print(f"图片处理错误: {e}, URL: {url}")
