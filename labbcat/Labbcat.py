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
    """
    
    def _labbcatUrl(self, resource):
        return self.labbcatUrl + resource

    # TODO newTranscript
    # TODO updateTranscript
    # TODO taskStatus
    # TODO waitForTask
    # TODO cancelTask
    # TODO releaseTask
    
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
