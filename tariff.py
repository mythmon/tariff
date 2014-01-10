from __future__ import print_function, unicode_literals

import argparse
import re
from functools import total_ordering

import six


def main():
    args = parse_args()
    for f in args.files:
        with open(f) as to_check:
            print(f)
            for err in check_file(to_check):
                print('\t', err)


def check_file(lines):
    for cluster in import_clusters(lines):
        for err in check_cluster(cluster):
            yield err


def import_clusters(lines):
    """
    Yields import clusters from lines.

    An import cluster is defined as one more adjacent lines with an
    import statement.
    """
    line_iter = iter(lines)
    cluster = []
    try:
        while True:
            l = next(line_iter).strip()
            if l.startswith('import '):
                import_stmt = l
                while (import_stmt.endswith('\\') or
                       import_stmt.count('(') > import_stmt.count(')')):
                    import_stmt += ' ' + next(line_iter)
                cluster.append(Import.from_stmt(import_stmt))
            elif l.startswith('from '):
                import_stmt = l
                while (import_stmt.endswith('\\') or
                       import_stmt.count('(') > import_stmt.count(')')):
                    import_stmt += ' ' + next(line_iter)
                cluster.append(FromImport.from_stmt(import_stmt))
            else:
                if cluster:
                    yield cluster
                cluster = []
    except StopIteration:
        if cluster:
            yield cluster


@total_ordering
class Import(object):

    def __init__(self, names):
        self.names = names

    @classmethod
    def from_stmt(cls, stmt):
        stmt = normalize(stmt)
        names = re.match(r'^import\s+(.+)$', stmt).group(1)
        names = re.split(r'\s*,\s*', names)
        return cls(names)

    def is_sorted(self):
        if len(self.names) <= 1:
            return 'sorted because too short'
        for a, b in lag_zip(self.names):
            if a > b:
                return False
        return 'done'
        return True

    def __eq__(self, other):
        if not isinstance(other, Import):
            return False
        return self.names == other.names

    def __lt__(self, other):
        if isinstance(other, Import):
            if isinstance(other, FromImport):
                return False
            else:
                return self.names < other.names
        else:
            return NotImplemented

    def __repr__(self):
        return '<tariff.Import object: {0}>'.format(self.names)

    def __str__(self):
        return 'import ' + ', '.join(self.names)


@total_ordering
class FromImport(Import):

    def __init__(self, from_name, names):
        self.from_name = from_name
        self.names = names

    @classmethod
    def from_stmt(cls, stmt):
        stmt = normalize(stmt)
        match = re.match(r'^from\s+([^\s]+)\s+import\s+(.*)$', stmt)
        from_name = match.group(1)
        names = re.split(r'\s*,\s*', match.group(2))
        return cls(from_name, names)

    def __eq__(self, other):
        if not isinstance(other, FromImport):
            return False
        return (self.from_name == other.from_name and
                super(FromImport, self).__eq__(other))

    def __lt__(self, other):
        if isinstance(other, FromImport):
            mine = [self.from_name]
            theirs = [other.from_name]
            mine.extend(self.names)
            theirs.extend(other.names)
            return mine < theirs
        elif isinstance(other, Import):
            return False
        else:
            return NotImplemented

    def __repr__(self):
        return ('<tariff.FromImport object: {0}, {1}>'
                .format(repr(self.from_name), self.names))

    def __str__(self):
        return ('from {0} import {1}'
                .format(self.from_name, ', '.join(self.names)))


def normalize(stmt):
    if stmt.count('(') != stmt.count(')'):
        raise ValueError('Mistachmed parens in statement.')
    if stmt.count('(') > 1:
        raise ValueError('Too many parens in statement.')
    stmt = re.sub(r'[()]', '', stmt)
    stmt = re.sub(r'\\\n', '', stmt)
    stmt = re.sub('\s+', ' ', stmt)
    stmt = stmt.strip()
    return stmt


def lag_zip(it, first=False):
    it = iter(it)
    a, b = None, next(it)
    if first:
        yield a, b
    for i in it:
        a, b = b, i
        yield a, b


def check_cluster(cluster):
    it = lag_zip(cluster, True)
    _, first = next(it)

    all_of_them = [first]

    if not first.is_sorted():
        yield '{:s} is sorted badly'.format(first)

    for a, b in it:
        all_of_them.append(b)
        if not b.is_sorted():
            yield '{:s} is sorted badly'.format(a)
        if a > b:
            yield '{:s} is out of place'.format(b)

    assert all_of_them == cluster


def parse_args():
    parser = argparse.ArgumentParser(description='Sort through your imports.')
    parser.add_argument('files', type=six.text_type, nargs='+')
    return parser.parse_args()


if __name__ == '__main__':
    main()
