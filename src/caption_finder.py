import tomd


def caption_finder(page, xml):

    if "<photo-caption>" in page:
        caption = xml.find("photo-caption").contents[0]
    elif "<video-caption>" in page:
        caption = xml.find("video-caption").contents[0]
    else:
        return None

    return tomd.convert(caption)
