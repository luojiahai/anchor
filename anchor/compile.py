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
    for identifier, fnptr in builtins.FUNCTION.items():
        name = ast.Name(identifier)
        parameters = list([ast.Name(arg) for arg in inspect.getfullargspec(fnptr)[0]])
        functiondef = ast.FunctionDef(name, parameters, None, ptr=fnptr, isbuiltin=True)
        functiondef.evaluate(st)

    # Include builtin classes
    for identifier, clsptr in builtins.CLASS.items():
        name = ast.Name(identifier)
        superclasses = list()
        properties = list()
        methods = list()
        for fnid, fnptr in inspect.getmembers(clsptr, predicate=inspect.isfunction):
            fnids = fnid.split('_')
            if (fnids[0] == 'Anchor'):
                fnname = ast.Name(fnids[1])
                parameters = list([ast.Name(arg) for arg in inspect.getfullargspec(fnptr)[0]])[1:]
                method = ast.FunctionDef(fnname, parameters, fnptr, isbuiltin=True)
                methods.append(method)
        block = ast.Block(properties + methods)
        csdef = ast.ClassDef(name, superclasses, block, isbuiltin=True)
        csdef.evaluate(st)
    
    # Parse
    parser = parse.AnchorParser(
        debuglex=system.GLOBAL.debuglex, 
        debugyacc=system.GLOBAL.debugyacc,
        debuglog=system.GLOBAL.log,
    )
    a = parser.parse(data)
    return a.evaluate(st)
