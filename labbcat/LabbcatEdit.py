import os
from labbcat.LabbcatView import LabbcatView

class LabbcatEdit(LabbcatView):
    """ API for querying and updating a `LaBB-CAT <https://labbcat.canterbury.ac.nz>`_
    annotation graph store; a database of linguistic transcripts represented using 
    `Annotation Graphs <https://nzilbb.github.io/ag/>`_
    
    This class inherits the *read-only* operations of LabbcatView and adds some *write*
    operations for updating data, i.e. those that can be performed by users with "edit"
    permission.
    
    Constructor arguments:    
    
    :param labbcatUrl: The 'home' URL of the LaBB-CAT server.
    :type labbcatUrl: str
    
    :param username: The username for logging in to the server, if necessary.
    :type username: str or None
    
    :param password: The password for logging in to the server, if necessary.
    :type password: str or None
    """
    
    def _storeEditUrl(self, resource):
        return self.labbcatUrl + "api/edit/store/" + resource

    def deleteTranscript(self, id):
        """ Deletes the given transcript, and all associated files.
        
        :param id: The ID transcript to delete.
        :type id: str
        """
        return(self._postRequest(self._storeEditUrl("deleteTranscript"), {"id":id}))
    
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
        
        :returns: The taskId of the resulting annotation layer generation task. The
                  task status can be updated using
                  `taskStatus() <#labbcat.LabbcatView.taskStatus>`_.
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
        """ Uploads a new version of an existing transcript.
        
        :param transcript: The path to the transcript to upload.
        :type transcript: str
        
        :returns: A dictionary of transcript IDs (transcript names) to task threadIds. The
                  task status can be updated using
                  `taskStatus() <#labbcat.LabbcatView.taskStatus>`_.
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
    
    def updateFragment(self, fragment):
        """ Update a transcript fragment.

        This function uploads a file (e.g. Praat TextGrid) representing a fragment of a
        transcript, with annotations or alignments to update in LaBB-CAT's version of the
        transcript. 
        
        :param fragment: The path to the fragment to upload.
        :type fragment: str
        
        :returns: A dictionary with information about the fragment that was updated, including
                  URL, start_time, and end_time
        :rtype: dictionary of str
        """
        params = {
            "todo" : "upload",
            "automaticMapping" : "true" }
        
        fragmentName = os.path.basename(fragment)
        files = {}
        f = open(fragment, 'rb')
        files["uploadfile"] = (fragmentName, f)
        
        try:
            model = self._postMultipartRequest(
                self._labbcatUrl("edit/uploadFragment"), params, files)
            return(model)
        finally:
            f.close()
        
    def deleteParticipant(self, id):
        """ Deletes the given participant, and all associated meta-data.
        
        :param id: The ID participant to delete.
        :type id: str
        """
        return(self._postRequest(self._storeEditUrl("deleteParticipant"), {"id":id}))
    
    def generateLayerUtterances(self, matchIds, layerId, collectionName=None):
        """ Generates a layer for a given set of utterances.

        This function generates annotations on a given layer for a given set of
        utterances, e.g. force-align selected utterances of a participant.
        
        :param matchIds: A list of annotation IDs, e.g. the MatchId column, or the URL
                         column, of a results set.  
        :type layerId: list of str
        
        :param layerId: The ID of the layer to generate.
        :type layerId: str
        
        :returns: The taskId of the resulting annotation layer generation task. The
                  task status can be updated using
                  `taskStatus() <#labbcat.LabbcatView.taskStatus>`_.
        :rtype: str
        """
        # we need a list of strings, so if we've got a list of dictionaries, convert it
        if len(matchIds) > 0:
            if isinstance(matchIds[0], dict):
                # map the dictionaries to their "MatchId" entry
                matchIds = [ m["MatchId"] for m in matchIds ]
        params = {
            "todo" : "generate-now",
            "generate_layer" : layerId,
            "utterances" : matchIds }
        if collectionName != None: params["collection_name"] = collectionName
        
        model = self._postRequest(self._labbcatUrl("generateLayerUtterances"), params)
        return(model["threadId"])
