import unittest
import labbcat

# YOU MUST ENSURE THE FOLLOWING SETTINGS ARE VALID FOR YOU TEST LABB-CAT SERVER:
labbcatUrl = "http://localhost:8080/labbcat/"
username = "labbcat"
password = "labbcat"

class TestGraphStore(unittest.TestCase):
    """ Unit tests for GraphStore.

    These tests test the functionality of the client library, not the server. 

    They assume the existence of a valid LaBB-CAT instance (configured by *labbcatUrl*)
    which responds correctly to requests, but do not generally test that the server behaves
    correctly , nor assume specific corpus content. For the tests to work, the first graph
    listed in LaBB-CAT must have some words and some media, and the first participant listed
    must have some transcripts.  
    """

    def setUp(self):
        self.store = labbcat.GraphStore(labbcatUrl, username, password)
        
    # TODO def test_deleteNonexistentTranscript(self):
    #     with self.assertRaises(LabbcatException):
    #         self.store.deleteTranscript("nonexistent transcript ID")    
          
if __name__ == '__main__':
    unittest.main()
