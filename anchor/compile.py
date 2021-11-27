import inspect
import anchor.parse as parse
import anchor.ast as ast
import anchor.symtable as symtable
import anchor.builtins as builtins


__all__ = ['execute',]


def execute(data):
    st = symtable.SymbolTable('main')

    def get_default_args(func):
        signature = inspect.signature(func)
        return {
            k: builtins.TYPE[type(v.default).__name__](v.default)
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
        }
    for identifier, function in builtins.FUNCTIONS.items():
        name = ast.Name(identifier)
        parameters = [
            ast.Name(arg)
            for arg in inspect.getfullargspec(function)[0]
        ]
        default_args = get_default_args(function)
        functiondef = ast.FunctionDef(
            name, parameters, function, default_args, is_builtin=True
        )
        functiondef.evaluate(st)
        
    parser = parse.AnchorParser(debug=True)
    a = parser.parse(data)
    return a.evaluate(st)
