import unittest
import os
import labbcat

# YOU MUST ENSURE THE FOLLOWING SETTINGS ARE VALID FOR YOU TEST LABB-CAT SERVER:
labbcatUrl = "http://localhost:8080/labbcat/"
username = "labbcat"
password = "labbcat"

class TestLabbcat(unittest.TestCase):
    """ Unit tests for Labbcat.

    These tests test the functionality of the client library, not the server. 

    They assume the existence of a valid LaBB-CAT instance (configured by *labbcatUrl*)
    which responds correctly to requests, but do not generally test that the server behaves
    correctly , nor assume specific corpus content. For the tests to work, the first graph
    listed in LaBB-CAT must have some words and some media, and the first participant listed
    must have some transcripts.  
    """

    def setUp(self):
        self.store = labbcat.Labbcat(labbcatUrl, username, password)
        
    def test_getTasks(self):
        tasks = self.store.getTasks()
        # there may be none
        if len(tasks) == 0:
            print("\nThere are no tasks, can't test for well-formed response.")
        else:
            for taskId in tasks:
                task = tasks[taskId]
                for key in ["threadId", "threadName", "running", "percentComplete", "status"]:
                    with self.subTest(key=key):
                        self.assertIn(key, task, "Has " + key)
            
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
            
    def test_getTrascriptAttributes(self):
        ids = self.store.getTranscriptIds()
        self.assertTrue(len(ids) > 0, "At least 3 transcripts in the corpus")
        ids = ids[:3]
        layerIds = ["transcript_type", "corpus"]
        fileName = self.store.getTranscriptAttributes(ids, layerIds)
        self.assertTrue(fileName.endswith(".csv"), "CSV file returned")
        self.assertTrue(os.path.isfile(fileName), "CSV file exists")
        os.remove(fileName)
            
    def test_getParticipantAttributes(self):
        ids = self.store.getParticipantIds()
        self.assertTrue(len(ids) > 0, "At least 3 participants in the corpus")
        ids = ids[:3]
        layerIds = ["participant_gender", "participant_notes"]
        fileName = self.store.getParticipantAttributes(ids, layerIds)
        self.assertTrue(fileName.endswith(".csv"), "CSV file returned: " + fileName)
        self.assertTrue(os.path.isfile(fileName), "CSV file exists: " + fileName)
        os.remove(fileName)
            
if __name__ == '__main__':
    unittest.main()
