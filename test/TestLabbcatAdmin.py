import unittest
import labbcat

# YOU MUST ENSURE THE FOLLOWING SETTINGS ARE VALID FOR YOU TEST LABB-CAT SERVER:
labbcatUrl = "http://localhost:8080/labbcat/"
username = "labbcat"
password = "labbcat"

class TestLabbcatAdmin(unittest.TestCase):
    """ Unit tests for LabbcatAdmin.

    These tests test the functionality of the client library, not the server. 

    They assume the existence of a valid LaBB-CAT instance (configured by *labbcatUrl*)
    which responds correctly to requests, but do not generally test that the server behaves
    correctly , nor assume specific corpus content. For the tests to work, the first graph
    listed in LaBB-CAT must have some words and some media, and the first participant listed
    must have some transcripts.  
    """

    def setUp(self):
        self.store = labbcat.LabbcatAdmin(labbcatUrl, username, password)
        
    def test_deleteNonexistentTranscript(self):
        with self.assertRaises(labbcat.ResponseException):
            self.store.deleteTranscript("nonexistent transcript ID")    
    
    def test_localization(self):
        
        # delete a corpus that doesn't exist, in English
        try:
            self.store.language = "en"
            self.store.deleteCorpus("this-corpus-doesn't-exist")
        except labbcat.ResponseException as x:
            message = x.response.errors[0]
            self.assertTrue(message.find("not found") >= 0, "Message is in English: " + message)
            pass
        
        # delete a corpus that doesn't exist, in Spanish
        try:
            self.store.language = "es"
            self.store.deleteCorpus("this-corpus-doesn't-exist")
        except labbcat.ResponseException as x:
            message = x.response.errors[0]
            self.assertTrue(message.find("no existe") >= 0, "Message is in Spanish: " + message)
            pass
    
    def test_corpora_CRUD(self):
        
        corpus_name = "unit-test"
        corpus_language = "en"
        corpus_description = "Temporary corpus for unit testing"

        # ensure the corpus doesn't exist to start with
        try:
            self.store.deleteCorpus(corpus_name)
        except labbcat.ResponseException as x:
            pass
                    
        # create corpus
        corpus = self.store.createCorpus(corpus_name, corpus_language, corpus_description)
        self.assertEqual(corpus["corpus_name"], corpus_name,
                         "corpus_name saved")
        self.assertEqual(corpus["corpus_language"], corpus_language,
                         "corpus_language saved")
        self.assertEqual(corpus["corpus_description"], corpus_description,
                         "corpus_description saved")
        
        # read corpora
        corpora = self.store.readCorpora()
        foundNewCorpus = False
        for c in corpora:
            if c["corpus_name"] == corpus_name:
                foundNewCorpus = True
        self.assertTrue(foundNewCorpus, "New corpus is present in list")
        
        # can't create an existing record
        try:
            self.store.createCorpus(corpus_name, corpus_language, corpus_description)
            fail("Delete non-existent corpus")
        except:
            pass
        
        # update corpus
        new_corpus_language = "es";
        new_corpus_description = "Temporary Spanish corpus for unit testing";
        updatedCorpus = self.store.updateCorpus(
            corpus_name, new_corpus_language, new_corpus_description)
        self.assertEqual(updatedCorpus["corpus_name"], corpus_name,
                         "corpus_name unchanged");
        self.assertEqual(updatedCorpus["corpus_language"], new_corpus_language,
                         "corpus_language changed");
        self.assertEqual(updatedCorpus["corpus_description"], new_corpus_description,
                         "corpus_description changed");
                
        # delete it
        self.store.deleteCorpus(corpus_name)
        
        # make sure it was deleted
        corpora = self.store.readCorpora()
        foundNewCorpus = False
        for c in corpora:
            if c["corpus_name"] == corpus_name:
                foundNewCorpus = True
        self.assertFalse(foundNewCorpus, "New corpus is gone from list")

        # can't delete a nonexistent record
        try:
            self.store.deleteCorpus(corpus_name)            
            fail("Delete non-existent corpus")
        except:
            pass

    def test_projects_CRUD(self):
        
        project_name = "unit-test"
        project_description = "Temporary project for unit testing"

        # ensure the project doesn't exist to start with
        try:
            self.store.deleteProject(project_name)
        except labbcat.ResponseException as x:
            pass
                    
        # create project
        project = self.store.createProject(project_name, project_description)
        self.assertEqual(project["project"], project_name,
                         "project name saved")
        self.assertEqual(project["description"], project_description,
                         "project description saved")
        
        # read projects
        projects = self.store.readProjects()
        foundNewProject = False
        for c in projects:
            if c["project"] == project_name:
                foundNewProject = True
        self.assertTrue(foundNewProject, "New project is present in list")
        
        # can't create an existing record
        try:
            self.store.createProject(project_name, project_description)
            fail("Delete non-existent project")
        except:
            pass
        
        # update project
        new_project_description = "Changed description";
        updatedProject = self.store.updateProject(
            project_name, new_project_description)
        self.assertEqual(updatedProject["project"], project_name,
                         "project name unchanged");
        self.assertEqual(updatedProject["description"], new_project_description,
                         "project description changed");
                
        # delete it
        self.store.deleteProject(project_name)
        
        # make sure it was deleted
        projects = self.store.readProjects()
        foundNewProject = False
        for c in projects:
            if c["project"] == project_name:
                foundNewProject = True
        self.assertFalse(foundNewProject, "New project is gone from list")

        # can't delete a nonexistent record
        try:
            self.store.deleteProject(project_name)            
            fail("Delete non-existent project")
        except:
            pass

    def test_mediaTracks_CRUD(self):
        
        suffix = "unit-test"
        description = "Temporary mediaTrack for unit testing"
        display_order = 99

        # ensure the mediaTrack doesn't exist to start with
        try:
            self.store.deleteMediaTrack(suffix)
        except labbcat.ResponseException as x:
            pass
                    
        # create mediaTrack
        mediaTrack = self.store.createMediaTrack(suffix, description, display_order)
        self.assertEqual(mediaTrack["suffix"], suffix,
                         "mediaTrack suffix saved")
        self.assertEqual(mediaTrack["description"], description,
                         "mediaTrack description saved")
        self.assertEqual(mediaTrack["display_order"], display_order,
                         "mediaTrack display_order saved")
        
        # read mediaTracks
        mediaTracks = self.store.readMediaTracks()
        foundNewMediaTrack = False
        for c in mediaTracks:
            if c["suffix"] == suffix:
                foundNewMediaTrack = True
        self.assertTrue(foundNewMediaTrack, "New mediaTrack is present in list")
        
        # can't create an existing record
        try:
            self.store.createMediaTrack(suffix, description, display_order)
            fail("Delete non-existent mediaTrack")
        except:
            pass
        
        # update mediaTrack
        new_language = "es";
        new_description = "Changed description";
        new_display_order = 100
        updatedMediaTrack = self.store.updateMediaTrack(
            suffix, new_description, new_display_order)
        self.assertEqual(updatedMediaTrack["suffix"], suffix,
                         "mediaTrack suffix unchanged");
        self.assertEqual(updatedMediaTrack["description"], new_description,
                         "mediaTrack description changed");
        self.assertEqual(updatedMediaTrack["display_order"], new_display_order,
                         "mediaTrack display_order changed");
                
        # delete it
        self.store.deleteMediaTrack(suffix)
        
        # make sure it was deleted
        mediaTracks = self.store.readMediaTracks()
        foundNewMediaTrack = False
        for c in mediaTracks:
            if c["suffix"] == suffix:
                foundNewMediaTrack = True
        self.assertFalse(foundNewMediaTrack, "New mediaTrack is gone from list")

        # can't delete a nonexistent record
        try:
            self.store.deleteMediaTrack(suffix)
            fail("Delete non-existent mediaTrack")
        except:
            pass

    def test_roles_CRUD(self):
        
        role_id = "unit-test"
        role_description = "Temporary role for unit testing"

        # ensure the role doesn't exist to start with
        try:
            self.store.deleteRole(role_id)
        except labbcat.ResponseException as x:
            pass
                    
        # create role
        role = self.store.createRole(role_id, role_description)
        self.assertEqual(role["role_id"], role_id,
                         "role name saved")
        self.assertEqual(role["description"], role_description,
                         "role description saved")
        
        # read roles
        roles = self.store.readRoles()
        foundNewRole = False
        for c in roles:
            if c["role_id"] == role_id:
                foundNewRole = True
        self.assertTrue(foundNewRole, "New role is present in list")
        
        # can't create an existing record
        try:
            self.store.createRole(role_id, role_description)
            fail("Delete non-existent role")
        except:
            pass
        
        # update role
        new_role_description = "Changed description";
        updatedRole = self.store.updateRole(
            role_id, new_role_description)
        self.assertEqual(updatedRole["role_id"], role_id,
                         "role name unchanged");
        self.assertEqual(updatedRole["description"], new_role_description,
                         "role description changed");
                
        # delete it
        self.store.deleteRole(role_id)
        
        # make sure it was deleted
        roles = self.store.readRoles()
        foundNewRole = False
        for c in roles:
            if c["role_id"] == role_id:
                foundNewRole = True
        self.assertFalse(foundNewRole, "New role is gone from list")

        # can't delete a nonexistent record
        try:
            self.store.deleteRole(role_id)            
            fail("Delete non-existent role")
        except:
            pass

    def test_rolePermissions_CRUD(self):
        
        role_id = "admin"
        entity = "t"
        layer = "corpus"
        value_pattern = "unit-test.*"

        # ensure the rolePermission doesn't exist to start with
        try:
            self.store.deleteRolePermission(role_id, entity)
        except labbcat.ResponseException as x:
            pass
                    
        # create rolePermission
        rolePermission = self.store.createRolePermission(role_id, entity, layer, value_pattern)
        self.assertEqual(rolePermission["role_id"], role_id,
                         "role_id saved")
        self.assertEqual(rolePermission["entity"], entity,
                         "entity saved")
        self.assertEqual(rolePermission["layer"], layer,
                         "layer saved")
        self.assertEqual(rolePermission["value_pattern"], value_pattern,
                         "value_pattern saved")
        
        # read rolePermissions
        rolePermissions = self.store.readRolePermissions(role_id)
        foundNewRolePermission = False
        for c in rolePermissions:
            self.assertEqual(c["role_id"], role_id, "only select role returned")
            if c["role_id"] == role_id and c["entity"] == entity:
                foundNewRolePermission = True
        self.assertTrue(foundNewRolePermission, "New rolePermission is present in list")
        
        # can't create an existing record
        try:
            self.store.createRolePermission(role_id, entity, layer, value_pattern)
            fail("Delete non-existent rolePermission")
        except:
            pass
        
        # update rolePermission
        new_layer = "transcript_language";
        new_value_pattern = "en.*";
        updatedRolePermission = self.store.updateRolePermission(
            role_id, entity, new_layer, new_value_pattern)
        self.assertEqual(updatedRolePermission["role_id"], role_id,
                         "role_id name unchanged")
        self.assertEqual(updatedRolePermission["entity"], entity,
                         "entity name unchange")
        self.assertEqual(updatedRolePermission["layer"], new_layer,
                         "layer name updated")
        self.assertEqual(updatedRolePermission["value_pattern"], new_value_pattern,
                         "value_pattern updated")
        
                
        # delete it
        self.store.deleteRolePermission(role_id, entity)
        
        # make sure it was deleted
        rolePermissions = self.store.readRolePermissions(role_id)
        foundNewRolePermission = False
        for c in rolePermissions:
            if c["rolePermission_id"] == rolePermission_id and c["entity"] == entity:
                foundNewRolePermission = True
        self.assertFalse(foundNewRolePermission, "New rolePermission is gone from list")

        # can't delete a nonexistent record
        try:
            self.store.deleteRolePermission(role_id, entity)
            fail("Delete non-existent rolePermission")
        except:
            pass

    def test_systemAttributes_RU(self):
        
        # read systemAttributes
        systemAttributes = self.store.readSystemAttributes()
        titleAttribute = None
        for a in systemAttributes:
            if a["attribute"] == "title":
                titleAttribute = a
        self.assertIsNotNone(titleAttribute, "title attribute is present in list")
        
        # update systemAttribute
        newValue = "unit-test";
        updatedSystemAttribute = self.store.updateSystemAttribute("title", newValue)
        self.assertEqual(updatedSystemAttribute["attribute"], "title", "attribute unchanged");
        self.assertEqual(updatedSystemAttribute["value"], newValue, "value changed");

        # restore original value
        self.store.updateSystemAttribute("title", titleAttribute["value"])

        # can't update a nonexistent record
        try:
            self.store.updateSystemAttribute("nonexistent", "unit-test")
            fail("Update non-existent system attribute")
        except:
            pass

    def test_saveLayer(self):
        
        # read systemAttributes
        originalTranscriptType = self.store.getLayer("transcript_type")
        
        editedTranscriptType1 = originalTranscriptType.copy()
        newOption1 = "unit-test-1"
        editedTranscriptType1["validLabels"] = editedTranscriptType1["validLabels"].copy()
        editedTranscriptType1["validLabels"][newOption1] = newOption1
            
        editedTranscriptType2 = originalTranscriptType.copy()
        newOption2 = "unit-test-2"
        editedTranscriptType2["validLabels"] = editedTranscriptType2["validLabels"].copy()
        editedTranscriptType2["validLabels"][newOption2] = newOption2

        # save first variant
        savedTranscriptType1 = self.store.saveLayer(
            editedTranscriptType1["id"], 
            editedTranscriptType1["parentId"], editedTranscriptType1["description"],
            editedTranscriptType1["alignment"], editedTranscriptType1["peers"],
            editedTranscriptType1["peersOverlap"], editedTranscriptType1["parentIncludes"],
            editedTranscriptType1["saturated"], editedTranscriptType1["type"],
            editedTranscriptType1["validLabels"], None)
        self.assertTrue(newOption1 in savedTranscriptType1["validLabels"], "newOption1 set");
        self.assertFalse(newOption2 in savedTranscriptType1["validLabels"], "newOption2 not set");

        # save second variant
        savedTranscriptType2 = self.store.saveLayer(
            editedTranscriptType2["id"], 
            editedTranscriptType2["parentId"], editedTranscriptType2["description"],
            editedTranscriptType2["alignment"], editedTranscriptType2["peers"],
            editedTranscriptType2["peersOverlap"], editedTranscriptType2["parentIncludes"],
            editedTranscriptType2["saturated"], editedTranscriptType2["type"],
            editedTranscriptType2["validLabels"], None)
        self.assertFalse(newOption1 in savedTranscriptType2["validLabels"], "newOption1 not set");
        self.assertTrue(newOption2 in savedTranscriptType2["validLabels"], "newOption2 set");

        # restore original value
        self.store.saveLayer(
            originalTranscriptType["id"], 
            originalTranscriptType["parentId"], originalTranscriptType["description"],
            originalTranscriptType["alignment"], originalTranscriptType["peers"],
            originalTranscriptType["peersOverlap"], originalTranscriptType["parentIncludes"],
            originalTranscriptType["saturated"], originalTranscriptType["type"],
            originalTranscriptType["validLabels"], None)

    def test_users_CRUDPassword(self):
        
        role_id = "unit-test"
        role_description = "Temporary role for unit testing"
        
        role = self.store.createRole(role_id, role_description)
        self.assertEqual(role["role_id"], role_id,
                         "role name saved")
        self.assertEqual(role["description"], role_description,
                         "role description saved")
        user_id = "unit-test"
        email = "unit-test@tld.org"
        resetPassword = True
        roles = [ role_id ]

        # ensure the user doesn't exist to start with
        try:
            self.store.deleteUser(user_id)
        except labbcat.ResponseException as x:
            pass
                    
        # create user
        user = self.store.createUser(user_id, email, resetPassword, roles)
        self.assertEqual(user["user"], user_id,
                         "user name saved")
        self.assertEqual(user["email"], email,
                         "user email saved")
        self.assertEqual(user["resetPassword"], resetPassword,
                         "user resetPassword saved")
        self.assertEqual(user["roles"], roles,
                         "user roles saved")
        
        # read users
        users = self.store.readUsers()
        foundNewUser = False
        for c in users:
            if c["user"] == user_id:
                foundNewUser = True
        self.assertTrue(foundNewUser, "New user is present in list")
        
        # can't create an existing record
        try:
            self.store.createUser(user_id, email, resetPassword, roles)
            fail("Delete non-existent user")
        except:
            pass
        
        # set password
        self.store.setPassword(user_id, "rglLkLt5PstyQWQFXXEG", True)
        
        # update user
        new_email = "new@tld.org";
        new_resetPassword = False
        new_roles = [ "view" ]
        updatedUser = self.store.updateUser(
            user_id, new_email, new_resetPassword, new_roles)
        self.assertEqual(updatedUser["user"], user_id,
                         "user name unchanged");
        self.assertEqual(updatedUser["email"], new_email,
                         "user email updated")
        self.assertEqual(updatedUser["resetPassword"], new_resetPassword,
                         "user resetPassword updated")
        self.assertEqual(updatedUser["roles"], new_roles,
                         "user roles updated")
                
        # delete it
        self.store.deleteUser(user_id)
        
        # make sure it was deleted
        users = self.store.readUsers()
        foundNewUser = False
        for c in users:
            if c["user"] == user_id:
                foundNewUser = True
        self.assertFalse(foundNewUser, "New user is gone from list")

        # can't delete a nonexistent record
        try:
            self.store.deleteUser(user_id)            
            fail("Delete non-existent user")
        except:
            pass

            
if __name__ == '__main__':
    unittest.main()
