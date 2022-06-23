#!/usr/bin/env python3

# This script uploads all transcript files it can find (and corresponsing media),
# deleting pre-existing versions first, to the LaBB-CAT server below:
#
# Dependencies:
#  - nzilbb-labbcat - run the following shell command: `pip install nzilbb-labbcat`
#  - progressbar - run the following shell command: `pip install progressbar`

import labbcat
import os
import progressbar
import sys

# the following are specified by command-line arguments:
url = "http://localhost:8080/labbcat"         # LaBB-CAT "home" URL
username = "labbcat"                          # LaBB-CAT username
password = "labbcat"                          # LaBB-CAT password
corpus = "corpus"                             # corpus to upload into
transcript_type = "interview"                 # transcript type to use
store = None
transcript_files = []

def delete_transcript(transcript):
    try:
        store.deleteTranscript(transcript)
    except labbcat.ResponseException as x:
        pass

def main(argv):
    global url
    global username
    global password
    global store
    
    print("Delete all except...");
    if len(argv) < 3:
        print("This script deletes all transcripts from LaBB-CAT *except* those in a given greenlist.")
        print("usage: " + argv[0] + " greenlist url [ username password]")
        print(" where:")
        print("  greenlist = a text file with one transcript name on each line")
        print("  url = the 'home' URL of the LaBB-CAT server")
        print("  username = (optional) the LaBB-CAT username")
        print("  password = (optional) the LaBB-CAT password")
    else:
        greenlist = argv[1]
        url = argv[2]
        username = None
        password = None
        if len(argv) > 4:
            username = argv[3]
            password = argv[4]
        print("Excepting transcripts named in "+greenlist+" ...")
        with open(greenlist) as f:
            exceptions = f.readlines()
        exceptions = [x.strip() for x in exceptions] 
        store = labbcat.LabbcatEdit(url, username, password)
        transcriptIds = store.getTranscriptIds()
        bar = progressbar.ProgressBar(len(transcriptIds)).start()
        deleteCount = 0
        for t, id in enumerate(transcriptIds):
            if not id in exceptions:
                delete_transcript(id)
                deleteCount = deleteCount+1
            bar.update(t)

        bar.finish()
        print("Finished, deleted " + str(deleteCount) + " transcripts")

if __name__ == "__main__":
    main(sys.argv)
