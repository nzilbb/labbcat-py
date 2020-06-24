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

            
if __name__ == '__main__':
    unittest.main()
