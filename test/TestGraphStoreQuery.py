import unittest
import labbcat

# YOU MUST ENSURE THE FOLLOWING SETTINGS ARE VALID FOR YOU TEST LABB-CAT SERVER:
labbcatUrl = "http://localhost:8080/labbcat/"
username = "labbcat"
password = "labbcat"

class TestGraphStoreQuery(unittest.TestCase):
    """ Unit tests for GraphStoreQuery.

    These tests test the functionality of the client library, not the server. 

    They assume the existence of a valid LaBB-CAT instance (configured by *labbcatUrl*)
    which responds correctly to requests, but do not generally test that the server behaves
    correctly , nor assume specific corpus content. For the tests to work, the first graph
    listed in LaBB-CAT must have some words and some media, and the first participant listed
    must have some transcripts.  
    """

    def setUp(self):
        self.store = labbcat.GraphStoreQuery(labbcatUrl, username, password)
        
    def test_getId(self):
        id = self.store.getId()
        self.assertEqual(id, labbcatUrl)
    
    def test_getLayerIds(self):
        ids = self.store.getLayerIds()
        #for id : ids: print("layer " + id)
        self.assertTrue(len(ids) > 0, "Some IDs are returned")
        self.assertIn("transcript", ids, "Has transcript layer")
        self.assertIn("turns", ids, "Has turns layer")
        self.assertIn("utterances", ids, "Has utterances layer")
        self.assertIn("transcript_type", ids, "Has transcript_type layer")

    def test_getLayers(self):
        layers = self.store.getLayers()
        #for (String id : ids) print("layer " + id)
        self.assertTrue(len(layers) > 0, "Some IDs are returned")
        layerIds = []
        for layer in layers:
            layerIds.append(layer["id"])
        
        self.assertIn("transcript", layerIds, "Has transcript layer")
        self.assertIn("turns", layerIds, "Has turns layer")
        self.assertIn("utterances", layerIds, "Has utterances layer")
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
        count = self.store.countAnnotations(graphId, "orthography")
        self.assertTrue(count > 0, "There are some matches")   

    def test_getAnnotations(self):
        ids = self.store.getMatchingTranscriptIds("/.+/.test(id)", 1, 0)
        self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
        graphId = ids[0]
        
        count = self.store.countAnnotations(graphId, "orthography")
        annotations = self.store.getAnnotations(graphId, "orthography", 2, 0)
        if count < 2:
            print("Too few annotations to test pagination")
        else:
            self.assertEqual(2, len(annotations), "Two annotations are returned")

            # do they look like annotations?
            annotation = annotations[0]
            for key in ["id", "label", "startId", "endId"]:
                with self.subTest(key=key):
                    self.assertIn(key, annotation, "Has " + key)

    def test_getAnchors(self):
        # get a graph to work with
        ids = self.store.getMatchingTranscriptIds("/.+/.test(id)", 1, 0)
        self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
        graphId = ids[0]

        # get some annotations so we have valid anchor IDs
        annotations = self.store.getAnnotations(graphId, "orthography", 2, 0)
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
   
    def test_getMedia(self):
        ids = self.store.getMatchingTranscriptIds("/AP511.+\\.eaf/.test(id)", 1, 0)
        self.assertTrue(len(ids) > 0, "Some graph IDs are returned")
        graphId = ids[0]
        url = self.store.getMedia(graphId, "", "audio/wav")
        self.assertIsNotNone(
            url, "There is some media (check the first graph listed) "+graphId+")")
    
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
        for key in ["id", "label", "startId", "endId"]:
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
          for key in ["name", "mimeType", "url", "trackSuffix"]:
              with self.subTest(key=key):
                  self.assertIn(key, file, "Has " + key)
          
if __name__ == '__main__':
    unittest.main()
