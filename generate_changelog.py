# -*- coding: utf-8
import os
import json
import requests
from optparse import OptionParser
from subprocess import Popen, PIPE


def read_commits(repo_path, from_tag):
    """
    Get all commits starting from specified tag
    :param repo_path: string directory name
    :param from_tag: string tag to start from
    :return: tuples (name, email, comment)
    """

    child = Popen(
        ['git', 'log', "--pretty=format:%aN,%aE,%s", from_tag + '..'],
        cwd=os.path.expanduser(repo_path),
        stdout=PIPE)

    results = []
    for line in child.stdout:
        if line:
            line = line.strip()
            name, email, comment = line.split(',', 2)
            results.append((name, email, comment))
    return results


def retrieve_author_url(name):
    """
    Search for github commiter profile by name.
    :param name: string
    :return: dict
    """
    response = requests.get('https://api.github.com/search/users', {'q': name})
    data = json.loads(response.text)
    if data.get('total_count', None) == 1:
        return data['items'][0]['html_url']
    else:
        print 'BOO', data
        return name


def generate_changelog(commits):
    """
    Retrieve github authors and generate changelog entries:

    * Fixed blah blah blah. Thanks: `<Author Name>`_.

    In the end, spit out list of authors:

    .. _`Author Name`: http://url

    :param commits: tuples
    :return: string
    """

    authors = {}

    for name, email, comment in commits:
        if email not in authors:
            authors[email] = {
                'name': name,
                'profile': retrieve_author_url(name)
            }

        # Make sure comment has a dot. And only one dot.
        comment = comment.strip('.')
        comment += '.'

        print "* {0} (Thanks: `{1}`_).".format(comment, name)

    print ''
    for k in sorted(authors.keys()):
        print ".. _`{0}`: {1}".format(authors[k]['name'], authors[k]['profile'])


def main():
    parser = OptionParser()
    parser.add_option("-r", "--repo", dest="repo", help="Repository location")
    parser.add_option("-s", "--start", dest="start",
                      help="Tag to start reading entries from.")
    opts, args = parser.parse_args()
    generate_changelog(read_commits(opts.repo, opts.start))


if __name__ == '__main__':
    main()
