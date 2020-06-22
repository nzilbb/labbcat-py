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

            
if __name__ == '__main__':
    unittest.main()
