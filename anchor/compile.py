import anchor.parse as parse
import anchor.symtable as symtable


__all__ = ['execute',]


def execute(data):
    st = symtable.SymbolTable('main')
    parser = parse.AnchorParser(debug=True)
    ast = parser.parse(data)
    print(ast)
