import typing


__all__ = ['pmdict', 'kwdict', 'NAME',]


PERCENT: typing.Literal         = 'PERCENT'
LPAR: typing.Literal            = 'LPAR'
RPAR: typing.Literal            = 'RPAR'
STAR: typing.Literal            = 'STAR'
DOUBLESTAR: typing.Literal      = 'DOUBLESTAR'
PLUS: typing.Literal            = 'PLUS'
COMMA: typing.Literal           = 'COMMA'
MINUS: typing.Literal           = 'MINUS'
RARROW: typing.Literal          = 'RARROW'
DOT: typing.Literal             = 'DOT'
SLASH: typing.Literal           = 'SLASH'
DOUBLESLASH: typing.Literal     = 'DOUBLESLASH'
COLON: typing.Literal           = 'COLON'
SEMI: typing.Literal            = 'SEMI'
EQUAL: typing.Literal           = 'EQUAL'
EQEQUAL: typing.Literal         = 'EQEQUAL'
NOTEQUAL: typing.Literal        = 'NOTEQUAL'
LESS: typing.Literal            = 'LESS'
LESSEQUAL: typing.Literal       = 'LESSEQUAL'
GREATER: typing.Literal         = 'GREATER'
GREATEREQUAL: typing.Literal    = 'GREATEREQUAL'
LSQB: typing.Literal            = 'LSQB'
RSQB: typing.Literal            = 'RSQB'
LBRACE: typing.Literal          = 'LBRACE'
RBRACE: typing.Literal          = 'RBRACE'
# tokens defined only for parsing
UPLUS: typing.Literal           = 'UPLUS'
UMINUS: typing.Literal          = 'UMINUS'

pmdict: dict[typing.Literal, str] = {
    COMMA                       : r',',
    LPAR                        : r'\(',
    RPAR                        : r'\)',
    PLUS                        : r'\+',
    MINUS                       : r'-',
    STAR                        : r'\*',
    DOUBLESTAR                  : r'\*\*',
    SLASH                       : r'/',
    DOUBLESLASH                 : r'//',
    PERCENT                     : r'%',
    RARROW                      : r'->',
    DOT                         : r'\.',
    COLON                       : r':',
    SEMI                        : r';',
    EQUAL                       : r'=',
    EQEQUAL                     : r'==',
    NOTEQUAL                    : r'!=',
    LESS                        : r'<',
    LESSEQUAL                   : r'<=',
    GREATER                     : r'>',
    GREATEREQUAL                : r'>=',
    LSQB                        : r'\[',
    RSQB                        : r'\]',
    LBRACE                      : r'{',
    RBRACE                      : r'}',
}


BEGIN: typing.Literal           = 'BEGIN'
END: typing.Literal             = 'END'
TRUE: typing.Literal            = 'TRUE'
FALSE: typing.Literal           = 'FALSE'
NULL: typing.Literal            = 'NULL'
OR: typing.Literal              = 'OR'
AND: typing.Literal             = 'AND'
NOT: typing.Literal             = 'NOT'
CLASS: typing.Literal           = 'CLASS'
INHERIT: typing.Literal         = 'INHERIT'
METHOD: typing.Literal          = 'METHOD'
FUNCTION: typing.Literal        = 'FUNCTION'
RETURN: typing.Literal          = 'RETURN'
PROPERTY: typing.Literal        = 'PROPERTY'
IF: typing.Literal              = 'IF'
THEN: typing.Literal            = 'THEN'
ELIF: typing.Literal            = 'ELIF'
ELSE: typing.Literal            = 'ELSE'
ITERATE: typing.Literal         = 'ITERATE'
FOR: typing.Literal             = 'FOR'
LOOP: typing.Literal            = 'LOOP'
CONTINUE: typing.Literal        = 'CONTINUE'
BREAK: typing.Literal           = 'BREAK'
PUBLIC: typing.Literal          = 'PUBLIC'
PRIVATE: typing.Literal         = 'PRIVATE'
PROTECTED: typing.Literal       = 'PROTECTED'
GET: typing.Literal             = 'GET'
SET: typing.Literal             = 'SET'
REF: typing.Literal             = 'REF'
VAL: typing.Literal             = 'VAL'

kwdict: dict[typing.Literal, str] = {
    BEGIN                       : 'begin',
    END                         : 'end',
    TRUE                        : 'True',
    FALSE                       : 'False',
    NULL                        : 'Null',
    OR                          : 'or',
    AND                         : 'and',
    NOT                         : 'not',
    CLASS                       : 'class',
    INHERIT                     : 'inherit',
    METHOD                      : 'method',
    FUNCTION                    : 'function',
    RETURN                      : 'return',
    PROPERTY                    : 'property',
    IF                          : 'if',
    THEN                        : 'then',
    ELIF                        : 'elif',
    ELSE                        : 'else',
    ITERATE                     : 'iterate',
    FOR                         : 'for',
    LOOP                        : 'loop',
    CONTINUE                    : 'continue',
    BREAK                       : 'break',
    PUBLIC                      : 'public',
    PRIVATE                     : 'private',
    PROTECTED                   : 'protected',
    GET                         : 'get',
    SET                         : 'set',
    REF                         : 'ref',
    VAL                         : 'val',
}


__all__.extend(
    [name for name, value in globals().items() if isinstance(value, str)]
)


NAME: dict[typing.Literal, str] = {
    value.replace('\\', ''): name 
    for name, value in (pmdict | kwdict).items()
}
