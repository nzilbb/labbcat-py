#!/usr/bin/python3 
# Script that extracts given subcorpus transcripts from LaBB-CAT, to a given format.
#
# Author: Robert Fromont
# Date: May 2023
# Dependencies:
#  - nzilbb-labbcat - run the following shell command: `pip install nzilbb-labbcat`
#  - progressbar - run the following shell command: `pip install progressbar`

import labbcat
import progressbar
import sys

def main(argv):
    
    print("Download media and transcripts...")
    if len(argv) < 7:
        print("This script given subcorpus transcripts from LaBB-CAT server, to a given format")
        print("usage: " + argv[0] + " corpus format dir url username password [start-at]")
        print(" where:")
        print("  corpus = the (sub)corpus of the desired transcripts (listed on the 'corpora' page)")
        print("  format = the content-type for the transcripts e.g. text/praat-textgrid")
        print("  dir = the directory/folder text/wav files are to be saved")
        print("  url = the 'home' URL of the LaBB-CAT server")
        print("  username = the LaBB-CAT username")
        print("  password = the LaBB-CAT password")
        print("  start-at = (optional) the first transcript to download (for resuming a previous download)")
    else:
        subcorpus = argv[1]
        mimeType = argv[2]
        dir = argv[3]
        url = argv[4]
        username = argv[5]
        password = argv[6]
        firstTranscript = None
        if len(argv) > 7:
            firstTranscript = argv[7]
        print("Connecting to "+url+" ...")
        corpus = labbcat.LabbcatView(url, username, password)
        print("Listing transcript IDs in "+subcorpus+" ...")
        transcriptIds = corpus.getTranscriptIdsInCorpus(subcorpus)
        if firstTranscript is not None:
            try:
                startIndex = transcriptIds.index(firstTranscript)
                transcriptIds = transcriptIds[startIndex:]
                print("Download "+str(len(transcriptIds))+" transcripts from "+subcorpus+" starting from "+firstTranscript)
            except:
                print("'"+firstTranscript+"' is not in " + subcorpus)
                exit(0)
        else:
            print("Download "+str(len(transcriptIds))+" transcripts from "+subcorpus)

        bar = progressbar.ProgressBar(len(transcriptIds)).start()
        
        for p, transcriptId in enumerate(transcriptIds):
            try:
                corpus.formatTranscript(transcriptId, ["utterance"], mimeType, dir=dir)
                bar.update(p)
            except KeyboardInterrupt:
                break
            except:                
                bar.update(p)
        
        bar.finish()
        print("Download complete.")

if __name__ == "__main__":
    main(sys.argv)
