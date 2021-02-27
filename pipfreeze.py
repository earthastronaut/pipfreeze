#!python
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


__version__ = '1.0.1'


def call_split(cmd):
    """Call command and return output lines."""
    return subprocess.check_output(cmd).decode("utf-8").rstrip().split("\n")


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

    if "egg=" in requirement_version:
        # parse `-e git+git@github.com:repo/package.git@master#egg=package-name`
        name = requirement_version.split("egg=")[-1]
    else:
        name, _, _ = requirement_version.partition("==")

    name = name_to_slug(name)
    info_lines = call_split(["pip", "show", name])
    data = {}
    for line in info_lines:
        key, _, value = line.partition(":")
        data[key] = value.strip()
    data["name"] = name
    data["requirement_version"] = requirement_version
    data["required_children"] = split_package_requires(data["Requires"])
    data["required_parents"] = split_package_requires(data["Required-by"])
    return data


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

    return {data["name"]: data for data in results}


def _formatted_requirements_recursive(requirements, recursive_kws=None, **kws):
    """Recursively format the requirements freeze, nesting dependencies by indenting"""

    indent_size = kws["indent_size"]
    add_info = kws["add_info"]

    recursive_kws = recursive_kws or {}
    names = recursive_kws.get("names")
    level = recursive_kws.get("level", 0)
    included = recursive_kws.get("included", set())

    if names is None:
        names = [
            key
            for key, data in requirements.items()
            if len(data["required_parents"]) == 0  # top level
        ]

    indent = level * indent_size * " "
    lines = []
    for name in sorted(names):
        comment = ""
        info_options = {
            "required_by": None,
            "included": None,
            "other": None,
        }

        if name in DEV_PKGS:
            info_options["other"] = "dev_pkg"
            comment = "# "
            data = {}
        else:
            data = requirements[name]
            if name in included:
                comment = "# "
                info_options["included"] = True
                info_options["required_by"] = ",".join(data["required_parents"])

        requirement_version = data.get("requirement_version", name)
        required_children = data.get("required_children", [])

        info_formatted = ""
        if add_info is not None and add_info != [""]:
            if isinstance(add_info, str):
                add_info = [add_info]
            if "all" in add_info:
                keys = info_options.keys()
            else:
                keys = list(add_info)
                missing = set(keys) - set(info_options.keys())
                if len(missing) > 0:
                    options = "all," + ",".join(info_options.keys())
                    raise KeyError(
                        "unknown keys in add_info: {} valid options are {}".format(
                            missing, options
                        )
                    )
            info_unformatted = {}
            for key in keys:
                value = info_options[key]
                if value is not None:
                    info_unformatted[key] = value
            if len(info_unformatted) > 0:
                info_formatted = "  # info=" + json.dumps(info_unformatted)

        lines.append(
            "{indent}{comment}{requirement_version}{info_formatted}".format(
                indent=indent,
                comment=comment,
                requirement_version=requirement_version,
                info_formatted=info_formatted,
            )
        )
        included.add(name)

        if len(required_children) > 0:
            children_included, children_lines = _formatted_requirements_recursive(
                requirements,
                recursive_kws=dict(
                    names=required_children,
                    level=level + 1,
                    included=included,
                ),
                **kws,
            )
            lines.extend(children_lines)
            included = included.union(children_included)

    return included, lines


def formatted_requirements(requirements, indent_size=4, add_info=None):
    """Format requirements into new nested format.

    Parameters:
        requirements: dict from get_requirements()
            key: str package name
            value: dict of package data.

    Returns:
        str: New joined lines.

    """
    _, lines = _formatted_requirements_recursive(
        requirements, indent_size=indent_size, add_info=add_info
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
    pargs = parser.parse_args()

    loglevel = pargs.loglevel or ("DEBUG" if pargs.verbose else "")
    if loglevel:
        logging.basicConfig(level=loglevel.upper())

    requirements = get_requirements(
        requirements_file=pargs.requirements_file,
        processes=pargs.processes,
    )
    content = formatted_requirements(
        requirements, indent_size=pargs.indent_size, add_info=pargs.add_info.split(",")
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
    reqs = get_requirements()
    content = formatted_requirements(reqs)
    print(content)
