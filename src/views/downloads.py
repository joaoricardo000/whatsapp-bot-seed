"""
    Media download request views.

    Handles the media url messages with utilities classes for it.
"""
from utils.media_downloader import ImageSender, VideoSender, YoutubeSender, UrlPrintSender


class MediaViews():
    def __init__(self, interface_layer):
        """
            Creates the regex routes and callbacks to handle media messages
        """
        self.image_sender = ImageSender(interface_layer)
        self.video_sender = VideoSender(interface_layer)
        self.yt_sender = YoutubeSender(interface_layer)
        self.url_print_sender = UrlPrintSender(interface_layer)
        self.routes = [
            ("https?:\/\/(?:[\w\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:jpe?g|gif|png)($|\?[^\s]+$)", self.send_image),
            ("https?:\/\/(?:[\w\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:mp4|webm)($|\?[^\s]+$)", self.send_video),
            ("youtu(?:be.com\/watch\?v=|\.be/)(?P<video_id>\w+)(&\S*)?$", self.send_yt_video),
            ("^https?:\/\/(?:www\.)?[^$]+$", self.send_url_print)
        ]

    def send_video(self, message, match):
        self.video_sender.send_by_url(jid=message.getFrom(), file_url=message.getBody())

    def send_yt_video(self, message, match):
        self.yt_sender.send_by_url(jid=message.getFrom(), file_url=match.group("video_id"))

    def send_image(self, message, match):
        self.image_sender.send_by_url(jid=message.getFrom(), file_url=message.getBody())

    def send_url_print(self, message, match):
        self.url_print_sender.send_by_url(jid=message.getFrom(), file_url=message.getBody())
