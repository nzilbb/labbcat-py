import json
import os
import tempfile
import time
from labbcat.GraphStoreAdministration import GraphStoreAdministration

class Labbcat(GraphStoreAdministration):
    """ Labbcat client, for accessing LaBB-CAT server functions programmatically. 
    
    `LaBB-CAT <https://labbcat.canterbury.ac.nz>`_ is an annotation graph store
    functionality; a database of linguistic transcripts represented using `Annotation
    Graphs <https://nzilbb.github.io/ag/>`_. 
    
    This class inherits the *read-write* operations of GraphStoreAdministration
    and adds some extra operations, including transcript upload and task management. 
    
    Constructor arguments:    
    
    :param labbcatUrl: The 'home' URL of the LaBB-CAT server.
    :type labbcatUrl: str
    
    :param username: The username for logging in to the server, if necessary.
    :type username: str or None
    
    :param password: The password for logging in to the server, if necessary.
    :type password: str or None
    
    Example::
        
        import labbcat
        
        # create annotation store client
        store = labbcat.Labbcat("https://labbcat.canterbury.ac.nz", "demo", "demo");
        
        # show some basic information
        
        print("Information about LaBB-CAT at " + store.getId())
        
        layerIds = store.getLayerIds()
        for layerId in layerIds: 
            print("layer: " + layerId) 
        
        corpora = store.getCorpusIds()
        for corpus in corpora:
            print("transcripts in: " + corpus)
            for transcript in store.getTranscriptIdsInCorpus(corpus):
                print(" " + transcript)

    """
    
    def _labbcatUrl(self, resource):
        return self.labbcatUrl + resource

    def newTranscript(self, transcript, media, mediaSuffix, transcriptType, corpus, episode):
        """ Uploads a new transcript.

        :param transcript: The path to the transcript to upload.
        :type transcript: str

        :param media: The path to media to upload, if any. 
        :type media: str

        :param mediaSuffix: The media suffix for the media.
        :type mediaSuffix: str

        :param transcriptType: The transcript type.
        :param type: str

        :param corpus: The corpus for the transcript.
        :type corpus: str

        :param episode: The episode the transcript belongs to.
        :type episode: str

        :returns: The task ID of the resulting annotation layer generation task. The
                  task status can be updated using Labbcat.taskStatus(taskId).
        :rtype: str
        """
        params = {
            "todo" : "new",
            "auto" : "true",
            "transcript_type" : transcriptType,
            "corpus" : corpus,
            "episode" : episode }
        
        transcriptName = os.path.basename(transcript)
        files = {}
        f = open(transcript, 'rb')
        files["uploadfile1_0"] = (transcriptName, f)
        
        if media != None:
            if mediaSuffix == None: mediaSuffix = ""
            mediaName = os.path.basename(media)
            files["uploadmedia"+mediaSuffix+"1"] = (mediaName, open(media, 'rb'))

        try:
            model = self._postMultipartRequest(
                self._labbcatUrl("edit/transcript/new"), params, files)
            if not "result" in model:
                raise ResponseException("Malformed response model, no result: " + str(model))
            else:
                if transcriptName not in model["result"]:
                    raise ResponseException(
                        "Malformed response model, '"+transcriptName+"' not present: "
                        + str(model))
                else:
                    threadId = model["result"][transcriptName]
                    return(threadId)
        finally:
            f.close()
        
    def updateTranscript(self, transcript):
        """ Uploads a new transcript.

        :param transcript: The path to the transcript to upload.
        :type transcript: str

        :returns: A dictionary of transcript IDs (transcript names) to task threadIds. The
                  task status can be updated using Labbcat.taskStatus(taskId).
        :rtype: dictionary of str
        """
        params = {
            "todo" : "update",
            "auto" : "true" }
        
        transcriptName = os.path.basename(transcript)
        files = {}
        f = open(transcript, 'rb')
        files["uploadfile1_0"] = (transcriptName, f)
        
        try:
            model = self._postMultipartRequest(
                self._labbcatUrl("edit/transcript/new"), params, files)
            if not "result" in model:
                raise ResponseException("Malformed response model, no result: " + str(model))
            else:
                if transcriptName not in model["result"]:
                    raise ResponseException(
                        "Malformed response model, '"+transcriptName+"' not present: "
                        + str(model))
                else:
                    threadId = model["result"][transcriptName]
                    return(threadId)
        finally:
            f.close()

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
        :rtype: dictionary
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

    def releaseTask(self, threadId):
        """ Release a finished task, to free up server resources.

        :param threadId: The ID of the task.
        :type threadId: str.
        """
        self._getRequest(self._labbcatUrl("threads"), {
            "threadId" : threadId, "command" : "release" })
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
            "todo" : "export",
            "exportType" : "csv",
            "layer" : ["graph"]+layerIds,
            "id" : transcriptIds }
        return (self._postRequestToFile(self._labbcatUrl("transcripts"), params))
    
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
        

    def search(self, pattern, participantIds=None, transcriptTypes=None, mainParticipant=True, aligned=False, matchesPerTranscript=None):
        """
        Searches for tokens that match the given pattern.

pattern = { "columns" : [ { "layers" : { "orthography" : { "pattern" : "the" } } } ] }
        
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
        
        Examples of valid pattern objects include:
        
        ## words starting with 'ps...'
        pattern = { "columns" : [ { "layers" : { "orthography" : { "pattern" : "ps.*" } } } ] }
        
        ## the word 'the' followed immediately or with one intervening word by
        ## a hapax legomenon (word with a frequency of 1) that doesn't start with a vowel
        pattern = { "columns" : [
            { "layers" : {
                "orthography" : { "pattern" : "the" } }
              "adj" : 2 },
            { "layers" : {
                "phonemes" : { "not" : True, "pattern" : "[cCEFHiIPqQuUV0123456789~#\\$@].*" },
                "frequency" : { max : "2" } } } ] }
        
        For ease of use, the function will also accept the following abbreviated forms:
        
        ## a single list representing a 'one column' search, 
        ## and string values, representing regular expression pattern matching
        pattern = { "orthography" : "ps.*" }
        
        ## a list containing the columns (adj defaults to 1, so matching tokens are contiguous)...
        pattern = [
            { "orthography" : "the" },
            { "phonemes" : { "not" : True, "pattern" : "[cCEFHiIPqQuUV0123456789~#\\$@].*" },
              "frequency" : { "max" : "2" } } ]
        
        :param pattern: An object representing the pattern to search for, which mirrors the
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
        
        :returns: The threadId of the resulting task, which can be passed in to
        getMatches(), taskStatus(), waitForTask(), etc. 
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
        model = self._getRequest(self._labbcatUrl("search"), parameters)
        return(model["threadId"])
    
    def getMatches(self, threadId, wordsContext=0, pageLength=None, pageNumber=None):
        """
        Gets a list of tokens that were matched by search(pattern)
        
        If the task is still running, then this function will wait for it to finish.
        
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
        
        :param threadId: A task ID returned by search(pattern).
        :type threadId: str
        
        :param wordsContext: Number of words context to include in the <q>Before Match</q>
        and <q>After Match</q> columns in the results.
        :type wordsContext: int
        
        :param pageLength: The maximum number of matches to return, or None to return all.
        :type pageLength: int or None
        
        :param pageNumber: The zero-based page number to return, or null to return the
        first page.
        :type pageNumber: int or None
        
        :returns: A list of IDs that can be used to identify utterances/tokens that were matched by
        search(pattern), or None if the task was cancelled. 
        :rtype" list of dict
        """
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
        
        :param layerIds: A vector of layer IDs.
        :type layerIds: list of str
        
        :param targetOffset: The distance from the original target of the match, e.g.
         -  0 : find annotations of the match target itself
         -  1 : find annotations of the token immediately *after* match target
         - -1 : find annotations of the token immediately *before* match target
        :type targetOffset: int
        
        :param annotationsPerLayer: The number of annotations on the given layer to
         retrieve. In most cases, there's only one annotation available. However, tokens may,
         for example, be annotated with `all possible phonemic transcriptions', in which case
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
        fd, fileName = tempfile.mkstemp(".csv", "labbcat-py-getMatchAnnotations")
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

    def getSoundFragments(self, transcriptIds, startOffsets=None, endOffsets=None, sampleRate=None, dir=None):
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
        
        :returns: A list of WAV files. If *dir* is None, these files will be stored
         under the system's temporary directory, so once processing is finished, they should
         be deleted by the caller, or moved to a more permanent location. 
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
            dir = tempfile.mkdtemp("_wav", "getSoundFragments_")
            tempFiles = True
        elif not os.path.exists(dir):
            os.mkdir(dir)

        # loop through each triple, getting fragments individually
        url = self._labbcatUrl("soundfragment")
        for i in range(len(transcriptIds)):
            if transcriptIds[i] == None or startOffsets[i] == None or endOffsets[i] == None:
                continue
            
            params = {
                "id" : transcriptIds[i],
                "start" : startOffsets[i],
                "end" : endOffsets[i]
            }
            if sampleRate != None:
                params["sampleRate"] = sampleRate

            try:
                fileName = self._postRequestToFile(url, params, dir)
                fragments.append(fileName)
            except ResponseException:
                fragments.append(None)
        
        return(fragments)
    
    def getFragments(self, transcriptIds, layerIds, mimeType, startOffsets=None, endOffsets=None, dir=None):
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
        
        :returns: A list of files. If *dir* is None, these files will be stored under the
         system's temporary directory, so once processing is finished, they should be
         deleted by the caller, or moved to a more permanent location. 
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
            dir = tempfile.mkdtemp("_wav", "getFragments_")
            tempFiles = True
        elif not os.path.exists(dir):
            os.mkdir(dir)

        # loop through each triple, getting fragments individually
        url = self._labbcatUrl("convertfragment")
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

            try:
                fileName = self._postRequestToFile(url, params, dir)
                fragments.append(fileName)
            except ResponseException:
                fragments.append(None)
        
        return(fragments)

