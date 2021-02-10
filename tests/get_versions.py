#!/usr/bin/env python
import sys
import json
from distutils.version import StrictVersion
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

def get_versions(package_name):
    url = "https://pypi.python.org/pypi/%s/json" % (package_name,)
    with urlopen(url=url) as stream:
        data = json.load(stream)
    versions = list(data["releases"].keys())
    return sorted(versions, key=StrictVersion)

if __name__ == "__main__":
    for version in get_versions(sys.argv[1]):
        print(version)
