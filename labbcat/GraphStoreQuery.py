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
        if resp.status_code <> requests.codes.ok and self.verbose:
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
        if resp.status_code <> requests.codes.ok and self.verbose:
            print("response status: " + resp.status_code)
            print("response text: " + resp.text)
        resp.raise_for_status()        
        return(resp.json()["model"])
         
    def getId(self):
        """ Gets the store's ID. """
        return(self._getRequest(self._storeQueryUrl("getId"), None))
        
    def getLayerIds(self):
        """ Gets a list of layer IDs (annotation 'types'). """
        return(self._getRequest(self._storeQueryUrl("getLayerIds"), None))
        
    def getLayers(self):
        """ Gets a list of layer definitions. """
        return(self._getRequest(self._storeQueryUrl("getLayers"), None))
        
    def getLayer(self, id):
        """ Gets a layer definition. """
        return(self._getRequest(self._storeQueryUrl("getLayer"), {"id":id}))
        
    def getCorpusIds(self):
        """ Gets a list of corpus IDs. """
        return(self._getRequest(self._storeQueryUrl("getCorpusIds"), None))
        
    def getParticipantIds(self):
        """ Gets a list of participant IDs. """
        return(self._getRequest(self._storeQueryUrl("getParticipantIds"), None))
        
    def getParticipant(self, id):
        """ Gets the participant record specified by the given identifier. """
        return(self._getRequest(self._storeQueryUrl("getParticipant"), {"id":id}))
        
    def countMatchingParticipantIds(self, expression):
        """ Counts the number of participants that match a particular pattern. """
        return(self._getRequest(
            self._storeQueryUrl("countMatchingParticipantIds"),
            { "expression":expression }))
        
    def getMatchingParticipantIds(self, expression, pageLength=None, pageNumber=None):
        """ Gets a list of IDs of participants that match a particular pattern. """
        return(self._getRequest(
            self._storeQueryUrl("getMatchingParticipantIds"),
            {"expression":expression,
             "pageLength":pageLength, "pageNumber":pageNumber}))
        
    def getTranscriptIds(self):
        """ Gets a list of transcript IDs. """
        return(self._getRequest(self._storeQueryUrl("getTranscriptIds"), None))
        
    def getTranscriptIdsInCorpus(self, id):
        """ Gets a list of transcript IDs in the given corpus. """
        return(self._getRequest(self._storeQueryUrl("getTranscriptIdsInCorpus"), {"id":id}))
        
    def getTranscriptIdsWithParticipant(self, id):
        """ Gets a list of IDs of transcripts that include the given participant. """
        return(self._getRequest(self._storeQueryUrl("getTranscriptIdsWithParticipant"), {"id":id}))
        
    def countMatchingTranscriptIds(self, expression):
        """ Counts the number of transcripts that match a particular pattern. """
        return(self._getRequest(
            self._storeQueryUrl("countMatchingTranscriptIds"),
            { "expression":expression }))
        
    def getMatchingTranscriptIds(self, expression, pageLength=None, pageNumber=None, order=None):
        """ Gets a list of IDs of transcripts that match a particular pattern. """
        return(self._getRequest(
            self._storeQueryUrl("getMatchingTranscriptIds"),
            { "expression":expression,
              "pageLength":pageLength, "pageNumber":pageNumber,
              "order":order}))
        
    def countMatchingAnnotations(self, expression):
        """ Counts the number of annotations that match a particular pattern. """
        return(self._getRequest(
            self._storeQueryUrl("countMatchingAnnotations"),
            { "expression":expression }))
        
    def getMatchingAnnotations(self, expression, pageLength=None, pageNumber=None):
        """ Gets a list of annotations that match a particular pattern. """
        return(self._getRequest(
            self._storeQueryUrl("getMatchingAnnotations"),
            { "expression":expression,
              "pageLength":pageLength, "pageNumber":pageNumber }))
        
    def countAnnotations(self, id, layerId):
        """ Gets the number of annotations on the given layer of the given transcript. """
        return(self._getRequest(
            self._storeQueryUrl("countAnnotations"),
            { "id":id, "layerId":layerId }))
        
    def getAnnotations(self, id, layerId, pageLength=None, pageNumber=None):
        """ Gets the annotations on the given layer of the given transcript. """
        return(self._getRequest(
            self._storeQueryUrl("getAnnotations"),
            { "id":id, "layerId":layerId,
              "pageLength":pageLength, "pageNumber":pageNumber }))
        
    def getAnchors(self, id, anchorIds):
        """ Gets the given anchors in the given transcript. """
        return(self._getRequest(
            self._storeQueryUrl("getAnchors"),
            { "id":id, "anchorIds":anchorIds }))
        
    def getTranscript(self, id, layerIds=None):
        """ Gets a transcript given its ID. """
        return(self._getRequest(
            self._storeQueryUrl("getTranscript"),
            { "id":id, "layerIds":layerIds }))
        
    def getMediaTracks(self):
        """ List the predefined media tracks available for transcripts. """
        return(self._getRequest(self._storeQueryUrl("getMediaTracks"), None))
        
    def getAvailableMedia(self, id):
        """ List the media available for the given transcript. """
        return(self._getRequest(
            self._storeQueryUrl("getAvailableMedia"),
            { "id":id }))
        
    def getMedia(self, id, trackSuffix, mimeType, startOffset=None, endOffset=None):
        """ Gets a given media track for a given transcript. """
        return(self._getRequest(
            self._storeQueryUrl("getMedia"),
            { "id":id, "trackSuffix":trackSuffix, "trackSuffix":trackSuffix,
              "startOffset":startOffset, "endOffset":endOffset }))
        
    def getEpisodeDocuments(self, id):
        """ Get a list of documents associated with the episode of the given transcript. """
        return(self._getRequest(
            self._storeQueryUrl("getEpisodeDocuments"),
            { "id":id }))
        

    # TODO getMatchingAnnotations
    # TODO getFragment
    # TODO getFragmentSeries
