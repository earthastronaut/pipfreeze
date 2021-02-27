#!/usr/bin/env python
""" Better pip freeze which is valid with requirements.txt
"""
import sys
import argparse
import json
import logging
import subprocess
import pip
import multiprocessing


DEV_PKGS = {"argparse", "pip", "setuptools", "distribute", "wheel"}
try:
    from pip._internal.commands.freeze import DEV_PKGS as DEV_PKGS_FREEZE
    DEV_PKGS = DEV_PKGS.union(DEV_PKGS_FREEZE)
except ImportError:
    pass


logger = logging.getLogger(__name__)


__version__ = "2.0.2"


def call_split(cmd):
    """Call command and return output lines."""
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    process.wait()
    return process.stdout.read().decode("utf-8").rstrip().split("\n")


def name_to_slug(name):
    """ Transform the name to standard format """
    return name.strip().lower()


def split_package_requires(requires):
    """Split the packages: "pandas, traits" from `Requires: pandas, traits`
    into a list of names.
    """
    return [
        name_to_slug(name) for name in requires.split(",") if len(name.rstrip()) > 0
    ]


class Requirement(dict):
    """ Data for requirements"""

    def __init__(self, name, requirement_version, required_children=None, required_parents=None, **kws):
        self.name = name
        self.requirement_version = requirement_version
        self.required_children = required_children or []
        self.required_parents = required_parents or []
        super(self.__class__, self).__init__(
            name=self.name,
            requirement_version=self.requirement_version,
            required_children=self.required_children,
            required_parents=self.required_parents,
            **kws
        )
    
    def __hash__(self):
        return hash(self.name)


def get_package_data(requirement_version):
    """Get data on package.

    Parameters:
        requirement_version: pip freeze requirement version. e.g `requests==1.0.0`

    Returns:
        dict: Dictionary of data with some standard values
            required_children: list of package names this package requires.
            required_parents: list of package names which require this package.
    """
    logger.info("getting package info: %s", requirement_version)

    if " @ " in requirement_version:
        name =  requirement_version.split("@")[0]
    elif "egg=" in requirement_version:
        # parse `-e git+git@github.com:repo/package.git@master#egg=package-name`
        name = requirement_version.split("egg=")[-1]
    else:
        name, _, _ = requirement_version.partition("==")

    name = name_to_slug(name)
    info_lines = call_split(["pip", "show", name])
    data = {}
    for line in info_lines:
        if ':' not in line:
            continue
        key, _, value = line.partition(":")
        data[key] = value.strip()
    requires = data["Requires"]
    return Requirement(
        name=name,
        requirement_version=requirement_version,
        required_children=split_package_requires(requires),
        **data
    )

def add_parents(requirements_data):
    """ Get the parents of the requirements """
    graph_parents = {}
    for req in requirements_data:
        for children in req.required_children:
            graph_parents.setdefault(children, []).append(req.name)
    for data in requirements_data:
        data.required_parents = graph_parents.get(data.name, [])
    return requirements_data


def get_requirements(requirements_file=None, processes=None):
    """Get the requirements as dict of Requirements.

    Parameters:
        requirements_file:
            None: If none, then reads from `pip freeze`
            str: If string, then opens a filename

    Returns:
        dict: Requirements
            key: package name
            value: dict of package data
    """
    if requirements_file is None:
        requirements_lines = call_split(["pip", "freeze"])
    else:
        with open(requirements_file) as buffer:
            requirements_lines = buffer.readlines()

    if processes == 0 or processes == 1:
        results = list(map(get_package_data, requirements_lines))
    else:
        if processes == -1:
            processes = multiprocessing.cpu_count() * 4
        with multiprocessing.Pool(processes=processes) as pool:
            results = pool.map_async(
                get_package_data, requirements_lines, chunksize=5
            ).get()

    add_parents(results)
    return {req.name: req for req in results}


def get_formatted_info(info, add_info=None):
    """ Take the info data and turn into string.

    Parameters:
        info: dict of information
        add_info: Keys to use or None to not return any
    
    Return:
        str: formatted string to include in text

    """
    if add_info is None or add_info == [""]:
        return ""

    if isinstance(add_info, str):
        add_info = [add_info]
    if "all" in add_info:
        keys = info.keys()
    else:
        keys = list(add_info)
        missing = set(keys) - set(info.keys())
        if len(missing) > 0:
            options = "all," + ",".join(info.keys())
            raise KeyError(
                "unknown keys in add_info: {} valid options are {}".format(
                    missing, options
                )
            )
    info_unformatted = {}
    for key in keys:
        value = info[key]
        if value is not None:
            info_unformatted[key] = value
    if len(info_unformatted) > 0:
        info_formatted = "  # info=" + json.dumps(info_unformatted)
    return info_formatted


