# 0.5.0

- New LabbcatAdmin function
  + *generateLayer*
- New LabbcatEdit functions
  + *generateLayerUtterances*
  + *updateFragment*

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

