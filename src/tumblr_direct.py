#!/usr/bin/python3

import json
import praw
import sys
import os

from link_finder import LinkFinder
from post_formatter import post_formatter


class TumblrDirect:

    PATH = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, configloc):
        # load config
        self.config = json.load(open(self.PATH + configloc))

        # load already done and blacklist
        self.done = open(self.PATH + self.config["files"]["done"]).read().split("\n")
        self.done = list(filter(None, self.done))  # clear blank lines
        self.blacklist = open(self.PATH + self.config["files"]["blacklist"]).read().split("\n")

        # make praw
        try:
            self.praw = praw.Reddit(username=self.config["reddit"]["user"],
                                    password=self.config["reddit"]["pass"],
                                    client_id=self.config["reddit"]["id"],
                                    client_secret=self.config["reddit"]["secret"],
                                    user_agent=self.config["reddit"]["user_agent"])

        # log error and exit
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def start(self):
        # get posts
        posts = self.praw.domain("tumblr.com").new()

        # loop though each post
        for post in posts:
            # check if over_18
            if not post.over_18:
                continue

            # check if sub-reddit blacklisted
            if str(post.subreddit).lower() in self.blacklist or str(post.author) in self.blacklist:
                continue

            # make sure its a post
            if "/post/" not in post.url:
                continue

            # make sure its not already done else add it to done list
            if post.id in self.done:
                continue
            else:
                self.done.append(post.id)

            # get links and caption
            post_links = LinkFinder(post.url)

            if post_links.error:
                print("Error finding links, {}".format(post.permalink))
                continue

            # make post text
            post_body = post_formatter(post_links, post)

            # make comment
            try:
                comment = post.reply(post_body)
            except Exception as e:
                print("Error posting reply, {}".format(str(e)))
                continue

            # try sticking comment
            try:
                comment.mod.distinguish(how='yes', sticky=True)
            except Exception:
                pass

    def stop(self):
        # write done arr to file
        with open(self.PATH + self.config["files"]["done"], "w") as file:
            for id in self.done:
                file.write(id + "\n")


if __name__ == "__main__":

    # bad practice but helps in development
    try:
        bot = TumblrDirect("/configs/config.json")
        bot.start()
        bot.stop()
    except Exception as e:
        print(str(e))
