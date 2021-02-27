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
astroid==2.4.2
certifi==2020.12.5
chardet==4.0.0
idna==2.10
isort==5.5.3
lazy-object-proxy==1.4.3
mccabe==0.6.1
pylint==2.6.0
requests==2.25.1
six==1.15.0
toml==0.10.1
urllib3==1.26.3
wrapt==1.12.1
```

This `pipfreeze` command produces output that is valid requirements.txt but is nested

``` bash
pylint==2.6.0
    astroid==2.4.2
        # latest_version=1.5.2 wheel
        lazy-object-proxy==1.4.3
        six==1.15.0
        wrapt==1.12.1
    # latest_version=5.7.0 wheel
    isort==5.5.3
    mccabe==0.6.1
    # latest_version=0.10.2 wheel
    toml==0.10.1
requests==2.25.1
    certifi==2020.12.5
    chardet==4.0.0
    # latest_version=3.1 wheel
    idna==2.10
    urllib3==1.26.3
```

## Contributing

Local development is controlled through docker. `docker-compose.yml` contains
different python environment containers to test this code out in.

`make test` will run the docker tests.

Makefile contains commands for development.