def _get_formatted_requirements_recursive(requirements, recursive_kws=None, **kws):
    """Recursively format the requirements freeze, nesting dependencies by indenting"""

    indent_size = kws["indent_size"]
    add_info = kws["add_info"]
    exclude = set(kws["exclude"] or [])

    recursive_kws = recursive_kws or {}
    names = recursive_kws.get("names")
    level = recursive_kws.get("level", 0)
    included = recursive_kws.get("included", set())

    if names is None:
        names = [
            key
            for key, req in requirements.items()
            if len(req.required_parents) == 0  # top level
        ]

    indent = level * indent_size * " "
    lines = []
    for name in sorted(names):
        comment = ""
        info = {
            "required_by": None,
            "included": None,
            "other": None,
        }

        if name in DEV_PKGS:
            info["other"] = "dev_pkg"
            comment = "# "
            req = Requirement(
                name=name,
                requirement_version=name,
            )
        elif name in exclude:
            continue
        else:
            req = requirements[name]
            if name in included:
                comment = "# "
                info["included"] = True
                info["required_by"] = ",".join(req.required_parents)

        lines.append(
            "{indent}{comment}{requirement_version}{info_formatted}".format(
                indent=indent,
                comment=comment,
                requirement_version=req.requirement_version,
                info_formatted=get_formatted_info(info, add_info=add_info),
            )
        )
        included.add(name)

        if len(req.required_children) > 0:
            children_included, children_lines = _get_formatted_requirements_recursive(
                requirements,
                recursive_kws=dict(
                    names=req.required_children,
                    level=level + 1,
                    included=included,
                ),
                **kws
            )
            lines.extend(children_lines)
            included = included.union(children_included)

    return included, lines


def formatted_requirements(requirements, indent_size=4, add_info=None, exclude=None):
    """Format requirements into new nested format.

    Parameters:
        requirements: dict from get_requirements()
            key: str package name
            value: dict of package data.

    Returns:
        str: New joined lines.

    """
    _, lines = _get_formatted_requirements_recursive(
        requirements, indent_size=indent_size, add_info=add_info, exclude=exclude,
    )
    return "\n".join(lines)


def cli():
    """Run as a CLI"""
    parser = argparse.ArgumentParser(description="Nested format for pip freeze")
    parser.add_argument(
        "-f",
        "--requirements-file",
        default=None,
        help=(
            "Optional. By default runs `pip freeze`. If provided, the uses this file "
            "as the base. Note: This still needs bo be run in the python env "
            "so that `pip show <package>` returns dependency data."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Optional. Location to write output to.",
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=-1,
        help=(
            "Number of processes. If -1 then runs will all available cores. "
            "If 0 or 1 then runs single threaded. Else runs with `processes` cores."
        ),
    )
    parser.add_argument(
        "--add-info",
        default="",
        help=(
            "List of info to add. By default non is added. Options:\n"
            "  all: Every key below\n"
            "  required_by: List of other parent packages\n"
            "  included: True if already included by another parent\n"
            "  other: Any other information\n"
        ),
    )
    parser.add_argument(
        "--exclude",
        default="",
        help="Exclude packages. Comma separated.",
    )    
    parser.add_argument(
        "--indent-size",
        type=int,
        default=4,
        help="Size of the indent.",
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        default=None,
        help="Log level: INFO, DEBUG, etc. None will not enable logging.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Shortcut for loglevel=DEBUG",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Display version",
    )    
    pargs = parser.parse_args()

    if pargs.version:
        sys.stdout.write(__version__)
        sys.stdout.write("\n")
        sys.exit(0)

    loglevel = pargs.loglevel or ("DEBUG" if pargs.verbose else "")
    if loglevel:
        logging.basicConfig(level=loglevel.upper())

    exclude = [
        name_to_slug(name) for name in pargs.exclude.split(",")
    ]

    requirements = get_requirements(
        requirements_file=pargs.requirements_file,
        processes=pargs.processes,
    )
    content = formatted_requirements(
        requirements,
        indent_size=pargs.indent_size,
        add_info=pargs.add_info.split(","),
        exclude=exclude,
    )
    if pargs.output is None:
        logger.info("---- pip freeze ----")
        for line in content.split("\n"):
            sys.stdout.write(line)
            sys.stdout.write("\n")
    else:
        logger.info("Writing to %s", pargs.output)
        with open(pargs.output, "w") as buffer:
            buffer.write(content)
            buffer.write("\n")


if __name__ == "__main__":
    reqs = get_requirements(processes=1)
    content = formatted_requirements(reqs)
    print(content)
