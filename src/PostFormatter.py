def post_formatter(links, post):

    body = ""
    photo_idx = 1

    for link in links.links:

        if link["type"] == links.PHOTO:
            body += "[Direct link, Photo {}]({})\n\n".format(str(photo_idx), link["url"])
            photo_idx += 1

        elif link["type"] == links.VIDEO:
            body += "[Direct link, Video]({})\n\n".format(link["url"])

        elif link["type"] == links.IFRAME:
            body += "[Embedded link, Semi-direct]({})\n\n".format(link["url"])

    # don't post caption if its the same as the post title, add \n\n in comparison
    if links.caption is not None:
        if links.caption != (post.title + "\n\n"):
            body += links.caption + "\n\n"

    body += "---\n\n"  # horizontal line
    body += "^(Bot by /u/oliverjrose99) ^| "  # bot ID
    body += "[^About ^& ^Source](https://github.com/oliverjrose99/TumblrDirect) ^| "  # about and source link
    body += "[^Report ^Issue](http://www.reddit.com/message/compose?to=oliverjrose99&subject=Tumblr+Direct+Issue&message=Link:%20{}%0AAdd%20message%20if%20needed)".format(post.permalink)  # report issue link

    return body
