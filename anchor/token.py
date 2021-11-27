from typing import *


__all__ = ['pmdict', 'kwdict', 'NAME',]


PERCENT: Literal        = 'PERCENT'
LPAR: Literal           = 'LPAR'
RPAR: Literal           = 'RPAR'
STAR: Literal           = 'STAR'
DOUBLESTAR: Literal     = 'DOUBLESTAR'
PLUS: Literal           = 'PLUS'
COMMA: Literal          = 'COMMA'
MINUS: Literal          = 'MINUS'
RARROW: Literal         = 'RARROW'
DOT: Literal            = 'DOT'
SLASH: Literal          = 'SLASH'
DOUBLESLASH: Literal    = 'DOUBLESLASH'
COLON: Literal          = 'COLON'
SEMI: Literal           = 'SEMI'
EQUAL: Literal          = 'EQUAL'
EQEQUAL: Literal        = 'EQEQUAL'
NOTEQUAL: Literal       = 'NOTEQUAL'
LESS: Literal           = 'LESS'
LESSEQUAL: Literal      = 'LESSEQUAL'
GREATER: Literal        = 'GREATER'
GREATEREQUAL: Literal   = 'GREATEREQUAL'
LSQB: Literal           = 'LSQB'
RSQB: Literal           = 'RSQB'
LBRACE: Literal         = 'LBRACE'
RBRACE: Literal         = 'RBRACE'
# tokens defined only for parsing
UPLUS: Literal          = 'UPLUS'
UMINUS: Literal         = 'UMINUS'

pmdict: dict[Literal, str] = {
    COMMA               : r',',
    LPAR                : r'\(',
    RPAR                : r'\)',
    PLUS                : r'\+',
    MINUS               : r'-',
    STAR                : r'\*',
    DOUBLESTAR          : r'\*\*',
    SLASH               : r'/',
    DOUBLESLASH         : r'//',
    PERCENT             : r'%',
    RARROW              : r'->',
    DOT                 : r'\.',
    COLON               : r':',
    SEMI                : r';',
    EQUAL               : r'=',
    EQEQUAL             : r'==',
    NOTEQUAL            : r'!=',
    LESS                : r'<',
    LESSEQUAL           : r'<=',
    GREATER             : r'>',
    GREATEREQUAL        : r'>=',
    LSQB                : r'\[',
    RSQB                : r'\]',
    LBRACE              : r'{',
    RBRACE              : r'}',
}


BEGIN: Literal          = 'BEGIN'
END: Literal            = 'END'
TRUE: Literal           = 'TRUE'
FALSE: Literal          = 'FALSE'
NULL: Literal           = 'NULL'
OR: Literal             = 'OR'
AND: Literal            = 'AND'
NOT: Literal            = 'NOT'
CLASS: Literal          = 'CLASS'
INHERIT: Literal        = 'INHERIT'
METHOD: Literal         = 'METHOD'
FUNCTION: Literal       = 'FUNCTION'
RETURN: Literal         = 'RETURN'
PROPERTY: Literal       = 'PROPERTY'
IF: Literal             = 'IF'
THEN: Literal           = 'THEN'
ELIF: Literal           = 'ELIF'
ELSE: Literal           = 'ELSE'
ITERATE: Literal        = 'ITERATE'
FOR: Literal            = 'FOR'
WHILE: Literal          = 'WHILE'
CONTINUE: Literal       = 'CONTINUE'
BREAK: Literal          = 'BREAK'
PUBLIC: Literal         = 'PUBLIC'
PRIVATE: Literal        = 'PRIVATE'
PROTECTED: Literal      = 'PROTECTED'
GET: Literal            = 'GET'
SET: Literal            = 'SET'
OPTIONAL: Literal       = 'OPTIONAL'
REF: Literal            = 'REF'
VAL: Literal            = 'VAL'

kwdict: dict[Literal, str] = {
    BEGIN               : 'begin',
    END                 : 'end',
    TRUE                : 'True',
    FALSE               : 'False',
    NULL                : 'Null',
    OR                  : 'or',
    AND                 : 'and',
    NOT                 : 'not',
    CLASS               : 'class',
    INHERIT             : 'inherit',
    METHOD              : 'method',
    FUNCTION            : 'function',
    RETURN              : 'return',
    PROPERTY            : 'property',
    IF                  : 'if',
    THEN                : 'then',
    ELIF                : 'elif',
    ELSE                : 'else',
    ITERATE             : 'iterate',
    FOR                 : 'for',
    WHILE               : 'while',
    CONTINUE            : 'continue',
    BREAK               : 'break',
    PUBLIC              : 'public',
    PRIVATE             : 'private',
    PROTECTED           : 'protected',
    GET                 : 'get',
    SET                 : 'set',
    OPTIONAL            : 'optional',
    REF                 : 'ref',
    VAL                 : 'val',
}


__all__.extend(
    [name for name, value in globals().items() if isinstance(value, str)]
)


NAME = {
    value.replace('\\', ''): name 
    for name, value in (pmdict | kwdict).items()
}
