import anchor.ply as ply
import anchor.token as token
import anchor.keyword as keyword


__all__ = ['AnchorLexer',]


# Regular expression utility functions
def group(*choices):    return '(' + '|'.join(choices) + ')'
def any(*choices):      return group(*choices) + '*'
def maybe(*choices):    return group(*choices) + '?'

# Ignore
Whitespace              = r'[ \f\t]*'
Comment                 = r'\#[^\r\n]*'
Ignore                  = Whitespace + any(r'\\\r?\n' + Whitespace) + maybe(Comment)

# Number
Hexnumber               = r'0[xX](?:_?[0-9a-fA-F])+'
Binnumber               = r'0[bB](?:_?[01])+'
Octnumber               = r'0[oO](?:_?[0-7])+'
Decnumber               = r'(?:0(?:_?0)*|[1-9](?:_?[0-9])*)'
Intnumber               = group(Hexnumber, Binnumber, Octnumber, Decnumber)
Exponent                = r'[eE][-+]?[0-9](?:_?[0-9])*'
Pointfloat              = group(
                            r'[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?',
                            r'\.[0-9](?:_?[0-9])*') + maybe(Exponent
                        )
Expfloat                = r'[0-9](?:_?[0-9])*' + Exponent
Floatnumber             = group(Pointfloat, Expfloat)
Imagnumber              = group(r'[0-9](?:_?[0-9])*[jJ]', Floatnumber + r'[jJ]')
Number                  = group(Imagnumber, Floatnumber, Intnumber)

# String
String = group(r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'", r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"')


class AnchorLexer:

    # List of token names
    tokens = tuple(token.EXACT_TOKEN_TYPES.values()) + (
        'NAME', 'INTEGER', 'FLOAT', 'COMPLEX', 'STRING',
    )

    # Regular expression rules for tokens
    t_ignore            = ' \f\t'
    t_ignore_COMMENT    = Comment
    t_INTEGER           = Intnumber
    t_FLOAT             = Floatnumber
    t_COMPLEX           = Imagnumber
    t_STRING            = String
    t_LPAR              = token.pmdict[token.LPAR]
    t_RPAR              = token.pmdict[token.RPAR]
    t_STAR              = token.pmdict[token.STAR]
    t_DOUBLESTAR        = token.pmdict[token.DOUBLESTAR]
    t_PLUS              = token.pmdict[token.PLUS]
    t_COMMA             = token.pmdict[token.COMMA]
    t_MINUS             = token.pmdict[token.MINUS]
    t_RARROW            = token.pmdict[token.RARROW]
    t_DOT               = token.pmdict[token.DOT]
    t_SLASH             = token.pmdict[token.SLASH]
    t_DOUBLESLASH       = token.pmdict[token.DOUBLESLASH]
    t_PERCENT           = token.pmdict[token.PERCENT]
    t_COLON             = token.pmdict[token.COLON]
    t_SEMI              = token.pmdict[token.SEMI]
    t_LESS              = token.pmdict[token.LESS]
    t_LESSEQUAL         = token.pmdict[token.LESSEQUAL]
    t_EQUAL             = token.pmdict[token.EQUAL]
    t_EQEQUAL           = token.pmdict[token.EQEQUAL]
    t_NOTEQUAL          = token.pmdict[token.NOTEQUAL]
    t_GREATER           = token.pmdict[token.GREATER]
    t_GREATEREQUAL      = token.pmdict[token.GREATEREQUAL]
    t_LSQB              = token.pmdict[token.LSQB]
    t_RSQB              = token.pmdict[token.RSQB]
    t_LBRACE            = token.pmdict[token.LBRACE]
    t_RBRACE            = token.pmdict[token.RBRACE]

    # Name
    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        if (keyword.iskeyword(t.value)):
            t.type = token.EXACT_TOKEN_TYPES[t.value]
        return t

    # Define a rule for newline so we can track line numbers
    def t_NEWLINE(self, t):
        r'\n'
        t.lexer.lineno += 1

    # Error handling rule
    def t_error(self, t):
        t.lexer.skip(1)

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = ply.lex.lex(module=self, **kwargs)

    # Test it output
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: 
                break
            print(tok)


# -----------------------------------------------------------------------------
# END lex.py
# -----------------------------------------------------------------------------
