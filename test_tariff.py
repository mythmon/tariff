from __future__ import unicode_literals

import tariff
from tariff import Import, FromImport


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
        assert not im1 < im2
        assert im2 < im1


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
