import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

class UniversityRankingsFetcher:
    def __init__(self, save_folder):
        self.save_folder = save_folder
        self.url = "https://www.shanghairanking.cn/rankings/bcur/2022"
        self.base_url = "https://www.shanghairanking.cn"

    def fetch_rankings(self):
        try:
            # 发送 HTTP 请求获取网页内容
            response = requests.get(self.url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找排名表格
            table = soup.find('table', class_='rk-table')
            if not table:
                print("未找到排名表，请检查页面结构。")
                return []

            # 解析表格数据
            rankings = self._parse_table(table)
            return rankings

        except requests.RequestException as e:
            print(f"网络请求错误: {e}")
            return []
        except Exception as e:
            print(f"数据获取错误: {e}")
            return []

    def _parse_table(self, table):
        rankings = []
        rows = table.find_all('tr')[1:]  # 跳过表头行
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                rank = cols[0].text.strip()
                name_col = cols[1]
                name_cn = name_col.find('span', class_='name-cn').text.strip()
                name_en = name_col.find('span', class_='name-en').text.strip()
                university_type = name_col.find('p', class_='tags').text.strip()
                score = cols[4].text.strip()
                rankings.append([rank, name_cn, name_en, score, university_type])
        return rankings

    def save_to_csv(self, data):
        if not data:
            print("没有数据可保存。")
            return

        # 创建保存路径
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.save_folder)
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, 'university_rankings_2022.csv')

        try:
            # 将数据保存到 CSV 文件
            df = pd.DataFrame(data, columns=['排名', '中文名', '英文名', '得分', '类型'])
            df.to_csv(file_path, encoding='utf-8-sig', index=False)
            print(f"排名数据已成功保存到 {file_path}")
        except Exception as e:
            print(f"保存 CSV 文件时出错: {e}")

def main():
    fetcher = UniversityRankingsFetcher('UniversityRankings')
    rankings = fetcher.fetch_rankings()
    fetcher.save_to_csv(rankings)

if __name__ == "__main__":
    main()