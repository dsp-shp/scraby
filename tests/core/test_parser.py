from json import dumps
from dataclasses import dataclass, field
import typing as t
import pytest
from scraby.core.parser import dialect, exp, LoadPage, ParseError, TokenError


@dataclass
class ParseTest:
    """ Dataclass for parse tests 

    Compare list' dump of parsed expressions' dumps to predefined list' dump
    
    """
    id: str
    sql: str
    exp_dump: str
    exc_type: t.Optional[type[Exception]] = None

    def __post_init__(self):
        self.id = self.id


@pytest.mark.parametrize("case", [
    #  TODO: fix tag tests & move data to separate JSON file
    # ParseTest(
    #     # Test tags parsing
    #     "tags",
    #     "SELECT <div id=\"id_1\" class=\"class_1\"> FROM b",
    #     '[{"class": "Select", "args": {"expressions": [{"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "<div id=\\"id_1\\" class=\\"class_1\\">", "quoted": false}}}}], "from": {"class": "From", "args": {"this": {"class": "Table", "args": {"this": {"class": "Identifier", "args": {"this": "b", "quoted": false}}}}}}}}]',
    # ),
    # ParseTest(
    #     # Test tags parsing in confusing situations
    #     "tags_confuse",
    #     "SELECT <div id=\"id_1\" class=\"class_1\">, mod<div id, mod>div, c FROM b as d WHERE <span>>1",
    #     '[{"class": "Select", "args": {"expressions": [{"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "<div id=\\"id_1\\" class=\\"class_1\\">", "quoted": false}}}}, {"class": "Alias", "args": {"this": {"class": "LT", "args": {"this": {"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "mod", "quoted": false}}}}, "expression": {"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "div", "quoted": false}}}}}}, "alias": {"class": "Identifier", "args": {"this": "id", "quoted": false}}}}, {"class": "GT", "args": {"this": {"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "mod", "quoted": false}}}}, "expression": {"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "div", "quoted": false}}}}}}, {"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "c", "quoted": false}}}}], "from": {"class": "From", "args": {"this": {"class": "Table", "args": {"this": {"class": "Identifier", "args": {"this": "b", "quoted": false}}, "alias": {"class": "TableAlias", "args": {"this": {"class": "Identifier", "args": {"this": "d", "quoted": false}}}}}}}}, "where": {"class": "Where", "args": {"this": {"class": "GT", "args": {"this": {"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "<span>", "quoted": false}}}}, "expression": {"class": "Literal", "args": {"this": "1", "is_string": false}}}}}}}}]',
    # ),
    # ParseTest(
    #     # Test tags parsing with child & alias
    #     "tags_with_child_&_alias",
    #     "SELECT <div id=r\"id_1\" class=\"class_1\">.tag_1 as a FROM b",
    #     '[{"class": "Select", "args": {"expressions": [{"class": "Alias", "args": {"this": {"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "tag_1", "quoted": false}}, "table": {"class": "Identifier", "args": {"this": "<div id=r\\"id_1\\" class=\\"class_1\\">", "quoted": false}}}}, "alias": {"class": "Identifier", "args": {"this": "a", "quoted": false}}}}], "from": {"class": "From", "args": {"this": {"class": "Table", "args": {"this": {"class": "Identifier", "args": {"this": "b", "quoted": false}}}}}}}}]',
    # ),
    # ParseTest(
    #     #  TODO: Test tags parsing with regular defined
    #     "tags",
    #     "SELECT <div id=r\"tag\\_[a-z]+\\_\\_.+\" class=\"class_1\"> FROM b",
    #     '[{"class": "Select", "args": {"expressions": [{"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "<div id=\\"id_1\\" class=\\"class_1\\">", "quoted": false}}}}], "from": {"class": "From", "args": {"this": {"class": "Table", "args": {"this": {"class": "Identifier", "args": {"this": "b", "quoted": false}}}}}}}}]',
    # ),
    ParseTest(
        # Test LOAD parsing with not enough args
        "load_with_no_args",
        "SELECT * FROM LOAD()",
        "",
        ParseError,
    ),
    ParseTest(
        # Test LOAD parsing in both SELECT & FROM with child & alias
        "load_with_child_&_alias",
        "SELECT d.a, LOAD('https://example.org', 1).tag_1.tag_2 as b, e.c FROM LOAD('https://example.org') as d, LOAD('https://example.org', 1) as e",
        '[{"class": "Select", "args": {"expressions": [{"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "a", "quoted": false}}, "table": {"class": "Identifier", "args": {"this": "d", "quoted": false}}}}, {"class": "Alias", "args": {"this": {"class": "Dot", "args": {"this": {"class": "Dot", "args": {"this": {"class": "scraby.core.parser.LoadPage", "args": {"this": {"class": "Literal", "args": {"this": "https://example.org", "is_string": true}}, "expression": {"class": "Literal", "args": {"this": "1", "is_string": false}}}}, "expression": {"class": "Identifier", "args": {"this": "tag_1", "quoted": false}}}}, "expression": {"class": "Identifier", "args": {"this": "tag_2", "quoted": false}}}}, "alias": {"class": "Identifier", "args": {"this": "b", "quoted": false}}}}, {"class": "Column", "args": {"this": {"class": "Identifier", "args": {"this": "c", "quoted": false}}, "table": {"class": "Identifier", "args": {"this": "e", "quoted": false}}}}], "from": {"class": "From", "args": {"this": {"class": "Table", "args": {"this": {"class": "scraby.core.parser.LoadPage", "args": {"this": {"class": "Literal", "args": {"this": "https://example.org", "is_string": true}}, "expression": {"class": "Neg", "args": {"this": {"class": "Literal", "args": {"this": "1", "is_string": false}}}}}}, "alias": {"class": "TableAlias", "args": {"this": {"class": "Identifier", "args": {"this": "d", "quoted": false}}}}}}}}, "joins": [{"class": "Join", "args": {"this": {"class": "Table", "args": {"this": {"class": "scraby.core.parser.LoadPage", "args": {"this": {"class": "Literal", "args": {"this": "https://example.org", "is_string": true}}, "expression": {"class": "Literal", "args": {"this": "1", "is_string": false}}}}, "alias": {"class": "TableAlias", "args": {"this": {"class": "Identifier", "args": {"this": "e", "quoted": false}}}}}}}}]}}]',
    ),
    ParseTest(
        # Test LOAD parsing with too many arguments
        "load_with_args_over_limit",
        "SELECT * FROM LOAD('https://example.org', 1, 2)",
        "",
        ParseError,
    ),
    ParseTest(
        # Test LOAD parsing with bad 1st argument
        "load_with_bad_first_arg",
        "SELECT LOAD(1)",
        "",
        TypeError,
    ),
    ParseTest(
        # Test LOAD parsing with bad 2nd argument
        "load_with_bad_second_arg",
        "SELECT * FROM LOAD('https://example.org', '1')",
        "",
        TypeError,
    ),
], ids=lambda x: x.id)
def test_parse(case):
    if case.exc_type:
        with pytest.raises(case.exc_type):
            dialect.parse(case.sql)
    else:
        assert dumps([x.dump() for x in dialect.parse(case.sql)], default=vars) == case.exp_dump


