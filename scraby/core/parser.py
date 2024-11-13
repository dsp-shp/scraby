from copy import deepcopy
import typing as t

from sqlglot import exp, Generator
from sqlglot.dialects import Dialect
from sqlglot.parser import Parser, ParseError
from sqlglot.tokens import Token, TokenType, Tokenizer, TokenError


class LoadPage(exp.Expression):
    """ Expression of the page loading function LOAD """
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
    """ These keywords are alpha strings that can be used in query and that will
        break tag construction: "... mod<div FROM ..." -> less than and not a tag
    """

    KEYWORDS = {
        ### add single-symbol kws
        *Tokenizer.SINGLE_TOKENS.values(),
        ### add punctuation kws
        *{v for k,v in Tokenizer.KEYWORDS.items() if not k.isalpha()},
        *ALPHA_KEYWORDS,
        TokenType.STRING,
        TokenType.NUMBER,
        TokenType.IDENTIFIER,
        TokenType.VAR,
        TokenType.DIV,
        #  TODO: add all posible tokens
    }
    """ All allowed keywords including single-symbol tokens """

    #  TODO: add all other
    TAGS = ("a", "div", "span")
    """ All posible HTML tags """

    class ScrabyGenerator(Generator):
        """ Custom generator with support of printing syntax trees  """
        def loadpage_sql(self, expression: LoadPage) -> str:
            this = self.sql(expression, "this")
            expr = self.sql(expression, "expression")
            expr = f", {expr}" if expr and int(expr) > 0 else ""
            return f"LOAD({this}{expr})"

    class ScrabyParser(Parser):
        """ Custom parser used to support correct parsing of new features """
        FUNC_TOKENS = {*Parser.FUNC_TOKENS, TokenType.LOAD,}

        def _parse_loadpage(self, e: exp.Expression) -> exp.Expression:
            """ Parse LOAD expression

            """
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
        print('\n'.join(str(x) for x in tokens))

        #  FIX: sqlglot & SQL dont handle tags, so it should be parsed manually
        #  WARNING: end counts as included: ... text: <, start: 13, end: 13, ...
        for i, x in enumerate(tokens):
            #  INFO: raise TokenError when not allowed token used
            if not x.token_type in self.KEYWORDS:
                raise TokenError(f"Invalid expression / Unexpected token: {x}")
            #  if starts with "<", close to next and contained in TAGS
            if x.token_type == TokenType.LT \
            and tokens[i+1].start == x.end + 1 \
            and tokens[i+1].text in self.TAGS:
                print(x.text)
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
                        end=tag_tokens[-1].end+1
                    )]

        print('\n' + '\n'.join(str(x) for x in tokens))
        result = self.parser(**opts).parse(tokens, sql)
        return result

dialect = ScrabyDialect()

def parse(sql: str, **kwargs) -> list[t.Optional[exp.Expression]]:
    return dialect.parse(sql, **kwargs)
