import unittest
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
            
if __name__ == '__main__':
    unittest.main()
