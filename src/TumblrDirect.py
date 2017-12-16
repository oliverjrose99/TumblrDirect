import logging
import signal
import json
import praw
import sys

from LinkFinder import LinkFinder


class TumblrDirect:

    running = True

    def __init__(self, configloc):
        # load config
        self.config = json.load(open(configloc))

        # load already done and blacklist
        self.done = open(self.config["done_loc"]).read().split("\n")
        self.done = list(filter(None, self.done))  # clear blank lines
        self.blacklist = open(self.config["blacklist_loc"]).read().split("\n")

        # reg signals
        signal.signal(signal.SIGTERM, self.handler)
        signal.signal(signal.SIGINT, self.handler)

        # make logger
        logging.basicConfig(filename=self.config["log_loc"],
                            level=logging.INFO,
                            format='%(asctime)s %(levelname)s - %(message)s',
                            datefmt="%Y/%m/%d %H-%M-%S")

        # make praw
        try:
            self.praw = praw.Reddit(username=self.config["user"],
                                    password=self.config["pass"],
                                    client_id=self.config["id"],
                                    client_secret=self.config["secret"],
                                    user_agent=self.config["user_agent"])
        except Exception as e:
            # log error and exit
            logging.log(logging.CRITICAL, "Exception making praw object, {}".format(str(e)))
            sys.exit(1)

    def handler(self, signum, frame):
        logging.log(logging.INFO, "Signal caught, stopping loop")
        self.running = False

    def start(self):
        # main loop
        while self.running:
            # get posts
            posts = self.praw.domain("tumblr.com").new()

            # loop though each post
            for post in posts:
                # check if over_18
                if not post.over_18:
                    continue

                # check if sub-reddit blacklisted
                if post.subreddit in self.blacklist:
                    continue

                # make sure its a post
                if "/post/" not in post.url:
                    continue

                # make sure its not already done else add it to done list
                if post.id in self.done:
                    continue
                else:
                    self.done.append(post.id)

                # get links
                post_links = LinkFinder(post.url)
                if post_links.type == LinkFinder.UNKNOWN:
                    logging.log(logging.ERROR, "Issue finding links, {}".format(post.permalink))
                    continue

                post_body = ""

                # make post format and text
                if post_links.type == LinkFinder.IFRAME:
                    post_body += "[Embedded link]({})  \n".format(post_links.link)
                    post_body += "Note: This link may still open ads"
                elif post_links.type == LinkFinder.VIDEO:
                    post_body += "[Direct link, Video]({})".format(post_links.link)
                elif post_links.type == LinkFinder.PHOTO:
                    post_body += "[Direct link, Photo]({})".format(post_links.link)
                elif post_links.type == LinkFinder.PHOTOSET:
                    # loop though each photo, adding link to body
                    for idx, link in enumerate(post_links.link):
                        post_body += "[Direct link, Photo {}]({})  \n".format(idx + 1, link)

                post_body += "  \n  \n---  \n  \n"  # horizontal line
                post_body += "^(Bot by /u/oliverjrose99) ^| "  # bot ID
                post_body += "[^About ^& ^Source](https://github.com/oliverjrose99/TumblrDirect) ^| "  # about and source link
                post_body += "[^Report ^Issue](http://www.reddit.com/message/compose?to=oliverjrose99&subject=Tumblr+Direct+Issue&message=Link:%20{}%0AAdd%20message%20if%20needed)".format(post.permalink)  # report issue link

                print(post_body)

    def stop(self):
        with open(self.config["done_loc"], "w") as file:
            for id in self.done:
                file.write(id + "\n")


if __name__ == "__main__":
    bot = TumblrDirect("configs/config.json")
    bot.start()
    bot.stop()
