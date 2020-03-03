# nzilbb-labbcat

Client library for communicating with LaBB-CAT servers using Python.

## Documentation

Detailed documentation is available [here](https://nzilbb.github.io/labbcat-py/)

# Basic usage

The following example shows how to upload a transcript.

For batch uploading and other example code, see the *examples* subdirectory.

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
store.newTranscript("test/labbcat-py.test.txt", None, None, transcript_type, corpus_id, "test")

```

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