# 0.11.1

- Add support for servers configured with FORM user auth

# 0.11.0

- New LabbcatView functions for accessing files of annotations with a MIME type (e.g. images)
  + *getMatchingAnnotationData*
  + *getFragmentAnnotationData*

# 0.10.0

- New LabbcatEdit functions for new upload API (LaBB-CAT v 20250430.1502)
  + *transcriptUpload*
  + *transcriptUploadParameters*
  + *transcriptUploadDelete*
- LabbcatEdit function implementation changes
  + *newTranscript* and *updateTranscript* use new API (above) by default.

# 0.9.1

- Fix LabbcatView function
  + *processWithPraat*/*processWithPraatAsync* - return results even when some offsets are missing

# 0.9.0

- New LabbcatView function
  + *processWithPraat*  and *processWithPraatAsync* - Process a set of intervals with Praat
    for extraction of acoustic measures.
- New labbcat functions for generating praat script snippets for processWithPraat...
  + *praatScriptFormants*
  + *praatScriptFastTrack*
  + *praatScriptCentreOfGravity*
  + *praatScriptIntensity*
  + *praatScriptPitch*
- Changed LabbcatView function
  + *getMatchAnnnotations* - now has 'offsetTheshold' parameter to allow retrieval of
    start/end times, and returns a 1D array (instead of 2D) if annotationsPerLayer == 1
    and only one layer is specified in layerIds

# 0.8.0

- New LabbcatEdit functions
  + *saveMedia* - saves the given media for the given transcript.
  + *saveEpisodeDocument* - adds the given document to the given transcript's episode documents.
  + *deleteMedia* - deletes media or episode document files.
- Changed LabbcatEdit function
  + GraphStore.newTranscript: rename mediaSuffix paramater as trackSuffix.

# 0.7.3

- New LabbcatEdit function
  + *saveParticipant* - add or update a participant record
- New LabbcatView function
  + *versionInfo* - gets version information of all components of LaBB-CAT
- Changed LabbcatView function
  + *getTranscriptAttributes* - now accepts a query expression for identifying transcripts, and an optional CSV file name to use
- New labbcat functions for generating query expressions...
  + *expressionFromAttributeValue* - ... from a single-value transcript/participant attribute name and possible values
  + *expressionFromAttributeValues* - ... from a multi-value transcript/participant attribute name and possible values
  + *expressionFromIds* - ... from a list of transcript/participant IDs
  + *expressionFromTranscriptTypes* - ... from a list of transcript types
  + *expressionFromCorpora* - ... from a list of corpora

Requires LaBB-CAT version 20230224.1731

# 0.7.2

- Changed LabbcatView functions
  + *countAnnotations* - new maxOrdinal parameter
  + *getAnnotations* - new maxOrdinal parameter
  + *updateTranscript* - new suppressGeneration parameter

Requires LaBB-CAT version 20230202.1600

# 0.7.1

- New LabbcatView function
  + *formatTranscript* - export a transcript in a given format

# 0.7.0

- New LabbcatView functions
  + *getDictionaries* - list the dictionaries available.
  + *getDictionaryEntries* - lookup entries in a dictionary.
- New LabbcatEdit functions
  + *getAnnotatorDescriptor* - gets annotator information.
  + *annotatorExt* - retrieve annotator's "ext" web-app resource.
  + *addLayerDictionaryEntry* - adds an entry to a layer dictionary.
  + *removeLayerDictionaryEntry* - removes an entry from a layer dictionary.
  + *addDictionaryEntry* - adds an entry to a dictionary.
  + *removeDictionaryEntry* - removes an entry from a dictionary.
- New LabbcatAdmin functions
  + *loadLexicon* - upload a flat lexicon file for lexical tagging.
  + *deleteLexicon* - delete a previously loaded lexicon.

Requires LaBB-CAT version 20220401.1858

# 0.6.0

- Changed LabbcatView function
  + *getMedia* - now downloads the media to a file instead of just returning the URL
- New LabbcatView functions
  + *getMediaUrl* - returns the URL of the given media, as *getMedia* used to do.
  + *getFragmentsAsync* - does what *getFragments* does, but asychronously by starting a task.
  + *taskResults* - downloads the results file(s) of a given task.

Requires LaBB-CAT version 20220307.1136

# 0.5.0

- New LabbcatAdmin function
  + *generateLayer*
- New LabbcatEdit functions
  + *generateLayerUtterances*
  + *updateFragment*
- New parameters for LabbcatAdmin.newLayer, to support creation of automated annotation layers:
  + *annotatorId*
  + *annotatorTaskParameters*
- New parameter for LabbcatView.getFragments and LabbcatView.getSoundFragments:
  + *prefixNames* - to prefix (or not) file names with serial

Requires LaBB-CAT version 20220302.1628

# 0.4.0

- New LabbcatAdmin CRUD operations for
  + users (including *setPassword*)
  + layers (*newLayer*/*deleteLayer*)
- New LabbcatView function
  + *allUtterances*

# 0.3.0

- New LabbcatAdmin CRUD operations for
  + corpora
  + projects
  + roles
  + permissions
  + system attributes (RU operations only)
  + tracks
  + *saveLayer* (CU operations)
- New LabbcatView function
  + *getSerializerDescriptors*
  + *getDeserializerDescriptors*
  + *getSystemAttribute*
  + *getUserInfo*
- Support for localization of server messages

# 0.2.2

Add support for calling getMatches() with a pattern instead of an already-started thread ID.

# 0.2.1

Refactored to remove confusing terminology and use class names that reflect LaBB-CAT user
authorization level.

# 0.2.0

- support for LaBB-CAT version 20200608.1507 API
- Labbcat.getTranscriptAttributes
- Labbcat.getParticipantAttributes

# 0.1.0

Provides basic access to LaBB-CAT server functionality, including query of corpora,
layers, participants and transcripts, and transcript uploading and deletion.

