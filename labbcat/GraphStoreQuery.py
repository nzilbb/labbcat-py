import requests

class GraphStoreQuery:
    """ API for querying an annotation graph store. """
    
    def __init__(self, labbcatUrl, username=None, password=None):
        """ Constructor for this class. """

        if labbcatUrl.endswith("/"):
            self.labbcatUrl = labbcatUrl
        else:
            self.labbcatUrl = labbcatUrl + "/"
            
        self.username = username
        self.password = password
        self.verbose = False

    def _storeQueryUrl(self, resource):
        return self.labbcatUrl + "store/" + resource

    def _getRequest(self, url, params):
        if self.verbose: print("_getRequest " + url + " : " + str(params))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)            
        resp = requests.get(url=url, params=params, auth=auth, headers={"Accept":"application/json"})
        # TODO check for 401 and ask for credentials if required        
        if resp.status_code != requests.codes.ok and self.verbose:
            print("response status: " + resp.status_code)
            print("response text: " + resp.text)
        resp.raise_for_status()
        return(resp.json()["model"])
        
    def _postRequest(self, url, params):
        if self.verbose: print("_postRequest " + url + " : " + str(params))
        if self.username == None:
            auth = None
        else:
            auth = (self.username, self.password)            
        resp = requests.post(url=url, params=params, auth=auth, headers={"Accept":"application/json"})
        # TODO check for 401 and ask for credentials if required
        if resp.status_code != requests.codes.ok and self.verbose:
            print("response status: " + resp.status_code)
            print("response text: " + resp.text)
        resp.raise_for_status()        
        return(resp.json()["model"])
         
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
        :rtype: list
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
        - ``labels('who').includes('Robert')``
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
        - ``!/Ada.+/.test(id) && my('corpus').label == 'CC' && labels('who').includes('Robert')`` 
        
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
        - ``labels('who').includes('Robert')``
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
        - ``!/Ada.+/.test(id) && my('corpus').label == 'CC' && labels('who').includes('Robert')``
        
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
        - ``my('who').label == 'Robert' && my('utterances').start.offset == 12.345`` 
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
        - ``my('who').label == 'Robert' && my('utterances').start.offset == 12.345`` 
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
        
    def getMedia(self, id, trackSuffix, mimeType, startOffset=None, endOffset=None):
        """ Gets a given media track for a given transcript. 
        
        :param id: The transcript ID.
        :type id: str
        
        :param trackSuffix: The track suffix of the media. 
        :type trackSuffix: str
        
        :param mimeType: The MIME type of the media, which may include parameters for type
            conversion, e.g. 'text/wav; samplerate=16000'
        :type mimeType: str
        
        :param startOffset: The start offset of the media sample, or null for the start of
            the whole recording. 
        :type startOffset: int or None

        :param endOffset: The end offset of the media sample, or null for the end of the
            whole recording. 
        :type endOffset: int or None

        :returns: A URL to the given media for the given transcript, or null if the given
            media doesn't exist. 
        :rtype: str
        """
        return(self._getRequest(
            self._storeQueryUrl("getMedia"),
            { "id":id, "trackSuffix":trackSuffix, "trackSuffix":trackSuffix,
              "startOffset":startOffset, "endOffset":endOffset }))
        
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
        

    # TODO getMatchingAnnotations
    # TODO getFragment
    # TODO getFragmentSeries