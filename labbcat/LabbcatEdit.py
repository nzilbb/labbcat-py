import os
from labbcat.LabbcatView import LabbcatView
from labbcat.ResponseException import ResponseException

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

    def transcriptUpload(self, transcript, media, merge, trackSuffix=None):
        """ Upload a transcript file and associated media files, as the first stage in adding or
        modifying a transcript to LaBB-CAT. The second stage is 
        `transcriptUploadParameters() <#labbcat.LabbcatEdit.transcriptUploadParameters>`_
        
        :param transcript: The path to the transcript to upload.
        :type transcript: str
        
        :param media: The path to media to upload, if any. 
        :type media: str

        :param merge: Whether the upload corresponds to updates to an existing transcript
                      (True) or a new transcript (False).
        :type merge: boolean

        :param trackSuffix: The track suffix for the media, which can be None.
        :type trackSuffix: str

        :returns: A dictionary containing the following entries:
        
        - "id" - The unique identifier to use for this upload when subsequently calling 
                 `transcriptUploadParameters() <#labbcat.LabbcatEdit.transcriptUploadParameters>`_
        - "parameters" - A list of dict representing the parameters that
                 require values to be passed into 
                 `transcriptUploadParameters() <#labbcat.LabbcatEdit.transcriptUploadParameters>`_
                 The parameters returned may include both information
                 required by the format deserializer (e.g. mappings from tiers to LaBB-CAT
                 layers) and also general information required by LaBB-CAT (e.g. the
                 corpus, episode, and type of the transcript).
        
        :rtype: dict
        
        Each parameter returned is a dict that may contain the following attributes:
        
        - "name" - The name that should be used when specifying the value for the parameter
               when calling 
               `transcriptUploadParameters() <#labbcat.LabbcatEdit.transcriptUploadParameters>`_
        - "label" - A label for the parameter intended for display to the user.
        - "hint" - A description of the purpose of the parameter, for display to the user.
        - "type" - The type of the parameter, e.g. "String", "Double", "Integer", "Boolean".
        - "required" - True if the value must be specified, False if it is optional.
        - "value" - A default value for the parameter.
        - "possibleValues" - A list of possible values, if the possibilities are limited 
               to a finite set.

        The required parameters may include both information required by the format deserializer 
        (e.g. mappings from tiers to LaBB-CAT layers) and also general information required by 
        LaBB-CAT, such as: 

        - "labbcat_corpus" - The corpus the new transcript(s) belong(s) to.
        - "labbcat_episode" - The episode the new transcript(s) belong(s) to.
        - "labbcat_transcript_type" - The transcript type for the new transcript(s).
        - "labbcat_generate" - Whether to re-regenerate layers of automated annotations or not.
        """
        params = {}
        if merge:
            params["merge"] = "true"
        
        transcriptName = os.path.basename(transcript)
        files = {}
        f = open(transcript, 'rb')
        files["transcript"] = (transcriptName, f)
        
        if media != None:
            if trackSuffix == None: trackSuffix = ""
            mediaName = os.path.basename(media)
            files["media"+trackSuffix] = (mediaName, open(media, 'rb'))

        try:
            return(self._postMultipartRequest(
                self._labbcatUrl("api/edit/transcript/upload"), params, files))
        finally:
            f.close()
        
    def transcriptUploadParameters(self, id, parameters):
        """ The second part of a transcript upload process started by a call to
        `transcriptUpload() <#labbcat.LabbcatEdit.transcriptUpload>`_, which specifies values
        for the parameters required to save the uploaded transcript to LaBB-CAT's database. 
        
        If the response includes more parameters, then this method should be called again
        to supply their values.
        
        :param id: Upload ID returned by the prior call to 
                   `transcriptUpload() <#labbcat.LabbcatEdit.transcriptUpload>`_.
        :type id: str
        
        :param parameters: A dictionary with an attribute and value for each parameter returned by 
         the prior call to `transcriptUpload() <#labbcat.LabbcatEdit.transcriptUpload>`_.
        :type parameters: dict
        
        :returns: A dictionary containing the following entries:
        
        - "transcripts" - a dictionary for which each key is a transcript name, and its 
                value is the threadId of the server task processing the uploaded transcript, 
                which can be passed to `taskStatus() <#labbcat.LabbcatView.taskStatus>`_
                to monitor progress.
        - "id" - The unique identifier for this upload for if a subsequent call is required to  
                 `transcriptUploadParameters() <#labbcat.LabbcatEdit.transcriptUploadParameters>`_
        - "parameters" - A list of dict representing the parameters that still
                 require values to be passed into 
                 `transcriptUploadParameters() <#labbcat.LabbcatEdit.transcriptUploadParameters>`_
                 if any.
        
        :rtype: dict
        """
        return(self._putRequest(self._labbcatUrl("api/edit/transcript/upload/"+id), parameters))
        
    def transcriptUploadDelete(self, id):
        """ Cancel a transcript upload started by a previous call to        
        `transcriptUpload() <#labbcat.LabbcatEdit.transcriptUpload>`_, 
        deleting any uploaded files from the server.

        :param id: Upload ID returned by the prior call to 
                   `transcriptUpload() <#labbcat.LabbcatEdit.transcriptUpload>`_.
        :type id: str
        """
        return(self._deleteRequest(self._labbcatUrl("api/edit/transcript/upload/"+id), {}))
    
    def newTranscript(self, transcript, media, trackSuffix, transcriptType, corpus, episode):
        """ Uploads a new transcript.
        
        :param transcript: The path to the transcript to upload.
        :type transcript: str
        
        :param media: The path to media to upload, if any. 
        :type media: str
        
        :param trackSuffix: The track suffix for the media, which can be None.
        :type trackSuffix: str
        
        :param transcriptType: The transcript type.
        :param type: str
        
        :param corpus: The corpus for the transcript.
        :type corpus: str
        
        :param episode: The episode the transcript belongs to.
        :type episode: str
        
        :returns: A dictionary of transcript IDs (transcript names) to task threadIds. The
                  task status can be updated using
                  `taskStatus() <#labbcat.LabbcatView.taskStatus>`_.
        :rtype: dictionary of str
        """
        try:
            response = self.transcriptUpload(transcript, media, False, trackSuffix)
            id = response["id"]
            parameters = response["parameters"]
            
            # set parameters with default values
            parameterValues = {}
            for parameter in parameters:
                parameterValues[parameter["name"]] = parameter["value"]
            response = self.transcriptUploadParameters(id, parameterValues)
            return(response["transcripts"])
        
        except ResponseException as x:
            # fall back to old API
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
                    return(model["result"])
            finally:
                f.close()
        
    def updateTranscript(self, transcript, suppressGeneration=False):
        """ Uploads a new version of an existing transcript.
        
        :param transcript: The path to the transcript to upload.
        :type transcript: str

        :param suppressGeneration: False (the default) to run automatic layer generation,
                                   True to suppress automatic layer generation.
        :type suppressGeneration: boolean
        
        :returns: A dictionary of transcript IDs (transcript names) to task threadIds. The
                  task status can be updated using
                  `taskStatus() <#labbcat.LabbcatView.taskStatus>`_.
        :rtype: dictionary of str
        """
        try:
            response = self.transcriptUpload(transcript, None, True)
            id = response["id"]
            parameters = response["parameters"]
            
            # set parameters with default values
            parameterValues = {}
            for parameter in parameters:
                if parameter["name"] == "labbcat_generate":
                    parameterValues[parameter["name"]] = not suppressGeneration
                else:
                    parameterValues[parameter["name"]] = parameter["value"]
            response = self.transcriptUploadParameters(id, parameterValues)
            return(response["transcripts"])
        
        except ResponseException as x:
            # fall back to legacy API
            params = {
                "todo" : "update",
                "auto" : "true" }
            if suppressGeneration:
                params["suppressGeneration"] = "true"
            
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
                    return model["result"]
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
        
    def saveMedia(self, id, media, trackSuffix):
        """ Saves the given media for the given transcript.
        
        :param id: The transcript ID.
        :type id: str
        
        :param media: The path to media to upload. 
        :type media: str
        
        :param trackSuffix: The track suffix for the media.
        :type trackSuffix: str
        
        :returns: A dictionary of attributes of the media file (name, url, etc.).
        :rtype: dictionary of str
        """
        params = {
            "id" : id,
            "trackSuffix" : trackSuffix }
        
        mediaName = os.path.basename(media)
        f = open(media, 'rb')
        files = {}
        files["media"] = (mediaName, f)

        try:
            model = self._postMultipartRequest(
                self._storeEditUrl("saveMedia"), params, files)
            return(model)
        finally:
            f.close()
        
    def saveEpisodeDocument(self, id, document):
        """ Saves the given media for the given transcript.
        
        :param id: The transcript ID.
        :type id: str
        
        :param media: The path to the document to upload. 
        :type media: str
        
        :returns: A dictionary of attributes of the document file (name, url, etc.).
        :rtype: dictionary of str
        """
        params = { "id" : id }
        
        documentName = os.path.basename(document)
        f = open(document, 'rb')
        files = {}
        files["document"] = (documentName, f)

        try:
            model = self._postMultipartRequest(
                self._storeEditUrl("saveEpisodeDocument"), params, files)
            return(model)
        finally:
            f.close()
        
    def deleteMedia(self, id, fileName):
        """ Delete a given media or episode document file.
        
        :param id: The ID transcript whose media will be deleted.
        :type id: str

        :param fileName: The media file name, e.g. mediaFile['name'].
        :type fileName: str
        """
        return(self._postRequest(self._storeEditUrl("deleteMedia"), {
            "id": id,
            "fileName": fileName }))
    
    def saveParticipant(self, id, label, attributes):
        """ Saves a participant, and all its tags, to the graph store.
            To change the ID of an existing participant, pass the old/current ID as the
            id, and pass the new ID as the label.
            If the participant ID does not already exist in the database, a new participant record
            is created. 
        
        :param id: The ID participant to update.
        :type id: str
        
        :param label: The new ID (name) for the participant.
        :type label: str
        
        :param attributes: Participant attribute values - the names are the participant attribute
                           layer IDs, and the values are the corresponding new attribute values.
                           The pass phrase for participant access can also be set by specifying
                           a "_password" attribute.
        :type attributes: dictionary of str
        
        :returns: True if the participant was updated, False if there were no changes to update.
        :rtype: boolean
        """
        attributes['id'] = id
        attributes['label'] = label
        return(self._postRequest(self._storeEditUrl("saveParticipant"), attributes))
    
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

    def getAnnotatorDescriptor(self, annotatorId):
        """ Gets annotator information.
        
        Retrieve information about an annotator. Annotators are modules that perform different
        annotation tasks. This function provides information about a given annotator, for
        example the currently installed version of the module, what configuration parameters it
        requires, etc.

        The retuned dictionary contains the following entries:
        
        - "annotatorId" - The annotators's unique ID  
        - "version" - The currently install version of the annotator.  
        - "info" - HTML-encoded description of the function of the annotator.  
        - "infoText" - A plain text version of $info (converted automatically).  
        - "hasConfigWebapp" - Determines whether the annotator includes a web-app for
          installation or general configuration. 
        - "configParameterInfo" - An HTML-encoded definition of the installation config parameters, including a list of all parameters, and the encoding of the parameter string.
        - "hasTaskWebapp" - Determines whether the annotator includes a web-app for
          task parameter configuration.
        - "taskParameterInfo" - An HTML-encoded definition of the task parameters,
          including a list of all parameters, and the encoding of the parameter string.  
        - "hasExtWebapp" - Determines whether the annotator includes an extras web-app
          which implements functionality for providing extra data or extending
          functionality in an annotator-specific way.
        - "extApiInfo" - An HTML-encoded document containing information about what
          endpoints are published by the ext web-app.
        
        :param annotatorId: ID of the annotator module.
        :type annotatorId: str
        
        :returns: The annotator info.
        :rtype: dictionary of str
        """
        return(self._getRequest(self._storeQueryUrl(
            "getAnnotatorDescriptor"), {"annotatorId":annotatorId}))

    def addLayerDictionaryEntry(self, layerId, key, entry):
        """ Adds an entry to a layer dictionary.
        
        This function adds a new entry to the dictionary that manages a given layer,
        and updates all affected tokens in the corpus. Words can have multiple entries.
        
        :param layerId: The ID of the layer with a dictionary configured to manage it.
        :type layerId: str
        
        :param key: The key (word) in the dictionary to add an entry for.
        :type key: str
        
        :param entry: The value (definition) for the given key.
        :type entry: str
        
        :returns: None if the entry was added, or an error message if not.
        :rtype: str or None
        """
        try:
            self._postRequest(self._labbcatUrl(
            "api/edit/dictionary/add"), { "layerId":layerId, "key":key, "entry":entry })
            return(None)
        except ResponseException as x:
            return(x.message)

    def removeLayerDictionaryEntry(self, layerId, key, entry=None):
        """ Removes an entry from a layer dictionary.

        This function removes an existing entry from the dictionary that manages a given layer,
        and updates all affected tokens in the corpus. Words can have multiple entries.
        
        :param layerId: The ID of the layer with a dictionary configured to manage it.
        :type layerId: str
        
        :param key: The key (word) in the dictionary to remove an entry for.
        :type key: str
        
        :param entry: The value (definition) to remove, or None to remove all the entries for key.
        :type entry: str
        
        :returns: None if the entry was removed, or an error message if not.
        :rtype: str or None
        """
        try:
            self._postRequest(self._labbcatUrl(
            "api/edit/dictionary/remove"), { "layerId":layerId, "key":key, "entry":entry })
            return(None)
        except ResponseException as x:
            return(x.message)

    def addDictionaryEntry(self, managerId, dictionaryId, key, entry):
        """ Adds an entry to a dictionary.
        
        This function adds a new entry to the given dictionary. Words can have multiple entries.
        
        :param managerId: The layer manager ID of the dictionary, as returned by
                          `getDictionaries() <#labbcat.LabbcatView.getDictionaries>`_
        :type managerId: str
        
        :param dictionaryId: The ID of the dictionary, as returned by 
                             `getDictionaries() <#labbcat.LabbcatView.getDictionaries>`_.
        :type dictionaryId: str
        
        :param key: The key (word) in the dictionary to add an entry for.
        :type key: str
        
        :param entry: The value (definition) for the given key.
        :type entry: str
        
        :returns: None if the entry was added, or an error message if not.
        :rtype: str or None
        """
        try:
            self._postRequest(self._labbcatUrl(
            "api/edit/dictionary/add"), {
                "layerManagerId" : managerId,
                "dictionaryId" : dictionaryId,
                "key" : key,
                "entry" : entry })
            return(None)
        except ResponseException as x:
            return(x.message)

    def removeDictionaryEntry(self, managerId, dictionaryId, key, entry=None):
        """ Removes an entry from a dictionary.

        This function removes an existing entry from the given dictionary. Words can have 
        multiple entries.
        
        :param managerId: The layer manager ID of the dictionary, as returned by getDictionaries
        :type managerId: str
        
        :param dictionaryId: The ID of the dictionary, as returned by 
                             `getDictionaries() <#labbcat.LabbcatView.getDictionaries>`_.
        :type dictionaryId: str
        
        :param key: The key (word) in the dictionary to remove an entry for.
        :type key: str
        
        :param entry: The value (definition) to remove, or None to remove all the entries for key.
        :type entry: str
        
        :returns: None if the entry was removed, or an error message if not.
        :rtype: str or None
        """
        try:
            self._postRequest(self._labbcatUrl(
            "api/edit/dictionary/remove"), {
                "layerManagerId" : managerId,
                "dictionaryId" : dictionaryId,
                "key" : key,
                "entry" : entry })
            return(None)
        except ResponseException as x:
            return(x.message)
    
    def annotatorExt(self, annotatorId, resource, parameters=None):
        """ Retrieve annotator's "ext" resource.

        Retrieve a given resource from an annotator's "ext" web app. Annotators are modules
        that perform different annotation tasks, and can optionally implement functionality for
        providing extra data or extending functionality in an annotator-specific way. If the
        annotator implements an "ext" web app, it can provide resources and implement a
        mechanism for iterrogating the annotator. This function provides a mechanism for
        accessing these resources via python.

        Details about the resources available for a given annotator are available by
        calling `getAnnotatorDescriptor() <#labbcat.LabbcatEdit.getAnnotatorDescriptor>`_
        and checking "hasExtWebapp" attribute to ensure an 'ext' webapp is implemented,
        and checking details the "extApiInfo" attribute.
        
        :param annotatorId: ID of the annotator to interrogate.
        :type annotatorId: str
        
        :param resource: The name of the file to retrieve or instance method (function) to
         invoke. Possible values for this depend on the specific annotator being interrogated.
        :type resource: str
        
        :param parameters: Optional list of ordered parameters for the instance method (function).
        :type parameters: str
        
        :returns: The resource requested.
        :rtype: str
        """
        queryString = ""
        if parameters != None:
            queryString = "?" + ",".join(parameters)
        path = "edit/annotator/ext/"+annotatorId+"/"+resource+queryString
        response = self._getRequestRaw(self._labbcatUrl(path), None)
        
        # ensure status was ok
        response.raise_for_status();

        # return the result
        return(response.text)
