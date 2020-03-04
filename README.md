# nzilbb-labbcat

Client library for communicating with [LaBB-CAT](https://labbcat.canterbury.ac.nz/)
servers using Python.

LaBB-CAT is a web-based linguistic annotation store that stores audio or video
recordings, text transcripts, and other annotations.

Annotations of various types can be automatically generated or manually added.

LaBB-CAT servers are usually password-protected linguistic corpora, and can be
accessed manually via a web browser, or programmatically using a client library like
this one.

## Documentation

Detailed documentation is available [here](https://nzilbb.github.io/labbcat-py/)

# Basic usage

<em>nzilbb.labbcat</em> is available in the Python Package Index
[here](https://pypi.org/project/nzilbb-labbcat/)

To install the module:

```
pip install nzilbb-labbcat
```

The following example shows how to:
1. upload a transcript to LaBB-CAT,
2. wait for the automatic annotation tasks to finish,
3. extract the annotation labels, and
4. delete the transcript from LaBB-CAT.

```python
import labbcat

# Connect to the LaBB-CAT annotation store
store = labbcat.Labbcat("http://localhost:8080/labbcat", "labbcat", "labbcat")

# List the corpora on the server
corpora = store.getCorpusIds()

# List the transcript types
transcript_type_layer = store.getLayer("transcript_type")
transcript_types = transcript_type_layer["validLabels"]

# Upload a transcript
corpus_id = corpora[0]
transcript_type = next(iter(transcript_types))
taskId = store.newTranscript(
    "test/labbcat-py.test.txt", None, None, transcript_type, corpus_id, "test")

# wait for the annotation generation to finish
store.waitForTask(taskId)
store.releaseTask(taskId)

# get the "POS" layer annotations
annotations = store.getAnnotations("labbcat-py.test.txt", "pos")
labels = list(map(lambda annotation: annotation["label"], annotations))

# delete tha transcript from the corpus
store.deleteTranscript("labbcat-py.test.txt")
```

For batch uploading and other example code, see the *examples* subdirectory.

# Developers

To build, test, release, and document the module, the following prerequisites are required:
 - `pip install twine`
 - `pip install pathlib`
 - `apt install python3-sphinx`

## Unit tests

```
python -m unittest
```

## Documentation generation

```
cd docs
make clean
make
```

## Publishing

```
python setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/*
```