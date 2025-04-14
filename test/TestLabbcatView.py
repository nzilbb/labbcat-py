import unittest
import os
import labbcat

# YOU MUST ENSURE THE FOLLOWING SETTINGS ARE VALID FOR YOU TEST LABB-CAT SERVER:
labbcatUrl = "http://localhost:8080/labbcat/"
username = "labbcat"
password = "labbcat"

class TestLabbcatView(unittest.TestCase):
    """ Unit tests for LabbcatView.

    These tests test the functionality of the client library, not the server. 

    They assume the existence of a valid LaBB-CAT instance (configured by *labbcatUrl*)
    which responds correctly to requests, but do not generally test that the server behaves
    correctly , nor assume specific corpus content. For the tests to work, the first graph
    listed in LaBB-CAT must have some words and some media, and the first participant listed
    must have some transcripts.  
    """

    def setUp(self):
        self.store = labbcat.LabbcatView(labbcatUrl, username, password)
        
    def test_versionInfo(self):
        versionInfo = self.store.versionInfo()
        self.assertIn("System", versionInfo, "Has System section")
        self.assertIn("LaBB-CAT", versionInfo["System"], "Has main LaBB-CAT version")
        print("\nLaBB-CAT version " + versionInfo["System"]["LaBB-CAT"])
    
    def test_getId(self):
        id = self.store.getId()
        self.assertEqual(id, labbcatUrl)
    
    def test_getLayerIds(self):
        ids = self.store.getLayerIds()
        #for id : ids: print("layer " + id)
        self.assertTrue(len(ids) > 0, "Some IDs are returned")
        self.assertIn("word", ids, "Has word layer")
        self.assertIn("turn", ids, "Has turn layer")
        self.assertIn("utterance", ids, "Has utterance layer")
        self.assertIn("transcript_type", ids, "Has transcript_type layer")

    def test_getLayers(self):
        layers = self.store.getLayers()
        #for (String id : ids) print("layer " + id)
        self.assertTrue(len(layers) > 0, "Some IDs are returned")
        layerIds = []
        for layer in layers:
            layerIds.append(layer["id"])
        
        self.assertIn("word", layerIds, "Has word layer")
        self.assertIn("turn", layerIds, "Has turn layer")
        self.assertIn("utterance", layerIds, "Has utterance layer")
        self.assertIn("transcript_type", layerIds, "Has transcript_type layer")

    def test_getCorpusIds(self):
        ids = self.store.getCorpusIds()
        # for (String id : ids) print("corpus " + id)
        self.assertTrue(len(ids) > 0, "Some IDs are returned")

    def test_getParticipantIds(self):
        ids = self.store.getParticipantIds()
        # for (String id : ids) print("participant " + id)
        self.assertTrue(len(ids) > 0, "Some IDs are returned")

    def test_getTranscriptIds(self):
        ids = self.store.getTranscriptIds()
        # for (String id : ids) print("graph " + id)
        self.assertTrue(len(ids) > 0, "Some IDs are returned")

    def test_countMatchingParticipantIds(self):
        count = self.store.countMatchingParticipantIds("/.+/.test(id)")
        self.assertTrue(count > 0, "There are some matches")

    def test_getMatchingParticipantIds(self):
      ids = self.store.getMatchingParticipantIds("/.+/.test(id)")
      self.assertTrue(len(ids) > 0, "Some IDs are returned")
      if len(ids) < 2:
          print("Too few participants to test pagination")
      else:
         ids = self.store.getMatchingParticipantIds("/.+/.test(id)", 2, 0)
         self.assertEqual(2, len(ids), "Two IDs are returned")

    def test_getTranscriptIdsInCorpus(self):
        ids = self.store.getCorpusIds()
        self.assertTrue(len(ids) > 0, "There's at least one corpus")
        corpus = ids[0]
        ids = self.store.getTranscriptIdsInCorpus(corpus)
        self.assertTrue(len(ids) > 0, "Some IDs are returned for corpus " + corpus)

    def test_getTranscriptIdsWithParticipant(self):
        ids = self.store.getParticipantIds()
        self.assertTrue(len(ids) > 0, "There's at least one participant")
        participant = ids[0]
        ids = self.store.getTranscriptIdsWithParticipant(participant)
        self.assertTrue(len(ids) > 0, "Some IDs are returned for participant " + participant)   

    def test_countMatchingTranscriptIds(self):
        count = self.store.countMatchingTranscriptIds("/.+/.test(id)")
        self.assertTrue(count > 0, "There are some matches")   

    def test_getMatchingTranscriptIds(self):
        ids = self.store.getMatchingTranscriptIds("/.+/.test(id)")
        self.assertTrue(len(ids) > 0, "Some IDs are returned")
        if len(ids) < 2:
            print("Too few graphs to test pagination")
        else:
            ids = self.store.getMatchingTranscriptIds("/.+/.test(id)", 2, 0, "id DESC")
            self.assertEqual(2, len(ids), "Two IDs are returned")   

    def test_countAnnotations(self):
        ids = self.store.getMatchingTranscriptIds("/.+/.test(id)", 1, 0)
        self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
        graphId = ids[0]
        countAll = self.store.countAnnotations(graphId, "phonemes")
        self.assertTrue(countAll > 0, "There are some matches")   
        countFirsts = self.store.countAnnotations(graphId, "phonemes", 1)
        self.assertTrue(
            countAll > countFirsts,
            "All phonemes ("+str(countAll)
            +") are not more numerous than maxOrdinal = 1 ("+str(countFirsts)+")")   

    def test_getAnnotations(self):
        ids = self.store.getMatchingTranscriptIds("/.+/.test(id)", 1, 0)
        self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
        graphId = ids[0]
        
        count = self.store.countAnnotations(graphId, "orthography")
        annotations = self.store.getAnnotations(graphId, "orthography", pageLength=2, pageNumber=0)
        if count < 2:
            print("Too few annotations to test pagination")
        else:
            self.assertEqual(2, len(annotations), "Two annotations are returned")

            # do they look like annotations?
            annotation = annotations[0]
            for key in ["id", "label", "startId", "endId"]:
                with self.subTest(key=key):
                    self.assertIn(key, annotation, "Has " + key)

        allAnnotations = self.store.getAnnotations(graphId, "phonemes")
        firstAnnotations = self.store.getAnnotations(graphId, "phonemes", maxOrdinal=1)
        self.assertTrue(
            len(allAnnotations) > len(firstAnnotations),
            "All phonemes ("+str(len(allAnnotations))
            +") are not more numerous than maxOrdinal = 1 ("+str(len(firstAnnotations))+")")   

    def test_getAnchors(self):
        # get a graph to work with
        ids = self.store.getMatchingTranscriptIds("/.+/.test(id)", 1, 0)
        self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
        graphId = ids[0]

        # get some annotations so we have valid anchor IDs
        annotations = self.store.getAnnotations(
            graphId, "orthography", pageLength=2, pageNumber=0)
        if len(annotations) == 0:
            print("Can't test getAnchors() - no annotations in " + graphId)
        else:
            # create an array of anchorIds
            anchorIds = []
            for annotation in annotations:
                anchorIds.append(annotation["startId"])
            
                # finally, get the anchors
                anchors = self.store.getAnchors(graphId, anchorIds)         
                self.assertEqual(len(anchorIds), len(anchors), "Correct number of anchors is returned")
                
                # do they look like anchors?
                anchor = anchors[0]
                for key in ["id", "offset", "confidence"]:
                    with self.subTest(key=key):
                        self.assertIn(key, anchor, "Has " + key)
   
    def test_getMediaUrl(self):
        ids = self.store.getMatchingTranscriptIds("/AP511.+\\.eaf/.test(id)", 1, 0)
        self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
        graphId = ids[0]
        url = self.store.getMediaUrl(graphId, "", "audio/wav")
        self.assertIsNotNone(
            url, "There is some media (check the first graph listed) "+graphId+")")
        self.assertTrue(url.startswith("http"), "Looks like a URL")
    
    def test_getMedia(self):
        ids = self.store.getMatchingTranscriptIds("/AP511.+\\.eaf/.test(id)", 1, 0)
        self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
        graphId = ids[0]
        fileName = self.store.getMedia(graphId, "", "audio/wav")
        self.assertIsNotNone(
            fileName, "There is some media (check the first graph listed) "+graphId+")")
        self.assertTrue(os.path.exists(fileName), "File downloaded")
        self.assertTrue(fileName.endswith(".wav"), "File name correct")
        os.remove(fileName)
    
    def test_formatTranscript(self):
        ids = self.store.getMatchingTranscriptIds("/AP511.+\\.eaf/.test(id)", 1, 0)
        self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
        graphId = ids[0]
        fileNames = self.store.formatTranscript(graphId, ["utterance"], "text/plain")
        self.assertIsNotNone(
            fileNames, "There is some media (check the first graph listed) "+graphId+")")
        self.assertIsNotNone(
            fileNames[0], "There is some media (check the first graph listed) "+graphId+")")
        self.assertTrue(os.path.exists(fileNames[0]), "File downloaded")
        self.assertTrue(fileNames[0].endswith(".txt"), "File name correct")
        os.remove(fileNames[0])
    
    def test_getMediaFragment(self):
      ids = self.store.getMatchingTranscriptIds("/AP511.+\\.eaf/.test(id)", 1, 0)
      self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
      graphId = ids[0]
      url = self.store.getMedia(graphId, "", "audio/wav", 1.0, 2.0)
      self.assertIsNotNone(url, "There is some media")   

    def test_getLayer(self):
        layer = self.store.getLayer("orthography")
        self.assertEqual("orthography", layer["id"], "Correct layer")   

        # does it look like a layer?
        for key in ["id", "description", "parentId", "peers", "peersOverlap"]:
            with self.subTest(key=key):
                self.assertIn(key, layer, "Has " + key)

    def test_getParticipant(self):
        # find a participant ID to use
        ids = self.store.getParticipantIds()
        # for (String id : ids) print("participant " + id)
        self.assertTrue(len(ids) > 0, "Some participant IDs exist")
        participantId = ids[0]
        participant = self.store.getParticipant(participantId)
        self.assertEqual(participantId, participant["label"], "Correct participant") # not getId()

        # does it look like an annotation
        for key in ["id", "label"]:
            with self.subTest(key=key):
                self.assertIn(key, participant, "Has " + key)

    def test_countMatchingAnnotations(self):
      count = self.store.countMatchingAnnotations("layer.id == 'orthography' && label == 'and'")
      self.assertTrue(count > 0, "There are some matches")   

    def test_getMatchingAnnotations(self):
      annotations = self.store.getMatchingAnnotations(
          "layer.id == 'orthography' && label == 'and'", 2, 0)
      self.assertEqual(2, len(annotations), "Two annotations are returned")
      
      # do they look like annotations?
      annotation = annotations[0]
      for key in ["id", "label", "startId", "endId"]:
          with self.subTest(key=key):
              self.assertIn(key, annotation, "Has " + key)

    def test_getMediaTracks(self):
        tracks = self.store.getMediaTracks()
        #for (String track : tracks) print("track " + track)
        self.assertTrue(len(tracks) > 0, "Some tracks are returned")
        idSet = []
        for track in tracks:
            idSet.append(track["suffix"])
            
            # does it look like a track?
            for key in ["suffix", "description"]:
                with self.subTest(key=key):
                    self.assertIn(key, track, "Has " + key)
        
        self.assertIn("", idSet, "Has default track")   
   
    def test_getAvailableMedia(self):
      # get a graph to work with
      ids = self.store.getMatchingTranscriptIds("/.+/.test(id)", 1, 0)
      self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
      graphId = ids[0]

      # get some annotations so we have valid anchor IDs
      files = self.store.getAvailableMedia(graphId)
      self.assertTrue(len(files) > 0, graphId + " has some tracks")

      # do they look like annotations?
      file = files[0]
      for key in ["name", "mimeType", "url", "trackSuffix"]:
          with self.subTest(key=key):
              self.assertIn(key, file, "Has " + key)
   
    def test_getEpisodeDocuments(self):
      # get a graph to work with
      ids = self.store.getMatchingTranscriptIds("/.+/.test(id)", 1, 0)
      self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
      graphId = ids[0]

      # get some annotations so we have valid anchor IDs
      files = self.store.getEpisodeDocuments(graphId)
      if len(files) == 0:
          print("\n" + graphId + " has no documents")
      else:
          # do they look like annotations?
          file = files[0]
          for key in ["name", "type", "url", "trackSuffix"]:
              with self.subTest(key=key):
                  self.assertIn(key, file, "Has " + key)
    
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
            
    def test_getTrascriptAttributes(self):
        ids = self.store.getTranscriptIds()
        self.assertTrue(len(ids) > 0, "At least 3 transcripts in the corpus")
        ids = ids[:3]
        layerIds = ["transcript_type", "corpus"]
        fileName = self.store.getTranscriptAttributes(ids, layerIds)
        self.assertTrue(fileName.endswith(".csv"), "ID list: CSV file returned")
        self.assertTrue(os.path.isfile(fileName), "ID list: CSV file exists")
        os.remove(fileName)
        
        fileName = self.store.getTranscriptAttributes(
            "['corpus'].includesAny(labels('corpus'))", layerIds, "test.csv")
        self.assertEqual("test.csv", fileName, "Query expression: Given CSV file returned")
        self.assertTrue(os.path.isfile(fileName), "Query expression: CSV file exists")
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
    
    def test_searchInvalidPattern(self):
        try:
            threadId = self.store.search({})
            fail("Search with invalid pattern fails")
        except:
            pass
    
    def test_searchAndCancelTask(self):
        # start a long-running search - all words
        pattern = { "orthography" : ".*" }
        threadId = self.store.search(pattern)
        self.store.cancelTask(threadId)
    
    def test_searchAndGetMatchesAndGetMatchAnnotations(self):
        # get a participant ID to use
        ids = self.store.getParticipantIds()
        self.assertTrue(len(ids) > 0, "getParticipantIds: Some IDs are returned")
        participantId = [ ids[0] ]

        # all instances of "and"
        pattern = {"orthography" : "and" }
        threadId = self.store.search(pattern, participantId, None, False, False, None)
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
                print("getMatches: No matches were returned, cannot test getMatchAnnotations")
            else:
                upTo = min(10, len(matches))
                
                matches = self.store.getMatches(threadId, 2, upTo, 0)
                self.assertEqual(upTo, len(matches), "pagination works ("+str(upTo)+")")
                
                layerIds = [ "orthography" ]
                annotations = self.store.getMatchAnnotations(matches, layerIds, 0, 1)
                self.assertEqual(len(matches), len(annotations),
                                  "annotations array is same size as matches array")
                self.assertEqual(1, len(annotations[0]), "row arrays are the right size")
                # do they look like annotations?
                annotation = annotations[0][0]
                for key in ["layerId", "id", "label", "startId", "endId"]:
                    with self.subTest(key=key):
                        self.assertIn(key, annotation, "Has " + key)
                # there should be no alignments
                self.assertNotIn("start", annotation, "Doesn't have start anchor")
                self.assertNotIn("end", annotation, "Doesn't have anchor")

                # now get alignments
                layerIds = [ "orthography" ]
                annotations = self.store.getMatchAnnotations(matches, layerIds, 0, 1, 0)
                self.assertEqual(len(matches), len(annotations),
                                  "annotations array is same size as matches array")
                self.assertEqual(1, len(annotations[0]), "row arrays are the right size")
                # do they look like annotations?
                annotation = annotations[0][0]
                for key in ["layerId", "id", "label", "startId", "endId", "start", "end"]:
                    with self.subTest(key=key):
                        self.assertIn(key, annotation, "Has " + key)
                # anchors have offsets
                self.assertIn("offset", annotation["start"], "Start anchor includes offset")
                self.assertIn("offset", annotation["end"], "End anchor includes offset")
                
                layerIds = [ "invalid layer ID" ]
                try:
                    self.store.getMatchAnnotations(matches, layerIds, 0, 1)
                    fail("getMatchAnnotations with invalid layerId should fail")
                except:
                    pass
        finally:
            self.store.releaseTask(threadId)

    def test_allUtterancesAndGetMatchesAndGetMatchAnnotations(self):
        # get a participant ID to use
        ids = self.store.getParticipantIds()
        self.assertTrue(len(ids) > 0, "getParticipantIds: Some IDs are returned")
        participantId = [ ids[0] ]

        threadId = self.store.allUtterances(participantId, None, True)
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
                print("getMatches: No matches were returned, cannot test getMatchAnnotations")
            else:
                upTo = min(10, len(matches))
                
                matches = self.store.getMatches(threadId, 2, upTo, 0)
                self.assertEqual(upTo, len(matches), "pagination works ("+str(upTo)+")")
                
        finally:
            self.store.releaseTask(threadId)

    def test_searchIPA(self):
        # get a participant ID to use
        ids = self.store.getParticipantIds()
        self.assertTrue(len(ids) > 0, "getParticipantIds: Some IDs are returned")
        participantId = [ ids[0] ]

        # all instances of "iː"
        pattern = {"segment" : "iː" }
        threadId = self.store.search(pattern, participantId, None, False, False, None)
        try:
            task = self.store.waitForTask(threadId, 30)
            # if the task is still running, it's taking too long, so cancel it
            if task["running"]:
                try:
                    self.store.cancelTask(threadId)
                except:
                    pass
            self.assertFalse(task["running"], "Search task finished in a timely manner")
         
        finally:
            self.store.releaseTask(threadId)

    def test_getMatchesWithPattern(self):
        # all instances of "then"
        pattern = {"orthography" : "end" }
        threadId = self.store.search(pattern)
        try:
            task = self.store.waitForTask(threadId, 30)
            # if the task is still running, it's taking too long, so cancel it
            if task["running"]:
                try:
                    self.store.cancelTask(threadId)
                except:
                    pass
            self.assertFalse(task["running"], "Search task finished in a timely manner")
         
            matchesWithThreadId = self.store.getMatches(threadId, 2)
            if len(matchesWithThreadId) == 0:
                print("getMatches: No matches were returned, cannot test getMatches with pattern")
            else:
                matchesWithPattern = self.store.getMatches(pattern)
                self.assertEqual(
                    len(matchesWithThreadId), len(matchesWithPattern),
                    "matches returns the same number of results with threadId and pattern")
        finally:
            self.store.releaseTask(threadId)

    def test_processWithPraat(self):
        # get a participant ID to use
        ids = self.store.getParticipantIds()
        self.assertTrue(len(ids) > 0, "getParticipantIds: Some IDs are returned")
        participantId = [ ids[0] ]
        
        # all instances of the "a" segment
        threadId = self.store.search({ "segment" : "a" }, participantId)
        try:
            task = self.store.waitForTask(threadId, 30)
            # if the task is still running, it's taking too long, so cancel it
            if task["running"]:
                try:
                    self.store.cancelTask(threadId)
                except:
                    pass
            self.assertFalse(task["running"], "Search task finished in a timely manner")
            
            matches = self.store.getMatches(threadId, 0)
            if len(matches) == 0:
                print("getMatches: No matches were returned, cannot test getFragments")
            else:
                upTo = min(5, len(matches))
                subset = matches[:upTo]

                segments = self.store.getMatchAnnotations(subset, [ "segment" ], 0, 1, 0)
                # flatten into a single list
                segments = [item for row in segments for item in row]
                startOffsets = list(
                    map(lambda annotation: annotation["start"]["offset"], segments))
                endOffsets = list(
                    map(lambda annotation: annotation["end"]["offset"], segments))
                
                praatScript = labbcat.praatScriptFormants() \
                    +labbcat.praatScriptCentreOfGravity() \
                    +labbcat.praatScriptIntensity() \
                    +labbcat.praatScriptPitch() \
                    +labbcat.praatScriptFastTrack()
                
                measures = self.store.processWithPraat(
                    subset, startOffsets, endOffsets, praatScript, 0.025)
                self.assertEqual(len(subset), len(measures),
                                 "measures array is same size as matches array")
                # they look like praat results
                for m in range(upTo):
                    results = measures[m]
                    for key in ["time_0_5", "f1_time_0_5", "f2_time_0_5", "Error"]:
                        with self.subTest(key=key):
                            self.assertIn(key, results, "Has " + key)
            
        finally:
            self.store.releaseTask(threadId)

    def test_searchExcludingOverlappingSpeech(self):
        # all instances of "mmm", which is common in overlapping speech
        pattern = {"orthography" : "mmm" }
        includeTaskId = self.store.search(pattern)
        excludeTaskId = self.store.search(pattern, overlapThreshold=5)
        try:
            includeOverlapping = self.store.getMatches(includeTaskId)
            if len(includeOverlapping) == 0:
                print("getMatches: No matches were returned, cannot test overlapThreshold")
            else:
                excludeOverlapping = self.store.getMatches(excludeTaskId)
                self.assertTrue(
                    len(includeOverlapping) > len(excludeOverlapping),
                    "excluding overlapping speech returns fewer results than including it")
        finally:
            self.store.releaseTask(includeTaskId)
            self.store.releaseTask(excludeTaskId)

    def test_getSoundFragments(self):
        # get a participant ID to use
        ids = self.store.getParticipantIds()
        self.assertTrue(len(ids) > 0, "getParticipantIds: Some IDs are returned")
        participantId = { ids[0] }      
        
        # all instances of "and"
        pattern = { "orthography" : "and" }
        threadId = self.store.search(pattern, participantId, None, False, False, None)
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
                print("getMatches: No matches were returned, cannot test getSoundFragments")
            else:
                upTo = min(5, len(matches))
                subset = matches[:upTo]
                
                wavs = self.store.getSoundFragments(subset)
                try:
                    self.assertEqual(len(subset), len(wavs))
                    
                    for m in range(upTo):
                        self.assertIsNotNone(wavs[m], "Non-None file: " + str(subset[m]))
                        self.assertTrue(len(wavs[m]) > 0, "Non-zero sized file: " + str(subset[m]))
                finally:
                    for wav in wavs:
                        if wav != None:
                            # duplicate names can exist, so the file may have already been deleted
                            if os.path.exists(wav): 
                                os.remove(wav)
            
        finally:
            self.store.releaseTask(threadId)

    def test_getFragments(self):
        # get a participant ID to use
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
                upTo = min(5, len(matches))
                subset = matches[:upTo]
                
                dir = "getFragments"
                layerIds = [ "orthography" ]
                fragments = self.store.getFragments(subset, layerIds, "text/praat-textgrid", dir)
                try:
                    self.assertEqual(len(subset), len(fragments),
                                      "files array is same size as matches array")
                    
                    for m in range(upTo):
                        self.assertIsNotNone(fragments[m], "Non-None file: " + str(subset[m]))
                        self.assertTrue(len(fragments[m]) > 0,
                                        "Non-zero sized file: " + str(subset[m]))
                finally:
                    for fragment in fragments:
                        if fragment != None:
                            # duplicate names can exist, so the file may have already been deleted
                            if os.path.exists(fragment): 
                                os.remove(fragment)
                    os.rmdir(dir)
        finally:
            self.store.releaseTask(threadId)

    def test_getFragmentsAsync_taskResults(self):
        # get a participant ID to use
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
                upTo = min(5, len(matches))
                subset = matches[:upTo]
                
                dir = "getFragments"
                layerIds = [ "orthography" ]
                fragmentsThreadId = self.store.getFragmentsAsync(
                    subset, layerIds, "text/praat-textgrid")
                fragmentsTask = self.store.waitForTask(fragmentsThreadId, 30)
                # if the task is still running, it's taking too long, so cancel it
                if fragmentsTask["running"]:
                    try:
                        self.store.cancelTask(fragmentsThreadId)
                    except:
                        pass
                self.assertFalse(task["running"], "Fragments task finished in a timely manner")
                
                fragments = self.store.taskResults(fragmentsThreadId, dir)
                self.store.releaseTask(fragmentsThreadId)
                try:
                    self.assertEqual(len(subset), len(fragments),
                                      "files array is same size as matches array")
                    
                    for m in range(upTo):
                        self.assertIsNotNone(fragments[m], "Non-None file: " + str(subset[m]))
                        self.assertTrue(len(fragments[m]) > 0,
                                        "Non-zero sized file: " + str(subset[m]))
                finally:
                    for fragment in fragments:
                        if fragment != None:
                            # duplicate names can exist, so the file may have already been deleted
                            if os.path.exists(fragment): 
                                os.remove(fragment)
                    os.rmdir(dir)
        finally:
            self.store.releaseTask(threadId)

    def test_getSerializerDescriptors(self):
        descriptors = self.store.getSerializerDescriptors()
        #for (String descriptor : descriptors) print("descriptor " + descriptor)
        self.assertTrue(len(descriptors) > 0, "Some descriptors are returned")
        idSet = []
        for descriptor in descriptors:
            idSet.append(descriptor["mimeType"])
            
            # does it look like a descriptor?
            for key in ["name", "mimeType", "version", "icon", "numberOfInputs", "fileSuffixes", "minimumApiVersion"]:
                with self.subTest(key=key):
                    self.assertIn(key, descriptor, "Has " + key)
        
        self.assertIn("text/plain", idSet, "Has plain text descriptor")
       
    def test_getDeserializerDescriptors(self):
        descriptors = self.store.getDeserializerDescriptors()
        #for (String descriptor : descriptors) print("descriptor " + descriptor)
        self.assertTrue(len(descriptors) > 0, "Some descriptors are returned")
        idSet = []
        for descriptor in descriptors:
            idSet.append(descriptor["mimeType"])
            
            # does it look like a descriptor?
            for key in ["name", "mimeType", "version", "icon", "numberOfInputs", "fileSuffixes", "minimumApiVersion"]:
                with self.subTest(key=key):
                    self.assertIn(key, descriptor, "Has " + key)
                    
    def test_getSystemAttribute(self):
        value = self.store.getSystemAttribute("title")
        #print("value " + value)
        self.assertIsNotNone(value, "Value is returned")
    
    def test_getUserInfo(self):
        user = self.store.getUserInfo()
        #print("user " + user)
        self.assertIsNotNone(user, "User is returned")
        
if __name__ == '__main__':
    unittest.main()
