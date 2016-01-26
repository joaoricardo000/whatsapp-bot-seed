"""
    The Media Sender Utilities

    The MediaSender superclass handles the download, upload to whatsapp server and delivery to the receipt
    The subclasses VideoSender, ImageSender and YoutubeSender extends it to configure media type.
"""
from yowsup.layers.protocol_media.mediauploader import MediaUploader
from yowsup.layers.protocol_media.protocolentities.iq_requestupload import RequestUploadIqProtocolEntity
from yowsup.layers.protocol_media.protocolentities.message_media_downloadable import \
    DownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities.message_media_downloadable_image import \
    ImageDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities.message_media_downloadable_video import \
    VideoDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities.message_media_downloadable_audio import \
    AudioDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

import subprocess
import time
import os
import logging
import requests
import shutil
import hashlib
import re
import config
from pytube import YouTube


class MediaSender():
    """
        This is a superclass that does the job of download/upload a media type.
        The classes bellow extends it and are used by the views.
    """

    def __init__(self, interface_layer, storage_path=config.media_storage_path):
        """
            The construction method receives the interface_layer (RouteLayer), so it can access the protocol methods
            to upload and send the media files
        """
        self.interface_layer = interface_layer
        self.storage_path = storage_path
        self.file_extension_regex = re.compile("^.*\.([0-9a-z]+)(?:[\?\/][^\s]*)?$")
        self.MEDIA_TYPE = None

    def send_by_url(self, jid, file_url, caption=None):
        """ Downloads and send a file_url """
        try:
            # self.interface_layer.toLower(TextMessageProtocolEntity("{...}", to=jid))
            file_path = self._download_file(file_url)
            self.send_by_path(jid, file_path, caption)
        except Exception as e:
            logging.exception(e)
            self._on_error(jid)

    def send_by_path(self, jid, path, caption=None):
        """
            Send a file by its absolute path.

            Creates a RequestUpload entity, that will verify if the media has already been uploaded.
            Then calls the _on_upload_result.
        """
        entity = RequestUploadIqProtocolEntity(self.MEDIA_TYPE, filePath=path)
        success_callback = lambda successEntity, originalEntity: self._on_upload_result(jid, path, successEntity,
                                                                                        originalEntity, caption)
        err_callback = lambda errorEntity, originalEntity: self._on_error(jid)
        self.interface_layer._sendIq(entity, success_callback, err_callback)

    def _download_file(self, file_url):
        """
            This method check for duplicate file before downloading,
            If not downloaded, download it, saves locally and returns the path
        """
        file_path = self._build_file_path(file_url)
        if not os.path.isfile(file_path):
            response = requests.get(file_url, stream=True)
            with open(file_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        return file_path

    def _on_upload_result(self, jid, file_path, upload_result, requestUploadIqProtocolEntity, caption=None):
        """
            If the file has never been uploaded, will be uploaded and then call the _do_send_file
        """
        if upload_result.isDuplicate():
            self._do_send_file(file_path, upload_result.getUrl(), jid, upload_result.getIp(), caption)
        else:
            callback = lambda file_path, jid, url: self._do_send_file(file_path, url, jid, upload_result.getIp(),
                                                                      caption)
            mediaUploader = MediaUploader(jid, self.interface_layer.getOwnJid(), file_path,
                                          upload_result.getUrl(),
                                          upload_result.getResumeOffset(),
                                          callback, self._on_error, self._on_upload_progress, async=True)
            mediaUploader.start()

    def _do_send_file(self, file_path, url, to, ip=None, caption=None):
        """
            Now the media file has been uploaded and the whatsapp server returns a media_path.
            The media_path is then sent to the receipt.
        """
        entity = None
        if self.MEDIA_TYPE == DownloadableMediaMessageProtocolEntity.MEDIA_TYPE_VIDEO:
            entity = VideoDownloadableMediaMessageProtocolEntity.fromFilePath(file_path, url, self.MEDIA_TYPE, ip, to)
        elif self.MEDIA_TYPE == DownloadableMediaMessageProtocolEntity.MEDIA_TYPE_IMAGE:
            entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(file_path, url, ip, to, caption=caption)
        elif self.MEDIA_TYPE == DownloadableMediaMessageProtocolEntity.MEDIA_TYPE_AUDIO:
            entity = AudioDownloadableMediaMessageProtocolEntity.fromFilePath(file_path, url, ip, to)
        self.interface_layer.toLower(entity)

    def _on_upload_progress(self, filePath, jid, url, progress):
        if progress % 50 == 0:
            logging.info("[Upload progress]%s => %s, %d%% \r" % (os.path.basename(filePath), jid, progress))

    def _on_error(self, jid, *args, **kwargs):
        self.interface_layer.toLower(TextMessageProtocolEntity("{!}", to=jid))

    def _get_file_ext(self, url):
        return self.file_extension_regex.findall(url)[0]

    def _build_file_path(self, url):
        id = hashlib.md5(url).hexdigest()
        return ''.join([self.storage_path, id, ".", self._get_file_ext(url)])


class VideoSender(MediaSender):
    def __init__(self, interface_layer):
        MediaSender.__init__(self, interface_layer)
        self.MEDIA_TYPE = RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO


class AudioSender(MediaSender):
    def __init__(self, interface_layer):
        MediaSender.__init__(self, interface_layer)
        self.MEDIA_TYPE = RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO


class ImageSender(MediaSender):
    def __init__(self, interface_layer):
        MediaSender.__init__(self, interface_layer)
        self.MEDIA_TYPE = RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE


class YoutubeSender(VideoSender):
    """
        Uses pytube to download youtube videos
    """

    def _download_file(self, video_id):
        file_path = self._build_file_path(video_id)
        if not os.path.isfile(file_path):
            yt = YouTube()
            yt.from_url("http://youtube.com/watch?v=" + video_id)
            video = yt.filter('mp4')[0]
            video.download(file_path)
        return file_path

    def _build_file_path(self, video_id):
        return ''.join([self.storage_path, video_id, ".mp4"])


class UrlPrintSender(ImageSender):
    """
        Uses wkhtmltoimage to printscreen a webpage
    """

    def _download_file(self, page_url):
        page_url = page_url.replace('"', "'")
        file_path = self._build_file_path(page_url)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        if not os.path.isfile(file_path):
            cmd = 'pageres "%s" 1024x2300 --crop  --filename=%s' % (page_url, file_name)
            p = subprocess.Popen(cmd, shell=True, cwd=self.storage_path)
            p.wait()
        return file_path

    def _build_file_path(self, page_url):
        id = hashlib.md5(page_url).hexdigest()
        return ''.join([self.storage_path, id, str(int(time.time()))[:-2], ".png"])


class EspeakTtsSender(AudioSender):
    """
        Uses espeak to text to speach
    """

    def send(self, jid, text, lang='en'):
        text = text.replace("'", '"')
        try:
            file_path = self.tts_record(text, lang)
            self.send_by_path(jid, file_path)
        except Exception as e:
            logging.exception(e)
            self._on_error(jid)

    def tts_record(self, text, lang='en'):
        file_path = self._build_file_path(text)
        cmd = "espeak -v%s -w %s '%s'" % (lang, file_path, text)
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).wait()
        return file_path

    def _build_file_path(self, text):
        id = hashlib.md5(text).hexdigest()
        return ''.join([self.storage_path, id, ".wav"])