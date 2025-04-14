import csv
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
        corpus = labbcat.LabbcatView("https://labbcat.canterbury.ac.nz", "demo", "demo")
        
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
        self.labbcatVersion = None

    def _labbcatUrl(self, resource):
        return self.labbcatUrl + resource

    def _storeQueryUrl(self, resource):
        return self.labbcatUrl + "api/store/" + resource

    def _getRequest(self, url, params):
        response = Response(self._getRequestRaw(url, params), self.verbose)
        if self.labbcatVersion is None:
            self.labbcatVersion = response.version
        response.checkForErrors()

        if self.verbose: print("response: " + str(response.text))
        return(response.model)
        
    def _getRequestRaw(self, url, params):
        if self.verbose: print("_getRequestRaw " + url + " : " + str(params))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)
        return(requests.get(
            url=url, params=params, auth=auth, headers={
                "Accept":"application/json",
                "Accept-Language":self.language,
                "user-agent": "labbcat-py/"+__version__}))
        
    def _postRequest(self, url, params, json=None):
        if self.verbose: print("_postRequest " + url + " : " + str(params) + " : " + str(json))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)
            
        response = Response(
            requests.post(
                url=url, data=params, json=json, auth=auth, headers={
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
         
    def _postRequestToFile(self, url, params, dir=None, fileName=None):
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

        if fileName == None:
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
         
    def _postMultipartRequestRaw(self, url, params, files):
        if self.verbose: print("_postMultipartRequestRaw " + url + " : " + str(params) + " - " + str(files))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)
            
        resp = requests.post(
            url=url, data=params, files=files, auth=auth, headers={
                "Accept":"text/plain",
                "Accept-Language":self.language,
                "user-agent": "labbcat-py/"+__version__
            })
        
        # close the files
        for param in files:
            name, fd = files[param]
            fd.close()
        
        return(resp)
         
    def versionInfo(self):
        """ Gets version information of all components of LaBB-CAT.

        Version information includes versions of all components and modules installed on the
        LaBB-CAT server, including format converters and annotator modules.

        :returns: A dictionary of sections, each section a dictionary of modules
                  indicating the version of that module.
        :rtype: dict
        """
        return(self._getRequest(self._labbcatUrl("version"), None))
        
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
            was not found. 
        :rtype: dictionary
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
        - ``!/Ada.+/.test(id) && first('corpus').label == 'CC'``
        - ``all('transcript_rating').length < 2``
        - ``all('participant_rating').length = 0``
        - ``!annotators('transcript_rating').includes('labbcat')``
        - ``first('participant_gender').label == 'NA'``

        The following functions can be used to generate an expression of common types:
        
        - `expressionFromAttributeValue() <#labbcat.expressionFromAttributeValue>`_
        - `expressionFromAttributeValues() <#labbcat.expressionFromAttributeValues>`_
        - `expressionFromIds() <#labbcat.expressionFromIds>`_
        - `expressionFromCorpora() <#labbcat.expressionFromCorpora>`_

        Example:: 
        
            numQbParticipants = corpus.countMatchingParticipantIds(
                labbcat.expressionFromCorpora("QB"))            
            
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
        - ``!/Ada.+/.test(id) && first('corpus').label == 'CC'``
        - ``all('transcript_rating').length < 2``
        - ``all('participant_rating').length = 0``
        - ``!annotators('transcript_rating').includes('labbcat')``
        - ``first('participant_gender').label == 'NA'``

        The following functions can be used to generate an expression of common types:
        
        - `expressionFromAttributeValue() <#labbcat.expressionFromAttributeValue>`_
        - `expressionFromAttributeValues() <#labbcat.expressionFromAttributeValues>`_
        - `expressionFromIds() <#labbcat.expressionFromIds>`_
        - `expressionFromCorpora() <#labbcat.expressionFromCorpora>`_

        Example:: 
        
            qbParticipants = corpus.getMatchingParticipantIds(
                labbcat.expressionFromCorpora("QB"))            
        
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
        - ``('CC', 'IA', 'MU').includes(first('corpus').label)``
        - ``first('episode').label == 'Ada Aitcheson'``
        - ``first('transcript_scribe').label == 'Robert'``
        - ``first('participant_languages').label == 'en'``
        - ``first('noise').label == 'bell'``
        - ``labels('transcript_languages').includes('en')``
        - ``labels('participant_languages').includes('en')``
        - ``labels('noise').includes('bell')``
        - ``all('transcript_languages').length gt; 1``
        - ``all('participant_languages').length gt; 1``
        - ``all('transcript').length gt; 100``
        - ``annotators('transcript_rating').includes('Robert')``
        - ``!/Ada.+/.test(id) && first('corpus').label == 'CC' && labels('participant').includes('Robert')`` 

        The following functions can be used to generate an expression of common types:
        
        - `expressionFromAttributeValue() <#labbcat.expressionFromAttributeValue>`_
        - `expressionFromAttributeValues() <#labbcat.expressionFromAttributeValues>`_
        - `expressionFromIds() <#labbcat.expressionFromIds>`_
        - `expressionFromTranscriptTypes() <#labbcat.expressionFromTranscriptTypes>`_
        - `expressionFromCorpora() <#labbcat.expressionFromCorpora>`_

        Example:: 
        
            numQuakeFaceTranscripts = corpus.countMatchingTranscriptIds(
                labbcat.expressionFromAttributeValue("transcript_quakeface", "1"))            
        
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
        - ``('CC', 'IA', 'MU').includes(first('corpus').label)``
        - ``first('episode').label == 'Ada Aitcheson'``
        - ``first('transcript_scribe').label == 'Robert'``
        - ``first('participant_languages').label == 'en'``
        - ``first('noise').label == 'bell'``
        - ``labels('transcript_languages').includes('en')``
        - ``labels('participant_languages').includes('en')``
        - ``labels('noise').includes('bell')``
        - ``all('transcript_languages').length gt; 1``
        - ``all('participant_languages').length gt; 1``
        - ``all('transcript').length gt; 100``
        - ``annotators('transcript_rating').includes('Robert')``
        - ``!/Ada.+/.test(id) && first('corpus').label == 'CC' && labels('participant').includes('Robert')``

        The following functions can be used to generate an expression of common types:
        
        - `expressionFromAttributeValue() <#labbcat.expressionFromAttributeValue>`_
        - `expressionFromAttributeValues() <#labbcat.expressionFromAttributeValues>`_
        - `expressionFromIds() <#labbcat.expressionFromIds>`_
        - `expressionFromTranscriptTypes() <#labbcat.expressionFromTranscriptTypes>`_
        - `expressionFromCorpora() <#labbcat.expressionFromCorpora>`_

        Example:: 
        
            quakeFaceTranscripts = corpus.getMatchingTranscriptIds(
                labbcat.expressionFromAttributeValue("transcript_quakeface", "1"))            
        
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
        - ``first('participant').label == 'Robert' && first('utterances').start.offset == 12.345`` 
        - ``graph.id == 'AdaAicheson-01.trs' && layer.id == 'orthography' && start.offset < 10.5`` 
        - ``previous.id == 'ew_0_456'``

        *NB* all expressions must match by either id or layer.id.
        
        :param expression: An expression that determines which annotations match.
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
        - ``first('participant').label == 'Robert' && first('utterances').start.offset == 12.345`` 
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
        
    def countAnnotations(self, id, layerId, maxOrdinal=None):
        """ Gets the number of annotations on the given layer of the given transcript. 
        
        :param id: The ID of the transcript.
        :type id: str
        
        :param layerId: The ID of the layer.
        :type layerId: str
        
        :param maxOrdinal: The maximum ordinal for the counted annotations.
           e.g. a maxOrdinal of 1 will ensure that only the first annotation for each
           parent is returned. If maxOrdinal is None, then all annotations are
           counted, regardless of their ordinal.
        :type maxOrdinal: int or None
        
        :returns: A (possibly empty) array of annotations.
        :rtype: int
        """
        return(self._getRequest(
            self._storeQueryUrl("countAnnotations"),
            { "id":id, "layerId":layerId, "maxOrdinal":maxOrdinal }))
        
    def getAnnotations(self, id, layerId, maxOrdinal=None, pageLength=None, pageNumber=None):
        """ Gets the annotations on the given layer of the given transcript.
        
        :param id: The ID of the transcript.
        :type id: str
        
        :param layerId: The ID of the layer.
        :type layerId:
        
        :param maxOrdinal: The maximum ordinal for the returned annotations.
           e.g. a maxOrdinal of 1 will ensure that only the first annotation for each
           parent is returned. If maxOrdinal is None, then all annotations are
           returned, regardless of their ordinal.
        :type maxOrdinal: int or None
        
        :param pageLength: The maximum number of IDs to return, or null to return all.
        :type pageLength: int or None
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :returns: A (possibly empty) list of annotations.
        :rtype: list of dictionaries
        """
        return(self._getRequest(
            self._storeQueryUrl("getAnnotations"),
            { "id":id, "layerId":layerId, "maxOrdinal":maxOrdinal,
              "pageLength":pageLength, "pageNumber":pageNumber }))

    # TODO getAnnotationData(expression, dir)
    # TODO getFragmentAnnotationData(transcriptIds, startOffsets, endOffsets, layerId, dir)
    # TODO getFragmentAnnotations(transcriptIds, participantIds, startOffsets, endOffsets, layerIds, sep, partialContainment)
        
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

        The returned object defines the annotation graph structure, and is a dictionary
        whose entries include:

        - "id" : the transcript ID
        - "schema" : a representation of the layer structure of the graph
        - "anchors" : a dictionary of temporal anchors that represent the start and/or end
                      time of an annotation (keyed by anchor ID)
        - "participant" : a list of participants in the transcript. Each participant is
                          represented by a dictionary that includes a "turn" entry which
                          is a list of speaker turns, each turn having an "utterance"
                          entry contatainging utterance boundary annotations, and a "word" entry
                          containing a list of word tokens.
        - entries for 'spanning' layers that are not assigned to a specific participant.

        Annotations are presented by dictionaries that have the following entries:

        - "id" : the unique identifier for the annotation
        - "label" : the annotation layer
        - "startId" and "endId" : the start and end anchors, which correspond to an entry
                                  in the "anchors" dictionary
        - "confidence" : label confidence rating, where 100 means it was labelled by a
                         human, and 50 means it was labelled by an automated process.
        
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
        try:
            url = self._getRequest(
                self._storeQueryUrl("getMedia"),
                { "id":id, "trackSuffix":trackSuffix, "mimeType":mimeType,
                  "startOffset":startOffset, "endOffset":endOffset })
            if url != None: url = url.replace("+","%20")
            return(url)
        except ResponseException:
            return None
        
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

        if url != None:
            # download the content of the URL
            if dir == None:
                dir = tempfile.mkdtemp("_wav", "getMedia_")
                tempFiles = True
            elif not os.path.exists(dir):
                os.mkdir(dir)
            return(self._postRequestToFile(url, None, dir))
        else:
            return(None)
        
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
    
    def getTranscriptAttributes(self, expression, layerIds, csvFileName=None):
        """ Get transcript attribute values.
        
        Retrieves transcript attribute values for a given transcript expression, saves them to
        a CSV file, and returns the name of the file.

        The expression parameter can be an explicit list of transcript IDs, or a string
        query expression that identifies which transcripts to return.
        
        The expression language is loosely based on JavaScript; expressions such as the
        following can be used: 
        
        - ``/Ada.+/.test(id)``
        - ``labels('participant').includes('Robert')``
        - ``('CC', 'IA', 'MU').includes(first('corpus').label)``
        - ``first('episode').label == 'Ada Aitcheson'``
        - ``first('transcript_scribe').label == 'Robert'``
        - ``first('participant_languages').label == 'en'``
        - ``first('noise').label == 'bell'``
        - ``labels('transcript_languages').includes('en')``
        - ``labels('participant_languages').includes('en')``
        - ``labels('noise').includes('bell')``
        - ``all('transcript_languages').length &gt; 1``
        - ``all('participant_languages').length y 1``
        - ``all('word').length &gt; 100``
        - ``annotators('transcript_rating').includes('Robert')``
        - ``!/Ada.+/.test(id) && first('corpus').label == 'CC' && labels('participant').includes('Robert')``

        The following functions can be used to generate an expression of common types:
        
        - `expressionFromAttributeValue() <#labbcat.expressionFromAttributeValue>`_
        - `expressionFromAttributeValues() <#labbcat.expressionFromAttributeValues>`_
        - `expressionFromIds() <#labbcat.expressionFromIds>`_
        - `expressionFromTranscriptTypes() <#labbcat.expressionFromTranscriptTypes>`_
        - `expressionFromCorpora() <#labbcat.expressionFromCorpora>`_
        
        In general, transcript attributes are layers whose ID is prefixed 'transcript',
        however formally it's any layer where layer.parentId == 'graph' and layer.alignment
        == 0, which includes 'corpus' as well as transcript attribute layers.
        
        The resulting file is the responsibility of the caller to delete when finished.

        Example:: 
        
            # duration/word count of QB corpus transcripts
            qbAttributesCsv = corpus.getTranscriptAttributes(
                labbcat.expressionFromCorpora("QB"),
                ["transcript_duration", "transcript_word count"])            
            
            # speech rate for spontaneous speech recordings
            spontaneousSpeechRateCsv = corpus.getTranscriptAttributes(
                labbcat.expressionFromTranscriptTypes(["monologue", "interview"]),
                ["transcript_syllables per minute"])
            
            # language for targeted transcripts
            languageCsv = corpus.getTranscriptAttributes(
                ["AP2505_Nelson.eaf", "AP2512_MattBlack.eaf"],
                "transcript_language")

            # tidily delete CSV files
            os.remove([qbAttributesCsv, spontaneousSpeechRateCsv, languageCsv])
        
        :param expression: An expression that determines which transcripts match,
                           or an explicit list of transcript IDs.
        :type expression: str or list of str.
        
        :param layerIds: A list of layer IDs corresponding to transcript attributes.
        :type layerIds: list of str.
        
        :param csvFileName: The file to save the resulting CSV rows to.
        :type csvFileName: str.
        
        :returns: The name of a CSV file with one row per transcript, and one column per attribute.
        :rtype: str
        """
        if isinstance(expression, str):
            params = {
                "layer" : ["transcript"]+layerIds,
                "query" : expression }
        else:
            params = {
                "layer" : ["transcript"]+layerIds,
                "id" : expression }
        return (self._postRequestToFile(self._labbcatUrl("api/attributes"), params, None, csvFileName))
    
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
        
        :returns: The name of a CSV file with one row per participant, and one column per attribute.
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
            
        endpoint = "api/search" # this endpoint was implemented as of LaBB-CAT 20230511.1949
        if self.labbcatVersion is None: self.getId() # ensure we know the server version
        if self.labbcatVersion < "20230511.1949": endpoint = "search"
        
        model = self._getRequest(self._labbcatUrl(endpoint), parameters)
        return(model["threadId"])
    
    def allUtterances(self, participantIds, transcriptTypes=None, mainParticipant=True):
        """
        Identifies all utterances by the given participants.

        A taskId is returned. To get the actual utterances, which are represented the same
        way as search results, call `getMatches() <#labbcat.LabbcatView.getMatches>`_
        
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
            
        endpoint = "api/utterances" # this endpoint was implemented as of LaBB-CAT 20230511.1949
        if self.labbcatVersion is None: self.getId() # ensure we know the server version
        if self.labbcatVersion < "20230511.1949": endpoint = "allUtterances"
        
        model = self._getRequest(self._labbcatUrl(endpoint), parameters)
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
        
        - "Title" : The title of the LaBB-CAT instance</dd>
        - "Version" : The current version of the LaBB-CAT instance</dd>
        - "MatchId" : An ID which encodes which token in which utterance by which
                      participant of which transcript matched.
        - "URL" : URL that opens the corresponding transcript page at the first matching word.
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

            
        endpoint = "api/results" # this endpoint was implemented as of LaBB-CAT 20230511.1949
        if self.labbcatVersion is None: self.getId() # ensure we know the server version
        if self.labbcatVersion < "20230511.1949": endpoint = "resultsStream"
        
        # send request
        model = self._getRequest(self._labbcatUrl(endpoint), parameters)
        
        # if search matrix was passed, releaseTask
        if releaseThread:
            self.releaseTask(threadId)
        
        return(model["matches"])
    
    def getMatchAnnotations(self, matchIds, layerIds, targetOffset=0, annotationsPerLayer=1, offsetThreshold=None):
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
        
        If offsetThreshold is a value between 0 and 100, the annotations may also include
        a "start" entry and an "end" entry, representing the start/end anchors of the
        annotation which define the position of the annotation in time. These values are
        dictionaries with the following entries: 
        
        - "id" : The anchor's unique ID
        - "offset" : The time (in seconds since the start of the recording, unless the
                     transcript is textual rather than speech, in which case it represents
                     the number of characters from the beginning of the document)
        - "confidence" : A rating of confidence in the alignment accuracy, from 0 (no
            confidence) to 100 (absolute confidence / manually specified)        
        
        :param matchIds: A list of MatchId strings, or a list of match dictionaries of the
                         kind returned by `getMatches() <#labbcat.LabbcatView.getMatches>`_
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

        :param offsetThreshold: The minimum confidence for alignments, e.g.
          - None -- do not return alignments;
          - *0* -- return all alignments, regardless of confidence;
          - *50* -- return only alignments that have been at least automatically aligned;
          - *100* -- return only manually-set alignments.
        :type offsetThreshold: int
        
        :returns: If annotationsPerLayer == 1 and only one layer is specified in layerIds, 
         a one-dimensional array of Annotations, of dimension len(*matchIds*) is returned. 
         Otherwise, the return value is an array of arrays of Annotations, of dimensions 
         len(*matchIds*) x (len(*layerIds*)x*annotationsPerLayer*). 
         Either way, the first index matches the corresponding index in *matchIds*.  
        :rtype: list of list of dictionary        
        """
        # we need a list of strings, so if we've got a list of dictionaries, convert it
        if len(matchIds) > 0:
            if isinstance(matchIds[0], dict):
                # map the dictionaries to their "MatchId" entry
                matchIds = [ m["MatchId"] for m in matchIds ]
        if isinstance(layerIds[0], str):
            # convert string into an array with one string element
            layerIds = [ layerIds ]

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
            "copyColumns" : False,
            "offsetThreshold" : offsetThreshold
        }
        
        # send the request
        model = self._postMultipartRequest(
            self._labbcatUrl("api/getMatchAnnotations"), parameters, files)
        
        # delete the temporary CSV file
        os.remove(fileName)

        if annotationsPerLayer == 1 and len(layerIds) == 1:
            # remove one of the dimensions of the result
            model = [item for row in model for item in row]
        
        return(model)

    def processWithPraat(self, praatScript, windowOffset, matchIds, offsets, endOffsets=None, 
                         genderAttribute="participant_gender", attributes=None):
        """
        Process a set of intervals with Praat.
        
        This function instructs the LaBB-CAT server to invoke Praat for a set of sound
        intervals, in order to extract acoustic measures.
        
        The exact measurements to return depend on the praatScript that is invoked. This is a
        Praat script fragment that will run once for each sound interval specified.
        
        There are functions to allow the generation of a number of pre-defined praat scripts
        for common tasks such as formant, pitch, intensity, and centre of gravity -- see
        
        - `praatScriptFormants() <#labbcat.praatScriptFormants>`_
        - `praatScriptFastTrack() <#labbcat.praatScriptFastTrack>`_
        - `praatScriptCentreOfGravity() <#labbcat.praatScriptCentreOfGravity>`_
        - `praatScriptIntensity() <#labbcat.praatScriptIntensity>`_
        - `praatScriptPitch() <#labbcat.praatScriptPitch>`_
        
        You can provide your own script, either by building a string with your code, or loading
        one from a file.
        
        LaBB-CAT prefixes praatScript with code to open a sound file and extract a defined part
        of it into a Sound object which is then selected.
        
        LaBB-CAT 'Remove's this Sound object after the script finishes executing. Any other objects
        created by the script must be 'Remove'd before the end of the script (otherwise
        Praat runs out of memory during very large batches)
        
        LaBB-CAT assumes that all calls to the function 'print' correspond to fields for export
        and each field must be printed on its own line. Specifically it scans for lines of the
        form:
        
        print 'myOutputVariable' 'newline$'
        
        Variables that can be assumed to be already set in the context of the script are:
        
        - *windowOffset*
           -- the value used for the Window Offset; how much context to include.
        - *windowAbsoluteStart*
           -- the start time of the window extracted relative to the start of the original audio file.
        - *windowAbsoluteEnd*
           -- the end time of the window extracted relative to the start of the original audio file.
        - *windowDuration*
           -- the duration of the window extracted (including window offset).
        - *targetAbsoluteStart*
           -- the start time of the target interval relative to the start of the original audio file.
        - *targetAbsoluteEnd*
           -- the end time of the target interval relative to the start of the original audio file.
        - *targetStart*
           -- the start time of the target interval relative to the start of the window extracted.
        - *targetEnd*
           -- the end time of the target interval relative to the start of the window extracted.
        - *targetDuration*
           -- the duration of the target interval.
        - *sampleNumber*
           -- the number of the sample within the set of samples being processed.
        - *sampleName$*
           -- the name of the extracted/selected Sound object.
        
        :param praatScript: Script to run on each match.
        :type praatScript: str
        
        :param windowOffset: In many circumstances, you will want some context before and after
         the sample start/end time.  For this reason, you can specify a "window offset" -
         this is a number of seconds to subtract from the sample start and add to the sample
         end time, before extracting that part of the audio for processing. For example, if
         the sample starts at 2.0s and ends at 3.0s, and you set the window offset to 0.5s,
         then Praat will extract a sample of audio from  1.5s to 3.5s, and do the selected
         processing on that sample. The best value for this depends on what the praatScript
         is doing; if you are getting formants from  vowels, including some context ensures
         that the formants at the edges are more accurate (in LaBB-CAT's web interface, the
         default value for this 0.025), but if you're getting max pitch or COG during a
         segment, most likely you want a window.offset of 0 to ensure neighbouring segments
         don't influence the measurement. 
        :type windowOffset: float

        :param matchIds: A list of MatchId strings, or a list of match dictionaries of the
                         kind returned by `getMatches() <#labbcat.LabbcatView.getMatches>`_
        :type matchIds: list of str or list of dict
        
        :param offsets: *Either* list of start offsets (in which case endOffsets must also
         be specified) *or* a list of Annotation dict objects of the kind returned by 
         `getMatchAnnotations() <#labbcat.LabbcatView.getMatchAnnotations>`_ (in which
         case endOffsets should be None). Either way, there must be one element for each
         element in *matchIds*. 
        :type offsets: list of float or None
        
        :param endOffsets: If offsets is a list of *start* offsets, this must be list of
         end offsets, with one element for each element in *matchtIds*. Otherwise, None
        :type endOffsets: list of float or None
        
        :param genderAttribute: Which participant attribute represents the participant's gender.
        :type genderAttribute: str
        
        :param attributes: A list of participant attribute names to make available to the script.
         For example, if you want to use different acoustic parameters depending on what the
         gender of the speaker is, including the "participant_gender" attribute will make a
         variable called participant_gender$ available to the praat script, whose value will
         be the gender of the speaker of that segment.
        :type attributes: list
        
        :returns: A list of dictionaries of acoustic measurements, one of each matchId.
        :rtype: list of dict
        """
        threadId = self.processWithPraatAsync(
            praatScript, windowOffset, matchIds, offsets, endOffsets, genderAttribute, attributes)

        # wait for it to finish
        task = self.waitForTask(threadId)

        # download the file
        fileNames = self.taskResults(threadId)
        if len(fileNames) == 0:
            raise Exception("No results returned by task " + threadId)

        # load values into an list of dict
        results = []
        with open(fileNames[0]) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            headers = None
            for row in csvReader:
                if headers == None:
                    headers = row
                else: # data row
                    result = {}
                    for c in range(len(row)):
                        value = row[c]
                        # we assume everything other than "Error" is a number!
                        if headers[c] != "Error":
                            try:
                                if "." in value:
                                    value = float(value)
                                else:
                                    value = int(value)
                            except:
                                pass
                        result[headers[c]] = value
                    results.append(result)
                    
        # tidy up
        self.releaseTask(threadId)
        for fileName in fileNames:
            os.remove(fileName)
        
        return(results)
        
    def processWithPraatAsync(self, praatScript, windowOffset, matchIds, offsets, endOffsets=None, 
                              genderAttribute="participant_gender", attributes=None):
        """
        Starts a server task for processing a set of intervals with Praat.
        
        The task continues running after this function returns, and can be 
        monitored with `taskStatus() <#labbcat.LabbcatView.taskStatus>`_, 
        cancelled with `cancelTask() <#labbcat.LabbcatView.cancelTask>`_,
        and the final results retrieved with `taskResults() <#labbcat.LabbcatView.taskResults>`_.
        The caller should eventually call `releaseTask() <#labbcat.LabbcatView.releaseTask>`_
        to free server resources after the task is cancelled or finished.
        
        This function instructs the LaBB-CAT server to invoke Praat for a set of sound
        intervals, in order to extract acoustic measures.
        
        The exact measurements to return depend on the praatScript that is invoked. This is a
        Praat script fragment that will run once for each sound interval specified.
        
        There are functions to allow the generation of a number of pre-defined praat scripts
        for common tasks such as formant, pitch, intensity, and centre of gravity -- see
        
        - `praatScriptFormants() <#labbcat.praatScriptFormants>`_
        - `praatScriptFastTrack() <#labbcat.praatScriptFastTrack>`_
        - `praatScriptCentreOfGravity() <#labbcat.praatScriptCentreOfGravity>`_
        - `praatScriptIntensity() <#labbcat.praatScriptIntensity>`_
        - `praatScriptPitch() <#labbcat.praatScriptPitch>`_
        
        You can provide your own script, either by building a string with your code, or loading
        one from a file.
        
        LaBB-CAT prefixes praatScript with code to open a sound file and extract a defined part
        of it into a Sound object which is then selected.
        
        LaBB-CAT 'Remove's this Sound object after the script finishes executing. Any other objects
        created by the script must be 'Remove'd before the end of the script (otherwise
        Praat runs out of memory during very large batches)
        
        LaBB-CAT assumes that all calls to the function 'print' correspond to fields for export
        and each field must be printed on its own line. Specifically it scans for lines of the
        form:
        
        print 'myOutputVariable' 'newline$'
        
        Variables that can be assumed to be already set in the context of the script are:
        
        - *windowOffset*
           -- the value used for the Window Offset; how much context to include.
        - *windowAbsoluteStart*
           -- the start time of the window extracted relative to the start of the original audio file.
        - *windowAbsoluteEnd*
           -- the end time of the window extracted relative to the start of the original audio file.
        - *windowDuration*
           -- the duration of the window extracted (including window offset).
        - *targetAbsoluteStart*
           -- the start time of the target interval relative to the start of the original audio file.
        - *targetAbsoluteEnd*
           -- the end time of the target interval relative to the start of the original audio file.
        - *targetStart*
           -- the start time of the target interval relative to the start of the window extracted.
        - *targetEnd*
           -- the end time of the target interval relative to the start of the window extracted.
        - *targetDuration*
           -- the duration of the target interval.
        - *sampleNumber*
           -- the number of the sample within the set of samples being processed.
        - *sampleName$*
           -- the name of the extracted/selected Sound object.
        
        :param praatScript: Script to run on each match.
        :type praatScript: str
        
        :param windowOffset: In many circumstances, you will want some context before and after
         the sample start/end time.  For this reason, you can specify a "window offset" -
         this is a number of seconds to subtract from the sample start and add to the sample
         end time, before extracting that part of the audio for processing. For example, if
         the sample starts at 2.0s and ends at 3.0s, and you set the window offset to 0.5s,
         then Praat will extract a sample of audio from  1.5s to 3.5s, and do the selected
         processing on that sample. The best value for this depends on what the praatScript
         is doing; if you are getting formants from  vowels, including some context ensures
         that the formants at the edges are more accurate (in LaBB-CAT's web interface, the
         default value for this 0.025), but if you're getting max pitch or COG during a
         segment, most likely you want a window.offset of 0 to ensure neighbouring segments
         don't influence the measurement. 
        :type windowOffset: float

        :param matchIds: A list of MatchId strings, or a list of match dictionaries of the
                         kind returned by `getMatches() <#labbcat.LabbcatView.getMatches>`_
        :type matchIds: list of str or list of dict
        
        :param offsets: *Either* list of start offsets (in which case endOffsets must also
         be specified) *or* a list of Annotation dict objects of the kind returned by 
         `getMatchAnnotations() <#labbcat.LabbcatView.getMatchAnnotations>`_ (in which
         case endOffsets should be None). Either way, there must be one element for each
         element in *matchIds*. 
        :type offsets: list of float or None
        
        :param endOffsets: If offsets is a list of *start* offsets, this must be list of
         end offsets, with one element for each element in *matchtIds*. Otherwise, None
        :type endOffsets: list of float or None
        
        :param genderAttribute: Which participant attribute represents the participant's gender.
        :type genderAttribute: str
        
        :param attributes: A list of participant attribute names to make available to the script.
         For example, if you want to use different acoustic parameters depending on what the
         gender of the speaker is, including the "participant_gender" attribute will make a
         variable called participant_gender$ available to the praat script, whose value will
         be the gender of the speaker of that segment.
        :type attributes: list
        
        :returns: The threadId of the resulting task, which can be passed in to
          `taskStatus() <#labbcat.LabbcatView.taskStatus>`_, 
          `waitForTask() <#labbcat.LabbcatView.waitForTask>`_
          `taskResults() <#labbcat.LabbcatView.taskResults>`_
          `releaseTask() <#labbcat.LabbcatView.releaseTask>`_, etc. 
        :rtype: str
        """
        # validation
        if len(matchIds) != len(offsets):
            raise Exception("matchIds ("+str(len(matchIds))+") and offsets ("
                            +str(len(offsets))+") must be the same length.")
        if endOffsets == None:
            # offsets must be an array of dict that includes "start" and "end" offsets
            # each with with an "offset" entry
            if "start" not in offsets[0] or "offset" not in offsets[0]["start"] \
               or "end" not in offsets[0] or "offset" not in offsets[0]["end"]:
                raise Exception("If endOffsets is not specified, offsets must be an array of "
                                "dict, each having a value for ['start']['offset']"
                                " and ['end']['offset']")
            endOffsets = []
            for annotation in offsets:
                if "end" in annotation and "offset" in annotation["end"]:
                    endOffsets.append(annotation["end"]["offset"])
                else:
                    endOffsets.append("")
            startOffsets = []
            for annotation in offsets:
                if "start" in annotation and "offset" in annotation["start"]:
                    startOffsets.append(annotation["start"]["offset"])
                else:
                    startOffsets.append("")
            offsets = startOffsets
        elif len(matchIds) != len(endOffsets):
            raise Exception("matchIds ("+str(len(matchIds))+") and endOffsets ("
                            +str(len(endOffsets))+") must be the same length.")
            
        
        # we need a list of strings, so if we've got a list of dictionaries, convert it
        if len(matchIds) > 0:
            if isinstance(matchIds[0], dict):
                # map the dictionaries to their "MatchId" entry
                matchIds = [ m["MatchId"] for m in matchIds ]

        # convert matchId list into two lists, transcriptIds and participantIds
        transcriptIds = list(
            map(lambda matchId: re.sub(r".*(g_[0-9]+);.*","\\1", matchId), matchIds))
        participantIds = list(
            map(lambda matchId: re.sub(r".*(p_[0-9]+);.*","\\1", matchId), matchIds))

        # save MatchIds as a CSV file
        fd, fileName = tempfile.mkstemp(".csv", "labbcat-py-processWithPraat-")
        if self.verbose: print("MatchId file: " + fileName)
        with open(fileName, "w") as file:
            file.write("Transcript,Participant,Start,End")
            for r in range(len(matchIds)):
                file.write(
                    "\n" + transcriptIds[r] + "," + participantIds[r]
                    + ","+ str(offsets[r]) + "," + str(endOffsets[r]))
        os.close(fd)
        files = {}
        f = open(fileName, 'r')
        files["csv"] = (fileName, f)

        # define parameters
        parameters = {
            "attributes" : attributes,
            "transcriptColumn" : 0,
            "participantColumn" : 1,
            "startTimeColumn" : 2,
            "endTimeColumn" : 3,
            "windowOffset" : windowOffset,
            "script" : praatScript,
            "passThroughData" : False
        }
        
        # send the request
        model = self._postMultipartRequest(self._labbcatUrl("api/praat"), parameters, files)
        
        # delete the temporary CSV file
        os.remove(fileName)

        # we got back a threadId, return it
        threadId = model["threadId"]
        return(threadId)
    
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
            except KeyboardInterrupt:
                break
            except:
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
         is not guaranteed; some formats generate a single file or a fixed collection of
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
        The task continues running after this function returns, and can be 
        monitored with `taskStatus() <#labbcat.LabbcatView.taskStatus>`_, 
        cancelled with `cancelTask() <#labbcat.LabbcatView.cancelTask>`_,
        and the final results retrieved with `taskResults() <#labbcat.LabbcatView.taskResults>`_.
        The caller should eventually call `releaseTask() <#labbcat.LabbcatView.releaseTask>`_
        to free server resources after the task is cancelled or finished.

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

    def formatTranscript(self, id, layerIds, mimeType, dir=None):
        """
        Get transcript in a specified format.

        :param id: The ID of the transcript to export.
        :type id: str
        
        :param layerIds: A list of IDs of annotation layers to include in the transcript.
        :type layerIds: list of str
        
        :param mimeType: The desired format, for example "text/praat-textgrid" for Praat
         TextGrids, "text/plain" for plain text, etc.
        :type mimeType: list of str
        
        :param dir: A directory in which the file(s) should be stored, or null for a temporary
         folder.  If specified, and the directory doesn't exist, it will be created. 
        :type dir: str
        
        :returns: A list of files. If *dir* is None, these files will be stored under the
         system's temporary directory, so once processing is finished, they should be
         deleted by the caller, or moved to a more permanent location. 
         *NB* Although many formats will generate exactly one file for each transcript, this
         is not guaranteed; some formats generate a mutiple files per transcript.
        :rtype: list of str
        """
        files = []
        
        tempFiles = False
        if dir == None:
            dir = tempfile.mkdtemp("_transcript", "formatTranscript_")
            tempFiles = True
        elif not os.path.exists(dir):
            os.mkdir(dir)

        # send all triples in one request, we should get a zip file back
        url = self._labbcatUrl("api/serialize/graphs")
        params = {
            "id" : id,
            "mimeType" : mimeType,
            "layerId" : layerIds
        }
        fileName = self._postRequestToFile(url, params, dir)
        files = [ fileName ]
        
        if fileName.endswith(".zip"):
            # extract the zip file
            with ZipFile(fileName, 'r') as zipObj:
                zipObj.extractall(dir)
                files = [os.path.join(dir, fileName) for fileName in zipObj.namelist()]
            
            # delete the temporary zip file
            os.remove(fileName)
                
        return(files)

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

    def getDictionaries(self):
        """ List the dictionaries available.
        
        :returns: A dictionary of lists, where keys are layer manager IDs, each of which 
         containing a list of IDs for dictionaries that the layer manager makes 
         available.
        :rtype: dict of lists
        """
        return(self._getRequest(self._labbcatUrl("dictionaries"), None))

    def getDictionaryEntries(self, managerId, dictionaryId, keys):
        """ Lookup entries in a dictionary.
        
        :param managerId: The layer manager ID of the dictionary, as returned by 
         `getDictionaries() <#labbcat.LabbcatView.getDictionaries>`_).
        :type managerId: str
        
        :param dictionaryId: The ID of the dictionary, as returned by 
         `getDictionaries() <#labbcat.LabbcatView.getDictionaries>`_).
        :type managerId: str
        
        :param keys: A list of keys (words) identifying entries to look up.
        :type keys: list of str or list of dict
        
        :returns: A dictionary of lists, where keys are given keys, each of which
         containing a list of entries. Keys with no corresponding entry in the given
         dictionary will be present in the returned result, but will have no entries.
        :rtype: dict of lists
        """
        if self.verbose:
            print("getDictionaryEntries " + managerId + ", " + dictionaryId + ", " + str(keys))
        # save keys to a CSV file
        fd, fileName = tempfile.mkstemp(".csv", "labbcat-py-getDictionaryEntries-")
        if self.verbose: print("keys file: " + fileName)
        with open(fileName, "w") as file:
            for key in keys:
                file.write(key + "\n")
        os.close(fd)
        
        # make request
        files = {}
        f = open(fileName, 'r')
        files["uploadfile"] = (fileName, f)
        response = self._postMultipartRequestRaw(
            self._labbcatUrl("dictionary"), {
                "managerId" : managerId,
                "dictionaryId" : dictionaryId
            }, files)
        
        # tidily remove upload file
        os.remove(fileName)
        
        # ensure status was ok
        response.raise_for_status();

        # save response to file
        if self.verbose: print("saving result to file: " + fileName)
        with open(fileName, "wb") as file:
            file.write(response.content)
        
        # load the returned entries into a dict
        dictionary = {}
        with open(fileName) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for row in csvReader:
                # first column is the key, the rest are entries
                key = row[0]
                entries = row[1:]
                if len(entries) == 1 and entries[0] == "":
                    entries = []
                dictionary[key] = entries
        
        # tidily remove the downloaded file
        os.remove(fileName)
        
        return(dictionary)    
        
    # TODO getFragment
    # TODO getFragmentSeries
