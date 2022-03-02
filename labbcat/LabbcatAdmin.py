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
    
    def newLayer(self, id, parentId, description, alignment,
                  peers, peersOverlap, parentIncludes, saturated, type,
                 validLabels={}, category=None, annotatorId=None, annotatorTaskParameters=None):
        """ Saves changes to a layer.
                
        :param id: The layer ID
        :type id: str
        
        :param parentId: The layer's parent layer id.
        :type parentId: str
        
        :param description: The description of the layer.
        :type description: str
        
        :param alignment: The layer's alignment - 0 for none, 1 for point alignment,
          2 for interval alignment. 
        :type alignment: number
        
        :param peers: Whether children on this layer have peers or not.
        :type peers: boolean
        
        :param peersOverlap: Whether child peers on this layer can overlap or not.
        :type peersOverlap: boolean
        
        :param parentIncludes: Whether the parent temporally includes the child.
        :type parentIncludes: boolean
        
        :param saturated: Whether children must temporally fill the entire parent duration (true)
          or not (false).
        :type saturated: boolean
        
        :param type: The type for labels on this layer, e.g. string, number, boolean, ipa.
        :type type: str
        
        :param validLabels: List of valid label values for this layer, or Nothing if the layer
          values are not restricted. The 'key' is the possible label value, and each key is
          associated with a description of the value (e.g. for displaying to users). 
        :type validLabels: dict
        
        :param category: Category for the layer, if any.
        :type category: str        
        
        :param annotatorId: The ID of the layer manager that automatically fills in
          annotations on the layer, if any
        :type annotatorId: str        
        
        :param annotatorTaskParameters: The configuration the layer manager should use when
          filling the layer with annotations. This is a string whose format is specific to
          each layer manager.
        :type annotatorTaskParameters: str        
        
        :returns: The resulting layer definition.
        :rtype: dict
        """
        return(self._postRequest(self._storeAdminUrl("newLayer"), {}, {
            "id" : id,
            "parentId" : parentId,
            "description" : description,
            "alignment" : alignment,
            "peers" : peers,
            "peersOverlap" : peersOverlap,
            "parentIncludes" : parentIncludes,
            "saturated" : saturated,
            "type" : type,
            "validLabels" : validLabels,
            "category" : category,
            "layer_manager_id" : annotatorId,
            "extra" : annotatorTaskParameters }))
    
    def saveLayer(self, id, parentId, description, alignment,
                  peers, peersOverlap, parentIncludes, saturated, type, validLabels, category):
        """ Saves changes to a layer.
                
        :param id: The layer ID
        :type id: str
        
        :param parentId: The layer's parent layer id.
        :type parentId: str
        
        :param description: The description of the layer.
        :type description: str
        
        :param alignment: The layer's alignment - 0 for none, 1 for point alignment,
          2 for interval alignment. 
        :type alignment: number
        
        :param peers: Whether children on this layer have peers or not.
        :type peers: boolean
        
        :param peersOverlap: Whether child peers on this layer can overlap or not.
        :type peersOverlap: boolean
        
        :param parentIncludes: Whether the parent temporally includes the child.
        :type parentIncludes: boolean
        
        :param saturated: Whether children must temporally fill the entire parent duration (true)
          or not (false).
        :type saturated: boolean
        
        :param type: The type for labels on this layer, e.g. string, number, boolean, ipa.
        :type type: str
        
        :param validLabels: List of valid label values for this layer, or Nothing if the layer
          values are not restricted. The 'key' is the possible label value, and each key is
          associated with a description of the value (e.g. for displaying to users). 
        :type validLabels: dict
        
        :param category: Category for the layer, if any.
        :type category: str        
        
        :returns: The resulting layer definition.
        :rtype: dict
        """
        return(self._postRequest(self._storeAdminUrl("saveLayer"), {}, {
            "id" : id,
            "parentId" : parentId,
            "description" : description,
            "alignment" : alignment,
            "peers" : peers,
            "peersOverlap" : peersOverlap,
            "parentIncludes" : parentIncludes,
            "saturated" : saturated,
            "type" : type,
            "validLabels" : validLabels,
            "category" : category}))
    
    def deleteLayer(self, id):
        """ Deletes a layer.
                
        :param id: The layer ID
        :type id: str
        
        """
        return(self._postRequest(self._storeAdminUrl("deleteLayer"), { "id" : id }))
    
    def createCorpus(self, corpus_name, corpus_language, corpus_description):
        """ Creates a new corpus record.
        
        The dictionary returned has the following entries:
        
        - "corpus_id"          : The database key for the record.
        - "corpus_name"        : The name/id of the corpus.
        - "corpus_language"    : The ISO 639-1 code for the default language.
        - "corpus_description" : The description of the corpus.
        - "_cantDelete"        : This is not a database field, but rather is present in
          records returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted. 
        
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
        - "_cantDelete"        : This is not a database field, but rather is present in
          records returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.  
        
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
        - "_cantDelete"        : This is not a database field, but rather is present in
          records returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.  
        
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
    
    def createProject(self, project, description):
        """ Creates a new project record.
        
        The dictionary returned has the following entries:
        
        - "project_id"  : The database key for the record.
        - "project"     : The name/id of the project.
        - "description" : The description of the project.
        - "_cantDelete" : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.   
        
        :param project: The name/id of the project.
        :type project: str
        
        :param description: The description of the project.
        :type description: str
        
        :returns: A copy of the project record
        :rtype: dict
        """
        return(self._postRequest(self._labbcatUrl("api/admin/projects"), {}, {
            "project" : project,
            "description" : description }))
    
    def readProjects(self, pageNumber=None, pageLength=None):
        """ Reads a list of project records.
        
        The dictionaries in the returned list have the following entries:
        
        - "project_id"  : The database key for the record.
        - "project"     : The name/id of the project.
        - "description" : The description of the project.
        - "_cantDelete" : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :param pageLength: The maximum number of records to return, or null to return all.
        :type pageLength: int or None
        
        :returns: A list of project records.
        :rtype: list of dict
        """
        # define request parameters
        parameters = {}
        if pageNumber != None:
            parameters["pageNumber"] = pageNumber
        if pageLength != None:
            parameters["pageLength"] = pageLength
        return(self._getRequest(self._labbcatUrl("api/admin/projects"), parameters))
        
    def updateProject(self, project, description):
        """ Updates an existing project record.
        
        The dictionary returned has the following entries:
        
        - "project_id"  : The database key for the record.
        - "project"     : The name/id of the project.
        - "description" : The description of the project.
        - "_cantDelete" : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.
        
        :param project: The name/id of the project.
        :type project: str
        
        :param description: The description of the project.
        :type description: str
        
        :returns: A copy of the project record
        :rtype: dict
        """
        return(self._putRequest(self._labbcatUrl("api/admin/projects"), {}, {
            "project" : project,
            "description" : description }))
    
    def deleteProject(self, project):
        """ Deletes an existing project record.
        
        :param project: The name/id of the project.
        :type project: str        
        """
        return(self._deleteRequest(self._labbcatUrl("api/admin/projects/"+project), {}))
    
    def createMediaTrack(self, suffix, description, display_order):
        """ Creates a new media track record.
        
        The dictionary returned has the following entries:
        
        - "suffix"        : The suffix associated with the media track.
        - "description"   : The description of the media track.
        - "display_order" : The position of the track amongst other tracks.
        - "_cantDelete"   : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted. 
        
        :param suffix: The suffix associated with the media track.
        :type suffix: str
        
        :param description: The description of the media track.
        :type description: str
        
        :param display_order: The position of the track amongst other tracks.
        :type display_order: str
        
        :returns: A copy of the media track record
        :rtype: dict
        """
        return(self._postRequest(self._labbcatUrl("api/admin/mediatracks"), {}, {
            "suffix" : suffix,
            "description" : description,
            "display_order" : display_order }))
    
    def readMediaTracks(self, pageNumber=None, pageLength=None):
        """ Reads a list of media track records.
        
        The dictionaries in the returned list have the following entries:
        
        - "suffix"        : The suffix associated with the media track.
        - "description"   : The description of the media track.
        - "display_order" : The position of the track amongst other tracks.
        - "_cantDelete"   : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :param pageLength: The maximum number of records to return, or null to return all.
        :type pageLength: int or None
        
        :returns: A list of media track records.
        :rtype: list of dict
        """
        # define request parameters
        parameters = {}
        if pageNumber != None:
            parameters["pageNumber"] = pageNumber
        if pageLength != None:
            parameters["pageLength"] = pageLength
        return(self._getRequest(self._labbcatUrl("api/admin/mediatracks"), parameters))
        
    def updateMediaTrack(self, suffix, description, display_order):
        """ Updates an existing media track record.
        
        The dictionary returned has the following entries:
        
        - "suffix"        : The suffix associated with the media track.
        - "description"   : The description of the media track.
        - "display_order" : The position of the track amongst other tracks.
        - "_cantDelete"   : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.   
        
        :param suffix: The suffix assocaited with the media track.
        :type suffix: str
        
        :param description: The description of the media track.
        :type description: str
        
        :param display_order: The position of the track amongst other tracks.
        :type display_order: str
        
        :returns: A copy of the media track record
        :rtype: dict
        """
        return(self._putRequest(self._labbcatUrl("api/admin/mediatracks"), {}, {
            "suffix" : suffix,
            "description" : description,
            "display_order" : display_order }))
    
    def deleteMediaTrack(self, suffix):
        """ Deletes an existing media track record.
        
        :param suffix: The suffix associated with the media track.
        :type suffix: str        
        """
        return(self._deleteRequest(self._labbcatUrl("api/admin/mediatracks/"+suffix), {}))
    
    def createRole(self, role_id, description):
        """ Creates a new role record.
        
        The dictionary returned has the following entries:
        
        - "role_id"     : The name/id of the role.
        - "description" : The description of the role.
        - "_cantDelete" : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.   
        
        :param role_id: The name/id of the role.
        :type role_id: str
        
        :param description: The description of the role.
        :type description: str
        
        :returns: A copy of the role record
        :rtype: dict
        """
        return(self._postRequest(self._labbcatUrl("api/admin/roles"), {}, {
            "role_id" : role_id,
            "description" : description }))
    
    def readRoles(self, pageNumber=None, pageLength=None):
        """ Reads a list of role records.
        
        The dictionaries in the returned list have the following entries:
        
        - "role_id"     : The name/id of the role.
        - "description" : The description of the role.
        - "_cantDelete" : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :param pageLength: The maximum number of records to return, or null to return all.
        :type pageLength: int or None
        
        :returns: A list of role records.
        :rtype: list of dict
        """
        # define request parameters
        parameters = {}
        if pageNumber != None:
            parameters["pageNumber"] = pageNumber
        if pageLength != None:
            parameters["pageLength"] = pageLength
        return(self._getRequest(self._labbcatUrl("api/admin/roles"), parameters))
        
    def updateRole(self, role_id, description):
        """ Updates an existing role record.
        
        The dictionary returned has the following entries:
        
        - "role_id"     : The name/id of the role.
        - "description" : The description of the role.
        - "_cantDelete" : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.
        
        :param role_id: The name/id of the role.
        :type role_id: str
        
        :param description: The description of the role.
        :type description: str
        
        :returns: A copy of the role record
        :rtype: dict
        """
        return(self._putRequest(self._labbcatUrl("api/admin/roles"), {}, {
            "role_id" : role_id,
            "description" : description }))
    
    def deleteRole(self, role_id):
        """ Deletes an existing role record.
        
        :param role_id: The name/id of the role.
        :type role_id: str        
        """
        return(self._deleteRequest(self._labbcatUrl("api/admin/roles/"+role_id), {}))
    
    def createRolePermission(self, role_id, entity, layer, value_pattern):
        """ Creates a new role permission record.
        
        The dictionary returned has the following entries:
        
        - "role_id"       : The ID of the role this permission applies to.
        - "entity"        : The media entity this permission applies to - a string
          made up of "t" (transcript), "a" (audio), "v" (video), or "i" (image). 
        - "layer"         : ID of the layer for which the label determines access. This is
          either a valid transcript attribute layer ID, or "corpus". 
        - "value_pattern" : Regular expression for matching against the layerId label. If
           the regular expression matches the label, access is allowed.  
        - "_cantDelete"   : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.   
        
        :param role_id: The ID of the role this permission applies to.
        :type role_id: str
        
        :param entity: The media entity this permission applies to.
        :type entity: str
        
        :param layer: ID of the layer for which the label determines access.
        :type layer: str
        
        :param value_pattern: Regular expression for matching against. 
        :type value_pattern: str
        
        :returns: A copy of the role permission record
        :rtype: dict
        """
        permission = self._postRequest(self._labbcatUrl("api/admin/roles/permissions"), {}, {
            "role_id" : role_id,
            "entity" : entity,
            "attribute_name" : layer.replace("transcript_",""),
            "value_pattern" : value_pattern })
        if permission["attribute_name"] == "corpus":
            permission["layer"] = permission["attribute_name"]
        else:
            permission["layer"] = "transcript_" + permission["attribute_name"]
        return(permission)
    
    def readRolePermissions(self, role_id, pageNumber=None, pageLength=None):
        """ Reads a list of role permission records.
        
        The dictionaries in the returned list have the following entries:
        
        - "role_id"       : The ID of the role this permission applies to.
        - "entity"        : The media entity this permission applies to - a string
          made up of "t" (transcript), "a" (audio), "v" (video), or "i" (image). 
        - "layer"         : ID of the layer for which the label determines access. This is
          either a valid transcript attribute layer ID, or "corpus". 
        - "value_pattern" : Regular expression for matching against the layerId label. If
           the regular expression matches the label, access is allowed.  
        - "_cantDelete"   : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.   
        
        :param role_id: The ID of the role this permission applies to.
        :type role_id: str
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :param pageLength: The maximum number of records to return, or null to return all.
        :type pageLength: int or None
        
        :returns: A list of role permission records.
        :rtype: list of dict
        """
        # define request parameters
        parameters = {}
        if pageNumber != None:
            parameters["pageNumber"] = pageNumber
        if pageLength != None:
            parameters["pageLength"] = pageLength
        permissions = self._getRequest(
            self._labbcatUrl("api/admin/roles/permissions/"+role_id), parameters)
        for permission in permissions:
            if permission["attribute_name"] == "corpus":
                permission["layer"] = permission["attribute_name"]
            else:
                permission["layer"] = "transcript_" + permission["attribute_name"]
        return permissions
        
    def updateRolePermission(self, role_id, entity, layer, value_pattern):
        """ Updates an existing role permission record.
        
        The dictionary returned has the following entries:
        
        - "role_id"       : The ID of the role this permission applies to.
        - "entity"        : The media entity this permission applies to - a string
          made up of "t" (transcript), "a" (audio), "v" (video), or "i" (image). 
        - "layer"         : ID of the layer for which the label determines access. This is
          either a valid transcript attribute layer ID, or "corpus". 
        - "value_pattern" : Regular expression for matching against the layerId label. If
           the regular expression matches the label, access is allowed.  
        - "_cantDelete"   : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.   
        
        :param role_id: The ID of the role this permission applies to.
        :type role_id: str
        
        :param entity: The media entity this permission applies to.
        :type entity: str
        
        :param layer: ID of the layer for which the label determines access.
        :type layer: str
        
        :param value_pattern: Regular expression for matching against. 
        :type value_pattern: str
        
        :returns: A copy of the role permission record
        :rtype: dict
        """
        permission = self._putRequest(self._labbcatUrl("api/admin/roles/permissions"), {}, {
            "role_id" : role_id,
            "entity" : entity,
            "attribute_name" : layer.replace("transcript_",""),
            "value_pattern" : value_pattern })
        if permission["attribute_name"] == "corpus":
            permission["layer"] = permission["attribute_name"]
        else:
            permission["layer"] = "transcript_" + permission["attribute_name"]
        return permission
    
    def deleteRolePermission(self, role_id, entity):
        """ Deletes an existing role permission record.
        
        :param role_id: The ID of the role this permission applies to.
        :type role_id: str
        
        :param entity: The media entity this permission applies to.
        :type entity: str        
        """
        return(self._deleteRequest(self._labbcatUrl("api/admin/roles/permissions/"+role_id+"/"+entity), {}))
    
    def readSystemAttributes(self):
        """ Reads a list of system attribute records.
        
        The dictionaries in the returned list have the following entries:
        
        - "attribute"   : ID of the attribute.
        - "type"        : The type of the attribute - "string", "boolean", "select", etc.
        - "style"       : UI style, which depends on "type".
        - "label"       : User-facing label for the attribute.
        - "description" : User-facing (long) description for the attribute.
        - "options"     : If 'type" == "select", this is a dict defining possible values.
        - "value"       : The value of the attribute.
        
        :returns: A list of system attribute records.
        :rtype: list of dict
        """
        # define request parameters
        return(self._getRequest(self._labbcatUrl("api/admin/systemattributes"), {}))
        
    def updateSystemAttribute(self, attribute, value):
        """ Updates the value of a existing system attribute record.
        
        The dictionary returned has the following entries:
        
        - "attribute"   : ID of the attribute.
        - "type"        : The type of the attribute - "string", "boolean", "select", etc.
        - "style"       : UI style, which depends on "type".
        - "label"       : User-facing label for the attribute.
        - "description" : User-facing (long) description for the attribute.
        - "options"     : If 'type" == "select", this is a dict defining possible values.
        - "value"       : The value of the attribute.
        
        :param attribut: ID of the attribute.
        :type systemAttribute: str
        
        :param value: The new value for the attribute.
        :type value: str
        
        :returns: A copy of the systemAttribute record
        :rtype: dict
        """
        return(self._putRequest(self._labbcatUrl("api/admin/systemattributes"), {}, {
            "attribute" : attribute,
            "value" : value }))
    
    def createUser(self, user, email, resetPassword, roles):
        """ Creates a new user record.
        
        The dictionary returned has the following entries:
        
        - "user"          : The id of the user.
        - "email"         : The email address of the user.
        - "resetPassword" : Whether the user must reset their password when they next log in. 
        - "roles"         : Roles or groups the user belongs to.
        - "_cantDelete" : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.   
        
        :param user: The ID of the user.
        :type user: str
        
        :param email: The email address of the user.
        :type email: str
        
        :param resetPassword: Whether the user must reset their password when they next log in. 
        :type resetPassword: boolean
        
        :param roles: Roles or groups the user belongs to.
        :type roles: list of str
        
        :returns: A copy of the user record
        :rtype: dict
        """
        if resetPassword:
            resetPassword = 1
        else:
            resetPassword = 0
        return(self._postRequest(self._labbcatUrl("api/admin/users"), {}, {
            "user" : user,
            "email" : email,
            "resetPassword" : resetPassword,
            "roles" : roles }))
    
    def readUsers(self, pageNumber=None, pageLength=None):
        """ Reads a list of user records.
        
        The dictionaries in the returned list have the following entries:
        
        - "user"          : The id of the user.
        - "email"         : The email address of the user.
        - "resetPassword" : Whether the user must reset their password when they next log in. 
        - "roles"         : Roles or groups the user belongs to.
        - "_cantDelete" : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.   
        
        :param pageNumber: The zero-based page number to return, or null to return the first page.
        :type pageNumber: int or None

        :param pageLength: The maximum number of records to return, or null to return all.
        :type pageLength: int or None
        
        :returns: A list of user records.
        :rtype: list of dict
        """
        # define request parameters
        parameters = {}
        if pageNumber != None:
            parameters["pageNumber"] = pageNumber
        if pageLength != None:
            parameters["pageLength"] = pageLength
        return(self._getRequest(self._labbcatUrl("api/admin/users"), parameters))
        
    def updateUser(self, user, email, resetPassword, roles):
        """ Updates an existing user record.
        
        The dictionary returned has the following entries:
        
        - "user"          : The id of the user.
        - "email"         : The email address of the user.
        - "resetPassword" : Whether the user must reset their password when they next log in. 
        - "roles"         : Roles or groups the user belongs to.
        - "_cantDelete" : This is not a database field, but rather is present in records
          returned from the server that can not currently be deleted; a string
          representing the reason the record can't be deleted.   
        
        :param user: The ID of the user.
        :type user: str
        
        :param email: The email address of the user.
        :type email: str
        
        :param resetPassword: Whether the user must reset their password when they next log in. 
        :type resetPassword: boolean
        
        :param roles: Roles or groups the user belongs to.
        :type roles: list of str
        
        :returns: A copy of the user record
        :rtype: dict
        """
        if resetPassword:
            resetPassword = 1
        else:
            resetPassword = 0
        return(self._putRequest(self._labbcatUrl("api/admin/users"), {}, {
            "user" : user,
            "email" : email,
            "resetPassword" : resetPassword,
            "roles" : roles }))
    
    def deleteUser(self, user):
        """ Deletes an existing user record.
        
        :param user: The ID of the user.
        :type user: str        
        """
        return(self._deleteRequest(self._labbcatUrl("api/admin/users/"+user), {}))
    
    def setPassword(self, user, password, resetPassword):
        """ Sets a given user's password.
                
        :param user: The ID of the user.
        :type user: str
        
        :param password: The new password.
        :type email: str
        
        :param resetPassword: Whether the user must reset their password when they next log in. 
        :type resetPassword: boolean
        """
        return(self._putRequest(self._labbcatUrl("api/admin/password"), {}, {
            "user" : user,
            "password" : password,
            "resetPassword" : resetPassword }))
    
    def generateLayer(self, layerId):
        """ Generates a layer.

        This function generates annotations on a given layer for all transcripts in the corpus.
        
        :param layerId: The ID of the layer to generate.
        :type layerId: str
        
        :returns: The taskId of the resulting annotation layer generation task. The
                  task status can be updated using
                  `taskStatus() <#labbcat.LabbcatView.taskStatus>`_.
        :rtype: str
        """
        params = {
            "layerId" : layerId,
            "sure" : "true" }
        model = self._postRequest(self._labbcatUrl("admin/layers/regenerate"), params)
        return(model["threadId"])
    
# TODO loadLexicon
# TODO deleteLexicon
