#!/usr/bin/env python

# This script uploads all transcript files it can find (and corresponsing media),
# deleting pre-existing versions first, to the LaBB-CAT server below:

import os
import sys
import labbcat

# the following are specified by command-line arguments:
ext = "trs"                                   # transcript file extension to look for
url = "http://localhost:8080/labbcat"         # LaBB-CAT "home" URL
username = "labbcat"                          # LaBB-CAT username
password = "labbcat"                          # LaBB-CAT password
corpus = "corpus"                             # corpus to upload into
transcript_type = "interview"                 # transcript type to use
store = None
transcript_files = []

def upload_next_transcript():
    if len(transcript_files) > 0:
        # delete it from the server first
        delete_transcript(transcript_files.pop())
    else:
        print("Finished.");

def delete_transcript(transcript):
    print(transcript + " ...");
    transcript_name = os.path.basename(transcript)
    try:
        store.deleteTranscript(transcript_name)
    except labbcat.ResponseException as x:
        pass
    
    upload_transcript(transcript)

def upload_transcript(transcript):
    print("uploading " + transcript);
    possible_media = [
        transcript.replace(ext,".wav"),
        transcript.replace(ext,".mp4"),
        transcript.replace(ext,".mp3")]
    media = None
    for m in possible_media:
        if os.path.isfile(m):
            media = m
    print("Media: " + media)
    store.newTranscript(transcript, media, None, transcript_type, corpus, None) 
    upload_next_transcript()

def main(argv):
    global ext
    global url
    global username
    global password
    global corpus
    global transcript_type
    global store
    global transcript_files
    
    print("Batch upload...");
    if len(argv) < 6:
        print("This script uploads all transcript files it can find (and corresponsing media),")
        print("deleting pre-existing versions first, to a given LaBB-CAT server.")
        print("usage: " + argv[0] + " dir ext corpus type url [ username password]")
        print(" where:")
        print("  dir = the directory/folder under which transcript files are to be found")
        print("  ext = the extension of the transcripts - e.g. trs or eaf")
        print("  corpus = the corpus to upload the transcripts to")
        print("  type = the transcript type to use")
        print("  url = the 'home' URL of the LaBB-CAT server")
        print("  username = (optional) the LaBB-CAT username")
        print("  password = (optional) the LaBB-CAT password")
    else:
        dir = argv[1]
        ext = "." + argv[2]
        corpus = argv[3]
        transcript_type = argv[4]
        url = argv[5]
        username = None
        password = None
        if len(argv) > 7:
            username = argv[6]
            password = argv[7]
        print("Looking for transcripts under "+dir+" ...")
        for (dirpath, dirnames, filenames) in os.walk(dir):
            for f in filenames:
                if f.endswith(ext):
                    path = os.path.join(dirpath, f)
                    print("Found " + path);
                    transcript_files.insert(0, path)
    
        print("Uploading "+str(len(transcript_files))+" transcripts to "+url+" ...")
        store = labbcat.Labbcat(url, username, password)
        upload_next_transcript()

if __name__ == "__main__":
    main(sys.argv)
