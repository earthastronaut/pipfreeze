# Pip Freeze

Tool to produce better formatted pip freeze.

Instead of a flat list of requirements, this indents requirements which are dependencies and those that are primary installs. Dependencies shared by multiple packages are commented out. 

This format can be re-read by the typical `pip install -r requirements.txt` and requires not adjustment to other code. 

## Installation

`pip install pipfreeze`

## Basic Usage

`pipfreeze > requirements.txt`

## Motivation

Typical `pip freeze` flattens all requirements, regardless of the dependency structure. 

``` bash
cycler==0.10.0
kiwisolver==1.3.1
matplotlib==3.3.4
numpy==1.20.1
pandas==1.2.2
Pillow==8.1.0
pyparsing==2.4.7
python-dateutil==2.8.1
pytz==2021.1
six==1.15.0
```

This `pipfreeze` command produces output that is valid requirements.txt but is nested

``` bash
matplotlib==3.3.4
    cycler==0.10.0
        six==1.15.0
    kiwisolver==1.3.1
    numpy==1.20.1
    Pillow==8.1.0
    pyparsing==2.4.7
    python-dateutil==2.8.1
        # six==1.15.0
pandas==1.2.2
    # numpy==1.20.1
    # python-dateutil==2.8.1
        # six==1.15.0
    pytz==2021.1
```

## Contributing

Local development is controlled through docker. `docker-compose.yml` contains
different python environment containers to test this code out in.

`make test` will run the docker tests.

Makefile contains commands for development.
