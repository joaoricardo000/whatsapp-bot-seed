"""
    The Media Downloader Utilities

    The Media Sender Superclass handles the download, upload to whataspp server and delivery to the receipt
    The subclasses VideoSender, ImageSender and YoutubeSender extends it to configure media type.
"""
import subprocess

from yowsup.layers.protocol_media.mediauploader import MediaUploader
from yowsup.layers.protocol_media.protocolentities.iq_requestupload import RequestUploadIqProtocolEntity
from yowsup.layers.protocol_media.protocolentities.message_media_downloadable import \
    DownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities.message_media_downloadable_image import \
    ImageDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities.message_media_downloadable_video import \
    VideoDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

import sys
import os
import logging
import requests
import shutil
import hashlib
import re
import time
import config
from pytube import YouTube

logger = logging.getLogger(__name__)


class MediaSender():
    """
        This class has two main public methods:
        send_by_url and send_by_path.
        As the name says, they send a media file by url, or path.
    """

    def __init__(self, interface_layer, storage_path=config.media_storage_path):
        """
            The construction method receives the interface_layer (RouteLayer), so it can access the protocol methods
            to upload and send the media files
        """
        self.interface_layer = interface_layer
        self.storage_path = storage_path
        self.file_extension_regex = re.compile("\.([0-9a-z]+)($|\?[^\s]*$)")
        self.MEDIA_TYPE = None

    def send_by_url(self, jid, file_url):
        """ Downloads and send a file_url """
        self.interface_layer.toLower(TextMessageProtocolEntity("{ Downloading [%s]... }" % self.MEDIA_TYPE, to=jid))
        file_path = self._download_file(file_url)  # downloads and save locally
        self.send_by_path(jid, file_path)

    def send_by_path(self, jid, path):
        """
            Send a file by its absolute path.

            Creates a RequestUpload entity, that will verify if the media has already been uploaded.
            Then calls the _on_upload_result.
        """
        entity = RequestUploadIqProtocolEntity(self.MEDIA_TYPE, filePath=path)
        success_callback = lambda upload_result, request_entity: self._on_upload_request_result(jid, path,
                                                                                                upload_result,
                                                                                                request_entity)
        err_callback = lambda error_result, request_entity: self._on_error(jid)
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

    def _on_upload_request_result(self, jid, file_path, upload_result, request_entity):
        """
            If the file has never been uploaded, will be uploaded and then call the _do_send_file
        """
        if upload_result.isDuplicate():
            self._do_send_file(file_path, upload_result.getUrl(), jid, upload_result.getIp())
        else:
            callback = lambda media_path, jid, url: self._do_send_file(media_path, url, jid, upload_result.getIp())
            mediaUploader = MediaUploader(jid, self.interface_layer.getOwnJid(), file_path,
                                          upload_result.getUrl(),
                                          upload_result.getResumeOffset(),
                                          callback, self._on_error, self._on_upload_progress, async=True)
            mediaUploader.start()

    def _do_send_file(self, media_path, url, to, ip=None, caption=None):
        """
            Now the media file has been uploaded and the whatsapp server returns a media_path.
            The media_path is then sent to the receipt.
        """
        entity = None
        if self.MEDIA_TYPE == DownloadableMediaMessageProtocolEntity.MEDIA_TYPE_VIDEO:
            entity = VideoDownloadableMediaMessageProtocolEntity.fromFilePath(media_path, url, self.MEDIA_TYPE, ip, to)
        elif self.MEDIA_TYPE == DownloadableMediaMessageProtocolEntity.MEDIA_TYPE_IMAGE:
            entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(media_path, url, ip, to, caption=caption)
        self.interface_layer.toLower(entity)

    def _on_upload_progress(self, filePath, jid, url, progress):
        sys.stdout.write("%s => %s, %d%% \r" % (os.path.basename(filePath), jid, progress))
        sys.stdout.flush()

    def _on_error(self, jid, *args, **kwargs):
        error_message = "{! Sorry, error processing request for [%s]... }" % self.MEDIA_TYPE
        self.interface_layer.toLower(TextMessageProtocolEntity(error_message, to=jid))

    def _get_file_ext(self, url):
        return self.file_extension_regex.findall(url)[0][0]

    def _build_file_path(self, url):
        id = hashlib.md5(url).hexdigest()
        return ''.join([self.storage_path, id, ".", self._get_file_ext(url)])


class VideoSender(MediaSender):
    def __init__(self, interface_layer):
        MediaSender.__init__(self, interface_layer)
        self.MEDIA_TYPE = RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO


class ImageSender(MediaSender):
    def __init__(self, interface_layer):
        MediaSender.__init__(self, interface_layer)
        self.MEDIA_TYPE = RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE


class YoutubeSender(VideoSender):
    def _download_file(self, video_id):
        file_path = self._build_file_path(video_id)
        if not os.path.isfile(file_path):
            yt = YouTube()
            yt.from_url("http://youtube.com/watch?v=" + video_id)
            yt.filter('mp4')[0].download(file_path)  # downloads the mp4 with lowest quality
        return file_path

    def _build_file_path(self, video_id):
        return ''.join([self.storage_path, video_id, ".mp4"])


class UrlPrintSender(ImageSender):
    def _download_file(self, page_url):
        file_path = self._build_file_path(page_url)
        if not os.path.isfile(file_path):
            cmd = "wkhtmltoimage --load-error-handling ignore --height 1500 %s %s" % (page_url, file_path)
            p = subprocess.Popen(cmd, shell=True)
            p.wait()
        return file_path

    def _build_file_path(self, page_url):
        id = hashlib.md5(page_url).hexdigest()
        return ''.join([self.storage_path, id, time.strftime("%d_%m_%H_%M"), ".jpeg"])
