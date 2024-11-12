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
    TAGS = ("a", "div",)
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
        #  TODO: make statements LOAD(...).(smth)... parseable
        #  TODO: make SELECT LOAD(...) AS "..." ... parseable
        def _parse_load(self):
            this = self._parse_assignment()

            #  INFO: with only url defined returns exp.Paren instead of exp.Tuple
            if isinstance(this, exp.Paren) and not this.args.get('expressions'):
                this = exp.Tuple(expressions=[
                    this.this,
                    exp.Neg(this=exp.Literal(this='1', is_string=False))
                ])

            if len(this.expressions) not in (1, 2):
                raise ParseError('Bad arguments for LOAD operator')
            this, expression, *_ = this.expressions

            #  TODO: validate url & pages_num types

            return LoadPage(this=this, expression=expression)

        def _parse_from(
            self,
            joins: bool = False,
            skip_from_token: bool = False
        ) -> t.Optional[exp.From]:
            if not skip_from_token and not self._match(TokenType.FROM):
                return None
            if self._match(TokenType.LOAD):
                return self._parse_load()
            return self.expression(
                exp.From, comments=self._prev_comments, this=self._parse_table(joins=joins)
            )

        def _parse_csv(
            self,
            parse_method: t.Callable,
            sep: TokenType = TokenType.COMMA
        ) -> t.List[exp.Expression]:
            parse_result = parse_method()
            items = [parse_result] if parse_result is not None else []

            while self._match(sep):
                if self._match(TokenType.LOAD):
                    items.append(self._parse_load())
                else:
                    self._add_comments(parse_result)
                    parse_result = parse_method()
                    if parse_result is not None:
                        items.append(parse_result)

            return items

        def _parse_expressions(self) -> t.List[exp.Expression]:
            if self._match(TokenType.LOAD):
                return self._parse_csv(self._parse_load)
            return self._parse_csv(self._parse_expression)

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
        # print('\n'.join(str(x) for x in tokens))

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

        result = self.parser(**opts).parse(tokens, sql)
        return result

dialect = ScrabyDialect()

def parse(sql: str, **kwargs) -> list[t.Optional[exp.Expression]]:
    return dialect.parse(sql, **kwargs)
