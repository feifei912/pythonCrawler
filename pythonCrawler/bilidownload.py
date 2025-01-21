import time
import re
import os
import asyncio
import aiohttp
import aiofiles
import requests
from concurrent.futures import ThreadPoolExecutor


class BiliVideoDownloader:
    def __init__(self):
        self.video = Video()
        self.error_download = []

    def set_cookie(self, sess_data):
        self.video.cookies = {"SESSDATA": sess_data}

    def download_video(self, bvid, directory, quality=80, pages=1):
        """下载单个或多个视频"""
        if not self.inspect_bvid(bvid):
            print('无效的BV号')
            return False

        # 确保目录存在
        if not self.is_directory_exist(directory):
            os.makedirs(directory)
            if not self.is_directory_exist(directory):
                print('无效的目录')
                return False

        # 如果是合集，创建目录
        if pages > 1:
            directory = os.path.join(directory, self.get_title(bvid))
            if not os.path.exists(directory):
                os.makedirs(directory)

        # 下载视频
        for page in range(1, pages + 1):
            print(f"\n正在处理视频 {page} 的 {pages}")
            self.download_single_video(bvid, directory, quality, page)

        if self.error_download:
            print(f"BV: {bvid} 下载失败的页面: {self.error_download}")
        else:
            print(f"BV: {bvid} 所有下载已完成")

    def download_single_video(self, bvid, directory, quality, page=1):
        """下载单个视频"""
        try:
            # 获取视频和音频流
            videore, audiore = self.video.get_video(bvid, pages=page, quality=quality)
            total_size = self.get_bit(videore, audiore)
            print(f"BV: {bvid} 页面: {page} 状态: 下载中, 质量: {quality}, 大小: {self.size(total_size)}")
            print(f"视频 URL: {videore.url}")
            print(f"音频 URL: {audiore.url}")

            # 下载并合并
            filename_temp = self.save(directory, videore, audiore)
            print(f"BV: {bvid} 页面: {page} 状态: 正在合并文件...")

            title = self.get_title_collection(bvid, page) if page > 1 else self.get_title(bvid)
            self.merge_videos(filename_temp, os.path.join(directory, title))
            print(f"BV: {bvid} 页面: {page} 状态: 完成")
            return True
        except Exception as e:
            print(f"下载视频时出错: {str(e)}")
            self.error_download.append(page)
            return False

    def merge_videos(self, filename_temp, filename_new):
        """合并视频和音频文件"""
        try:
            import subprocess
            video_path = f"{filename_temp}.mp4"
            audio_path = f"{filename_temp}.mp3"

            if not os.path.exists(video_path) or not os.path.exists(audio_path):
                raise ValueError("视频或音频文件丢失")

            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-y',
                f"{filename_new}.mp4"
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise Exception(f"FFmpeg失败: {stderr.decode()}")

            # 清理临时文件
            self.remove(filename_temp)

        except Exception as e:
            print(f"合并失败: {str(e)}")
            return False

    def save(self, directory, videore, audiore):
        """优化后的异步保存视频和音频文件"""
        filename_temp = os.path.join(directory, str(time.time()))
        max_retries = 3  # 最大重试次数
        chunk_size = 8 * 1024 * 1024  # 8MB 块
        chunk_count = 16  # 16个并发下载块
        download_timeout = 10  # 超时时间 (秒)

        async def download_file(url, filename, headers, cookies, description):
            total_size = 0
            downloaded = [0]  # 使用列表以便在嵌套函数中修改

            async def download_range(start, end):
                range_headers = headers.copy()
                range_headers['Range'] = f'bytes={start}-{end}'

                for retry in range(max_retries):
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, headers=range_headers, cookies=cookies) as response:
                                async with aiofiles.open(filename + f'.part{start}', 'wb') as f:
                                    async for chunk in response.content.iter_chunked(chunk_size):
                                        if chunk:
                                            await f.write(chunk)
                                            downloaded[0] += len(chunk)
                                            percentage = (downloaded[0] / total_size) * 100 if total_size else 0
                                            print(f"\r{description}: {percentage:.1f}%", end="", flush=True)
                                            # 重置超时计时器
                                            await asyncio.sleep(0)
                        break  # 成功下载后跳出重试循环
                    except Exception as e:
                        print(f"下载块 {start}-{end} 时出错: {str(e)}，重试 {retry + 1}/{max_retries}")
                        if retry == max_retries - 1:
                            raise

            # 获取文件大小
            async with aiohttp.ClientSession() as session:
                async with session.head(url, headers=headers, cookies=cookies) as response:
                    total_size = int(response.headers.get('content-length', 0))

            # 分块下载设置
            chunk_size = max(total_size // chunk_count, 1024 * 1024)  # 确保每块至少1MB
            chunks = []

            # 创建下载任务
            for i in range(chunk_count):
                start = i * chunk_size
                end = start + chunk_size - 1 if i < chunk_count - 1 else total_size - 1
                if start < total_size:  # 确保不会超出文件大小
                    chunks.append(asyncio.wait_for(download_range(start, end), timeout=download_timeout))

            # 并发下载
            try:
                await asyncio.gather(*chunks)
            except Exception as e:
                print(f"下载文件 {description} 时出错: {str(e)}")
                return False

            # 合并文件块
            async with aiofiles.open(filename, 'wb') as outfile:
                for i in range(chunk_count):
                    part_file = filename + f'.part{i * chunk_size}'
                    try:
                        async with aiofiles.open(part_file, 'rb') as infile:
                            content = await infile.read()
                            await outfile.write(content)
                        # 删除临时文件
                        os.remove(part_file)
                    except FileNotFoundError:
                        continue  # 跳过不存在的分块文件

            print()  # 换行
            return True

        async def download_both():
            tasks = []
            # 视频下载任务
            tasks.append(
                download_file(
                    videore.url,
                    f"{filename_temp}.mp4",
                    self.video.headers,
                    self.video.cookies,
                    "视频下载"
                )
            )
            # 音频下载任务
            tasks.append(
                download_file(
                    audiore.url,
                    f"{filename_temp}.mp3",
                    self.video.headers,
                    self.video.cookies,
                    "音频下载"
                )
            )
            # 独立执行任务
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return all(result is True for result in results)

        # 使用线程池执行异步任务
        with ThreadPoolExecutor(max_workers=16) as executor:
            future = executor.submit(lambda: asyncio.run(download_both()))
            try:
                success = future.result()  # 等待下载完成
                if not success:
                    raise Exception("下载过程中发生错误")
            except Exception as e:
                print(f"下载出错: {str(e)}")
                raise

        return filename_temp

    # 原始代码的辅助方法
    def remove(self, filename_temp):
        try:
            os.remove(f"{filename_temp}.mp4")
            os.remove(f"{filename_temp}.mp3")
        except:
            pass

    def get_bit(self, videore, audiore):
        return int(videore.headers.get('Content-Length')) + int(audiore.headers.get('Content-Length'))

    def size(self, bit):
        value = int(bit)
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return "%.2f%s" % (value, units[i])
            value = value / size

    def is_directory_exist(self, directory):
        return os.path.exists(directory)

    def title_filterate(self, title):
        return re.sub(r"\/|\,|\:|\*|\?|\<|\>|\\|\&|$|$|\.\.|\||\'|\"", "", title)

    def inspect_bvid(self, bvid):
        if bool(re.match(r'^BV[a-zA-Z0-9]{10}$', bvid)):
            return self.video.get_info(bvid) is not False
        return False

    def get_title(self, bvid):
        data = self.video.get_info(bvid)
        title = data['data']['title']
        return self.title_filterate(title)

    def get_title_collection(self, bvid, pages):
        data = self.video.get_info(bvid)
        title = data['data']['pages'][pages - 1]['part']
        return 'P' + str(pages) + ' ' + self.title_filterate(title)


class Video:
    def __init__(self):
        self.api_info = 'https://api.bilibili.com/x/web-interface/view?bvid={}'
        self.api_url = 'https://api.bilibili.com/x/player/wbi/playurl?bvid={}&cid={}&fnval=4048'
        self.headers = {
            "referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/108.0.0.0 Safari/537.36 "
        }
        # 初始化 cookies
        self.cookies = {}

    def set_cookie(self, cookie):
        """ 设置cookie """
        self.cookies = {"SESSDATA": cookie}

    def get_info(self, bvid):
        """ 获取视频信息 """
        url = self.api_info.format(bvid)
        response = requests.get(url=url, headers=self.headers)
        if response.status_code == 200:
            if response.json()['code'] == 0:
                return response.json()
            else:
                return False
        else:
            return False

    def get_cid(self, bvid, pages):
        """ 获取视频cid """
        url = self.api_info.format(bvid)
        response = requests.get(url=url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                cid = data['data']['pages'][pages - 1]['cid']
                return cid
            else:
                return False
        else:
            return False

    def get_quality(self, bvid, cid):
        """ 获取视频质量列表 """
        url = self.api_url.format(bvid, cid)
        response = requests.get(url=url, headers=self.headers, cookies=self.cookies)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                quality_dict = []
                if 'dash' in data['data']:
                    for i in data['data']['dash']['video']:
                        quality_dict.append(i['id'])
                return quality_dict
            else:
                print(f"获取质量列表时出错: {data['message']}")
                return []
        else:
            print(f"请求质量列表时出错: {response.status_code}")
            return []

    def request_url(self, bvid, cid):
        """ 获取视频和音频的url """
        url = self.api_url.format(bvid, cid)
        response = requests.get(url=url, headers=self.headers, cookies=self.cookies)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                return data['data']
            else:
                print(f"获取视频和音频URL时出错: {data['message']}")
                return None
        else:
            print(f"请求视频和音频URL时出错: {response.status_code}")
            return None

    def get_video(self, bvid, pages=1, quality=80):
        """ 视频下载 """
        cid = self.get_cid(bvid, pages)
        quality_list = self.get_quality(bvid, cid)
        print(f"可用质量参数: {quality_list}")
        if quality not in quality_list:
            raise ValueError(f"无效的质量参数: {quality}")
        data = self.request_url(bvid, cid)
        if data is None:
            raise ValueError("无法获取视频和音频的URL")
        video_url = next(i['baseUrl'] for i in data['dash']['video'] if i['id'] == quality)
        audio_url = data['dash']['audio'][0]['baseUrl']
        print(f"视频 URL: {video_url}")
        print(f"音频 URL: {audio_url}")
        self.videore = requests.get(url=video_url, headers=self.headers, cookies=self.cookies, stream=True)
        self.audiore = requests.get(url=audio_url, headers=self.headers, cookies=self.cookies, stream=True)
        return self.videore, self.audiore


def main():
    downloader = BiliVideoDownloader()

    # 创建保存目录（当前文件夹的父级文件夹中的"video"文件夹）
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
    parent_dir = os.path.dirname(current_dir)  # 获取父级目录
    directory = os.path.join(parent_dir, "video")  # 在父级目录下创建video文件夹路径

    # 如果video文件夹不存在，则创建
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 获取用户输入
    sess_data = input("输入SESSDATA cookie: ")
    downloader.set_cookie(sess_data)

    bvid = input("输入BV号: ")
    quality = int(input("输入质量 (80为1080p, 64为720p, 32为480p, 16为360p): "))
    is_collection = input("是否为合集? (y/n): ").lower() == 'y'

    if is_collection:
        pages = int(input("输入要下载的视频数量: "))
    else:
        pages = 1

    # 开始下载
    downloader.download_video(bvid, directory, quality, pages)


if __name__ == '__main__':
    main()