#!/usr/bin/python3

import json
import os
import sys
import logging

import praw
import prawcore

from LinkFinder import LinkFinder, ExceptionGettingAPI, MediaNotFound
from PostFormatter import post_formatter


def read_file(loc):
    with open(loc, "r") as f:
        return f.read()


def split_clear(loc):
    f = read_file(loc)
    f = f.split("\n")
    f = list(filter(None, f))
    return f


class TumblrDirect:

    config_loc = "/etc/tumblrdirect/config.json"
    done_loc = "/etc/tumblrdirect/done.txt"
    blacklist_loc = "/etc/tumblrdirect/black.txt"
    pid_loc = "/var/run/td.pid"

    def __init__(self):

        # setup log
        logging.basicConfig(filename="/var/log/td.log", level=logging.INFO)

        # exit if pid found, else write pid
        if os.path.exists(self.pid_loc):
            logging.info("Already running, exiting")
            exit(0)
        else:
            with open(self.pid_loc, "w") as f:
                f.write(str(os.getpid()))

        # load config, done and black list
        self.config = json.loads(read_file(self.config_loc))
        self.done = split_clear(self.done_loc)
        self.blacklist = split_clear(self.blacklist_loc)

        # make praw obj
        self.praw = praw.Reddit(
            client_id=self.config["reddit"]["id"],
            client_secret=self.config["reddit"]["secret"],
            username=self.config["reddit"]["user"],
            password=self.config["reddit"]["pass"],
            user_agent=self.config["reddit"]["user_agent"]
        )

    def run(self):
        for post in self.praw.domain("tumblr.com").new(limit=100):

            # check if not NSFW
            if not post.over_18:
                continue

            # make sure its tumblr post
            if "/post/" not in post.url:
                continue

            # if subreddit or author blacklisted
            if str(post.subreddit).lower() in self.blacklist or str(post.author).lower() in self.blacklist:
                continue

            # if already done
            if post.id in self.done:
                continue
            else:
                self.done.append(post.id)

            try:
                # get post links and caption
                links = LinkFinder(post.url, self.config["tumblr"]["key"])
                post_text = post_formatter(links, post)

                # comment and pin post
                comment = post.reply(post_text)
                logging.info("Made comment on {}".format(post.id))
                comment.mod.distinguish(how='yes', sticky=True)

            except ExceptionGettingAPI as e:
                logging.error("Error getting API page, id: {}, url: {}".format(post.id, links.api_url))

            except MediaNotFound as e:
                logging.error("Error getting media, id: {}, url: {}".format(post.id, post.url))

            except prawcore.Forbidden as e:
                pass

            except Exception as e:
                logging.error("EXCEPTION: {}".format(str(e)))

    def stop(self):
        # only save 100 ids
        self.done = self.done[-100:]

        # write arr to file
        with open(self.done_loc, "w") as f:
            f.write("\n".join(self.done))

        # del pid
        os.remove(self.pid_loc)


if __name__ == '__main__':
    try:

        td = TumblrDirect()
        td.run()
        td.stop()
    except Exception as e:
        print("EXCEPTION")
        print(e)
