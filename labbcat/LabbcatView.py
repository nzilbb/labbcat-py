import json
import os
import re
import requests
import tempfile
import time
from zipfile import ZipFile
from labbcat.Response import Response
from labbcat.ResponseException import ResponseException
from labbcat import __version__

class LabbcatView:
    """ API for querying a `LaBB--CAT <https://labbcat.canterbury.ac.nz/>`_ annotation graph
    store; a database of linguistic transcripts represented using 
    `Annotation Graphs <https://nzilbb.github.io/ag/>`_
    
    This interface provides only *read-only* operations, i.e. those that can be performed
    by users with "view" permission.

    Constructor arguments:    
    
    :param labbcatUrl: The 'home' URL of the LaBB-CAT server.
    :type labbcatUrl: str
    
    :param username: The username for logging in to the server, if necessary.
    :type username: str or None
    
    :param password: The password for logging in to the server, if necessary.
    :type password: str or None
    
    Attributes:
        language: The language code for server message localization, e.g. "es-AR"
    
    Example:: 
        
        import labbcat
        
        # create annotation store client
        corpus = labbcat.LabbcatView("https://labbcat.canterbury.ac.nz", "demo", "demo");
        
        # show some basic information
        
        print("Information about LaBB-CAT at " + corpus.getId())
        
        layerIds = corpus.getLayerIds()
        for layerId in layerIds: 
            print("layer: " + layerId) 
        
        corpora = corpus.getCorpusIds()
        for c in corpora:
            print("transcripts in: " + c)
            for transcript in corpus.getTranscriptIdsInCorpus(c):
                print(" " + transcript)

    """
    
    def __init__(self, labbcatUrl, username=None, password=None):
        """ Constructor. """

        if labbcatUrl.endswith("/"):
            self.labbcatUrl = labbcatUrl
        else:
            self.labbcatUrl = labbcatUrl + "/"
            
        self.username = username
        self.password = password
        self.verbose = False
        self.language = "en"

    def _labbcatUrl(self, resource):
        return self.labbcatUrl + resource

    def _storeQueryUrl(self, resource):
        return self.labbcatUrl + "api/store/" + resource

    def _getRequest(self, url, params):
        if self.verbose: print("_getRequest " + url + " : " + str(params))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)

        response = Response(
            requests.get(
                url=url, params=params, auth=auth, headers={
                    "Accept":"application/json",
                    "Accept-Language":self.language,
                    "user-agent": "labbcat-py/"+__version__}), 
            self.verbose)
        response.checkForErrors()

        if self.verbose: print("response: " + str(response.text))
        return(response.model)
        
    def _postRequest(self, url, params, json=None):
        if self.verbose: print("_postRequest " + url + " : " + str(params) + " : " + str(json))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)
            
        response = Response(
            requests.post(
                url=url, params=params, json=json, auth=auth, headers={
                    "Accept":"application/json",
                    "Accept-Language":self.language,
                    "user-agent": "labbcat-py/"+__version__}),
            self.verbose)
        response.checkForErrors()
        
        if self.verbose: print("model: " + str(response.model))
        return(response.model)
         
    def _putRequest(self, url, params, json=None):
        if self.verbose: print("_putRequest " + url + " : " + str(params) + " : " + str(json))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)
            
        response = Response(
            requests.put(
                url=url, params=params, json=json, auth=auth, headers={
                    "Accept":"application/json",
                    "Accept-Language":self.language,
                    "user-agent": "labbcat-py/"+__version__
                }), 
            self.verbose)
        response.checkForErrors()
        
        if self.verbose: print("model: " + str(response.model))
        return(response.model)
         
    def _deleteRequest(self, url, params, json=None):
        if self.verbose: print("_deleteRequest " + url + " : " + str(params) + " : " + str(json))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)
            
        response = Response(
            requests.delete(
                url=url, params=params, json=json, auth=auth, headers={
                    "Accept":"application/json",
                    "Accept-Language":self.language,
                    "user-agent": "labbcat-py/"+__version__
                }),
            self.verbose)
        response.checkForErrors()
        
        if self.verbose: print("model: " + str(response.model))
        return(response.model)
         
    def _postRequestToFile(self, url, params, dir=None):
        if self.verbose: print("_postRequestToFile " + url + " : " + str(params) + " -> " + dir)
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)
        
        response = requests.post(
            url=url, data=params, auth=auth, headers={
                "Accept":"application/json",
                    "Accept-Language":self.language,
                    "user-agent": "labbcat-py/"+__version__
                })
        if self.verbose: print(response.request.body)
        # ensure status was ok
        response.raise_for_status();
        
        # figure out the content type
        contentType = response.headers['Content-Type'];
        if self.verbose: print("Content-Type: " + contentType)
        extension = ".bin"
        if contentType.startswith("text/csv"): extension = ".csv"
        elif contentType.startswith("application/json"): extension = ".json"
        elif contentType.startswith("text/plain"): extension = ".txt"
        elif contentType.startswith("text/html"): extension = ".html"
        elif contentType.startswith("application/zip"): extension = ".zip"
        elif contentType.startswith("audio/wav"): extension = ".wav"
        elif contentType.startswith("audio/x-wav"): extension = ".wav"
        elif contentType.startswith("audio/mpeg"): extension = ".mp3"
        elif contentType.startswith("video/mpeg"): extension = ".mp4"

        fileName = None
        if dir == None:
            # save to temporary file
            fd, fileName = tempfile.mkstemp(extension, "labbcat-py-")
            if self.verbose: print("file: " + fileName)
            with open(fileName, "wb") as file:
                file.write(response.content)
            os.close(fd)
        else:
            # save into the given directory...
            # use the name given by the server, if any
            contentDisposition = None
            if "content-disposition" in response.headers:
                contentDisposition = response.headers["content-disposition"];
                if self.verbose: print("contentDisposition: " + contentDisposition)
            if contentDisposition != None:                
                # something like attachment; filename=blah.wav
                equals = contentDisposition.find("=")
                if equals >= 0:
                    fileName = contentDisposition[equals + 1:]
                    if self.verbose: print("fileName: " + fileName)
                    if fileName == "":
                        fileName = None
                    else:
                        fileName = os.path.join(dir, fileName)
            if fileName == None:
                lastSlash = url.rfind('/')
                if lastSlash >= 0:
                    fileName = url[lastSlash + 1:]
                    if not fileName.endswith(extension): fileName = fileName + extension
                    fileName = os.path.join(dir, fileName)
                else:
                    fd, fileName = tempfile.mkstemp(extension, "labbcat-py-", dir)
                    os.close(fd)
            if self.verbose: print("file: " + fileName)
            with open(fileName, "wb") as file:
                file.write(response.content)
            
        return(fileName)
         
    def _postMultipartRequest(self, url, params, files):
        if self.verbose: print("_postMultipartRequest " + url + " : " + str(params) + " - " + str(files))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)
            
        response = Response(requests.post(
            url=url, data=params, files=files, auth=auth, headers={
                "Accept":"application/json",
                    "Accept-Language":self.language,
                    "user-agent": "labbcat-py/"+__version__
                }))
        
        # close the files
        for param in files:
            name, fd = files[param]
            fd.close()
        
        # check for errors
        response.checkForErrors()
        
        if self.verbose: print("model: " + str(response.model))
        return(response.model)
         
    def getId(self):
        """ Gets the store's ID. 

        :returns: The annotation store's ID.
        :rtype: str
        """
        return(self._getRequest(self._storeQueryUrl("getId"), None))
        
    def getLayerIds(self):
        """ Gets a list of layer IDs (annotation 'types'). 
        
        :returns: A list of layer IDs.
        :rtype: list
        """
        return(self._getRequest(self._storeQueryUrl("getLayerIds"), None))
        
    def getLayers(self):
        """ Gets a list of layer definitions. 

        :returns: A list of layer definitions.
        :rtype: list of dictionaries
        """
        return(self._getRequest(self._storeQueryUrl("getLayers"), None))
        
    def getLayer(self, id):
        """ Gets a layer definition. 

        :param id: ID of the layer to get the definition for.
        :type id: str

        :returns: The definition of the given layer.
        :rtype: dictionary
        """
        return(self._getRequest(self._storeQueryUrl("getLayer"), {"id":id}))
        
    def getCorpusIds(self):
        """ Gets a list of corpus IDs. 

        :returns: A list of corpus IDs.
        :rtype: list
        """
        return(self._getRequest(self._storeQueryUrl("getCorpusIds"), None))
        
    def getParticipantIds(self):
        """ Gets a list of participant IDs. 
        

        :returns: A list of participant IDs.
        :rtype: list
        """
        return(self._getRequest(self._storeQueryUrl("getParticipantIds"), None))
        
    def getParticipant(self, id):
        """ Gets the participant record specified by the given identifier. 
        
        :param id: The ID of the participant, which could be their name or their database
            annotation ID. 
        :type id: str

        :returns: An annotation representing the participant, or null if the participant
        :rtype: dictionary
            was not found. 
        """
        return(self._getRequest(self._storeQueryUrl("getParticipant"), {"id":id}))
        
    def countMatchingParticipantIds(self, expression):
        """ Counts the number of participants that match a particular pattern. 
                
        The expression language is loosely based on JavaScript; expressions such as the
        following can be used:
        
        - ``/Ada.+/.test(id)``
        - ``labels('corpus').includes('CC')``
        - ``labels('participant_languages').includes('en')``
        - ``labels('transcript_language').includes('en')``
        - ``!/Ada.+/.test(id) && my('corpus').label == 'CC'``
        - ``list('transcript_rating').length < 2``
        - ``list('participant_rating').length = 0``
        - ``!annotators('transcript_rating').includes('labbcat')``
        - ``my('participant_gender').label == 'NA'``

        :param expression: An expression that determines which participants match.
        :type expression: str
        
        :returns: The number of matching participants.
        :rtype: int
        """
        return(self._getRequest(
            self._storeQueryUrl("countMatchingParticipantIds"),
            { "expression":expression }))
        
    def getMatchingParticipantIds(self, expression, pageLength=None, pageNumber=None):
        """ Gets a list of IDs of participants that match a particular pattern. 
        
        The expression language is loosely based on JavaScript; expressions such as the
        following can be used:  
        
        - ``/Ada.+/.test(id)``
        - ``labels('corpus').includes('CC')``
        - ``labels('participant_languages').includes('en')``
        - ``labels('transcript_language').includes('en')``
        - ``!/Ada.+/.test(id) && my('corpus').label == 'CC'``
        - ``list('transcript_rating').length < 2``
        - ``list('participant_rating').length = 0``
        - ``!annotators('transcript_rating').includes('labbcat')``
        - ``my('participant_gender').label == 'NA'``
        
        :param expression: An expression that determines which participants match.
        :type expression: str
        
        :param pageLength: The maximum number of IDs to return, or null to return all.
        :type pageLength: int or None

        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :returns: A list of participant IDs.
        :rtype: list
        """
        return(self._getRequest(
            self._storeQueryUrl("getMatchingParticipantIds"),
            {"expression":expression,
             "pageLength":pageLength, "pageNumber":pageNumber}))
        
    def getTranscriptIds(self):
        """ Gets a list of transcript IDs.         

        :returns: A list of transcript IDs.
        :rtype: list
        """
        return(self._getRequest(self._storeQueryUrl("getTranscriptIds"), None))
        
    def getTranscriptIdsInCorpus(self, id):
        """ Gets a list of transcript IDs in the given corpus. 
        
        :param id: A corpus ID.
        :type id: str

        :returns: A list of transcript IDs.
        :rtype: list
        """
        return(self._getRequest(self._storeQueryUrl("getTranscriptIdsInCorpus"), {"id":id}))
        
    def getTranscriptIdsWithParticipant(self, id):
        """ Gets a list of IDs of transcripts that include the given participant. 
        
        :param id: A participant ID.
        :type id: str
        
        :returns: A list of transcript IDs.
        :rtype: list of str
        """
        return(self._getRequest(self._storeQueryUrl("getTranscriptIdsWithParticipant"), {"id":id}))
        
    def countMatchingTranscriptIds(self, expression):
        """ Counts the number of transcripts that match a particular pattern. 
        
        The expression language is loosely based on JavaScript; expressions such as the
        following can be used: 
        
        - ``/Ada.+/.test(id)``
        - ``labels('participant').includes('Robert')``
        - ``('CC', 'IA', 'MU').includes(my('corpus').label)``
        - ``my('episode').label == 'Ada Aitcheson'``
        - ``my('transcript_scribe').label == 'Robert'``
        - ``my('participant_languages').label == 'en'``
        - ``my('noise').label == 'bell'``
        - ``labels('transcript_languages').includes('en')``
        - ``labels('participant_languages').includes('en')``
        - ``labels('noise').includes('bell')``
        - ``list('transcript_languages').length gt; 1``
        - ``list('participant_languages').length gt; 1``
        - ``list('transcript').length gt; 100``
        - ``annotators('transcript_rating').includes('Robert')``
        - ``!/Ada.+/.test(id) && my('corpus').label == 'CC' && labels('participant').includes('Robert')`` 
        
        :param expression: An expression that determines which transcripts match.
        :type expression: str

        :returns: The number of matching transcripts.
        :rtype: int
        """
        return(self._getRequest(
            self._storeQueryUrl("countMatchingTranscriptIds"),
            { "expression":expression }))
        
    def getMatchingTranscriptIds(self, expression, pageLength=None, pageNumber=None, order=None):
        """ Gets a list of IDs of transcripts that match a particular pattern. 
        
        The results can be exhaustive, by omitting pageLength and pageNumber, or they can
        be a subset (a 'page') of results, by given pageLength and pageNumber values. 
        
        The order of the list can be specified.  If ommitted, the transcripts are listed
        in ID order. 
        
        The expression language is loosely based on JavaScript; expressions such as the
        following can be used: 
        
        - ``/Ada.+/.test(id)``
        - ``labels('participant').includes('Robert')``
        - ``('CC', 'IA', 'MU').includes(my('corpus').label)``
        - ``my('episode').label == 'Ada Aitcheson'``
        - ``my('transcript_scribe').label == 'Robert'``
        - ``my('participant_languages').label == 'en'``
        - ``my('noise').label == 'bell'``
        - ``labels('transcript_languages').includes('en')``
        - ``labels('participant_languages').includes('en')``
        - ``labels('noise').includes('bell')``
        - ``list('transcript_languages').length gt; 1``
        - ``list('participant_languages').length gt; 1``
        - ``list('transcript').length gt; 100``
        - ``annotators('transcript_rating').includes('Robert')``
        - ``!/Ada.+/.test(id) && my('corpus').label == 'CC' && labels('participant').includes('Robert')``
        
        :param expression: An expression that determines which transcripts match.        
        :type expression: str
        
        :param pageLength: The maximum number of IDs to return, or null to return all.
        :type pageLength: int or None
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None
        
        :param order: The ordering for the list of IDs, a string containing a
            comma-separated list of expressions, which may be appended by " ASC" or " DESC",
            or null for transcript ID order.
        :type order: str

        :returns: A list of transcript IDs.
        :rtype: list of str
        """
        return(self._getRequest(
            self._storeQueryUrl("getMatchingTranscriptIds"),
            { "expression":expression,
              "pageLength":pageLength, "pageNumber":pageNumber,
              "order":order}))
        
    def countMatchingAnnotations(self, expression):
        """ Counts the number of annotations that match a particular pattern. 
        
        The expression language is loosely based on JavaScript; expressions such as the
        following can be used: 
        
        - ``id == 'ew_0_456'``
        - ``!/th[aeiou].&#47;/.test(label)``
        - ``my('participant').label == 'Robert' && my('utterances').start.offset == 12.345`` 
        - ``graph.id == 'AdaAicheson-01.trs' && layer.id == 'orthography' && start.offset < 10.5`` 
        - ``previous.id == 'ew_0_456'``

        *NB* all expressions must match by either id or layer.id.
        
        :param expression: An expression that determines which participants match.
        :type expression: str

        :returns: The number of matching annotations.
        :rtype: int
        """
        return(self._getRequest(
            self._storeQueryUrl("countMatchingAnnotations"),
            { "expression":expression }))
        
    def getMatchingAnnotations(self, expression, pageLength=None, pageNumber=None):
        """ Gets a list of annotations that match a particular pattern. 
        
        The expression language is loosely based on JavaScript; expressions such as the
        following can be used:
        
        - ``id == 'ew_0_456'``
        - ``!/th[aeiou].&#47;/.test(label)``
        - ``my('participant').label == 'Robert' && my('utterances').start.offset == 12.345`` 
        - ``graph.id == 'AdaAicheson-01.trs' && layer.id == 'orthography' && start.offset < 10.5`` 
        - ``previous.id == 'ew_0_456'``
        
        *NB* all expressions must match by either id or layer.id.
        :param expression: An expression that determines which transcripts match.
        :type expression: str
        
        :param pageLength: The maximum number of annotations to return, or null to return all.
        :type pageLength: int or None
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :returns: A list of matching Annotations.
        :rtype: list of dictionaries
        """
        return(self._getRequest(
            self._storeQueryUrl("getMatchingAnnotations"),
            { "expression":expression,
              "pageLength":pageLength, "pageNumber":pageNumber }))
        
    def countAnnotations(self, id, layerId):
        """ Gets the number of annotations on the given layer of the given transcript. 
        
        :param id: The ID of the transcript.
        :type id: str
        
        :param layerId: The ID of the layer.
        :type layerId: str

        :returns: A (possibly empty) array of annotations.
        :rtype: int
        """
        return(self._getRequest(
            self._storeQueryUrl("countAnnotations"),
            { "id":id, "layerId":layerId }))
        
    def getAnnotations(self, id, layerId, pageLength=None, pageNumber=None):
        """ Gets the annotations on the given layer of the given transcript.
        
        :param id: The ID of the transcript.
        :type id: str
        
        :param layerId: The ID of the layer.
        :type layerId:
        
        :param pageLength: The maximum number of IDs to return, or null to return all.
        :type pageLength: int or None
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :returns: A (possibly empty) list of annotations.
        :rtype: list of dictionaries
        """
        return(self._getRequest(
            self._storeQueryUrl("getAnnotations"),
            { "id":id, "layerId":layerId,
              "pageLength":pageLength, "pageNumber":pageNumber }))
        
    def getAnchors(self, id, anchorIds):
        """ Gets the given anchors in the given transcript. 
        
        :param id: The ID of the transcript.
        :type id: str
        
        :param anchorIds: A list of anchor IDs.
        :type anchorIds: list of str

        :returns: A (possibly empty) list of anchors.
        :rtype: list of dictionaries
        """
        return(self._getRequest(
            self._storeQueryUrl("getAnchors"),
            { "id":id, "anchorIds":anchorIds }))
        
    def getTranscript(self, id, layerIds=None):
        """ Gets a transcript given its ID. 
        
        :param id: The given transcript ID.
        :type id: str
        
        :param layerIds: The IDs of the layers to load, or null if only transcript data is
            required. 
        :type layerIds: list of str

        :returns: The identified transcript.
        :rtype: dictionary
        """
        return(self._getRequest(
            self._storeQueryUrl("getTranscript"),
            { "id":id, "layerIds":layerIds }))
        
    def getMediaTracks(self):
        """ List the predefined media tracks available for transcripts. 
        

        :returns: An ordered list of media track definitions.
        :rtype: list of dictionaries
        """
        return(self._getRequest(self._storeQueryUrl("getMediaTracks"), None))
        
    def getAvailableMedia(self, id):
        """ List the media available for the given transcript. 
        
        :param id: The transcript ID.
        :type id: str

        :returns: List of media files available for the given transcript.
        :rtype: list of dictionaries
        """
        return(self._getRequest(
            self._storeQueryUrl("getAvailableMedia"),
            { "id":id }))
        
    def getMediaUrl(self, id, trackSuffix, mimeType, startOffset=None, endOffset=None):
        """ Gets a given media track URL for a given transcript. 
        
        :param id: The transcript ID.
        :type id: str
        
        :param trackSuffix: The track suffix of the media. 
        :type trackSuffix: str
        
        :param mimeType: The MIME type of the media, which may include parameters for type
            conversion, e.g. 'text/wav; samplerate=16000'
        :type mimeType: str
        
        :param startOffset: The start offset of the media sample, or null for the start of
            the whole recording. 
        :type startOffset: float or None

        :param endOffset: The end offset of the media sample, or null for the end of the
            whole recording. 
        :type endOffset: float or None

        :returns: A URL to the given media for the given transcript, or null if the given
            media doesn't exist. 
        :rtype: str
        """
        return(self._getRequest(
            self._storeQueryUrl("getMedia"),
            { "id":id, "trackSuffix":trackSuffix, "mimeType":mimeType,
              "startOffset":startOffset, "endOffset":endOffset }))
        
    def getMedia(self, id, trackSuffix, mimeType, startOffset=None, endOffset=None, dir=None):
        """ Downloads a given media track URL for a given transcript. 
        
        :param id: The transcript ID.
        :type id: str
        
        :param trackSuffix: The track suffix of the media. 
        :type trackSuffix: str
        
        :param mimeType: The MIME type of the media, which may include parameters for type
            conversion, e.g. 'text/wav; samplerate=16000'
        :type mimeType: str
        
        :param startOffset: The start offset of the media sample, or null for the start of
            the whole recording. 
        :type startOffset: float or None

        :param endOffset: The end offset of the media sample, or null for the end of the
            whole recording. 
        :type endOffset: float or None

        :param dir: A directory in which the file should be stored, or null for a temporary
         folder.  If specified, and the directory doesn't exist, it will be created. 
        :type dir: str
        
        :returns: The file name of the resulting file. If *dir* is None, this file will be stored
         under the system's temporary directory, so once processing is finished, it should
         be deleted by the caller, or moved to a more permanent location. 
        :rtype: list of str
        """

        # get the URL of the media
        url = self.getMediaUrl(id, trackSuffix, mimeType, startOffset, endOffset)

        # download the content of the URL
        if dir == None:
            dir = tempfile.mkdtemp("_wav", "getMedia_")
            tempFiles = True
        elif not os.path.exists(dir):
            os.mkdir(dir)
        return(self._postRequestToFile(url, None, dir))
        
    def getEpisodeDocuments(self, id):
        """ Get a list of documents associated with the episode of the given transcript. 
        
        :param id: The transcript ID.
        :type id: str

        :returns: List of URLs to documents.
        :rtype: list of str
        """
        return(self._getRequest(
            self._storeQueryUrl("getEpisodeDocuments"),
            { "id":id }))

    def taskStatus(self, threadId):
        """ Gets the current state of the given task.

        :param threadId: The ID of the task.
        :type threadId: str.

        :returns: The status of the task.
        :rtype: dictionary
        """
        return(self._getRequest(self._labbcatUrl("thread"), { "threadId" : threadId }))

    def waitForTask(self, threadId, maxSeconds=0):
        """Wait for the given task to finish.

        :param threadId: The task ID.
        :type threadId: str

        :param maxSeconds: The maximum time to wait for the task, or 0 for forever.
        :type maxSeconds: int
    
        :returns: The final task status. To determine whether the task finished or waiting
                  timed out, check *result.running*, which will be false if the task finished.
        :rtype: dict
        """
        if maxSeconds == 0: maxSeconds = -1 
        status = self.taskStatus(threadId)
        if self.verbose: print("status : " + str(status["running"]))
        while status["running"] and maxSeconds != 0:
            if self.verbose: print("sleeping...")
            time.sleep(1)
            if maxSeconds != 0: maxSeconds = maxSeconds - 1
            status = self.taskStatus(threadId)
            if self.verbose: print("status "+str(maxSeconds)+" : " + str(status["running"]))

        return(status)

    def taskResults(self, threadId, dir=None):
        """ Gets the results of the given task, as a file or list of files.
        
        Some tasks produce a file for download when they're finished
        (e.g. `getFragmentsAsync() <#labbcat.LabbcatView.getFragmentsAsync>`_)
        so this function provides acces to this results file. If the results are
        compressed into a zip file, this function automatically unpacks the contained files.

        :param threadId: The ID of the task.
        :type threadId: str.

        :param dir: A directory in which the files should be stored, or null for a temporary
         folder.  If specified, and the directory doesn't exist, it will be created. 
        :type dir: str
        
        :returns: A list of files. If *dir* is None, these files will be stored under the
         system's temporary directory, so once processing is finished, they should be
         deleted by the caller, or moved to a more permanent location. 
         If the task has no results (yet) this function returns None.
        :rtype: list of str
        """
        status = self.taskStatus(threadId)
        if "resultUrl" in status:
            resultUrl = status["resultUrl"]
            
            fragments = []        
            tempFiles = False
            if dir == None:
                dir = tempfile.mkdtemp("_"+str(threadId), "taskResults_")
                tempFiles = True
            elif not os.path.exists(dir):
                os.mkdir(dir)

            # get result
            fileName = self._postRequestToFile(resultUrl, None, dir)
            fileNames = [ fileName ]
            
            if fileName.endswith(".zip"):
                # extract the zip file
                with ZipFile(fileName, 'r') as zipObj:
                    zipObj.extractall(dir)
                    fileNames = [os.path.join(dir, fileName) for fileName in zipObj.namelist()]
                
                # delete the temporary zip file
                os.remove(fileName)

            return fileNames
            
        else: # no resultUrl
            return None
    
    def releaseTask(self, threadId):
        """ Release a finished task, to free up server resources.

        :param threadId: The ID of the task.
        :type threadId: str.
        """
        self._getRequest(self._labbcatUrl("threads"), {
            "threadId" : threadId, "command" : "release" })
        return()

    def cancelTask(self, threadId):
        """ Cancels (but does not release) a running task.

        :param threadId: The ID of the task.
        :type threadId: str.
        """
        self._getRequest(self._labbcatUrl("threads"), {
            "threadId" : threadId, "command" : "cancel" })
        return()

    def getTasks(self):
        """ Gets a list of all tasks on the server. 
        
        :returns: A list of all task statuses.
        :rtype: list of dictionaries
        """
        return(self._getRequest(self._labbcatUrl("threads"), None))
    
    def getTranscriptAttributes(self, transcriptIds, layerIds):
        """ Get transcript attribute values.
        
        Retrieves transcript attribute values for given transcript IDs, saves them to
        a CSV file, and returns the name of the file.

        In general, transcript attributes are layers whose ID is prefixed 'transcript',
        however formally it's any layer where layer.parentId == 'graph' and layer.alignment
        == 0, which includes 'corpus' as well as transcript attribute layers.
        
        The resulting file is the responsibility of the caller to delete when finished.
        
        :param transcriptIds: A list of transcript IDs
        :type transcriptIds: list of str.
        
        :param layerIds: A list of layer IDs corresponding to transcript attributes.
        :type layerIds: list of str.
        
        :rtype: str
        """
        params = {
            "layer" : ["transcript"]+layerIds,
            "id" : transcriptIds }
        return (self._postRequestToFile(self._labbcatUrl("api/attributes"), params))
    
    def getParticipantAttributes(self, participantIds, layerIds):
        """ Gets participant attribute values.
        
        Retrieves participant attribute values for given participant IDs, saves them
        to a CSV file, and returns the name of the file.

        In general, participant attributes are layers whose ID is prefixed 'participant',
        however formally it's any layer where layer.parentId == 'participant' and
        layer.alignment == 0. 
        
        The resulting file is the responsibility of the caller to delete when finished.
        
        :param participantIds: A list of participant IDs
        :type participantIds: list of str.
        
        :param layerIds: A list of layer IDs corresponding to participant attributes. 
        :type layerIds: list of str.
        
        :rtype: str
        """
        params = {
            "type" : "participant",
            "content-type" : "text/csv",
            "csvFieldDelimiter" : ",",
            "layer" : layerIds,
            "participantId" : participantIds }
        return (self._postRequestToFile(self._labbcatUrl("participantsExport"), params))
        

    def search(self, pattern, participantIds=None, transcriptTypes=None, mainParticipant=True, aligned=False, matchesPerTranscript=None, overlapThreshold=None):
        """
        Searches for tokens that match the given pattern.
        
        Example::
        
          pattern = {"columns":[{"layers":{"orthography":{"pattern":"the"}}}]}
        
        Strictly speaking, *pattern* should be a dictionary that matches the structure of
        the search matrix in the browser interface of LaBB-CAT; i.e. a dictionary with
        with one entrye called "columns", which is a list of dictionaries.
        
        Each element in the "columns" list contains a dictionary with an entry named
        "layers", whose value is a dictionary for patterns to match on each layer, and
        optionally an element named "adj", whose value is a number representing the
        maximum distance, in tokens, between this column and the next column - if "adj"
        is not specified, the value defaults to 1, so tokens are contiguous.
        
        Each element in the "layers" dictionary is named after the layer it matches, and
        the value is a dictionary with the following possible entries:
        
        - "pattern" : A regular expression to match against the label
        - "min" : An inclusive minimum numeric value for the label
        - "max" : An exclusive maximum numeric value for the label
        - "not" : True to negate the match
        - "anchorStart" : True to anchor to the start of the annotation on this layer
           (i.e. the matching word token will be the first at/after the start of the matching
           annotation on this layer)
        - "anchorEnd" : True to anchor to the end of the annotation on this layer
           (i.e. the matching word token will be the last before/at the end of the matching
           annotation on this layer)
        - "target" : True to make this layer the target of the search; the results will
           contain one row for each match on the target layer
        
        Some examples of valid pattern objects are shown below.
        
        Example:: 
          
          ## words starting with 'ps...'
          pattern = {"columns":[{"layers":{"orthography":{"pattern":"ps.*"}}}]}
          
          ## the word 'the' followed immediately or with one intervening word by
          ## a hapax legomenon (word with a frequency of 1) that doesn't start with a vowel
          pattern = { "columns" : [
            { "layers" : {
                "orthography" : { "pattern" : "the" } }
              "adj" : 2 },
            { "layers" : {
                "phonemes" : { "not" : True, "pattern" : "[cCEFHiIPqQuUV0123456789~#\\$@].*" },
                "frequency" : { max : "2" } } } ] }
        
        For ease of use, the function will also accept the following abbreviated forms;
        some examples are shown below.
        
        Example:: 
          
          ## a single list representing a 'one column' search, 
          ## and string values, representing regular expression pattern matching
          pattern = { "orthography" : "ps.*" }
          
          ## a list containing the columns (adj defaults to 1, so matching tokens are contiguous)...
          pattern = [
            { "orthography" : "the" },
            { "phonemes" : { "not" : True, "pattern" : "[cCEFHiIPqQuUV0123456789~#\\$@].*" },
              "frequency" : { "max" : "2" } } ]
        
        :param pattern: A dict representing the pattern to search for, which mirrors the
          Search Matrix in the browser interface.
        :type dictionary:
        
        :param participantIds: An optional list of participant IDs to search the utterances
          of. If null, all utterances in the corpus will be searched.
        :type list of str:
        
        :param transcriptTypes: An optional list of transcript types to limit the results
          to. If null, all transcript types will be searched. 
        :type list of str:
        
        :param mainParticipant: true to search only main-participant utterances, false to
          search all utterances. 
        :type boolean:
        
        :param aligned: true to include only words that are aligned (i.e. have anchor
          confidence &ge; 50, false to search include un-aligned words as well. 
        :type boolean:
        
        :param matchesPerTranscript: Optional maximum number of matches per transcript to
          return. *None* means all matches.
        :type int:
        
        :param overlapThreshold: Optional percentage overlap with other utterances before
          simultaneous speech is excluded. *None* means include all overlapping utterances.
        
        :returns: The threadId of the resulting task, which can be passed in to
          `getMatches() <#labbcat.LabbcatView.getMatches>`_, 
          `taskStatus() <#labbcat.LabbcatView.taskStatus>`_, 
          `waitForTask() <#labbcat.LabbcatView.waitForTask>`_
          `releaseTask() <#labbcat.LabbcatView.releaseTask>`_, etc. 
        :rtype: str
        """

        ## first normalize the pattern...
        
        ## if pattern isn't a list with a "columns" element, wrap a list around it
        if "columns" not in pattern: pattern = { "columns" : pattern }
        
        ## if pattern["columns"] isn't a list wrap a list around it
        if not isinstance(pattern["columns"], list): pattern["columns"] = [ pattern["columns"] ]
        
        ## columns contain lists with no "layers" element, wrap a list around them
        for c in range(len(pattern["columns"])):
            if "layers" not in pattern["columns"][c]:
                pattern["columns"][c] = { "layers" : pattern["columns"][c] }
        
        ## convert layer=string to layer=list(pattern=string)
        for c in range(len(pattern["columns"])): # for each column
            for l in pattern["columns"][c]["layers"]: # for each layer in the column
                # if the layer value isn't a dictionary
                if not isinstance(pattern["columns"][c]["layers"][l], dict):
                    # wrap a list(pattern=...) around it
                    pattern["columns"][c]["layers"][l] = { "pattern": pattern["columns"][c]["layers"][l] }

        # define request parameters
        parameters = {
            "command" : "search",
            "searchJson" : json.dumps(pattern),
            "words_context" : 0
        }
        if mainParticipant:
            parameters["only_main_speaker"] = "true"
        if aligned:
            parameters["only_aligned"] = "true"
        if matchesPerTranscript != None:
            parameters["matches_per_transcript"] = matchesPerTranscript
        if participantIds != None:
            parameters["participant_id"] = participantIds
        if transcriptTypes != None:
            parameters["transcript_type"] = transcriptTypes
        if overlapThreshold != None:
            parameters["overlap_threshold"] = overlapThreshold
        model = self._getRequest(self._labbcatUrl("search"), parameters)
        return(model["threadId"])
    
    def allUtterances(self, participantIds, transcriptTypes=None, mainParticipant=True):
        """
        Identifies all utterances by the given participants.        
        
        :param participantIds: A list of participant IDs to identify the utterances of.
        :type list of str:
        
        :param transcriptTypes: An optional list of transcript types to limit the results
          to. If null, all transcript types will be searched. 
        :type list of str:
        
        :param mainParticipant: true to search only main-participant utterances, false to
          search all utterances. 
        :type boolean:
        
        :returns: The threadId of the resulting task, which can be passed in to
          `getMatches() <#labbcat.LabbcatView.getMatches>`_, 
          `taskStatus() <#labbcat.LabbcatView.taskStatus>`_, 
          `waitForTask() <#labbcat.LabbcatView.waitForTask>`_
          `releaseTask() <#labbcat.LabbcatView.releaseTask>`_, etc. 
        :rtype: str
        """

        # define request parameters
        parameters = {
            "list" : "search",
            "id" : participantIds
        }
        if mainParticipant:
            parameters["only_main_speaker"] = "true"
        if transcriptTypes != None:
            parameters["transcript_type"] = transcriptTypes
        model = self._getRequest(self._labbcatUrl("allUtterances"), parameters)
        return(model["threadId"])
    
    def getMatches(self, search, wordsContext=0, pageLength=None, pageNumber=None):
        """
        Gets a list of tokens that were matched by search(pattern)
        
        The *search* parameter can be *either* 
        
        - a threadId returned from a previous call to `search() <#labbcat.LabbcatView.search>`_ 
          *or* 
        - a dict representing a pattern to search for.
        
        If it is a threadId, and the task is still running, then this function will wait
        for it to finish. 
        
        If it is a pattern dict, then `search() <#labbcat.LabbcatView.search>`_ is called
        for the given pattern, the matches are retrieved, and
        `releaseTask() <#labbcat.LabbcatView.releaseTask>`_ is called to
        free the search resources. Some example patterns are shown below; for more
        detailed information, see `search() <#labbcat.LabbcatView.search>`_.
        
        Example:: 
          
          ## a single list representing a 'one column' search, 
          ## and string values, representing regular expression pattern matching
          pattern = { "orthography" : "ps.*" }
          
          ## a list containing the columns (adj defaults to 1, so matching tokens are contiguous)...
          pattern = [
            { "orthography" : "the" },
            { "phonemes" : { "not" : True, "pattern" : "[cCEFHiIPqQuUV0123456789~#\\$@].*" },
              "frequency" : { "max" : "2" } } ]
        
        This function returns a list of match dictionaries, where each item has the
        following entries:
        
        - "MatchId" : An ID whichencodes which token in which utterance by which
                      participant of which transcript matched.
        - "Transcript" : The name of the transcript document that the match is from. 
        - "Participant" :  The name of the participant who uttered the match.
        - "Corpus" : The corpus the match comes from.
        - "Line" : The start time of the utterance.
        - "LineEnd" : The end time of the utterance.
        - "BeforeMatch" : The context before the match.
        - "Text" : The match text.
        - "AfterMatch" : The context after the match.
        
        :param search: This can be *either* a threadId returned from a previous call to
          `search() <#labbcat.LabbcatView.search>`_ *or* a dict representing a pattern to
          search for. 
        :type search: str or dict
        
        :param wordsContext: Number of words context to include in the <q>Before Match</q>
          and <q>After Match</q> columns in the results.
        :type wordsContext: int
        
        :param pageLength: The maximum number of matches to return, or None to return all.
        :type pageLength: int or None
        
        :param pageNumber: The zero-based page number to return, or null to return the
          first page.
        :type pageNumber: int or None
        
        :returns: A list of IDs that can be used to identify utterances/tokens that were
          matched by search(pattern), or None if the task was cancelled. 
        :rtype: list of dict
        """
        # is search a dict or str?
        threadId = search
        releaseThread = False
        if not isinstance(search, str):
            threadId = self.search(search)
            releaseThread = True
        
        # ensure it's finished
        self.waitForTask(threadId)
        
        # define request parameters
        parameters = {
            "threadId" : threadId,
            "words_context" : wordsContext,
        }
        if pageLength != None:
            parameters["pageLength"] = pageLength
        if pageNumber != None:
            parameters["pageNumber"] = pageNumber

        # send request
        model = self._getRequest(self._labbcatUrl("resultsStream"), parameters)
        
        # if search matrix was passed, releaseTask
        if releaseThread:
            self.releaseTask(threadId)
        
        return(model["matches"])
    
    def getMatchAnnotations(self, matchIds, layerIds, targetOffset=0, annotationsPerLayer=1):
        """
        Gets annotations on selected layers related to search results returned by a previous
        call to getMatches(threadId).
        
        The returned list of lists contains dictionaries that represent individual
        annotations, with the following entries:
        
        - "id" : The annotation's unique ID
        - "layerId" : The layer the annotation comes from
        - "label" : The annotation's label or value
        - "startId" : The ID of the annotations start anchor
        - "endId" : The ID of the annotations end anchor
        - "parentId" : The annotation's parent annotation ID
        - "ordinal" : The annotation's position amongst its peers
        - "confidence" : A rating of confidence in the label accuracy, from 0 (no
            confidence) to 100 (absolute confidence / manually annotated)
        
        :param matchIds: A list of MatchId strings, or a list of match dictionaries
        :type matchIds: list of str or list of dict
        
        :param layerIds: A list of layer IDs.
        :type layerIds: list of str
        
        :param targetOffset: The distance from the original target of the match, e.g.
         -  0 : find annotations of the match target itself
         -  1 : find annotations of the token immediately *after* match target
         - -1 : find annotations of the token immediately *before* match target
        :type targetOffset: int
        
        :param annotationsPerLayer: The number of annotations on the given layer to
         retrieve. In most cases, there's only one annotation available. However, tokens may,
         for example, be annotated with 'all possible phonemic transcriptions', in which case
         using a value of greater than 1 for this parameter provides other phonemic
         transcriptions, for tokens that have more than one.
        :type annotationsPerLayer: int
        
        :returns: An array of arrays of Annotations, of dimensions 
         len(*matchIds*) x (len(*layerIds*) x *annotationsPerLayer*). The first index matches the
         corresponding index in *matchIds*.  
        :rtype: list of list of dictionary
        """
        # we need a list of strings, so if we've got a list of dictionaries, convert it
        if len(matchIds) > 0:
            if isinstance(matchIds[0], dict):
                # map the dictionaries to their "MatchId" entry
                matchIds = [ m["MatchId"] for m in matchIds ]

        # save MatchIds as a CSV file
        fd, fileName = tempfile.mkstemp(".csv", "labbcat-py-getMatchAnnotations-")
        if self.verbose: print("MatchId file: " + fileName)
        with open(fileName, "w") as file:
            file.write("MatchId")
            for matchId in matchIds:
                file.write("\n" + matchId)
        os.close(fd)
        files = {}
        f = open(fileName, 'r')
        files["uploadfile"] = (fileName, f)

        # define parameters
        parameters = {
            "layer" : layerIds,
            "targetOffset" : targetOffset,
            "annotationsPerLayer" : annotationsPerLayer,
            "csvFieldDelimiter" : ",",
            "targetColumn" : 0,
            "copyColumns" : False
        }
        
        # send the request
        model = self._postMultipartRequest(
            self._labbcatUrl("api/getMatchAnnotations"), parameters, files)
        
        # delete the temporary CSV file
        os.remove(fileName)
        
        return(model)

    def getSoundFragments(self, transcriptIds, startOffsets=None, endOffsets=None, sampleRate=None, dir=None, prefixNames=True):
        """
        Downloads WAV sound fragments.

        The intervals to extract can be defined in two possible ways:
        
         1. transcriptIds is a list of strings, and startOffsets and endOffsets are lists
            of floats 
         2. transcriptIds is a list of dict objects returned by getMatches(threadId), and
            startOffsets and endOffsets are None

        :param transcriptIds: A list of transcript IDs (transcript names), or a list of
         dictionaries returned by getMatches(threadId).
        :type transcriptIds: list of str or list of dict
        
        :param startOffsets: A list of start offsets, with one element for each element in
         *transcriptIds*. 
        :type startOffsets: list of float or None
        
        :param endOffsets: A list of end offsets, with one element for each element in
         *transcriptIds*. 
        :type endOffsets: list of float or None
        
        :param sampleRate: The desired sample rate, or null for no preference.
        :type sampleRate: int
        
        :param dir: A directory in which the files should be stored, or null for a temporary
         folder.  If specified, and the directory doesn't exist, it will be created. 
        :type dir: str
        
        :param prefixNames: Whether to prefix fragment names with a numeric serial number or not.
        :type prefixNames: boolean
        
        :returns: A list of WAV files. If *dir* is None, these files will be stored
         under the system's temporary directory, so once processing is finished, they should
         be deleted by the caller, or moved to a more permanent location. 
        :rtype: list of str
        """
        prefixes = None
        # have they passed matches as transcriptIds, instead of strings?
        if len(transcriptIds) > 0:
            if isinstance(transcriptIds[0], dict) and startOffsets == None and endOffsets == None:
                prefixExtractor = re.compile('.*prefix=([^;]+).*')
                startOffsets = [ m["Line"] for m in transcriptIds ]
                endOffsets = [ m["LineEnd"] for m in transcriptIds ]
                prefixes = []
                for m in transcriptIds:
                    prefix = None
                    match = prefixExtractor.match(m["MatchId"])
                    if match != None:
                        prefix = match.group(1)
                    prefixes.append(prefix)
                transcriptIds = [ m["Transcript"] for m in transcriptIds ]
        
        # validate parameters
        if len(transcriptIds) != len(startOffsets) or len(transcriptIds) != len(endOffsets):
            raise ResponseException(
                "transcriptIds ("+str(len(transcriptIds))
                +"), startOffsets ("+str(len(startOffsets))
                +"), and endOffsets ("+str(len(endOffsets))+") must be lists of equal size.");
        
        fragments = []        
        tempFiles = False
        if dir == None:
            dir = tempfile.mkdtemp("_wav", "getSoundFragments_")
            tempFiles = True
        elif not os.path.exists(dir):
            os.mkdir(dir)

        # loop through each triple, getting fragments individually
        url = self._labbcatUrl("soundfragment")
        prefixChars = len(str(len(transcriptIds)))
        for i in range(len(transcriptIds)):
            if transcriptIds[i] == None or startOffsets[i] == None or endOffsets[i] == None:
                continue
            
            params = {
                "id" : transcriptIds[i],
                "start" : startOffsets[i],
                "end" : endOffsets[i],
            }
            if sampleRate != None:
                params["sampleRate"] = sampleRate
            if prefixNames:
                if prefixes != None and prefixes[i] != None:
                    params["prefix"] = prefixes[i]
                else:
                    params["prefix"] = str(i+1).zfill(prefixChars)+"-"

            try:
                fileName = self._postRequestToFile(url, params, dir)
                fragments.append(fileName)
            except ResponseException:
                fragments.append(None)
        
        return(fragments)
    
    def getFragments(self, transcriptIds, layerIds, mimeType, dir=None, startOffsets=None, endOffsets=None, prefixNames=True):
        """
        Get transcript fragments in a specified format.

        The intervals to extract can be defined in two possible ways:
        
         1. transcriptIds is a list of strings, and startOffsets and endOffsets are lists
            of floats 
         2. transcriptIds is a list of dict objects returned by getMatches(threadId), and
            startOffsets and endOffsets are None

        :param transcriptIds: A list of transcript IDs (transcript names), or a list of
         dictionaries returned by getMatches(threadId).
        :type transcriptIds: list of str or list of dict
        
        :param startOffsets: A list of start offsets, with one element for each element in
         *transcriptIds*. 
        :type startOffsets: list of float or None
        
        :param endOffsets: A list of end offsets, with one element for each element in
         *transcriptIds*. 
        :type endOffsets: list of float or None
        
        :param layerIds: A list of IDs of annotation layers to include in the fragment.
        :type layerIds: list of str
        
        :param mimeType: The desired format, for example "text/praat-textgrid" for Praat
         TextGrids, "text/plain" for plain text, etc.
        :type mimeType: list of str
        
        :param dir: A directory in which the files should be stored, or null for a temporary
         folder.  If specified, and the directory doesn't exist, it will be created. 
        :type dir: str
        
        :param prefixNames: Whether to prefix fragment names with a numeric serial number or not.
        :type prefixNames: boolean
        
        :returns: A list of files. If *dir* is None, these files will be stored under the
         system's temporary directory, so once processing is finished, they should be
         deleted by the caller, or moved to a more permanent location. 
         *NB* Although many formats will generate exactly one file for each interval, this
         is not guaranted; some formats generate a single file or a fixed collection of
         files regardless of how many fragments there are.
        :rtype: list of str
        """
        # have they passed matches as transcriptIds, instead of strings?
        if len(transcriptIds) > 0:
            if isinstance(transcriptIds[0], dict) and startOffsets == None and endOffsets == None:
                startOffsets = [ m["Line"] for m in transcriptIds ]
                endOffsets = [ m["LineEnd"] for m in transcriptIds ]
                transcriptIds = [ m["Transcript"] for m in transcriptIds ]
        
        # validate parameters
        if len(transcriptIds) != len(startOffsets) or len(transcriptIds) != len(endOffsets):
            raise ResponseException(
                "transcriptIds ("+str(len(transcriptIds))
                +"), startOffsets ("+str(len(startOffsets))
                +"), and endOffsets ("+str(len(endOffsets))+") must be lists of equal size.");
        
        fragments = []        
        tempFiles = False
        if dir == None:
            dir = tempfile.mkdtemp("_frag", "getFragments_")
            tempFiles = True
        elif not os.path.exists(dir):
            os.mkdir(dir)

        # send all triples in one request, we should get a zip file back
        url = self._labbcatUrl("api/serialize/fragment")
        params = {
            "id" : transcriptIds,
            "start" : startOffsets,
            "end" : endOffsets,
            "mimeType" : mimeType,
            "layerId" : layerIds
        }
        if prefixNames:
            params["prefix"] = True
        try:
            zipFileName = self._postRequestToFile(url, params, dir)
            with ZipFile(zipFileName, 'r') as zipObj:
                zipObj.extractall(dir)
                fragments = [os.path.join(dir, fileName) for fileName in zipObj.namelist()]
                
            # delete the temporary zip file
            os.remove(zipFileName)
            
        except ResponseException:
            # fall back to looping through each triple, getting fragments individually
            for i in range(len(transcriptIds)):
                if transcriptIds[i] == None or startOffsets[i] == None or endOffsets[i] == None:
                    continue
                
                params = {
                    "id" : transcriptIds[i],
                    "start" : startOffsets[i],
                    "end" : endOffsets[i],
                    "mimeType" : mimeType,
                    "layerId" : layerIds
                }
                if prefixNames:
                    params["prefix"] = True
                
                try:
                    fileName = self._postRequestToFile(url, params, dir)
                    fragments.append(fileName)
                except ResponseException:
                    fragments.append(None)
        
        return(fragments)

    def getFragmentsAsync(self, transcriptIds, layerIds, mimeType, startOffsets=None, endOffsets=None, prefixNames=True):
        """
        Starts a server task for getting transcript fragments in a specified format.

        The intervals to extract can be defined in two possible ways:
        
         1. transcriptIds is a list of strings, and startOffsets and endOffsets are lists
            of floats 
         2. transcriptIds is a list of dict objects returned by getMatches(threadId), and
            startOffsets and endOffsets are None

        :param transcriptIds: A list of transcript IDs (transcript names), or a list of
         dictionaries returned by getMatches(threadId).
        :type transcriptIds: list of str or list of dict
        
        :param startOffsets: A list of start offsets, with one element for each element in
         *transcriptIds*. 
        :type startOffsets: list of float or None
        
        :param endOffsets: A list of end offsets, with one element for each element in
         *transcriptIds*. 
        :type endOffsets: list of float or None
        
        :param layerIds: A list of IDs of annotation layers to include in the fragment.
        :type layerIds: list of str
        
        :param mimeType: The desired format, for example "text/praat-textgrid" for Praat
         TextGrids, "text/plain" for plain text, etc.
        :type mimeType: list of str
        
        :param prefixNames: Whether to prefix fragment names with a numeric serial number or not.
        :type prefixNames: boolean
        
        :returns: The threadId of the resulting task, which can be passed in to
          `taskStatus() <#labbcat.LabbcatView.taskStatus>`_, 
          `waitForTask() <#labbcat.LabbcatView.waitForTask>`_
          `taskResults() <#labbcat.LabbcatView.taskResults>`_
          `releaseTask() <#labbcat.LabbcatView.releaseTask>`_, etc. 
        :rtype: str
        """
        # have they passed matches as transcriptIds, instead of strings?
        if len(transcriptIds) > 0:
            if isinstance(transcriptIds[0], dict) and startOffsets == None and endOffsets == None:
                startOffsets = [ m["Line"] for m in transcriptIds ]
                endOffsets = [ m["LineEnd"] for m in transcriptIds ]
                transcriptIds = [ m["Transcript"] for m in transcriptIds ]
        
        # validate parameters
        if len(transcriptIds) != len(startOffsets) or len(transcriptIds) != len(endOffsets):
            raise ResponseException(
                "transcriptIds ("+str(len(transcriptIds))
                +"), startOffsets ("+str(len(startOffsets))
                +"), and endOffsets ("+str(len(endOffsets))+") must be lists of equal size.");
        
        # send all triples in one request, we should get a zip file back
        url = self._labbcatUrl("api/serialize/fragment")
        params = {
            "id" : transcriptIds,
            "start" : startOffsets,
            "end" : endOffsets,
            "mimeType" : mimeType,
            "layerId" : layerIds,
            "async" : "true"
        }
        if prefixNames:
            params["prefix"] = True

        model = self._postRequest(url, params)
        return(model["threadId"])

    def getSerializerDescriptors(self):
        """ Lists the descriptors of all registered serializers.        
        
        Serializers are modules that export annotation structures as a specific file
        format, e.g. Praat TextGrid, plain text, etc., so the mimeType of descriptors
        reflects what mimeTypes can be specified for  
        `getFragments() <#labbcat.LabbcatView.getFragments>`_
        
        :returns: A list of the descriptors of all registered serializers. 
        :rtype: list of dictionaries
        """
        return(self._getRequest(self._storeQueryUrl("getSerializerDescriptors"), None))
        
    def getDeserializerDescriptors(self):
        """ Lists the descriptors of all registered serializers.        
        
        Deserializers are modules that import annotation structures from a specific file
        format, e.g. Praat TextGrid, plain text, etc.
        
        :returns: A list of the descriptors of all registered serializers. 
        :rtype: list of dictionaries
        """
        return(self._getRequest(self._storeQueryUrl("getDeserializerDescriptors"), None))

    def getSystemAttribute(self, attribute):
        """ Gets the value of the given system attribute.
        
        :param attribute: Name of the attribute.
        :type attribute: str
        
        :returns: The value of the given attribute, or None if the attribute doesn't exist.
        :rtype: str
        """
        try:
            return(self._getRequest(
                self._labbcatUrl("api/systemattributes/"+attribute), None)["value"])
        except ResponseException:
            return(None)
    
    def getUserInfo(self):
        """ Gets information about the current suer, including the roles or groups they are in.
        
        :returns: The user record, including a "user" entry with the user ID, and a
         "roles" entry which is a list of str.
        :rtype: dict
        """
        return(self._getRequest(self._labbcatUrl("api/user"), None))
    
    # TODO getFragment
    # TODO getFragmentSeries
