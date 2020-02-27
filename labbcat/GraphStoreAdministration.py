from labbcat.GraphStore import GraphStore

class GraphStoreAdministration(GraphStore):
    """ API for querying, updating, and administering an annotation graph store. """

    def _storeAdminUrl(self, resource):
        return self.labbcatUrl + "admin/store/" + resource

