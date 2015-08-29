# -*- coding: utf-8
import os
from optparse import OptionParser
from subprocess import Popen, PIPE


def generate_authors(repo_path):
    """
    Generate list of authors using 'git shortlog -n -s'
    :param repo_path: string path to directory
    :return: None. Prints out the list.
    """
    child = Popen(
        ['git', 'shortlog', '-n', '-s'],
        cwd=os.path.expanduser(repo_path),
        stdout=PIPE)

    for line in child.stdout:
        if line:
            line = line.strip()
            commits, name = line.split(None, 1)
            print "* {0}".format(name)


def main():
    parser = OptionParser()
    parser.add_option("-r", "--repo", dest="repo", help="Repository location")
    opts, args = parser.parse_args()
    generate_authors(opts.repo)


if __name__ == '__main__':
    main()
