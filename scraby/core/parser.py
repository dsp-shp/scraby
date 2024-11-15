import re
import typing as t

from copy import deepcopy
from sqlglot import exp, Generator
from sqlglot.dialects import Dialect
from sqlglot.parser import Parser, ParseError
from sqlglot.tokens import Token, TokenType, Tokenizer, TokenError
from scraby.utils.html import HTMLTag


class TagAttr(exp.Expression):
    """ Expression of the HTML tag' attribute 

    Parameters:
        this (str): stands for attribute name, e.g. "id", "class", "href", ...
        expression (str): stands for attribute value, e.g. "scrollable", "main", ...
        is_regular (bool): is expression r-prefixed regexp string or not

    """
    arg_types = {"this": True, "expression": False, "is_regular": False}


class Tag(exp.Expression):
    """ Expression of the HTML tag 

    Parameters:
        this (HTMLTag): enum element specifying this string tag, e.g. HTMLTag.DIV
        expression (TagAttr): expression specifying tag attributes

    """


class LoadPage(exp.Expression):
    """ Expression of the page loading function LOAD 

    Parameters:
        this (exp.Literal): stands for url string, e.g. "https://example.org"
        expression (exp.Literal): stands for number of pages from first to scrap

    """
    arg_types = {"this": True, "expression": False}


