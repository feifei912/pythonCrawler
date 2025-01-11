# pythonCrawler

#### 介绍
这是一个使用Python编写的多功能网络爬虫项目，目前支持以下功能：
1. 新浪新闻爬虫（实时新闻和热门排行）
2. GitHub热门项目数据爬取（今日、每周、每月）
3. Bilibili热门视频信息和封面爬取（入站必刷和每周必看）

#### 软件架构
本项目采用模块化设计，每个功能模块独立实现，便于扩展和维护。主要模块包括：

1. **新浪新闻爬虫模块**：负责抓取新浪新闻的实时新闻和热门排行榜。
2. **GitHub热门项目爬虫模块**：负责抓取GitHub热门项目的star数据和增长趋势。
3. **Bilibili视频爬虫模块**：负责抓取Bilibili热门视频的信息和封面。

#### 集成环境
**开发环境**：

- 操作系统：Windows 11
- Python版本：3.13
- 浏览器：Chrome
- 驱动：ChromeDriver

**编辑器**：

- Visual Studio Code
- PyCharm

#### 安装教程

1. **安装依赖**：
    ```
    pip install pathlib ruamel-yaml requests beautifulsoup4 matplotlib pillow flask
    pip install selenium==4.5.0
    ```

2. **安装Chrome浏览器**：
    - 下载并安装对应版本的Chrome浏览器以及ChromeDriver驱动。

3. **安装ChromeDriver并配置环境变量**：
    - Chrome版本114及以下：[下载地址](http://chromedriver.storage.googleapis.com/index.html)
    - Chrome版本115至最新：[下载地址](https://googlechromelabs.github.io/chrome-for-testing/#stable)

4. **测试ChromeDriver是否正常运行**：
    ```python
    from selenium import webdriver
    if __name__ == '__main__':
        driver = webdriver.Chrome()
        url = 'https://www.baidu.com/'
        driver.get(url)
        driver.maximize_window()
    ```

#### 使用说明

1. **运行项目**：
    ```bash
    在项目根目录下运行：
    python main.py
    或者运行：
    python app.py
    ```
    前者在终端中让用户选择要执行的功能，并在终端中运行；后者会启动一个Web服务，在前端中运行爬虫。

#### 使用界面

本项目提供了两种使用界面，分别通过命令行和浏览器进行交互：

**1. 命令行界面 (main.py)**：

- 通过命令行交互界面选择要执行的功能。
- 跟随提示输入相应的选项。
- 查看输出结果和生成的数据可视化图表。
- 图表悬停可查看具体数据。

**2. 浏览器界面 (app.py)**：

- 直接在浏览器中运行爬虫，无需在终端中输入命令。
- 在浏览器中查看爬取的数据和生成的数据可视化图表。
- 点击相应的按钮执行相应的功能。
- 图表悬停可查看具体数据。

#### 运行方式

**命令行界面**：
```
python main.py
```

**浏览器界面**：
```
python app.py
```

然后在浏览器中打开提供的URL（`http://127.0.0.1:5000`）即可使用浏览器界面。

#### 数据文件

- 新浪新闻数据保存在`News`文件夹。
- Bilibili视频封面保存在`BilibiliCovers`文件夹。
- 可视化图表会自动显示。

#### 更新日志
---
##### v1.0.0
- 2024-10-20：更新项目结构，增加新浪新闻爬虫模块。
- 2024-10-27：增加GitHub热门项目爬虫模块。
- 2024-10-28：增加Bilibili视频爬虫模块。
- 2024-11-5：增加Web服务，提供浏览器界面。
- 2024-11-13：增加数据保存功能，优化用户体验。
- 2024-12-14：增加数据可视化功能，优化代码结构。
---
##### v1.1.0
- 正在开发中...
- 2025-1-11：更换新浪微博时事新闻多线程为异步IO，提高爬取效率。
- 2025-1-11：B站每周必看出现问题，无法爬取到数据。
- 2025-1-11：新浪微博热门新闻在前端页面上输出格式错误。
---

#### 注意事项

- 确保网络连接稳定。
- 遵守网站的robots协议。
- 适当控制爬取频率，避免对目标网站造成压力。
- 抓取的内容仅用于学习和研究用途。

#### 参与贡献

1. Fork 本仓库
2. 新建分支
3. 提交代码
4. 新建 Pull Request

#### Donate

如果觉得这个项目对你有帮助，可以给作者点个STAR

感谢您的支持！