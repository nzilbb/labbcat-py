from labbcat.GraphStoreQuery import GraphStoreQuery

class GraphStore(GraphStoreQuery):
    """ API for querying and updating a `LaBB-CAT <https://labbcat.canterbury.ac.nz>`_
    annotation graph store; a database of linguistic transcripts represented using 
    `Annotation Graphs <https://nzilbb.github.io/ag/>`_
    
    This class inherits the *read-only* operations of GraphStoreQuery
    and adds some *write* operations for updating data.
    
    Constructor arguments:    
    
    :param labbcatUrl: The 'home' URL of the LaBB-CAT server.
    :type labbcatUrl: str
    
    :param username: The username for logging in to the server, if necessary.
    :type username: str or None
    
    :param password: The password for logging in to the server, if necessary.
    :type password: str or None
    """
    
    def _storeEditUrl(self, resource):
        return self.labbcatUrl + "edit/store/" + resource

    def deleteTranscript(self, id):
        """ Deletes the given transcript, and all associated files.
        
        :param id: The ID transcript to save.
        :type id: str
        """
        return(self._postRequest(self._storeEditUrl("deleteTranscript"), {"id":id}))
