import unittest
import os
import labbcat

# YOU MUST ENSURE THE FOLLOWING SETTINGS ARE VALID FOR YOU TEST LABB-CAT SERVER:
labbcatUrl = "http://localhost:8080/labbcat/"
username = "labbcat"
password = "labbcat"

class TestLabbcatEdit(unittest.TestCase):
    """ Unit tests for TextLabbcatEdit.

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
    
    def test_participantCRUD(self):
        originalId = "TestLabbcatEdit-participant";
        changedId = "TestLabbcatEdit-participant-changed";
        
        # create participant
        self.assertTrue(
            self.store.saveParticipant(originalId, originalId, {"participant_gender":"X"}),
            "Participant created")
        
        # check it's really there
        participant = self.store.getParticipant(originalId)
        self.assertIsNotNone(participant, "New participant exists")
        self.assertEqual(originalId, participant["label"], "Correct participant") # not getId()

        # update it
        self.assertTrue(
            self.store.saveParticipant(originalId, changedId, {"participant_gender":"Y"}),
            "Participant updated")
        
        # check it's been updated
        participant = self.store.getParticipant(changedId)
        self.assertIsNotNone(participant, "Changed participant exists under new ID")
        self.assertEqual(changedId, participant["label"], "Correct participant") # not getId()

        # delete it
        self.store.deleteParticipant(changedId)

        # check it's been deleted
        participant = self.store.getParticipant(changedId)
        self.assertIsNone(participant, "Deleted participant isn't there")

    
    def test_uploadTranscriptAPI(self):
        transcriptName = "labbcat-py.test.txt"
        transcriptPath = "/home/robert/nzilbb/labbcat-py/test/" + transcriptName
        mediaPath = "/home/robert/nzilbb/labbcat-py/test/labbcat-py.test.wav"
        documentPath = "/home/robert/nzilbb/labbcat-py/test/labbcat-py.test.doc"
        participantName = "UnitTester"

        # ensure the transcript/participant don't exist to start with
        try:
            self.store.deleteTranscript(transcriptName)
        except labbcat.ResponseException as x:
            pass
        try:
            self.store.deleteParticipant(participantName)
        except labbcat.ResponseException as x:
            pass
            
        # get valid attribute values
        corpusId = self.store.getCorpusIds()[0]
        typeLayer = self.store.getLayer("transcript_type")
        transcriptType = next(iter(typeLayer["validLabels"]))
        
        # upload transcript (with no media)
        result = self.store.transcriptUpload(transcriptPath, None, False)
        self.assertIn("id", result, "Has id")
        id = result["id"]
        self.assertIn("parameters", result, "Has parameters")
        parameters = result["parameters"]

        # delete upload
        self.store.transcriptUploadDelete(id)
        
        # upload transcript (with media)
        result = self.store.transcriptUpload(transcriptPath, mediaPath, False)
        self.assertIn("id", result, "transcriptUpload has id")
        id = result["id"]
        self.assertIn("parameters", result, "transcriptUpload has parameters")
        parameters = result["parameters"]
 
        # set the parameters
        parameterValues = {}
        for parameter in parameters:
            if parameter["name"] == "labbcat_corpus":
                parameterValues[parameter["name"]] = corpusId
            elif parameter["name"] == "labbcat_episode":
                parameterValues[parameter["name"]] = "unit-test"
            elif parameter["name"] == "labbcat_transcript_type":
                parameterValues[parameter["name"]] = transcriptType
            else:
                parameterValues[parameter["name"]] = parameter["value"]
        # finish the upload
        result = self.store.transcriptUploadParameters(id, parameterValues)
        self.assertIn("transcripts", result, "transcriptUploadParameters has transcripts")
        transcripts = result["transcripts"]
        self.assertIn(transcriptName, transcripts, "transcripts includes " + transcriptName)
        threadId = transcripts[transcriptName]
        
        # wait for task generation to finish
        self.store.waitForTask(threadId)
        self.store.releaseTask(threadId)
        
        # ensure the transcript/participant are there
        count = self.store.countMatchingTranscriptIds("id = '"+transcriptName+"'")
        self.assertEqual(1, count, "Transcript is in the store")
        count = self.store.countMatchingParticipantIds("id = '"+participantName+"'")
        self.assertEqual(1, count, "Participant '"+participantName+"' is in the store")
        
        # ensure there is media
        files = self.store.getAvailableMedia(transcriptName)
        self.assertTrue(1 <= len(files), "Media is present")
        
        # delete transcript/participant
        self.store.deleteTranscript(transcriptName)
        self.store.deleteParticipant(participantName)
        
        # make sure they were deleted
        count = self.store.countMatchingTranscriptIds("id = '"+transcriptName+"'")
        self.assertEqual(0, count, "Transcript is gone")
        count = self.store.countMatchingParticipantIds("id = '"+participantName+"'")
        self.assertEqual(0, count, "Participant is in the store")

    def test_transcriptParticipantAndMediaCRUD(self):
        transcriptName = "labbcat-py.test.txt"
        transcriptPath = "/home/robert/nzilbb/labbcat-py/test/" + transcriptName
        mediaPath = "/home/robert/nzilbb/labbcat-py/test/labbcat-py.test.wav"
        documentPath = "/home/robert/nzilbb/labbcat-py/test/labbcat-py.test.doc"
        participantName = "UnitTester"

        # ensure the transcript/participant don't exist to start with
        try:
            self.store.deleteTranscript(transcriptName)
        except labbcat.ResponseException as x:
            pass
        try:
            self.store.deleteParticipant(participantName)
        except labbcat.ResponseException as x:
            pass
            
        # get valid attribute values
        corpusId = self.store.getCorpusIds()[0]
        typeLayer = self.store.getLayer("transcript_type")
        transcriptType = next(iter(typeLayer["validLabels"]))
        
        # upload transcript (with no media)
        result = self.store.newTranscript(
            transcriptPath, None, None, transcriptType, corpusId, "test")
        threadId = result[transcriptName]
        
        # wait for task generation to finish
        self.store.waitForTask(threadId)
        self.store.releaseTask(threadId)
        
        # ensure the transcript/participant are there
        count = self.store.countMatchingTranscriptIds("id = '"+transcriptName+"'")
        self.assertEqual(1, count, "Transcript is in the store")
        count = self.store.countMatchingParticipantIds("id = '"+participantName+"'")
        self.assertEqual(1, count, "Participant '"+participantName+"' is in the store")
        
        # re-upload transcript (with no media)
        result = self.store.updateTranscript(transcriptPath)
        threadId = result[transcriptName]
        
        # wait for task generation to finish
        self.store.waitForTask(threadId)
        self.store.releaseTask(threadId)
        
        # ensure the transcript is there
        count = self.store.countMatchingTranscriptIds("id = '"+transcriptName+"'")
        self.assertEqual(1, count, "Transcript is in the store")

        # ensure there is no media
        files = self.store.getAvailableMedia(transcriptName)
        self.assertEqual(0, len(files), "No media is present")
        # upload media
        mediaFile = self.store.saveMedia(transcriptName, mediaPath, None)
        ##print(mediaFile)
        self.assertIsNotNone(mediaFile, "mediaFile returned")
        self.assertIsNotNone(mediaFile["name"], "media file name returned")
        # ensure there is now media
        files = self.store.getAvailableMedia(transcriptName)
        self.assertTrue(1 <= len(files), "Now media is present")
        # delete media
        self.store.deleteMedia(transcriptName, mediaFile["name"])
        # ensure the media is now gone
        files = self.store.getAvailableMedia(transcriptName)
        self.assertEqual(0, len(files), "Media was deleted")
        
        # ensure there is no document
        files = self.store.getEpisodeDocuments(transcriptName)
        self.assertEqual(0, len(files), "No media is present")
        # upload document
        docFile = self.store.saveEpisodeDocument(transcriptName, documentPath)
        ##print(docFile)
        self.assertIsNotNone(docFile, "docFile returned")
        self.assertIsNotNone(docFile["name"], "document file name returned")
        # ensure there is now a document
        files = self.store.getEpisodeDocuments(transcriptName)
        self.assertTrue(1 <= len(files), "Now document is present")
        # delete media
        self.store.deleteMedia(transcriptName, docFile["name"])
        # ensure the media is now gone
        files = self.store.getEpisodeDocuments(transcriptName);
        self.assertEqual(0, len(files), "Document was deleted")
        
        # delete transcript/participant
        self.store.deleteTranscript(transcriptName)
        self.store.deleteParticipant(participantName)
        
        # make sure they were deleted
        count = self.store.countMatchingTranscriptIds("id = '"+transcriptName+"'")
        self.assertEqual(0, count, "Transcript is gone")
        count = self.store.countMatchingParticipantIds("id = '"+participantName+"'")
        self.assertEqual(0, count, "Participant is in the store")

    def test_generateLayerUtterances(self):
        
        # get a participant ID to use
        ids = self.store.getParticipantIds()
        self.assertTrue(len(ids) > 0, "getParticipantIds: Some IDs are returned")
        participantId = [ ids[0] ]

        utterancesThreadId = self.store.allUtterances(participantId, None, True)
        try:
            task = self.store.waitForTask(utterancesThreadId, 30)
            # if the task is still running, it's taking too long, so cancel it
            if task["running"]:
                try:
                    self.store.cancelTask(utterancesThreadId)
                except:
                    pass
            self.assertFalse(task["running"], "Search task finished in a timely manner")
         
            matches = self.store.getMatches(utterancesThreadId, 2)
            if len(matches) == 0:
                print("getMatches: No matches were returned, cannot test getMatchAnnotations")
            else:
                upTo = min(5, len(matches))
                matches = matches[:upTo]
                
                # generate htk layer
                threadId = self.store.generateLayerUtterances(matches, "htk", "UnitTester")
                self.assertIsNotNone(threadId, "There is a threadId")
                
                try:
                    task = self.store.waitForTask(threadId, 60)
                    self.assertIn("running", task, "Is a valid task " + str(threadId))
                    
                    # if the task is still running, it's taking too long, so cancel it
                    if task["running"]:
                        try:
                            self.store.cancelTask(threadId)
                        except:
                            pass
                    self.assertFalse(task["running"], "Task finished in a timely manner")
                finally:
                    self.store.releaseTask(threadId)
        finally:
            self.store.releaseTask(utterancesThreadId)

    def test_updateFragment(self):
        ids = self.store.getParticipantIds()
        self.assertTrue(len(ids) > 0, "getParticipantIds: Some IDs are returned")
        participantId = [ ids[0] ]
        
        # all instances of "and"
        threadId = self.store.search({ "orthography" : "quakes" }, participantId)
        try:
            task = self.store.waitForTask(threadId, 30)
            # if the task is still running, it's taking too long, so cancel it
            if task["running"]:
                try:
                    self.store.cancelTask(threadId)
                except:
                    pass
            self.assertFalse(task["running"], "Search task finished in a timely manner")
            
            matches = self.store.getMatches(threadId, 2)
            if len(matches) == 0:
                print("getMatches: No matches were returned, cannot test getFragments")
            else:
                matches = matches[:2]
                
                dir = "getFragments"
                layerIds = [ "utterance", "word" ]
                fragments = self.store.getFragments(matches, layerIds, "text/praat-textgrid")
                try:
                    result = self.store.updateFragment(fragments[0])
                    self.assertIn("url", result, "Result includes URL")
                finally:
                    for fragment in fragments:
                        if fragment != None:
                            # duplicate names can exist, so the file may have already been deleted
                            if os.path.exists(fragment): 
                                os.remove(fragment)
                
        finally:
            self.store.releaseTask(threadId)

if __name__ == '__main__':
    unittest.main()
