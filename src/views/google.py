"""
    GoogleViews:
    /s(earch) <term>
    /i(mage) <term>
    /t(ts) <text>
    youtube urls

"""
from utils.media_sender import ImageSender, VideoSender, YoutubeSender, UrlPrintSender, GoogleTtsSender
import requests, urllib


class GoogleViews():
    def __init__(self, interface_layer):
        self.image_sender = ImageSender(interface_layer)
        self.video_sender = VideoSender(interface_layer)
        self.yt_sender = YoutubeSender(interface_layer)
        self.url_print_sender = UrlPrintSender(interface_layer)
        self.google_tts_sender = GoogleTtsSender(interface_layer)
        self.routes = [
            (".*https?:\/\/(?:www\.|m\.)?youtu(?:be.com\/watch\?v=|\.be/)(?P<video_id>[\w-]+)(&\S*)?$",
             self.send_yt_video),
            ("/t(ts)?\s(?P<text>[^\[]{1,500})\s?\[?(?P<lang>[A-Za-z\-]{2,6})?\]?$", self.send_tts),
            ("/s(earch)?\s(?P<term>[^$]+)$", self.google_search),
            #("/i(mage)?\s(?P<term>[^$]+)$", self.google_image_search)
        ]

    def send_yt_video(self, message, match):
        self.yt_sender.send_by_url(jid=message.getFrom(), file_url=match.group("video_id"))

    def send_tts(self, message, match):
        self.google_tts_sender.send(jid=message.getFrom(), text=match.group("text"), lang=match.group("lang"))

    def google_search(self, message, match):
        req = requests.get("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % match.group("term"))
        page_url = urllib.unquote(req.json()["responseData"]["results"][0]["url"])
        self.url_print_sender.send_by_url(jid=message.getFrom(), file_url=page_url)

    def google_image_search(self, message, match):
        req = requests.get("http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s" % match.group("term"))
        image_url = urllib.unquote(req.json()["responseData"]["results"][0]["url"])
        self.image_sender.send_by_url(jid=message.getFrom(), file_url=image_url)
