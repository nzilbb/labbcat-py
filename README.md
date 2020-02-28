# nzilbb-labbcat

Client library for communicating with LaBB-CAT servers using Python.

## Documentation

Detailed documentation is available [here](https://nzilbb.github.io/labbcat-py/)

# Usage

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