#  TODO: completely rewrite print tests
# @dataclass
# class PrintTest:
#     """ Dataclass for print tests
#
#     Compare exp.Expression(...).sql() to predefined result sql string
#
#     """
#     id: str
#     expression: exp.Expression
#     sql: str
#     exc_type: t.Optional[type[Exception]] = None
#
#
# @pytest.mark.parametrize("case", [
#     PrintTest(
#         "test_print_load_only_args_1",
#         exp.Select(expressions=[LoadPage(
#             this=exp.Literal(this="https://example.org", is_string=True),
#             expression=exp.Neg(this=exp.Literal(this="1", is_string=False)),
#         )]),
#         "SELECT LOAD('https://example.org')",
#     ),
#     PrintTest(
#         "test_print_load_only_args_2",
#         exp.Select(expressions=[LoadPage(
#             this=exp.Literal(this="https://example.org", is_string=True),
#             expression=exp.Literal(this=1, is_string=False),
#         )]),
#         "SELECT LOAD('https://example.org', 1)",
#     ),
#     PrintTest(
#         "test_print_load_args_1",
#         exp.Select(expressions=[exp.Star()]).from_(LoadPage(
#             this=exp.Literal(this="https://example.org", is_string=True),
#             expression=exp.Neg(this=exp.Literal(this="1", is_string=False)),
#         )),
#         "SELECT * FROM LOAD('https://example.org')",
#     ),
#     PrintTest(
#         "test_print_load_args_2",
#         exp.Select(expressions=[exp.Star()]).from_(LoadPage(
#             this=exp.Literal(this="https://example.org", is_string=True),
#             expression=exp.Literal(this=1, is_string=False),
#         )),
#         "SELECT * FROM LOAD('https://example.org', 1)",
#     ),
# ])
# def test_print(case):
#     if case.exc_type:
#         with pytest.raises(case.exc_type):
#             dialect.generate(case.expression)
#     else:
#         assert dialect.generate(case.expression) == case.sql
