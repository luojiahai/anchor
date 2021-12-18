import typing
import anchor.system as system
import anchor.token as token
import anchor.keyword as keyword
import anchor.ply.lex as lex


__all__: typing.List[str] = list(['AnchorLexer',])


# Regular expression utility functions
def group(*choices) -> typing.AnyStr: return '(' + '|'.join(choices) + ')'
def any(*choices) -> typing.AnyStr: return group(*choices) + '*'
def maybe(*choices) -> typing.AnyStr: return group(*choices) + '?'

# Comment
Comment: typing.AnyStr = r'\#[^\r\n]*'

# Number
Hexnumber: typing.AnyStr = r'0[xX](?:_?[0-9a-fA-F])+'
Binnumber: typing.AnyStr = r'0[bB](?:_?[01])+'
Octnumber: typing.AnyStr = r'0[oO](?:_?[0-7])+'
Decnumber: typing.AnyStr = r'(?:0(?:_?0)*|[1-9](?:_?[0-9])*)'
Intnumber: typing.AnyStr = group(Hexnumber, Binnumber, Octnumber, Decnumber)
Exponent: typing.AnyStr = r'[eE][-+]?[0-9](?:_?[0-9])*'
Pointfloat: typing.AnyStr = group(
    r'[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?',
    r'\.[0-9](?:_?[0-9])*') + maybe(Exponent
)
Expfloat: typing.AnyStr = r'[0-9](?:_?[0-9])*' + Exponent
Floatnumber: typing.AnyStr = group(Pointfloat, Expfloat)
Imagnumber: typing.AnyStr = group(r'[0-9](?:_?[0-9])*[jJ]', Floatnumber + r'[jJ]')
Number: typing.AnyStr = group(Imagnumber, Floatnumber, Intnumber)

# String
String: typing.AnyStr = group(
    r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'", r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"'
)


class AnchorLexer(object):

    # List of token names
    tokens = tuple(token.NAME.values()) + tuple((
        'NAME', 'INTEGER', 'FLOAT', 'COMPLEX', 'STRING',
    ))

    # Regular expression rules for tokens
    t_ignore            = ' \f\t'
    t_ignore_COMMENT    = Comment
    t_INTEGER           = Intnumber
    t_FLOAT             = Floatnumber
    t_COMPLEX           = Imagnumber
    t_STRING            = String
    t_LPAR              = token.namedict[token.LPAR]
    t_RPAR              = token.namedict[token.RPAR]
    t_STAR              = token.namedict[token.STAR]
    t_DOUBLESTAR        = token.namedict[token.DOUBLESTAR]
    t_PLUS              = token.namedict[token.PLUS]
    t_COMMA             = token.namedict[token.COMMA]
    t_MINUS             = token.namedict[token.MINUS]
    t_RARROW            = token.namedict[token.RARROW]
    t_DOT               = token.namedict[token.DOT]
    t_SLASH             = token.namedict[token.SLASH]
    t_DOUBLESLASH       = token.namedict[token.DOUBLESLASH]
    t_PERCENT           = token.namedict[token.PERCENT]
    t_COLON             = token.namedict[token.COLON]
    t_SEMI              = token.namedict[token.SEMI]
    t_LESS              = token.namedict[token.LESS]
    t_LESSEQUAL         = token.namedict[token.LESSEQUAL]
    t_EQUAL             = token.namedict[token.EQUAL]
    t_EQEQUAL           = token.namedict[token.EQEQUAL]
    t_NOTEQUAL          = token.namedict[token.NOTEQUAL]
    t_GREATER           = token.namedict[token.GREATER]
    t_GREATEREQUAL      = token.namedict[token.GREATEREQUAL]
    t_LSQB              = token.namedict[token.LSQB]
    t_RSQB              = token.namedict[token.RSQB]
    t_LBRACE            = token.namedict[token.LBRACE]
    t_RBRACE            = token.namedict[token.RBRACE]

    # Name
    def t_NAME(self, t: lex.LexToken) -> lex.LexToken:
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        if (keyword.iskeyword(t.value)):
            t.type = token.NAME[t.value]
        return t

    # Define a rule for newline so we can track line numbers
    def t_NEWLINE(self, t: lex.LexToken) -> lex.LexToken:
        r'\n'
        t.lexer.lineno += 1

    # Error handling rule
    def t_error(self, t: lex.LexToken) -> lex.LexToken:
        t.lexer.skip(1)

    # Build the lexer
    def build(self, **kwargs) -> None:
        self.lexer = lex.lex(module=self, **kwargs)

    # Test
    def debug(self, data: str) -> None:
        self.lexer.input(data)
        while True:
            t: lex.LexToken = self.lexer.token()
            if (not t): 
                break
            system.GLOBAL.logger.debug(t)
