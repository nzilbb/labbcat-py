import unittest
import os
import labbcat

class TestAGQL(unittest.TestCase):
    """ Unit tests for AGQL.

    These tests ensure functions for generating 'AGQL' expressions work as expected. 
    """

    def test_expressionFromAttributeValue(self):
        # single value
        self.assertEqual(
            "first('transcript_language').label == 'en'",
            labbcat.expressionFromAttributeValue("transcript_language", "en"),
            "single value")
        # single item list
        self.assertEqual(
            "first('transcript_language').label == 'en'",
            labbcat.expressionFromAttributeValue("transcript_language", ["en"]),
            "single item list")
        # multiple item list
        self.assertEqual(
            "['en-US','en-NZ'].includes(first('transcript_language').label)",
            labbcat.expressionFromAttributeValue("transcript_language", ["en-US","en-NZ"]),
            "multiple item list")
        # single value with negation
        self.assertEqual(
            "first('transcript_language').label <> 'en'",
            labbcat.expressionFromAttributeValue("transcript_language", "en", True),
            "single value with negation")
        # single item list with negation
        self.assertEqual(
            "first('transcript_language').label <> 'en'",
            labbcat.expressionFromAttributeValue("transcript_language", ["en"], True),
            "single item list with negation")
        # multiple item list with negation
        self.assertEqual(
            "!['en-US','en-NZ'].includes(first('transcript_language').label)",
            labbcat.expressionFromAttributeValue("transcript_language", ["en-US","en-NZ"], True),
            "multiple item list with negation")
        # single item with quote
        self.assertEqual(
            "first('participant_surname').label == 'O\\'Reilly'",
            labbcat.expressionFromAttributeValue("participant_surname", ["O'Reilly"]),
            "single item with quote")
        # multiple items with quote
        self.assertEqual(
            "['O\\'Reilly','\"Prince\"'].includes(first('participant_surname').label)",
            labbcat.expressionFromAttributeValue("participant_surname", ["O'Reilly","\"Prince\""]),
            "multiple items with quote")
        # attribute with quote
        self.assertEqual(
            "first('participant_parents\\' languages').label == 'en'",
            labbcat.expressionFromAttributeValue("participant_parents' languages", "en"),
            "attribute with quote - one value")
        self.assertEqual(
            "['en','mi'].includes(first('participant_parents\\' languages').label)",
            labbcat.expressionFromAttributeValue("participant_parents' languages", ["en", "mi"]),
            "attribute with quote - multiple values")

    def test_expressionFromAttributeValues(self):
        # single value
        self.assertEqual(
            "labels('transcript_language').includes('en')",
            labbcat.expressionFromAttributeValues("transcript_language", "en"),
            "single value")
        # single item list
        self.assertEqual(
            "labels('transcript_language').includes('en')",
            labbcat.expressionFromAttributeValues("transcript_language", ["en"]),
            "single item list")
        # multiple item list
        self.assertEqual(
            "['en-US','en-NZ'].includesAny(labels('transcript_language'))",
            labbcat.expressionFromAttributeValues("transcript_language", ["en-US","en-NZ"]),
            "multiple item list")
        # single value with negation
        self.assertEqual(
            "!labels('transcript_language').includes('en')",
            labbcat.expressionFromAttributeValues("transcript_language", "en", True),
            "single value with negation")
        # single item list with negation
        self.assertEqual(
            "!labels('transcript_language').includes('en')",
            labbcat.expressionFromAttributeValues("transcript_language", ["en"], True),
            "single item list with negation")
        # multiple item list with negation
        self.assertEqual(
            "!['en-US','en-NZ'].includesAny(labels('transcript_language'))",
            labbcat.expressionFromAttributeValues("transcript_language", ["en-US","en-NZ"], True),
            "multiple item list with negation")
        # single item with quote
        self.assertEqual(
            "labels('participant_surname').includes('O\\'Reilly')",
            labbcat.expressionFromAttributeValues("participant_surname", ["O'Reilly"]),
            "single item with quote")
        # multiple items with quote
        self.assertEqual(
            "['O\\'Reilly','\"Prince\"'].includesAny(labels('participant_surname'))",
            labbcat.expressionFromAttributeValues("participant_surname", ["O'Reilly","\"Prince\""]),
            "multiple items with quote")
        # attribute with quote
        self.assertEqual(
            "labels('participant_parents\\' languages').includes('en')",
            labbcat.expressionFromAttributeValues("participant_parents' languages", "en"),
            "attribute with quote - one value")
        self.assertEqual(
            "['en','mi'].includesAny(labels('participant_parents\\' languages'))",
            labbcat.expressionFromAttributeValues("participant_parents' languages", ["en", "mi"]),
            "attribute with quote - multiple values")

    def test_expressionFromIds(self):
        # single value
        self.assertEqual(
            "id == 'AP511_MikeThorpe.eaf'",
            labbcat.expressionFromIds("AP511_MikeThorpe.eaf"),
            "single value")
        # single item list
        self.assertEqual(
            "id == 'AP511_MikeThorpe.eaf'",
            labbcat.expressionFromIds(["AP511_MikeThorpe.eaf"]),
            "single item list")
        # multiple item list
        self.assertEqual(
            "['AP511_MikeThorpe.eaf','AP513_Steve.eaf'].includes(id)",
            labbcat.expressionFromIds(["AP511_MikeThorpe.eaf", "AP513_Steve.eaf"]),
            "multiple item list")
        # single value with negation
        self.assertEqual(
            "id <> 'AP511_MikeThorpe.eaf'",
            labbcat.expressionFromIds("AP511_MikeThorpe.eaf", True),
            "single value with negation")
        # single item list with negation
        self.assertEqual(
            "id <> 'AP511_MikeThorpe.eaf'",
            labbcat.expressionFromIds(["AP511_MikeThorpe.eaf"], True),
            "single item list with negation")
        # multiple item list with negation
        self.assertEqual(
            "!['AP511_MikeThorpe.eaf','AP513_Steve.eaf'].includes(id)",
            labbcat.expressionFromIds(["AP511_MikeThorpe.eaf", "AP513_Steve.eaf"], True),
            "multiple item list with negation")
        # single item with quote
        self.assertEqual(
            "id == 'EG112_WJO\\'Halloran'",
            labbcat.expressionFromIds(["EG112_WJO'Halloran"]),
            "single item with quote")
        # multiple items with quote
        self.assertEqual(
            "['EG112_WJO\\'Halloran','Dwayne \"The Rock\" Johnson'].includes(id)",
            labbcat.expressionFromIds(["EG112_WJO'Halloran","Dwayne \"The Rock\" Johnson"]),
            "multiple items with quote")
        
    def test_expressionFromTranscriptTypes(self):
        # single value
        self.assertEqual(
            "first('transcript_type').label == 'wordlist'",
            labbcat.expressionFromTranscriptTypes("wordlist"),
            "single value")
        # single item list
        self.assertEqual(
            "first('transcript_type').label == 'wordlist'",
            labbcat.expressionFromTranscriptTypes(["wordlist"]),
            "single item list")
        # multiple item list
        self.assertEqual(
            "['wordlist','reading'].includes(first('transcript_type').label)",
            labbcat.expressionFromTranscriptTypes(["wordlist","reading"]),
            "multiple item list")
        # single value with negation
        self.assertEqual(
            "first('transcript_type').label <> 'wordlist'",
            labbcat.expressionFromTranscriptTypes("wordlist", True),
            "single value with negation")
        # single item list with negation
        self.assertEqual(
            "first('transcript_type').label <> 'wordlist'",
            labbcat.expressionFromTranscriptTypes(["wordlist"], True),
            "single item list with negation")
        # multiple item list with negation
        self.assertEqual(
            "!['wordlist','reading'].includes(first('transcript_type').label)",
            labbcat.expressionFromTranscriptTypes(["wordlist","reading"], True),
            "multiple item list with negation")
        # single item with quote
        self.assertEqual(
            "first('transcript_type').label == 'Interviewee\\'s pepeha'",
            labbcat.expressionFromTranscriptTypes(["Interviewee's pepeha"]),
            "single item with quote")
        # multiple items with quote
        self.assertEqual(
            "['Interviewee\\'s pepeha','\"Interviewer\\'s description\"'].includes(first('transcript_type').label)",
            labbcat.expressionFromTranscriptTypes(
                ["Interviewee's pepeha","\"Interviewer's description\""]),
            "multiple items with quote")
        
    def test_expressionFromCorpora(self):
        # single value
        self.assertEqual(
            "labels('corpus').includes('QB')",
            labbcat.expressionFromCorpora("QB"),
            "single value")
        # single item list
        self.assertEqual(
            "labels('corpus').includes('QB')",
            labbcat.expressionFromCorpora(["QB"]),
            "single item list")
        # multiple item list
        self.assertEqual(
            "['CC','MU'].includesAny(labels('corpus'))",
            labbcat.expressionFromCorpora(["CC","MU"]),
            "multiple item list")
        # single value with negation
        self.assertEqual(
            "!labels('corpus').includes('QB')",
            labbcat.expressionFromCorpora("QB", True),
            "single value with negation")
        # single item list with negation
        self.assertEqual(
            "!labels('corpus').includes('QB')",
            labbcat.expressionFromCorpora(["QB"], True),
            "single item list with negation")
        # multiple item list with negation
        self.assertEqual(
            "!['CC','MU'].includesAny(labels('corpus'))",
            labbcat.expressionFromCorpora(["CC","MU"], True),
            "multiple item list with negation")


if __name__ == '__main__':
    unittest.main()
