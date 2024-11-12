from json import dumps
from dataclasses import dataclass, field
import typing as t
import pytest
from scraby.parser import dialect, exp, LoadPage, ParseError, TokenError


@dataclass
class ParseTest:
    """ Dataclass for parse tests 

    Compare list' dump of parsed expressions' dumps to predefined list' dump
    
    """
    id: str
    sql: str
    exp_dump: str
    exc_type: t.Optional[type[Exception]] = None

@pytest.mark.parametrize("case", [
    ParseTest(
        "test_parse_load_args_0",
        "SELECT * FROM LOAD()",
        "",
        ParseError,
    ),
    ParseTest(
        "test_parse_load_args_1",
        "SELECT * FROM LOAD('https://example.org')",
        '[{"class": "Select", "args": {"expressions": [{"class": "Star", "args": {}}], "from": {"class": "scraby.parser.LoadPage", "args": {"this": {"class": "Literal", "args": {"this": "https://example.org", "is_string": true}}, "expression": {"class": "Neg", "args": {"this": {"class": "Literal", "args": {"this": "1", "is_string": false}}}}}}}}]',
    ),
    ParseTest(
        "test_parse_load_args_2",
        "SELECT * FROM load('https://example.org', 1)",
        '[{"class": "Select", "args": {"expressions": [{"class": "Star", "args": {}}], "from": {"class": "scraby.parser.LoadPage", "args": {"this": {"class": "Literal", "args": {"this": "https://example.org", "is_string": true}}, "expression": {"class": "Literal", "args": {"this": "1", "is_string": false}}}}}}]',
    ),
    ParseTest(
        "test_parse_load_args_3",
        "SELECT * FROM LOAD('https://example.org', 1, 2)",
        "",
        ParseError,
    ),
    ParseTest(
        "test_parse_load_only_args_0",
        "SELECT LOAD()",
        "",
        ParseError,
    ),
    ParseTest(
        "test_parse_load_only_args_1",
        "SELECT LOAD('https://example.org')",
        '[{"class": "Select", "args": {"expressions": [{"class": "scraby.parser.LoadPage", "args": {"this": {"class": "Literal", "args": {"this": "https://example.org", "is_string": true}}, "expression": {"class": "Neg", "args": {"this": {"class": "Literal", "args": {"this": "1", "is_string": false}}}}}}]}}]',
    )
])
def test_parse(case):
    if case.exc_type:
        with pytest.raises(case.exc_type):
            dialect.parse(case.sql)
    else:
        assert dumps([x.dump() for x in dialect.parse(case.sql)]) == case.exp_dump


@dataclass
class PrintTest:
    """ Dataclass for print tests

    Compare exp.Expression(...).sql() to predefined result sql string

    """
    id: str
    expression: exp.Expression
    sql: str
    exc_type: t.Optional[type[Exception]] = None

@pytest.mark.parametrize("case", [
    PrintTest(
        "test_print_load_only_args_1",
        exp.Select(expressions=[LoadPage(
            this=exp.Literal(this="https://example.org", is_string=True),
            expression=exp.Neg(this=exp.Literal(this="1", is_string=False)),
        )]),
        "SELECT LOAD('https://example.org')",
    ),
    PrintTest(
        "test_print_load_only_args_2",
        exp.Select(expressions=[LoadPage(
            this=exp.Literal(this="https://example.org", is_string=True),
            expression=exp.Literal(this=1, is_string=False),
        )]),
        "SELECT LOAD('https://example.org', 1)",
    ),
    PrintTest(
        "test_print_load_args_1",
        exp.Select(expressions=[exp.Star()]).from_(LoadPage(
            this=exp.Literal(this="https://example.org", is_string=True),
            expression=exp.Neg(this=exp.Literal(this="1", is_string=False)),
        )),
        "SELECT * FROM LOAD('https://example.org')",
    ),
    PrintTest(
        "test_print_load_args_2",
        exp.Select(expressions=[exp.Star()]).from_(LoadPage(
            this=exp.Literal(this="https://example.org", is_string=True),
            expression=exp.Literal(this=1, is_string=False),
        )),
        "SELECT * FROM LOAD('https://example.org', 1)",
    ),
])
def test_print(case):
    if case.exc_type:
        with pytest.raises(case.exc_type):
            dialect.generate(case.expression)
    else:
        assert dialect.generate(case.expression) == case.sql
