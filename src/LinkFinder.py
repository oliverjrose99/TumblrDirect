import requests
from bs4 import BeautifulSoup


class LinkFinder:

    UNKNOWN = "UNKNOWN"
    IFRAME = "IFRAME"
    VIDEO = "VIDEO"
    PHOTOSET = "PHOTOSET"
    PHOTO = "PHOTO"

    link = None

    def __init__(self, url):
        self.page = self.get_page(url)
        self.page_xml = BeautifulSoup(self.page, "html.parser")

        if "&lt;iframe " in self.page:
            self.type = self.IFRAME
            self.get_iframe()

        elif "photoset" in self.page:
            self.type = self.PHOTOSET
            self.get_photoset()

        elif "video-player" in self.page:
            self.type = self.VIDEO
            self.get_video()

        elif "photo-url" in self.page:
            self.type = self.PHOTO
            self.get_photo()

        else:
            self.type = self.UNKNOWN

    def get_iframe(self):
        # get iframe
        iframe_start = self.page.find("&lt;iframe ") + 11
        iframe_end = self.page.find("&lt;/iframe&gt;", iframe_start)
        iframe = self.page[iframe_start:iframe_end]

        # replace all ' with "
        iframe = iframe.replace("'", "\"")

        # get src
        src_start = iframe.find("src=\"") + 5
        src_end = iframe.find("\"", src_start)
        self.link = iframe[src_start:src_end]

    def get_video(self):
        # get video player
        video_player = self.page_xml.find_all("video-player")[0].contents[0]

        # find src
        src_start = video_player.find("<source src=\"") + 13
        src_end = video_player.find("\"", src_start)
        self.link = video_player[src_start:src_end]

    def get_photoset(self):
        # get all elements of photo
        photos = self.page_xml.find_all("photo")

        # loop though each photo adding url to arr
        self.link = []
        for i in photos:
            self.link.append(i.contents[0].contents[0])

    def get_photo(self):
        try:
            # find first photo-url element and get its contents
            self.link = self.page_xml.find_all("photo-url")[0].contents[0]
        except:
            self.link = None

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
