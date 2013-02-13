# -*- coding: utf-8 -*-
#
#  files
#  *****
#
# Backend supports for jQuery File Uploader, and implementation of the
# classes executed when an HTTP client contact /files/* URI

from __future__ import with_statement
from twisted.internet import fdesc
from twisted.internet.defer import inlineCallbacks
from cyclone.web import HTTPError, asynchronous, os
from globaleaks.handlers.base import BaseHandler
from globaleaks.utils import log
from globaleaks import settings
from globaleaks.rest.errors import SubmissionGusNotFound, InvalidInputFormat, TipGusNotFound, FileGusNotFound

__all__ = ['Download', 'FileInstance']

# This is different from FileInstance, just because there are a different authentication requirements
class FileAdd(BaseHandler):
    """
    T4
    WhistleBlower interface for upload a new file
    """

    @asynchronous
    @inlineCallbacks
    def get(self, tip_gus, *args):
        """
        Parameters: tip_gus
        Request: None
        Response: Unknown
        Errors: Unknown
        """

        # is this ever used by JQFU ?
        answer = yield FileOperations().get_files(tip_gus)

        self.write(answer['data'])
        self.set_status(200)


    @asynchronous
    @inlineCallbacks
    def post(self, tip_gus, *args):
        """
        Parameter: submission_gus
        Request: Unknown
        Response: Unknown
        Errors: SubmissionGusNotFound, SubmissionConcluded
        """

        answer = yield FileOperations().new_files(tip_gus, self.request, is_tip=True)

        self.write(answer['data'])
        self.set_status(answer['code'])



class FileInstance(BaseHandler):
    """
    U4
    This is the Storm interface to supports JQueryFileUploader stream
    """

    @asynchronous
    @inlineCallbacks
    def get(self, submission_gus, *args):
        """
        Parameters: submission_gus
        Request: None
        Response: Unknown
        Errors: Unknown

        GET return list of files uploaded in this submission
        Doubt: Is this API needed ? because in JQueryFileUploader do not exists
            but in our GL-API-Style design could. At the moment the client
            do not plan to use them.
        """

        # is this ever used by JQFU ?
        answer = yield FileOperations().get_files(submission_gus)

        self.write(answer['data'])
        self.set_status(200)


    @asynchronous
    @inlineCallbacks
    def post(self, submission_gus, *args):
        """
        Parameter: submission_gus
        Request: Unknown
        Response: Unknown
        Errors: SubmissionGusNotFound, SubmissionConcluded
        """

        answer = yield FileOperations().new_files(submission_gus, self.request, is_tip=False)

        self.write(answer['data'])
        self.set_status(answer['code'])

        self.finish()


class Download(BaseHandler):

    @asynchronous
    @inlineCallbacks
    def get(self, tip_gus, CYCLON_DIRT, file_gus, *uriargs):

        # tip_gus needed to authorized the download
        print tip_gus, file_gus

        answer = yield FileOperations().get_file_access(tip_gus, file_gus)

        # verify if receiver can, in fact, download the file, otherwise
        # raise DownloadLimitExceeded

        fileContent = answer['data']
        # keys:  'content'  'sha2sum'  'size' : 'content_type' 'file_name'

        self.set_status(answer['code'])

        self.set_header('Content-Type', fileContent['content_type'])
        self.set_header('Content-Length', fileContent['size'])
        self.set_header('Etag', '"%s"' % fileContent['sha2sum'])

        filelocation = os.path.join(settings.config.advanced.submissions_dir, file_gus)

        chunk_size = 8192
        filedata = ''
        with open(filelocation, "rb") as requestf:
            fdesc.setNonBlocking(requestf.fileno())
            while True:
                chunk = requestf.read(chunk_size)
                filedata += chunk
                if len(chunk) == 0:
                    break

        self.write(filedata)
        self.finish()
