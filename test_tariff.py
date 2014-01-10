from __future__ import unicode_literals

import tariff
from tariff import FromImport, Import


def test_import_clusters():
    data = """
        import foo
        import bar

        from baz import qux

        import wat
        from huh import lol
    """
    lines = data.split('\n')
    clusters = list(tariff.import_clusters(lines))
    assert clusters == [
        [Import(['foo']), Import(['bar'])],
        [FromImport('baz', ['qux'])],
        [Import(['wat']), FromImport('huh', ['lol'])]
    ]


def test_import_clusters_one_line():
    lines = ['import foo']
    cluster = list(tariff.import_clusters(lines))
    assert cluster == [[Import(['foo'])]]


class TestImport(object):

    def test_from_stmt_single(self):
        im = Import.from_stmt('import foo')
        assert im.names == ['foo']

    def test_from_stmt_multi(self):
        im = Import.from_stmt('import foo, bar, baz')
        assert im.names == ['foo', 'bar', 'baz']

    def test_from_stmt_parens(self):
        im = Import.from_stmt('import (foo, bar, baz)')
        assert im.names == ['foo', 'bar', 'baz']

    def test_from_stmt_newlines_escapes(self):
        im = Import.from_stmt('import foo, \\\n bar')
        assert im.names == ['foo', 'bar']

    def test_dunder_equal_yes(self):
        im1 = Import(['foo', 'bar'])
        im2 = Import(['foo', 'bar'])
        assert im1 == im2

    def test_dunder_equal_no(self):
        im1 = Import(['foo', 'bar'])
        im2 = Import(['bar', 'foo'])
        assert im1 != im2

    def test_dunder_lt_yes(self):
        im1 = Import(['a'])
        im2 = Import(['b'])
        assert im1 < im2
        im1 = Import(['a', 'b'])
        im2 = Import(['a', 'c'])
        assert im1 < im2

    def test_dunder_lt_no(self):
        im1 = Import(['a'])
        im2 = Import(['a'])
        assert not im1 < im2
        im1 = Import(['a', 'b'])
        im2 = Import(['a', 'a'])
        assert not im1 < im2

    def test_total_ordering(self):
        """Test that total_ordering correctly implemented all the cases."""
        im1 = Import(['a'])
        im2 = Import(['a'])
        im3 = Import(['b'])
        assert im1 == im1
        assert im1 >= im1
        assert im1 <= im1
        assert im1 == im2
        assert im1 <= im2
        assert im1 < im3
        assert im1 <= im3
        assert im2 == im1
        assert im2 >= im1
        assert im2 == im2
        assert im2 != im3

    def test_is_sorted(self):
        assert Import(['a']).is_sorted()
        assert Import(['a', 'b']).is_sorted()
        assert Import(['a', 'b', 'c']).is_sorted()
        assert not Import(['b', 'a']).is_sorted()
        assert not Import(['b', 'a', 'c']).is_sorted()

    def test_dunder_str(self):
        assert str(Import(['a', 'b'])) == 'import a, b'


