import time
import os
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
        

    # TODO search
    # TODO getMatches
    # TODO getMatchAnnotations
    # TODO getSoundFragments
    # TODO getFragments
