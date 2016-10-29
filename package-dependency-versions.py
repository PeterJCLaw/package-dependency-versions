#!/usr/bin/env python

"""
Find the installed versions of a package and all of its dependencies.
"""

from __future__ import print_function

import argparse
from collections import namedtuple
import itertools
import subprocess

PackageInfo = namedtuple(
    'PackageInfo',
    ('name', 'version', 'status', 'dependencies'),
)


def parse_dpkg_depends(depends):
    if not depends.strip():
        return []

    dependencies = []

    for name_version in depends.split(','):
        name = name_version.strip().split(None, 1)[0]
        dependencies.append(name)

    return dependencies


def get_infos(*package_names):
    cmd = (
        'dpkg-query',
        '--show',
        r'--showformat=${Package}%${Version}%${db%Status-Status}%${Depends}\n',
    ) + package_names
    output = subprocess.check_output(cmd)

    package_infos = {}
    for line in output.splitlines():
        name, version, status, depends = line.split('%')

        dependencies = parse_dpkg_depends(depends)

        package_info = PackageInfo(name, version, status, dependencies)
        package_infos[name] = package_info

    return package_infos


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'package',
        help="The package to show the installed dependency versions for.",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    missing = packages = set([args.package])

    package_infos = {}

    while missing:
        infos = get_infos(*missing)

        packages |= set(itertools.chain.from_iterable(
            info.dependencies for info in infos.values(),
        ))

        package_infos.update(infos)

        missing = packages - set(package_infos.keys())

    maxlen = max(len(info.name) for info in package_infos.values())

    for name, package_info in sorted(package_infos.items()):
        print("%s %s" % (name.ljust(maxlen), package_info.version))


if __name__ == '__main__':
    main()
