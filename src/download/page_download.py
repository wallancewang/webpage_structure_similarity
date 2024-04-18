import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from src.config.config_loader import HtmlCfg


class Downloader:
    def __init__(self, cfg):
        self.cfg = cfg

    def get_html(self, url):
        raise NotImplementedError


class BaseDownloader(Downloader):
    def __init__(self, cfg):
        super(BaseDownloader, self).__init__(cfg)
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

    def get_html(self, url):
        trial = 0
        html_src = ''
        while trial < 3:
            try:
                response = requests.get(url, headers=self.headers, timeout=2)
                if response.status_code == 200:
                    return response.text
                else:
                    trial += 1
            except:
                trial += 1
        return html_src


class WebDriverDownloader(Downloader):
    def __init__(self, cfg: HtmlCfg):
        super(WebDriverDownloader, self).__init__(cfg)
        self.driver = webdriver.Chrome(service=Service(cfg.driver_file))

    def get_html(self, url):
        try:
            self.driver.get(url)
        except:
            return ''
        time.sleep(1)
        html_src = self.driver.page_source
        return html_src
