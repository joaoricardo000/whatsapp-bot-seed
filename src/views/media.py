"""
    Media download request views.

    Handles the media url messages with utilities classes for it.
"""
import urlparse
import hashlib
import config
import subprocess
from utils.media_sender import ImageSender, VideoSender, YoutubeSender, UrlPrintSender, GoogleTtsSender


class MediaViews():
    def __init__(self, interface_layer):
        """
            Creates the regex routes and callbacks to handle media messages
        """
        self.image_sender = ImageSender(interface_layer)
        self.video_sender = VideoSender(interface_layer)
        self.url_print_sender = UrlPrintSender(interface_layer)
        self.routes = [
            ("https?:\/\/(?:[\w\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:jpe?g|gif|png)($|\?[^\s]+$)", self.send_image),
            ("https?:\/\/(?:[\w\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:mp4|webm)($|\?[^\s]+$)", self.send_video),
            ("https?:\/\/[^$]+$", self.send_url_print),
            ("^/t(ts)?\s(?P<tts_text>[^$]+)$", self.send_tts),
        ]

    def send_video(self, message, match):
        self.video_sender.send_by_url(jid=message.getFrom(), file_url=message.getBody())

    def send_image(self, message, match):
        self.image_sender.send_by_url(jid=message.getFrom(), file_url=message.getBody())

    def send_url_print(self, message, match):
        url = message.getBody()
        self.url_print_sender.send_by_url(jid=message.getFrom(), file_url=url)
    
    def send_tts(self, message, match):
        name = hashlib.md5(match.group("tts_text")).hexdigest() + ".wav"
        cmd = "espeak \"" + match.group("tts_text") + "\" --stdout -ven+f2 -s150 -p80 > " + config.media_storage_path + name
        tts = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        tts.wait()
        self.video_sender.send_by_path(jid=message.getFrom(), path=config.media_storage_path + name)
