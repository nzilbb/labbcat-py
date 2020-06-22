from labbcat.LabbcatEdit import LabbcatEdit

class LabbcatAdmin(LabbcatEdit):
    """ API for querying, updating, and administering a `LaBB-CAT
    <https://labbcat.canterbury.ac.nz>`_ annotation graph store; a database of linguistic
    transcripts represented using `Annotation Graphs <https://nzilbb.github.io/ag/>`_

    This class inherits the *read-write* operations of GraphStore
    and adds some administration operations, including definition of layers,
    registration of converters, etc., i.e. those that can be performed by users with
    "admin" permission.
    
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
    
    def createCorpus(self, corpus_name, corpus_language, corpus_description):
        """ Creates a new corpus record.
        
        The dictionary returned has the following entries:
        
        - "corpus_id"          : The database key for the record.
        - "corpus_name"        : The name/id of the corpus.
        - "corpus_language"    : The ISO 639-1 code for the default language.
        - "corpus_description" : The description of the corpus.
        - "_cantDelete"        : This is not a database field, but rather is present
                                 in records returned from the server that can not
                                 currently be deleted; a string representing the reason
                                 the record can't be deleted.  
        
        :param corpus_name: The name/id of the corpus.
        :type corpus_name: str
        
        :param corpus_language: The ISO 639-1 code for the default language.
        :type corpus_language: str
        
        :param corpus_description: The description of the corpus.
        :type corpus_description: str
        
        :returns: A copy of the corpus record
        :rtype: dict
        """
        return(self._postRequest(self._labbcatUrl("api/admin/corpora"), {}, {
            "corpus_name" : corpus_name,
            "corpus_language" : corpus_language,
            "corpus_description" : corpus_description }))
    
    def readCorpora(self, pageNumber=None, pageLength=None):
        """ Reads a list of corpus records.
        
        The dictionaries in the returned list have the following entries:
        
        - "corpus_id"          : The database key for the record.
        - "corpus_name"        : The name/id of the corpus.
        - "corpus_language"    : The ISO 639-1 code for the default language.
        - "corpus_description" : The description of the corpus.
        - "_cantDelete"        : This is not a database field, but rather is present
                                 in records returned from the server that can not
                                 currently be deleted; a string representing the reason
                                 the record can't be deleted.  
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :param pageLength: The maximum number of records to return, or null to return all.
        :type pageLength: int or None
        
        :returns: A list of corpus records.
        :rtype: list of dict
        """
        # define request parameters
        parameters = {}
        if pageNumber != None:
            parameters["pageNumber"] = pageNumber
        if pageLength != None:
            parameters["pageLength"] = pageLength
        return(self._getRequest(self._labbcatUrl("api/admin/corpora"), parameters))
        
    def updateCorpus(self, corpus_name, corpus_language, corpus_description):
        """ Updates an existing corpus record.
        
        The dictionary returned has the following entries:
        
        - "corpus_id"          : The database key for the record.
        - "corpus_name"        : The name/id of the corpus.
        - "corpus_language"    : The ISO 639-1 code for the default language.
        - "corpus_description" : The description of the corpus.
        - "_cantDelete"        : This is not a database field, but rather is present
                                 in records returned from the server that can not
                                 currently be deleted; a string representing the reason
                                 the record can't be deleted.  
        
        :param corpus_name: The name/id of the corpus.
        :type corpus_name: str
        
        :param corpus_language: The ISO 639-1 code for the default language.
        :type corpus_language: str
        
        :param corpus_description: The description of the corpus.
        :type corpus_description: str
        
        :returns: A copy of the corpus record
        :rtype: dict
        """
        return(self._putRequest(self._labbcatUrl("api/admin/corpora"), {}, {
            "corpus_name" : corpus_name,
            "corpus_language" : corpus_language,
            "corpus_description" : corpus_description }))
    
    def deleteCorpus(self, corpus_name):
        """ Deletes an existing corpus record.
        
        :param corpus_name: The name/id of the corpus.
        :type corpus_name: str        
        """
        return(self._deleteRequest(self._labbcatUrl("api/admin/corpora/"+corpus_name), {}))
    
