from GraphStoreQuery import GraphStoreQuery

class GraphStore(GraphStoreQuery):
    """ API for querying and updating an annotation graph store. """
    
    def _storeEditUrl(self, resource):
        return self.labbcatUrl + "edit/store/" + resource

    def deleteTranscript(self, id):
        """ Deletes the given transcript, and all associated files. """
        return(self._postRequest(self._storeEditUrl("deleteTranscript"), {"id":id}))
