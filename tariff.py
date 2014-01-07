from __future__ import print_function, unicode_literals

import argparse
import re
from functools import total_ordering

import six


def main():
    args = parse_args()
    for f in args.files:
        with open(f) as to_check:
            print(list(import_clusters(to_check)))


def check_file(path):
    pass


def import_clusters(lines):
    """
    Yields import clusters from lines.

    An import cluster is defined as one more adjacent lines with an
    import statement.
    """
    line_iter = iter(lines)
    try:
        cluster = []
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
        pass


@total_ordering
class Import(object):

    def __init__(self, names):
        self.names = names

    @classmethod
    def from_stmt(cls, stmt):
        stmt = normalize(stmt)
        print(stmt)

        names = re.match(r'^import\s+(.+)$', stmt).group(1)
        names = re.split(r'\s*,\s*', names)
        return cls(names)

    def __eq__(self, other):
        return self.names == other.names

    def __lt__(self, other):
        if isinstance(other, Import):
            if isinstance(other, FromImport):
                return False
            else:
                return self.names < other.names
        else:
            return NotImplemented


@total_ordering
class FromImport(Import):

    def __init__(self, from_name, names):
        self.from_name = from_name
        self.names = names

    @classmethod
    def from_stmt(cls, stmt):
        stmt = normalize(stmt)
        print(stmt)

        match = re.match(r'^from\s+([^s]+)\s+import\s+(.*)$', stmt)
        from_name = match.group(1)
        names = re.split(r'\s*,\s*', match.group(2))
        return cls(from_name, names)

    def __eq__(self, other):
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
            return True
        else:
            return NotImplemented


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


def parse_args():
    parser = argparse.ArgumentParser(description='Sort through your imports.')
    parser.add_argument('files', type=six.text_type, nargs='+')
    return parser.parse_args()


if __name__ == '__main__':
    main()
