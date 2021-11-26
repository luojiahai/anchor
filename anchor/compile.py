from anchor.ply import *
from anchor.lex import *
from anchor.parse import *


__all__ = ['execute',]


def execute(data):
    # Parse
    parser = AnchorParser(debug=True)
    ast = parser.parse(data)
    print(ast)


