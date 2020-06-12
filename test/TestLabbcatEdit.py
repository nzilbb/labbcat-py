import unittest
import labbcat

# YOU MUST ENSURE THE FOLLOWING SETTINGS ARE VALID FOR YOU TEST LABB-CAT SERVER:
labbcatUrl = "http://localhost:8080/labbcat/"
username = "labbcat"
password = "labbcat"

class TestLabbcatEdit(unittest.TestCase):
    """ Unit tests for GraphStore.

    These tests test the functionality of the client library, not the server. 

    They assume the existence of a valid LaBB-CAT instance (configured by *labbcatUrl*)
    which responds correctly to requests, but do not generally test that the server behaves
    correctly , nor assume specific corpus content. For the tests to work, the first graph
    listed in LaBB-CAT must have some words and some media, and the first participant listed
    must have some transcripts.  
    """

    def setUp(self):
        self.store = labbcat.LabbcatEdit(labbcatUrl, username, password)
        
    def test_deleteNonexistentTranscript(self):
        with self.assertRaises(labbcat.ResponseException):
            self.store.deleteTranscript("nonexistent transcript ID")    
    
    def test_newTranscript_updateTranscript_deleteTranscript(self):
        transcriptName = "labbcat-py.test.txt"
        transcriptPath = "/home/robert/nzilbb/labbcat-py/test/" + transcriptName

        # ensure the transcript doesn't exist to start with
        try:
            self.store.deleteTranscript(transcriptName)
        except labbcat.ResponseException as x:
            pass
            
        # get valid attribute values
        corpusId = self.store.getCorpusIds()[0]
        typeLayer = self.store.getLayer("transcript_type")
        transcriptType = next(iter(typeLayer["validLabels"]))
        
        # upload transcript (with no media)
        threadId = self.store.newTranscript(
            transcriptPath, None, None, transcriptType, corpusId, "test")
        
        # wait for task generation to finish
        self.store.waitForTask(threadId)
        self.store.releaseTask(threadId)
        
        # ensure the transcript is there
        count = self.store.countMatchingTranscriptIds("id = '"+transcriptName+"'")
        self.assertEqual(1, count, "Transcript is in the store")
        
        # re-upload transcript (with no media)
        threadId = self.store.updateTranscript(transcriptPath)
        
        # wait for task generation to finish
        self.store.waitForTask(threadId)
        self.store.releaseTask(threadId)
        
        # ensure the transcript is there
        count = self.store.countMatchingTranscriptIds("id = '"+transcriptName+"'")
        self.assertEqual(1, count, "Transcript is in the store")
        
        # delete it
        self.store.deleteTranscript(transcriptName)
        
        # make sure it was deleted
        count = self.store.countMatchingTranscriptIds("id = '"+transcriptName+"'")
        self.assertEqual(0, count, "Transcript is gone")
            
if __name__ == '__main__':
    unittest.main()
