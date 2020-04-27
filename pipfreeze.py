#!python
import json
import sys
from collections import OrderedDict
from pip._internal.commands.list import ListCommand
from pip._internal.commands.freeze import DEV_PKGS
from pip._internal.operations.freeze import FrozenRequirement


__version__ = '1.0.0'


def pip_list_packages(*args):
    """ List of installed packages. 

    Returns package objects associated with `pip list [args]`

    Args:
        *args: Arguments passed to `pip list [args]`.

    Returns:
        List[DistPackage]: List of installed package objects.

    """

    class ListCommandPackages(ListCommand):

        def output_package_listing(self, packages, options):
            self.packages = OrderedDict()

            for pkg in self.iter_packages_latest_infos(packages, options):
                if pkg.key in self.packages:
                    raise ValueError(
                        'Key conflict, {} in {}'.format(pkg.key, self.packages)
                    )
                pkg._requires = set((r.key for r in pkg.requires()))
                self.packages[pkg.key] = pkg

            for pkg_required in self.packages.values():
                pkg_required._required_by = set()
                for pkg_requiring in self.packages.values():
                    if pkg_required.key in pkg_requiring._requires:
                        pkg_required._required_by.add(pkg_requiring.key)

    cmd = ListCommandPackages('_list', '', isolated=False)
    exitcode = cmd.main(list(args))
    if exitcode != 0:
        sys.exit(exitcode)
    return cmd.packages


def _recursive_requires_freeze(packages, key, frozen_packages, depth=0):
    """ Follow package dependencies and indent them """
    pkg = packages[key]
    freeze = FrozenRequirement.from_dist(pkg)

    indent_size = 4  # PEP8
    indent = ' ' * indent_size * depth

    if key in frozen_packages:
        # freeze.comments.append(
        #     '# required by={}'.format(tuple(pkg._required_by))
        # )
        indent += '# '
    else:
        frozen_packages.add(key)

    if pkg.latest_version != pkg.parsed_version:
        freeze.comments.append(
            '# latest_version={} {}'
            .format(pkg.latest_version, pkg.latest_filetype)
        )

    lines = [indent + l for l in str(freeze).rstrip().split('\n')]

    for require_key in pkg._requires:
        lines.extend(
            _recursive_requires_freeze(
                packages, require_key, frozen_packages, depth=depth+1
            )
        )
    return lines


def get_requirements_freeze(packages, skip=None):
    """ Pip freeze output string.

    Same output as `pip freeze` only with dependencies indented.

    Args:
        packages (List[DistPackage]): List of installed package objects.
        skip (List[Str]): List, tuple, or set of packages to skip.

    Returns:
        str: The full freeze text
    """
    skip = skip or DEV_PKGS

    frozen_packages = set()
    lines = []

    for key, pkg in packages.items():
        # skip if not root module
        if len(pkg._required_by) > 0:
            continue

        if key in skip:
            continue

        lines.extend(
            _recursive_requires_freeze(
                packages, key, frozen_packages, depth=0
            )
        )
    return '\n'.join(lines)


def main():
    packages = pip_list_packages()
    freeze = get_requirements_freeze(packages)
    print(freeze)


if __name__ == '__main__':
    main()
