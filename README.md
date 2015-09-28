# git-tools

Scripts to help with releasing a new package.

## Authors

Usage:

```
$ python generate_authors.py --repo /path/to/code/repository
```

* **--repo** is the path to the directory on disk where the code is checked out.

## Changelog

Usage:

```
$ python generate_changelog.py --repo /path/to/code/repository --from v1.0.0
```

* **--from** is the name of the tag to use as a starting point (ending point is HEAD).
