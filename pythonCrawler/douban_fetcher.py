import requests
from bs4 import BeautifulSoup

class DouBanFetcher:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_movies(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._parse_movies(soup)
        except requests.RequestException as e:
            print(f"网络请求错误: {e}")
            return []
        except Exception as e:
            print(f"数据解析错误: {e}")
            return []

    def _parse_movies(self, soup):
        movies = []
        for item in soup.find_all('tr', class_='item'):
            title_tag = item.find('a', class_='nbg')
            title = title_tag['title']
            link = title_tag['href']
            rating = item.find('span', class_='rating_nums').text
            movies.append({"title": title, "link": link, "rating": rating})
        return movies

def main():
    url = "https://movie.douban.com/chart"
    fetcher = DouBanFetcher(url)
    movies = fetcher.fetch_movies()
    for movie in movies:
        print(f"电影名称: {movie['title']}, 链接: {movie['link']}, 评分: {movie['rating']}")

if __name__ == "__main__":
    main()