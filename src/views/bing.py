"""
    BingViews:
    /i(mage) <term>

"""
from utils.media_sender import ImageSender
import requests, urllib
import config

class BingViews():
    def __init__(self, interface_layer):
        self.image_sender = ImageSender(interface_layer)
        self.routes = [
            ("/i(mage)?\s(?P<term>[^$]+)$", self.bing_image_search)
        ]

    def bing_image_search(self, message, match):
        req = requests.get("https://api.datamarket.azure.com/Bing/Search/v1/Image?Query=%27{}%27&$format=json&$top=1".format(match.group("term")), auth=("",config.bing_api))
        image_url = urllib.unquote(req.json()['d']['results'][0]['MediaUrl'].encode('utf-8'))
        self.image_sender.send_by_url(jid=message.getFrom(), file_url=image_url)
