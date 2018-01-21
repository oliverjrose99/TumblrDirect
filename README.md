# Tumblr Direct
A Reddit bot written in Python which takes NSFW Tumblr posts and posts the direct links in the comments.

## Requirements
* Python 3
* PRAW
* BeautifulSoup4
* Html2text

## Why
Because people/bots post links on Reddit to Tumblr posts which, when opened, will either redirect to ads or the post will have ads around it. As soon as you click or even look at it funny, your PC/mobile will have aids, there will be horny single moms in your area and The Real Fuckbook will be back. Many of the subreddits this bot works on are either abandoned by the mods or the mods don't care.

## Blacklist Addition/Removal
This bot works by looking at the domain stream produced by Reddit, e.g. reddit.com/domain/example.com/. As such a number of subreddits have been blacklisted, either at request or as they are properly moderated and don't require this bot.

If you would like to be added to or removed from the blacklist, please message me on Github or Reddit at [/u/oliverjrose99](https://www.reddit.com/user/oliverjrose99). You could also just block the bot from the subreddit 

# Auto Pinning
If the bot is a moderator of the subreddit it will automatically pin the comment to the top of the thread. Send a mod request with post permissions and when accepted it will automatically do this. 