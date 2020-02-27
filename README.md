# nzilbb-labbcat

Client library for communicating with LaBB-CAT servers using Python.

# Usage

# Developers

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