#!/usr/bin/python3 
# Script that extracts all media and transcript files from LaBB-CAT.
#
# Author: Robert Fromont
# Date: June 2022
# Dependencies:
#  - nzilbb-labbcat - run the following shell command: `pip install nzilbb-labbcat`
#  - progressbar - run the following shell command: `pip install progressbar`

import labbcat
import progressbar
import sys

def main(argv):
    
    print("Download media and transcripts...")
    if len(argv) < 4:
        print("This script downloads audio files and transcripts for all utterances in given")
        print("LaBB-CAT server.")
        print("usage: " + argv[0] + " transcript-format dir url [ username password ]")
        print(" where:")
        print("  transcript-format = the content-type for the transcripts e.g. text/praat-textgrid")
        print("  dir = the directory/folder text/wav files are to be saved")
        print("  url = the 'home' URL of the LaBB-CAT server")
        print("  username = (optional) the LaBB-CAT username")
        print("  password = (optional) the LaBB-CAT password")
    else:
        mimeType = argv[1]
        dir = argv[2]
        url = argv[3]
        username = None
        password = None
        if len(argv) > 5:
            username = argv[4]
            password = argv[5]
        print("Connecting to "+url+" ...")
        corpus = labbcat.LabbcatView(url, username, password)
        transcriptIds = corpus.getTranscriptIds()
        print("Download "+str(len(transcriptIds))+" transcripts")

        bar = progressbar.ProgressBar(len(transcriptIds)).start()
        
        for p, transcriptId in enumerate(transcriptIds):
            # get media
            try:
                corpus.formatTranscript(transcriptId, ["utterance"], mimeType, dir=dir)
                corpus.getMedia(transcriptId, "", "audio/wav", dir=dir)
                bar.update(p)
            except:                
                bar.update(p)
        
        bar.finish()
        print("Download complete.")

if __name__ == "__main__":
    main(sys.argv)
