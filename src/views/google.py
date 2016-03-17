"""
    GoogleViews:
    /s(earch) <term>
    /i(mage) <term>
    youtube urls
    /tr(anslate) <what> <lang>

"""
from utils.media_sender import EspeakTtsSender, ImageSender, VideoSender, YoutubeSender, UrlPrintSender
import requests, urllib
from GoogleTranslate import translate
from yowsup.layers.protocol_messages.protocolentities.message_text import TextMessageProtocolEntity #msg sender


class GoogleViews():
    def __init__(self, interface_layer):
        self.image_sender = ImageSender(interface_layer)
        self.video_sender = VideoSender(interface_layer)
        self.yt_sender = YoutubeSender(interface_layer)
        self.url_print_sender = UrlPrintSender(interface_layer)
        self.tts_sender = EspeakTtsSender(interface_layer)
        self.routes = [
            (".*https?:\/\/(?:www\.|m\.)?youtu(?:be.com\/watch\?v=|\.be/)(?P<video_id>[\w-]+)(&\S*)?$",
             self.send_yt_video),
            ("/s(earch)?\s(?P<term>[^$]+)$", self.google_search),
            ("/tr(anslate)?\s(?P<what>[^$]+)\s(?P<lang>[^$]+)$", self.translate),
        ]

    def send_yt_video(self, message, match):
        self.yt_sender.send_by_url(jid=message.getFrom(), file_url=match.group("video_id"))

    def google_search(self, message, match):
        req = requests.get("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % match.group("term"))
        page_url = urllib.unquote(req.json()["responseData"]["results"][0]["url"])
        self.url_print_sender.send_by_url(jid=message.getFrom(), file_url=page_url)
        
    def translate(self, message=None, match=None, to=None):
	    what = match.group("what") #Saves what to translate
        lang = match.group("lang") #Saves which language
        translateoutput = translate(what,lang,"auto") #Translate :P
        translateoutputf = str(translateoutput) 
        translateoutputf1 = translateoutputf.replace("&quot;", "") #Delete &quot;
        tts_text = translateoutputf1 #Set's text-to-speech text
        self.tts_sender.send(jid=message.getFrom(), text=tts_text, lang=lang) #Generate in another file a speech and upload it to sender
        
        msgts = "Translated\nOrg Text: " + what + "\nTranslated: " + translateoutputf1
        return TextMessageProtocolEntity(msgts, to=message.getFrom()) #Send message to sender
