import html

import html2text
import requests
from bs4 import BeautifulSoup


class MediaNotFound(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ExceptionGettingAPI(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class LinkFinder:
    PHOTO = 0
    VIDEO = 1
    IFRAME = 2

    def __init__(self, url, api_key):
        self.url = url
        self.key = api_key

        self.api_url = "https://api.tumblr.com/v2/blog/{}/posts?api_key={}&id={}"
        self.response = None

        self.caption = ""
        self.soup = None
        self.links = []

        self.get_api()
        self.get_caption()

        self.get_photos()
        self.get_videos()
        self.get_iframes()

        self.caption = html2text.html2text(str(self.soup))

        if not self.links:
            raise MediaNotFound

    def get_api(self):

        # remove safe-mode
        if "safe-mode?url=" in self.url:
            self.url = self.url.split("safe-mode?url=")[1]

        # split and make api url
        split = self.url.split("/")
        self.api_url = self.api_url.format(split[2], self.key, split[4])

        # make request
        r = requests.get(self.api_url)

        # if error, return
        if r.status_code != 200 or r.json()["meta"]["status"] != 200:
            print("Cant find page, {}, url: {}".format(r.json()["meta"]["status"], self.url))
            raise ExceptionGettingAPI
        else:
            self.response = r.json()["response"]["posts"][0]

    def get_caption(self):
        if "caption" in self.response:
            self.soup = BeautifulSoup(html.unescape(self.response["caption"]), "html.parser")
        else:
            self.soup = BeautifulSoup("", "html.parser")

    def get_photos(self):
        if "photos" in self.response:
            for photo in self.response["photos"]:
                arr = {"type": self.PHOTO, "url": photo["original_size"]["url"], "caption": photo["caption"]}
                self.links.append(arr)

        for img in self.soup.find_all("img"):
            self.links.append({"type": self.PHOTO, "url": img["src"]})
            img.parent.decompose()

    def get_videos(self):
        if "video_type" in self.response:

            if self.response["video_type"] == "tumblr":
                self.links.append({"type": self.VIDEO, "url": self.response["video_url"]})
            else:
                embed_code = BeautifulSoup(self.response["player"][0]["embed_code"], "html.parser")
                self.links.append({"type": self.IFRAME, "url": embed_code.find("iframe")["src"]})

    def get_iframes(self):
        for frame in self.soup.find_all("iframe"):
            self.links.append({"type": self.IFRAME, "url": frame["src"]})
            frame.decompose()
