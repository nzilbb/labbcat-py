#!/usr/bin/python3 
# Script that extracts utterance audio and transcript data from LaBB-CAT.
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
    
    print("Download utterances...");
    if len(argv) < 3:
        print("This script downloads audio files and trnascript for all utterances in given,")
        print("LaBB-CAT server.")
        print("usage: " + argv[0] + " dir url [ username password ]")
        print(" where:")
        print("  dir = the directory/folder text/wav files are to be saved")
        print("  url = the 'home' URL of the LaBB-CAT server")
        print("  username = (optional) the LaBB-CAT username")
        print("  password = (optional) the LaBB-CAT password")
    else:
        dir = argv[1]
        url = argv[2]
        username = None
        password = None
        if len(argv) > 4:
            username = argv[3]
            password = argv[4]
        print("Connecting to "+url+" ...")
        corpus = labbcat.LabbcatView(url, username, password)
        participantIds = corpus.getParticipantIds()
        print("Download utterances for "+str(len(participantIds))+" participants")

        bar = progressbar.ProgressBar(len(participantIds)).start()
        
        for p, participantId in enumerate(participantIds):
            # get all main-participant utterances by this participant
            taskId = corpus.allUtterances(participantId)
            utterances = corpus.getMatches(taskId)
            if len(utterances) > 0:
                # get text file for each utterance
                corpus.getFragments(
                    transcriptIds=[u['Transcript'] for u in utterances],
                    startOffsets=[u['Line'] for u in utterances],
                    endOffsets=[u['LineEnd'] for u in utterances],
                    dir=dir,
                    prefixNames=False,
                    layerIds=["word"],
                    mimeType="text/plain")
                # get audio file for each utterance
                corpus.getSoundFragments(
                    transcriptIds=[u['Transcript'] for u in utterances],
                    startOffsets=[u['Line'] for u in utterances],
                    endOffsets=[u['LineEnd'] for u in utterances],
                    dir=dir,
                    prefixNames=False)
                
            bar.update(p)
        
        bar.finish()
        print("Download complete.")

if __name__ == "__main__":
    main(sys.argv)
