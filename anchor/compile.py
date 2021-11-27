from anchor.ply import *
from anchor.lex import *
from anchor.parse import *
from anchor.symtable import *


__all__ = ['execute',]


def execute(data):
    symtable = SymbolTable('main')
    parser = AnchorParser(debug=True)
    ast = parser.parse(data)
    print(ast)
