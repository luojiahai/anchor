import inspect
import anchor.system as system
import anchor.parse as parse
import anchor.ast as ast
import anchor.symtable as symtable
import anchor.builtins as builtins


__all__ = ['execute',]


def execute(data):
    st = symtable.SymbolTable('main')

    # Include builtin functions
    for identifier, function in builtins.FUNCTION.items():
        name = ast.Name(identifier)
        parameters = list([ast.Name(arg) for arg in inspect.getfullargspec(function)[0]])
        functiondef = ast.FunctionDef(name, parameters, function, isbuiltin=True)
        functiondef.evaluate(st)
        
    parser = parse.AnchorParser(
        debuglex=system.GLOBAL.debuglex, 
        debugyacc=system.GLOBAL.debugyacc,
        debuglog=system.GLOBAL.log,
    )
    a = parser.parse(data)
    return a.evaluate(st)
