# -*- coding: utf-8
import os
import json
import requests
from optparse import OptionParser
from subprocess import Popen, PIPE
from pylru import lrudecorator


class Commit(object):

    href = None
    author = None
    email = None
    comment = None
    parents = None

    def __init__(self, href, author, email, comment, parents=None):
        self.href = href
        self.author = author
        self.email = email
        self.comment = comment
        self.parents = parents

    def is_merge(self):
        return len(self.parents) > 1

    def __str__(self):
        return "".format('{0}:\n{1}\n{2}\n{3}\nParents:\n{4}',
                         self.href,
                         self.author,
                         self.email,
                         self.comment,
                         self.parents)


class CommitList(object):

    commits = []

    def add(self, line):
        elements = CommitList.parse_log_command(line)
        commit = Commit(*elements)
        self.commits.append(commit)

    @staticmethod
    def parse_log_command(line):
        line = line.strip()
        refs, details = line.rsplit('|', 1)
        href, parent_hrefs = refs.split(',', 1)
        parents = parent_hrefs.split()
        name, email, comment = details.split(',', 2)
        return href, name, email, comment, parents

    @staticmethod
    def create_log_command(from_tag):
        return [
            'git',
            'log',
            "--pretty=format:%h,%p|%aN,%aE,%s",
            from_tag + '..'
        ]


def read_commits(repo_path, from_tag):
    """
    Get all commits starting from specified tag
    :param repo_path: string directory name
    :param from_tag: string tag to start from
    :return: tuples (name, email, comment)
    """

    commit_list = CommitList()

    child = Popen(
        CommitList.create_log_command(from_tag),
        cwd=os.path.expanduser(repo_path),
        stdout=PIPE)

    for line in child.stdout:
        if line:
            commit_list.add(line)

    return commit_list


@lrudecorator(300)
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
        print "--- ERROR: no author URL retrieved for '{0}' ---".format(
            response.url)
        return name


def generate_changelog(commit_list, filetype='rst'):
    """
    Retrieve github authors and generate changelog entries:

    * Fixed blah blah blah. Thanks: `<Author Name>`_.

    In the end, spit out list of authors:

    .. _`Author Name`: http://url

    :param commit_list: CommitList
    :return: string
    """

    authors = {}

    for commit in commit_list.commits:
        if commit.email not in authors:
            authors[commit.email] = {
                'name': commit.author,
                'profile': retrieve_author_url(commit.author)
            }

        # Make sure comment has a dot. And only one dot.
        comment = commit.comment.strip('.')
        comment += '.'

        prefix = '' if commit.is_merge() else '*'
        if filetype == 'rst':
            print "{2} {0} (Thanks: `{1}`_).".format(
                comment,
                commit.author,
                prefix)
        else:
            print "{2} {0} (Thanks: [{1}]).".format(
                comment,
                commit.author,
                prefix)

    print ''
    for k in sorted(authors.keys()):
        if filetype == 'rst':
            print ".. _`{0}`: {1}".format(authors[k]['name'], authors[k]['profile'])
        else:
            print '[{0}]: {1}'.format(authors[k]['name'], authors[k]['profile'])


def main():
    parser = OptionParser()
    parser.add_option("-r", "--repo", dest="repo", default='.', help="Repository location")
    parser.add_option("-f", "--filetype", dest="filetype", default='rst',
                      help="Filetype for output. rst or md")
    parser.add_option("-s", "--start", dest="start",
                      help="Tag to start reading entries from.")
    opts, args = parser.parse_args()
    generate_changelog(read_commits(opts.repo, opts.start), filetype=opts.filetype)


if __name__ == '__main__':
    main()
