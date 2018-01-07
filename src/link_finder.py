import html

import html2text
import requests
from bs4 import BeautifulSoup


class LinkFinder:

    PHOTO = 0
    PHOTOSET = 1
    VIDEO = 2
    IFRAME = 3

    def __init__(self, url):
        # get and setup vars
        self.page = self.get_page(url)
        self.soup = BeautifulSoup(html.unescape(self.page), "html.parser")

        self.links = []
        self.error = False
        self.caption = None

        # get photoset or photo
        if self.soup.find("photoset"):
            self.get_photoset()
        else:
            self.get_photo()

        # try and get: iframes, video, caption
        self.get_iframe()
        self.get_video()
        self.get_caption()

        # if no links found, set error
        if not self.links:
            self.error = True

    def get_caption(self):

        if self.soup.find("photo-caption"):
            caption = self.soup.find("photo-caption").contents[0]
        elif self.soup.find("video-caption"):
            caption = self.soup.find("video-caption").contents[0]
        else:
            return

        self.caption = html2text.html2text(str(caption))

    def get_iframe(self):

        frames = self.soup.find_all("iframe")
        for frame in frames:
            self.links.append([self.IFRAME, frame["src"]])

    def get_video(self):

        # check post has video
        if not self.soup.find("video-player"):
            return

        # find video player and add source to arr
        player = self.soup.find("video-player").find("source")
        if player is not None:
            self.links.append([self.VIDEO, player["src"]])

    def get_photoset(self):

        ps = []
        photos = self.soup.find_all("photo")

        for photo in photos:
            ps.append(photo.find("photo-url").contents[0])

        self.links.append([self.PHOTOSET, ps])

    def get_photo(self):

        if not self.soup.find("photo-url"):
            return

        src = self.soup.find("photo-url").contents[0]
        self.links.append([self.PHOTO, src])

    @staticmethod
    def get_page(url):

        # remove embed
        if "/embed" in url:
            url = url[:-6]

        # remove safe-mode
        if "safe-mode?url=" in url:
            url = url.split("safe-mode?url=")[1]

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
