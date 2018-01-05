import html

import html2text
import requests
from bs4 import BeautifulSoup


class LinkFinder:
    # set "constants"
    PHOTO = 0
    PHOTOSET = 1
    VIDEO = 2
    IFRAME = 3

    def __init__(self, url):
        # get and setup vars
        self.page = self.get_page(url)
        self.soup = BeautifulSoup(html.unescape(self.page), "html.parser")
        self.type = self.soup.find("post")["type"]

        self.url = url
        self.links = []
        self.error = False
        self.caption = None

        # run method for appropriate type
        if self.type == "regular":
            self.get_iframe()
            self.type = self.IFRAME

        elif self.type == "video":
            self.get_video()
            self.type = self.VIDEO

        elif self.type == "photo":
            if self.soup.find("photoset"):
                self.get_photoset()
                self.type = self.PHOTOSET

            else:
                self.get_photo()
                self.type = self.PHOTO

        self.get_caption()

        if not self.links:
            self.error = True

    def get_caption(self):

        if self.soup.find("photo-caption"):
            caption = self.soup.find("photo-caption").contents[0]
        elif self.soup.find("video-caption"):
            caption = self.soup.find("video-caption").contents[0]
        else:
            return

        self.caption = html2text.html2text(caption)

    def get_iframe(self):

        frames = self.soup.find_all("iframe")
        for frame in frames:
            self.links.append([self.IFRAME, frame["src"]])

    def get_video(self):

        # find video player, return src if valid
        player = self.soup.find("video-player").find("source")
        if player is not None:
            self.links.append([self.VIDEO, player["src"]])

        # if not tumblr video, find iframes
        self.get_iframe()

    def get_photoset(self):

        photos = self.soup.find_all("photo")
        for photo in photos:
            self.links.append(photo.find("photo-url").contents[0])

    def get_photo(self):

        src = self.soup.find("photo-url").contents[0]
        self.links.append([self.PHOTO, src])

    @staticmethod
    def get_page(url):

        # make url
        url = url.split("#")[0]
        url = url.split("?")[0]
        url += "/xml"

        # get page
        request = requests.get(url, allow_redirects=False)
        loc = request.headers.get("location")

        # if redirect, get page using new url
        if loc is not None:
            url = loc
            url = url.split("#")[0]
            url = url.split("?")[0]
            url += "/xml"

            request = requests.get(url, allow_redirects=False)

        return request.text
