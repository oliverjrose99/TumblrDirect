#!/usr/bin/python3

import logging
import signal
import time
import json
import praw
import sys

from link_finder import LinkFinder
from post_formatter import post_formatter


class TumblrDirect:

    running = True

    def __init__(self, configloc):
        # load config
        self.config = json.load(open(configloc))

        # load already done and blacklist
        self.done = open(self.config["files"]["done"]).read().split("\n")
        self.done = list(filter(None, self.done))  # clear blank lines
        self.blacklist = open(self.config["files"]["blacklist"]).read().split("\n")

        # reg signals
        signal.signal(signal.SIGTERM, self.handler)
        signal.signal(signal.SIGINT, self.handler)

        # make logger
        logging.basicConfig(filename=self.config["files"]["log"],
                            level=logging.INFO,
                            format='%(asctime)s %(levelname)s - %(message)s',
                            datefmt="%Y/%m/%d %H-%M-%S")

        # make praw
        try:
            self.praw = praw.Reddit(username=self.config["reddit"]["user"],
                                    password=self.config["reddit"]["pass"],
                                    client_id=self.config["reddit"]["id"],
                                    client_secret=self.config["reddit"]["secret"],
                                    user_agent=self.config["reddit"]["user_agent"])

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

                # check if still running
                if not self.running:
                    break

                # get links and caption
                post_links = LinkFinder(post.url)

                if post_links.error:
                    logging.log(logging.ERROR, "Error finding links, {}".format(post.permalink))
                    continue

                # make post text
                post_body = post_formatter(post_links, post)

                # make comment
                try:
                    comment = post.reply(post_body)
                except Exception as e:
                    logging.log(logging.ERROR, "Error posting reply, {}".format(str(e)))
                    continue

                # try sticking comment
                try:
                    comment.mod.distinguish(how='yes', sticky=True)
                except:
                    pass

    def stop(self):
        # write done arr to file
        with open(self.config["files"]["done"], "w") as file:
            for id in self.done:
                file.write(id + "\n")


if __name__ == "__main__":

    bot = TumblrDirect("configs/config.json")

    # bad practice but helps in development
    try:
        bot.start()
    except Exception as e:
        with open("configs/crash.log", "a") as f:
            f.write(str(e))

    bot.stop()