class ScrabyDialect(Dialect):
    """ Custom SQLGlot dialect with handling of web-related things """
    ALPHA_KEYWORDS = {
        TokenType.SET,
        TokenType.COPY,
        TokenType.LOAD,
        TokenType.SELECT,
        TokenType.FROM,
        TokenType.JOIN,
        TokenType.WHERE,
        TokenType.ORDER_BY,
        TokenType.LIMIT,
        TokenType.ALIAS,
        TokenType.COMMA,
    }
    """ Query alpha strings that break tag construction

    Example: in string "... mod<div FROM ..." tag construction starts at "<" point
    and breaks on alpha "FROM" keyword, which indicates that this part is a query
    part rather than a tag internals.
    
    """

    KEYWORDS = {
        # add single-symbol kws
        *Tokenizer.SINGLE_TOKENS.values(),
        # add punctuation kws
        *{v for k,v in Tokenizer.KEYWORDS.items() if not k.isalpha()},
        *ALPHA_KEYWORDS,
        TokenType.STRING,
        TokenType.NUMBER,
        TokenType.IDENTIFIER,
        TokenType.VAR,
        TokenType.DIV,
        #  TODO: add all other posible tokens
    }
    """ All allowed keywords including single-symbol tokens """

    TAGS = {
        *HTMLTag.__members__
    }
    """ All posible HTML tags taken from HTMLTag enum """

    class ScrabyGenerator(Generator):
        """ Custom SQLGlot generator

        Basically used for correct printing of added and modified expressions.

        """
        def loadpage_sql(self, expression: LoadPage) -> str:
            this = self.sql(expression, "this")
            expr = self.sql(expression, "expression")
            expr = f", {expr}" if expr and int(expr) > 0 else ""
            return f"LOAD({this}{expr})"

        def tag_sql(self, expression: Tag) -> str:
            #  WARNING: Tag.this should always be HTMLTag enum object
            this = expression.this.value
            attributes = ' '.join(map(
                lambda x: f"{x.this}=\"{x.expression}\"",
                expression.args.get('expressions', [])
            ))
            attributes = f" {attributes}" if attributes else ""
            return f"<{this}{attributes}>"

    class ScrabyParser(Parser):
        """ Custom SQLGLot parser 

        Basically used for correct parsing of added or modified expressions.
        
        Currently Scraby overrides:
            LOAD: to define url and pages number parameters
            TAG: to fully represent HTML tags and their children elements

        """
        # Make LOAD operator a function, so it could be correctly parsed
        FUNC_TOKENS = {*Parser.FUNC_TOKENS, TokenType.LOAD,}
        # Get rid of default exp.Tag usages in Parser to overwrite it's behavior
        DB_CREATABLES = {x for x in Parser.DB_CREATABLES if x not in (TokenType.TAG,)}
        CREATABLES = {x for x in Parser.CREATABLES if x not in (TokenType.TAG,)}

        def _parse_tag(self, tag: str) -> Tag:
            """ Parse HTML tag as expression

            Converts string tags into special expressions which are further used
            as normal SQL attributes/columns.

            """
            def _parse_tagattr(
                name_or_namevalue: str,
                value: t.Optional[str] = None
            ) -> TagAttr:
                """ Parse HTML tag' attributes as expression

                Converts 'name="value"'-like strings into TagAttr expressions.

                """
                if not value:
                    name_or_namevalue, value = name_or_namevalue.split('=', 1)
                return self.expression(
                    TagAttr,
                    this=name_or_namevalue,
                    expression=value.lstrip("r").strip("\""),
                    is_regular=value.startswith("r\"")
                )

            #  INFO: bs4 can't properly handle r-prefixed attrs with w/spaces
            name, attrs, *_ = tag.strip('<>').split(' ', 1) + ['']
            expressions = [_parse_tagattr(x) for x in re.findall(
                r'[a-z]+=r?".*?(?=" )"', attrs + " "
            )]
            return self.expression(Tag, this=HTMLTag(name), expressions=expressions)

        def _parse_loadpage(self, e: exp.Expression) -> exp.Expression:
            """ Parse LOAD stmt as expression """
            if len(e.expressions) not in (1, 2):
                raise ParseError('Bad arguments for LOAD function')

            this, expression, *_ = [
                *e.expressions,
                exp.Neg(this=exp.Literal(this='1', is_string=False))
            ]
            if not this.find(exp.Literal).is_string:
                raise TypeError('Bad type for arguments')
            if expression.find(exp.Literal).is_string:
                raise TypeError('Bad type for arguments')

            return self.expression(LoadPage, this=this, expression=expression)

        def _parse_function(self, *args, **kwargs) -> t.Optional[exp.Expression]:
            e = super()._parse_function(*args, **kwargs)
            if e and isinstance(e, exp.Anonymous) and e.this == 'LOAD':
                e = self._parse_loadpage(e)
            return e

        def _parse_identifier(self) -> t.Optional[exp.Expression]:
            if self._curr and Tag.__name__ in self._curr.comments and self._match(TokenType.VAR):
                #  INFO: dont forget to remove this TAG comment
                self._prev.comments.remove(Tag.__name__)
                return self._parse_tag(self._prev.text)
            return super()._parse_identifier()

    #  INFO: overriden in terms of defining custom parser & generator properties
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parser_class = self.ScrabyParser
        self.generator_class = self.ScrabyGenerator

    #  INFO: overriden in terms of custom tokenization
    def parse(self, sql: str, **opts) -> t.List[t.Optional[exp.Expression]]:
        """ Parse SQL string into syntax tree

        Things to do here:
        - handle HTML tags as if they are normal attributes or fields
        - handle new LOAD & READ tokens behavior and raise Exception if used wrong
        - define all allowed keywords and raise an exception if other was passed
        
        """
        tokens = self.tokenize(sql)

        #  FIX: sqlglot & SQL dont handle tags, so it should be parsed manually
        #  WARNING: end counts as included: ... text: <, start: 13, end: 13, ...
        for i, x in enumerate(tokens):
            #  INFO: raise TokenError when not allowed token used
            if not x.token_type in self.KEYWORDS:
                raise TokenError(f"Invalid expression / Unexpected token: {x}")
            #  if starts with "<", close to next and contained in TAGS
            if x.token_type == TokenType.LT \
            and tokens[i+1].start == x.end + 1 \
            and tokens[i+1].text in HTMLTag.values():
                tag_tokens: list[Token] = []
                _tokens = deepcopy(tokens[i:])
                while _tokens:
                    # reset all if has SQL statements in body
                    if _tokens[0].token_type in self.ALPHA_KEYWORDS:
                        _tokens = tag_tokens = []
                    # end tag construct if found ">"
                    elif _tokens[0].token_type == TokenType.GT:
                        tag_tokens.append(_tokens[0])
                        _tokens = []
                    # else just append tokens to list
                    else:
                        tag_tokens.append(_tokens.pop(0))

                if tag_tokens:
                    # replace range of found tag' tokens with one VAR token
                    tokens[i:i+len(tag_tokens)] = [Token(
                        token_type=TokenType.VAR,
                        # text=''.join(tag_str),
                        text=sql[tag_tokens[0].start:tag_tokens[-1].end+1],
                        line=tag_tokens[0].line,
                        start=tag_tokens[0].start,
                        end=tag_tokens[-1].end+1,
                        comments=['Tag']
                    )]

        result = self.parser(**opts).parse(tokens, sql)
        return result


dialect = ScrabyDialect()


def parse(sql: str, **kwargs) -> list[t.Optional[exp.Expression]]:
    return dialect.parse(sql, **kwargs)