class TestFromImport(object):

    def test_from_stmt_single(self):
        im = FromImport.from_stmt('from foo import bar')
        assert im.from_name == 'foo'
        assert im.names == ['bar']

    def test_from_stmt_multi(self):
        im = FromImport.from_stmt('from foo import bar, baz, qux')
        assert im.from_name == 'foo'
        assert im.names == ['bar', 'baz', 'qux']

    def test_from_stmt_parens(self):
        im = FromImport.from_stmt('from foo import (bar, baz, qux)')
        assert im.from_name == 'foo'
        assert im.names == ['bar', 'baz', 'qux']

    def test_from_stmt_newlines_escapes(self):
        im = FromImport.from_stmt('from foo import bar, \\\n baz')
        assert im.from_name == 'foo'
        assert im.names == ['bar', 'baz']

    def test_dunder_equal_yes(self):
        im1 = FromImport('baz', ['foo', 'bar'])
        im2 = FromImport('baz', ['foo', 'bar'])
        assert im1 == im2

    def test_dunder_equal_no(self):
        im1 = FromImport('baz', ['foo', 'bar'])
        im2 = FromImport('baz', ['bar', 'foo'])
        assert im1 != im2
        im1 = FromImport('baz', ['foo', 'bar'])
        im2 = FromImport('qux', ['foo', 'bar'])
        assert im1 != im2

    def test_dunder_lt_yes(self):
        im1 = FromImport('a', ['a'])
        im2 = FromImport('a', ['b'])
        assert im1 < im2
        im1 = FromImport('a', ['a', 'b'])
        im2 = FromImport('a', ['a', 'c'])
        assert im1 < im2
        im1 = FromImport('a', ['a'])
        im2 = FromImport('b', ['a'])
        assert im1 < im2
        im1 = FromImport('a', ['b'])
        im2 = FromImport('b', ['a'])
        assert im1 < im2

    def test_dunder_lt_no(self):
        im1 = FromImport('a', ['a'])
        im2 = FromImport('a', ['a'])
        assert not im1 < im2
        im1 = FromImport('a', ['a', 'b'])
        im2 = FromImport('a', ['a', 'a'])
        assert not im1 < im2
        im1 = FromImport('a', ['a', 'a'])
        im2 = FromImport('a', ['a', 'a'])
        assert not im1 < im2
        im1 = FromImport('b', ['a', 'a'])
        im2 = FromImport('a', ['a', 'a'])
        assert not im1 < im2
        im1 = FromImport('b', ['a', 'a'])
        im2 = FromImport('a', ['b', 'a'])
        assert not im1 < im2

    def test_dunder_lt_Import(self):
        """Imports are always greater than FromImports."""
        im1 = Import(['a'])
        im2 = FromImport('a', ['a'])
        assert im1 < im2
        assert not im2 < im1

    def test_dunder_str(self):
        assert str(FromImport('a', ['b', 'c'])) == 'from a import b, c'

    def test_is_sorted(self):
        assert FromImport('foo', ['a']).is_sorted()
        assert FromImport('foo', ['a', 'b']).is_sorted()
        assert FromImport('foo', ['a', 'b', 'c']).is_sorted()
        assert not FromImport('foo', ['b', 'a']).is_sorted()
        assert not FromImport('foo', ['b', 'a', 'c']).is_sorted()


def test_import_normalize():
    def _t(inp, expected):
        assert expected == tariff.normalize(inp)
    cases = [
        ('import foo', 'import foo'),
        ('import foo, bar', 'import foo, bar'),
        ('import (foo, bar)', 'import foo, bar'),
        ('import (\nfoo,\nbar)', 'import foo, bar'),
        ('import foo, \\\n bar', 'import foo, bar'),
        (' \t import   foo \n ', 'import foo'),

        ('from bar import foo', 'from bar import foo'),
        ('from bar import foo, bar', 'from bar import foo, bar'),
        ('from bar import (foo, bar)', 'from bar import foo, bar'),
        ('from bar import (\nfoo,\nbar)', 'from bar import foo, bar'),
        ('from bar import \\\n foo, bar', 'from bar import foo, bar'),
        (' \t from bar   import foo \n ', 'from bar import foo'),
    ]
    for inp, expected in cases:
        yield _t, inp, expected


def test_check_cluster():
    def _t(cluster, err_count):
        errs = list(tariff.check_cluster(cluster))
        assert len(errs) == err_count

    data = """
        import a
        import b

        import a
        from a import b, c

        import b
        import a

        from a import b
        import c

        import a
        from a import c, b
    """
    lines = data.split('\n')
    clusters = list(tariff.import_clusters(lines))

    yield _t, clusters[0], 0
    yield _t, clusters[1], 0
    yield _t, clusters[2], 1
    yield _t, clusters[3], 1
    yield _t, clusters[4], 1


sources = [
    """
    import a
    import b

    import c
    from d import e, f
    from g import h, i, j

    a.foo()
    b.bar()
    c.baz(e, f)
    h(i, j)
    """,

    """
    import b
    from d import e, f
    import c

    from g import j, h, i
    import a
    """,

    'from a import c, b',
]


def test_check_file():
    def _t(source, expected):
        source = source.splitlines()
        errs = list(tariff.check_file(source))
        assert len(errs) == expected

    yield _t, sources[0], 0
    yield _t, sources[1], 3
    yield _t, sources[2], 1


def test_lag_zip_no_first():
    li = [0, 1, 2, 3, 4]
    it = tariff.lag_zip(li)
    assert next(it) == (0, 1)
    assert next(it) == (1, 2)
    assert next(it) == (2, 3)
    assert next(it) == (3, 4)
    try:
        next(it)
        assert False
    except StopIteration:
        assert True
    except:
        assert False


def test_lag_zip_first():
    li = [0, 1, 2, 3, 4]
    it = tariff.lag_zip(li, True)
    assert next(it) == (None, 0)
    assert next(it) == (0, 1)
    assert next(it) == (1, 2)
    assert next(it) == (2, 3)
    assert next(it) == (3, 4)
    try:
        next(it)
        assert False
    except StopIteration:
        assert True
    except:
        assert False
