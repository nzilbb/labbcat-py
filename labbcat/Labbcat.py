from labbcat.GraphStoreAdministration import GraphStoreAdministration

class Labbcat(GraphStoreAdministration):
    """ Labbcat client, for accessing LaBB-CAT server functions programmatically. """
    
    def _labbcatUrl(self, resource):
        return self.labbcatUrl + resource

    # TODO newTranscript
    # TODO updateTranscript
    # TODO taskStatus
    # TODO waitForTask
    # TODO cancelTask
    # TODO releaseTask
    
    def getTasks(self):
        """ Gets a list of all tasks on the server. """
        return(self._getRequest(self._labbcatUrl("threads"), None))

    # TODO search
    # TODO getMatches
    # TODO getMatchAnnotations
    # TODO getSoundFragments
    # TODO getFragments
