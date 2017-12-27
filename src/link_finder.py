import requests
from bs4 import BeautifulSoup


class LinkFinder:

    PHOTO = 0
    PHOTOSET = 1
    VIDEO = 2
    IFRAME = 3

    def __init__(self, url):
        self.page = self.get_page(url)
        self.page_xml = BeautifulSoup(self.page, "html.parser")

        self.links = []
        self.error = False
        self.type = -1

        if "&lt;iframe src=\"" in self.page:
            self.type = self.IFRAME
            self.get_iframe()

            try:
                self.get_photo()  # try getting photo, might not exist
            except:
                pass

        elif "<video-player>" in self.page:
            self.type = self.VIDEO
            self.get_video()

        elif "<photoset>" in self.page:
            self.type = self.PHOTOSET
            self.get_photoset()

        elif "<photo-url" in self.page:
            self.type = self.PHOTO
            self.get_photo()

        else:
            self.error = True

    def get_iframe(self):
        count = self.page.count("&lt;iframe src=\"")
        last = 0

        # loop though each iframe
        for i in range(count):
            start = self.page.find("&lt;iframe src=\"", last) + 16
            end = self.page.find("\"", start)

            self.links.append([self.IFRAME, self.page[start:end]])
            last = end

    def get_video(self):
        # get first video and contents
        video = self.page_xml.find("video-player")
        contents = video.contents[0]

        # find src
        src_start = contents.find("<source src=\"") + 13
        src_end = contents.find("\"", src_start)

        self.links.append([self.VIDEO, contents[src_start:src_end]])

    def get_photoset(self):
        photoset = self.page_xml.find("photoset")

        # loop though photos in photoset
        for photo in photoset.children:
            self.links.append(photo.find("photo-url").contents[0])

    def get_photo(self):
        self.links.append([self.PHOTO, self.page_xml.find("photo-url").contents[0]])

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
