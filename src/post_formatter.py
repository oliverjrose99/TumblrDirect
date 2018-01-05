def post_formatter(link_finder, permalink):
    body = ""

    # if photoset
    if link_finder.type == 1:
        for idx, link in enumerate(link_finder.links):
            body += "[Direct link, Image {}]({})\n\n".format(idx + 1, link)

    else:  # all other post types
        for link in link_finder.links:
            if link[0] == 3:  # iframe
                body += "[Embedded link, Semi-direct]({})\n\n".format(link[1])

            elif link[0] == 2:  # video
                body += "[Direct link, Video]({})\n\n".format(link[1])

            elif link[0] == 0:  # single photo
                body += "[Direct link, Image]({})\n\n".format(link[1])

    if link_finder.caption is not None:
        body += link_finder.caption + "\n\n"

    body += "---\n\n"  # horizontal line
    body += "^(Bot by /u/oliverjrose99) ^| "  # bot ID
    body += "[^About ^& ^Source](https://github.com/oliverjrose99/TumblrDirect) ^| "  # about and source link
    body += "[^Report ^Issue](http://www.reddit.com/message/compose?to=oliverjrose99&subject=Tumblr+Direct+Issue&message=Link:%20{}%0AAdd%20message%20if%20needed)".format(permalink)  # report issue link

    return body