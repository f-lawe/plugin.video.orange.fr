"""Helpers for Kodi GUI."""

from xbmcgui import ListItem


def create_directory_items(data: list) -> list:
    """Create a list of directory items from data."""
    items = []

    for d in data:
        is_folder = bool(d["is_folder"])

        list_item = ListItem(label=d["label"], path=d["path"])
        list_item.setIsFolder(is_folder)

        if "art" in d:
            list_item.setArt(
                {
                    "poster": d["art"].get("poster", None),
                    "thumb": d["art"].get("thumb", None),
                }
            )

        if not is_folder:
            list_item.setProperties(
                {
                    "inputstream": "inputstream.adaptive",
                    "IsPlayable": "true",
                }
            )

            if "info" in d:
                video_info_tag = list_item.getVideoInfoTag()
                video_info_tag.setDuration(d["info"].get("duration", None))
                video_info_tag.setGenres(d["info"].get("genres", None))
                video_info_tag.setPlot(d["info"].get("plot", None))
                video_info_tag.setYear(d["info"].get("year", None))
                video_info_tag.setPremiered(d["info"].get("premiered", None))

        items.append((d["path"], list_item, is_folder))

    return items


def create_video_item(stream_info: dict) -> ListItem:
    """Create a video item from stream data."""
    list_item = ListItem(path=stream_info["path"])
    list_item.setMimeType(stream_info["mime_type"])
    list_item.setContentLookup(False)
    list_item.setProperty("inputstream", "inputstream.adaptive")
    list_item.setProperty("inputstream.adaptive.play_timeshift_buffer", "true")
    list_item.setProperty("inputstream.adaptive.manifest_config", '{"timeshift_bufferlimit":14400}')
    list_item.setProperty("inputstream.adaptive.license_type", stream_info["license_type"])
    list_item.setProperty("inputstream.adaptive.license_key", stream_info["license_key"])

    return list_item
