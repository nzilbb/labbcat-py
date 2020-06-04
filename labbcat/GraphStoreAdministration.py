from labbcat.GraphStore import GraphStore

class GraphStoreAdministration(GraphStore):
    """ API for querying, updating, and administering a `LaBB-CAT
    <https://labbcat.canterbury.ac.nz>`_ annotation graph store; a database of linguistic
    transcripts represented using `Annotation Graphs <https://nzilbb.github.io/ag/>`_

    This class inherits the *read-write* operations of GraphStore
    and adds some administration operations, including definition of layers,
    registration of converters, etc.
    
    Constructor arguments:    
    
    :param labbcatUrl: The 'home' URL of the LaBB-CAT server.
    :type labbcatUrl: str
    
    :param username: The username for logging in to the server, if necessary.
    :type username: str or None
    
    :param password: The password for logging in to the server, if necessary.
    :type password: str or None

    """

    def _storeAdminUrl(self, resource):
        return self.labbcatUrl + "api/admin/store/" + resource

