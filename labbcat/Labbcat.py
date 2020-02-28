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

    # TODO newTranscript
    # TODO updateTranscript
    def taskStatus(self, threadId):
        """ Gets the current state of the given task.

        :param threadId: The ID of the task.
        :type threadId: str.

        :returns: The status of the task.
        :rtype:
        """
        return(self._getRequest(self._labbcatUrl("thread"), { "threadId" : threadId }))

    # TODO waitForTask
    
    def cancelTask(self, threadId):
        """ Cancels a running task.

        :param threadId: The ID of the task.
        :type threadId: str.
        """
        return(self._getRequest(self._labbcatUrl("threads"), {
            "threadId" : threadId, "command" : "cancel" }))

    def releaseTask(self, threadId):
        """ Release a finished task, to free up server resources.

        :param threadId: The ID of the task.
        :type threadId: str.
        """
        return(self._getRequest(self._labbcatUrl("threads"), {
            "threadId" : threadId, "command" : "release" }))

    def getTasks(self):
        """ Gets a list of all tasks on the server. 
        
        :returns: A list of all task statuses.
        :rtype: list of dictionaries
        """
        return(self._getRequest(self._labbcatUrl("threads"), None))

    # TODO search
    # TODO getMatches
    # TODO getMatchAnnotations
    # TODO getSoundFragments
    # TODO getFragments
